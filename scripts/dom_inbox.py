#!/usr/bin/env python3
"""Dom's inbox: every open decision the scheduled runs leave for Dom, in one
place (CLAUDE.md rule 37, amendment 2026-11-17).

Before this, open items were spread over rating-proposals.md (47 open, the
oldest a month old), report paragraphs, log lines and one-line Mac banners, and
the reports carried only a count. This script collects them, ranks them by what
touches money, and writes `tracking/needs-dom.md`. Scheduled runs rebuild it and
mirror it to a Notion table where Dom ticks Approve / Decline / Discuss.

Sources:
  rating   — `tracking/rating-proposals.md` entries whose Status is PROPOSED
  hold     — `00-master/entry-holds.json` holds lapsed or expiring within 10 days
  ask      — `tracking/dom-asks.json`: anything else a run needs Dom for (EPS
             rulings, data fixes, hold candidates a run may not add, questions)

Commands:
  build                       write tracking/needs-dom.md, print a one-line summary
  summary                     print the one-line summary only (for the notification)
  list [--json]               print open items
  expire [--dry-run]          mark stale and superseded rating proposals
  ask --kind K --ticker T --text ... [--source S] [--key K]
  close ID --note "..."       close an ask (Dom decided, or it no longer applies)
  notion-plan                 JSON: rows to create, re-prioritise and close in Notion
  notion-record [--created ID=PAGE ...] [--closed ID ...]   after writing to Notion

It never changes a rating, a score, a hold or a ruling. `expire` only rewrites
the Status line of a proposal nobody acted on.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROPOSALS = ROOT / 'tracking/rating-proposals.md'
HOLDS = ROOT / '00-master/entry-holds.json'
OVERRIDES = ROOT / '00-master/eps-yoy-overrides.json'
ASKS = ROOT / 'tracking/dom-asks.json'
INBOX = ROOT / 'tracking/needs-dom.md'
NOTION_MAP = ROOT / 'tracking/needs-dom-notion.json'
SCORE_HISTORY = ROOT / 'tracking/score-history.csv'

# The Notion table "Dom inbox" (child of the AI Supply Chain overview page).
NOTION_DB_URL = 'https://app.notion.com/p/41cb69da11c0817284b1cb6eb543c7f0'
NOTION_DATA_SOURCE = 'collection://41cb69da-11c0-8108-b90f-000b01ecac83'
NOTION_TEXT_MAX = 600           # a phone-readable summary; the Source holds the rest

# A proposal built on prices or estimate revisions (M1, M2) describes a market
# that has moved on within two weeks; everything else rests on filings and
# lasts longer. Expired proposals are re-checked by /rating-research, not lost.
TTL_DAYS = {'M1': 14, 'M2': 14}
DEFAULT_TTL_DAYS = 45
HOLD_WARN_DAYS = 10
HOLD_URGENT_DAYS = 3
HOLD_LAPSED_DAYS = 30
TOP_RANK = 25
ASK_KINDS = ('eps_ruling', 'data_fix', 'hold_candidate', 'question')

PRIORITY_LABEL = {1: 'Decide first', 2: 'Held or top 25', 3: 'Everything else'}

_HEAD = re.compile(
    r'^## (\d{4}-\d{2}-\d{2}) — ([A-Z0-9.\-]+) — ([A-Z]\d)\b(.*?)'
    r'(\d)\s*→\s*(\d)\s*(?:\((.*)\))?\s*$')


def _date(s) -> dt.date | None:
    try:
        return dt.date.fromisoformat(str(s)[:10])
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------- proposals

def parse_proposals(text: str) -> list[dict]:
    """Every rating proposal in the file, open or not, with its line number."""
    lines = text.split('\n')
    out, cur = [], None
    for i, line in enumerate(lines, 1):
        if line.startswith('## '):
            m = _HEAD.match(line)
            cur = None
            if m:
                date, t, dim, name, old, new, conf = m.groups()
                cur = {'date': date, 'ticker': t, 'dim': dim,
                       'name': name.strip(), 'old': int(old), 'new': int(new),
                       'confidence': (conf or '').replace('confidence', '').strip(),
                       'line': i, 'status': None, 'status_line': None,
                       'effect': '', 'why': ''}
                out.append(cur)
            continue
        if cur is None:
            continue
        if line.startswith('Status:') and cur['status'] is None:
            cur['status'] = line[len('Status:'):].strip()
            cur['status_line'] = i
        elif line.startswith('Effect if approved:'):
            cur['effect'] = line[len('Effect if approved:'):].strip()
        elif line.startswith('Why:'):
            cur['why'] = line[len('Why:'):].strip()
    return out


def is_open(p: dict) -> bool:
    return bool(p['status']) and p['status'].startswith('PROPOSED')


def proposal_id(p: dict) -> str:
    return f"rating:{p['date']}:{p['ticker']}:{p['dim']}"


def ttl_days(dim: str) -> int:
    return TTL_DAYS.get(dim, DEFAULT_TTL_DAYS)


def expiry_plan(props: list[dict], today: dt.date) -> list[tuple[dict, str]]:
    """(proposal, new Status text) for open proposals to retire: superseded
    by a newer open proposal on the same name and dimension, or past TTL."""
    plan, newest = [], {}
    for p in props:
        if is_open(p):
            k = (p['ticker'], p['dim'])
            if k not in newest or p['date'] >= newest[k]['date']:
                newest[k] = p
    for p in props:
        if not is_open(p):
            continue
        n = newest[(p['ticker'], p['dim'])]
        if n is not p:
            plan.append((p, f"SUPERSEDED {today} by the {n['date']} proposal "
                            f"(dom_inbox expire)"))
            continue
        age = (today - _date(p['date'])).days
        if age > ttl_days(p['dim']):
            plan.append((p, f"EXPIRED {today} — {age} days old, past the "
                            f"{ttl_days(p['dim'])}-day limit for {p['dim']}; "
                            f"/rating-research re-checks it if the name is held "
                            f"or top {TOP_RANK} (dom_inbox expire)"))
    return plan


def apply_expiry(text: str, plan: list[tuple[dict, str]]) -> str:
    lines = text.split('\n')
    for p, status in plan:
        i = p['status_line'] - 1
        assert lines[i].startswith('Status:'), lines[i]
        lines[i] = f'Status: {status}'
    return '\n'.join(lines)


def _effect_bits(effect: str) -> tuple[str, bool]:
    m = re.search(r'Total\s+([\d.]+)\s*→\s*([\d.]+)', effect)
    r = re.search(r'rank\s+(\d+)\s*→\s*(\d+)', effect)
    bits = []
    if m:
        bits.append(f'{m.group(1)}→{m.group(2)}')
    if r:
        bits.append(f'rank {r.group(1)}→{r.group(2)}')
    moves = bool(re.search(r'membership change:\s*yes', effect, re.I))
    return ', '.join(bits), moves


# ---------------------------------------------------------------- holds / asks

def hold_items(holds: dict, today: dt.date) -> list[dict]:
    out = []
    for t, h in holds.items():
        if t.startswith('_') or not isinstance(h, dict):
            continue
        exp = _date(h.get('expires'))
        if exp is None:
            out.append({'id': f'hold:{t}:unreadable', 'kind': 'hold', 'ticker': t,
                        'title': f'{t} entry hold has no readable expiry (fails closed)',
                        'raised': h.get('set') or str(today), 'urgent': True,
                        'detail': h.get('reason', ''), 'expires': None,
                        'source': '00-master/entry-holds.json'})
            continue
        days = (exp - today).days
        # Ask from 10 days before expiry until 30 days after it. A lapsed hold
        # no longer blocks entry, so after a month the default has stood.
        if days > HOLD_WARN_DAYS or days < -HOLD_LAPSED_DAYS:
            continue
        if days < 0:
            title = (f'{t} entry hold lapsed {exp} — it can enter again. '
                     f'Renew it, or confirm the lapse?')
        else:
            when = 'expires today' if days == 0 else f'expires {exp}'
            title = f'{t} entry hold {when}: renew, or let it lapse?'
        out.append({
            'id': f'hold:{t}:{exp}', 'kind': 'hold', 'ticker': t,
            'title': title,
            'raised': str(min(today, exp - dt.timedelta(days=HOLD_WARN_DAYS))),
            'expires': str(exp), 'urgent': abs(days) <= HOLD_URGENT_DAYS,
            'detail': f"{str(h.get('reason', '')).rstrip('. ')}. Review event: "
                      f"{h.get('review_event', 'n/a')}",
            'source': '00-master/entry-holds.json'})
    return out


def ask_key(kind: str, ticker: str, key: str | None) -> str:
    return f"{kind}:{ticker or '-'}" + (f':{key}' if key else '')


def ask_items(asks: dict, overrides: dict) -> list[dict]:
    out = []
    for aid, a in asks.items():
        if aid.startswith('_') or a.get('closed'):
            continue
        t = a.get('ticker') or ''
        if a.get('kind') == 'eps_ruling':
            ruled = _date((overrides.get(t) or {}).get('ruled'))
            raised = _date(a.get('raised'))
            if ruled and raised and ruled >= raised:
                continue                       # Dom ruled after it was asked
        label = {'eps_ruling': 'EPS YoY ruling (rule 15)',
                 'data_fix': 'Data fix', 'hold_candidate': 'Entry-hold candidate (rule 35)',
                 'question': 'Question'}.get(a.get('kind'), a.get('kind', 'Ask'))
        out.append({'id': f'ask:{aid}', 'kind': a.get('kind', 'question'),
                    'ticker': t, 'title': f'{t + " " if t else ""}{label}: {a.get("text", "")}',
                    'raised': a.get('raised'), 'expires': None,
                    'urgent': bool(a.get('urgent')), 'detail': '',   # the title carries it
                    'source': a.get('source', 'tracking/dom-asks.json')})
    return out


# ---------------------------------------------------------------- context

def portfolio_context(root: Path = ROOT) -> tuple[set, dict, list[str]]:
    """(held tickers, {ticker: latest rank}, problems). A failed read is
    reported, never treated as 'nothing held' silently (rule 3)."""
    problems, held, ranks = [], set(), {}
    try:
        sys.path.insert(0, str(root / 'scripts'))
        from portfolio_theses import portfolio_tickers
        held = set(portfolio_tickers(root))
    except Exception as e:                                  # noqa: BLE001
        problems.append(f'could not read held names ({type(e).__name__})')
    try:
        import csv
        rows = list(csv.DictReader(open(root / 'tracking/score-history.csv')))
        last = max(r['date'] for r in rows)
        ranks = {r['ticker']: int(r['rank']) for r in rows if r['date'] == last}
    except Exception as e:                                  # noqa: BLE001
        problems.append(f'could not read ranks ({type(e).__name__})')
    return held, ranks, problems


def priority(item: dict, held: set, ranks: dict) -> int:
    t = item.get('ticker')
    if item.get('moves_membership') or item.get('urgent'):
        return 1
    if item['kind'] == 'eps_ruling' and t in held:
        return 1        # a blank or unruled EPS cell keeps a held name's buys off tickets
    if t in held or ranks.get(t, 10**6) <= TOP_RANK:
        return 2
    return 3


def collect(root: Path = ROOT, today: dt.date | None = None) -> dict:
    today = today or dt.date.today()
    props = parse_proposals((root / 'tracking/rating-proposals.md').read_text())
    held, ranks, problems = portfolio_context(root)
    items = []
    for p in props:
        if not is_open(p):
            continue
        eff, moves = _effect_bits(p['effect'])
        exp = _date(p['date']) + dt.timedelta(days=ttl_days(p['dim']))
        cond = '' if p['status'] == 'PROPOSED' else f" [{p['status'][len('PROPOSED'):].strip(' —-')}]"
        items.append({
            'id': proposal_id(p), 'kind': 'rating', 'ticker': p['ticker'],
            'title': f"{p['ticker']} {p['dim']} {p['name']} {p['old']} → {p['new']}"
                     f"{' (' + p['confidence'] + ')' if p['confidence'] else ''}{cond}",
            'raised': p['date'], 'expires': str(exp), 'effect': eff,
            'moves_membership': moves, 'detail': p['why'],
            'source': f"tracking/rating-proposals.md:{p['line']}"})
    try:
        holds = json.loads((root / '00-master/entry-holds.json').read_text())
        items += hold_items(holds, today)
    except (OSError, ValueError) as e:
        problems.append(f'could not read entry holds ({type(e).__name__})')
    asks = _load(root / 'tracking/dom-asks.json')
    try:
        overrides = json.loads((root / '00-master/eps-yoy-overrides.json').read_text())
    except (OSError, ValueError):
        overrides = {}
    items += ask_items(asks, overrides)
    for it in items:
        it['priority'] = priority(it, held, ranks)
        it['held'] = it.get('ticker') in held
        it['rank'] = ranks.get(it.get('ticker'))
    items.sort(key=lambda i: (i['priority'], i.get('raised') or '', i['id']))
    stale = sum(1 for p, _ in expiry_plan(props, today))
    return {'today': str(today), 'items': items, 'problems': problems,
            'expirable': stale}


# ---------------------------------------------------------------- output

def summary_line(c: dict) -> str:
    items = c['items']
    if not items:
        return 'Inbox: nothing waiting for you.'
    first = [i for i in items if i['priority'] == 1]
    s = f'Inbox: {len(items)} open'
    if first:
        names = sorted({i['ticker'] for i in first if i.get('ticker')})
        s += f", {len(first)} to decide first ({', '.join(names[:5])})"
    if c['expirable']:
        s += f", {c['expirable']} stale (run expire)"
    return s + '.'


def render(c: dict) -> str:
    out = ['# Needs Dom', '',
           'Generated by `scripts/dom_inbox.py build` — do not edit by hand. '
           'Decide in the Notion table "Dom inbox" or run `/review-inbox` in a '
           'session; the source file named on each line is the record.', '',
           f"_{summary_line(c)}_  ", f"_Built {c['today']}._", '']
    for prob in c['problems']:
        out.append(f'> **Could not check:** {prob} — priorities may be understated.')
    if c['problems']:
        out.append('')
    for pr in (1, 2, 3):
        group = [i for i in c['items'] if i['priority'] == pr]
        if not group:
            continue
        out += [f'## {PRIORITY_LABEL[pr]} ({len(group)})', '']
        for i in group:
            tags = []
            if i.get('held'):
                tags.append('held')
            elif i.get('rank'):
                tags.append(f"rank {i['rank']}")
            if i.get('moves_membership'):
                tags.append('**changes the portfolio**')
            if i.get('effect'):
                tags.append(i['effect'])
            tags.append(f"raised {i['raised']}")
            if i.get('expires') and i['kind'] == 'rating':
                tags.append(f"stale after {i['expires']}")
            out.append(f"- **{i['title']}** — {'; '.join(tags)}. "
                       f"[{i['source']}]({_link(i['source'])}) `{i['id']}`")
        out.append('')
    if not c['items']:
        out += ['Nothing waiting.', '']
    return '\n'.join(out)


def _link(source: str) -> str:
    """Relative link from tracking/needs-dom.md to a source like
    `tracking/rating-proposals.md:88` or `tracking/x.md (2026-11-02)`."""
    path = source.split(' (')[0].strip()
    path, _, line = path.partition(':')
    rel = path[len('tracking/'):] if path.startswith('tracking/') else '../' + path
    return f'{rel}#L{line}' if line.isdigit() else rel


# ---------------------------------------------------------------- state files

def _load(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return {}


def _save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + '\n')


def add_ask(asks: dict, kind: str, ticker: str, text: str, source: str | None,
            key: str | None, today: dt.date, urgent: bool = False) -> str:
    if kind not in ASK_KINDS:
        raise ValueError(f'kind must be one of {ASK_KINDS}')
    aid = ask_key(kind, ticker, key)
    prev = asks.get(aid)
    if prev and not prev.get('closed'):
        prev.update({'text': text, 'source': source or prev.get('source'),
                     'updated': str(today), 'urgent': urgent or prev.get('urgent', False)})
        return aid
    if prev:                       # closed earlier: keep the record, open a new one
        aid = f'{aid}:{today}'
    asks[aid] = {'kind': kind, 'ticker': ticker, 'text': text,
                 'source': source or '', 'raised': str(today), 'urgent': urgent}
    return aid


def close_ask(asks: dict, aid: str, note: str, today: dt.date) -> None:
    aid = aid[len('ask:'):] if aid.startswith('ask:') else aid
    if aid not in asks:
        raise KeyError(aid)
    asks[aid].update({'closed': str(today), 'note': note})


def notion_properties(i: dict) -> dict:
    """One row of the Notion table, in the create-pages property format."""
    def cut(s):
        s = ' '.join(str(s or '').split())
        return s if len(s) <= NOTION_TEXT_MAX else s[:NOTION_TEXT_MAX - 1] + '…'
    props = {'Item': cut(i['title']), 'Inbox ID': i['id'], 'Kind': i['kind'],
             'Priority': f"{i['priority']} {PRIORITY_LABEL[i['priority']]}",
             'Ticker': i.get('ticker') or '', 'Effect': cut(i.get('effect')),
             'Why': cut(i.get('detail')), 'Source': cut(i.get('source')),
             'State': 'Open'}
    if i.get('raised'):
        props['date:Raised:start'] = str(i['raised'])[:10]
    if i.get('expires') and i['kind'] == 'rating':
        props['date:Stale after:start'] = str(i['expires'])[:10]
    return props


def notion_plan(c: dict, mapping: dict) -> dict:
    """Rows to create (open items with no page yet), pages to close (tracked
    items no longer open) and pages whose priority changed since they were
    written, so the table's sort stays true. `mapping` is
    {id: {"page": url, "priority": n}}."""
    items = {i['id']: i for i in c['items']}
    tracked = {k: v for k, v in mapping.items() if not k.startswith('_')}
    return {
        'data_source': NOTION_DATA_SOURCE,
        'create': [notion_properties(i) for i in c['items'] if i['id'] not in tracked],
        'update': [{'id': k, 'page': v['page'],
                    'Priority': f"{items[k]['priority']} {PRIORITY_LABEL[items[k]['priority']]}"}
                   for k, v in sorted(tracked.items())
                   if k in items and v.get('priority') != items[k]['priority']],
        'close': [{'id': k, 'page': v['page']} for k, v in sorted(tracked.items())
                  if k not in items]}


# ---------------------------------------------------------------- cli

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('build')
    sub.add_parser('summary')
    ls = sub.add_parser('list')
    ls.add_argument('--json', action='store_true')
    ex = sub.add_parser('expire')
    ex.add_argument('--dry-run', action='store_true')
    a = sub.add_parser('ask')
    a.add_argument('--kind', required=True, choices=ASK_KINDS)
    a.add_argument('--ticker', default='')
    a.add_argument('--text', required=True)
    a.add_argument('--source')
    a.add_argument('--key', help='distinguishes two asks of one kind on one name')
    a.add_argument('--urgent', action='store_true')
    cl = sub.add_parser('close')
    cl.add_argument('id')
    cl.add_argument('--note', required=True)
    sub.add_parser('notion-plan')
    nr = sub.add_parser('notion-record')
    nr.add_argument('--created', nargs='*', default=[], metavar='ID=PAGE',
                    help='rows written (or re-prioritised) in Notion')
    nr.add_argument('--closed', nargs='*', default=[], metavar='ID')
    args = ap.parse_args(argv)
    today = dt.date.today()

    if args.cmd == 'expire':
        text = PROPOSALS.read_text()
        plan = expiry_plan(parse_proposals(text), today)
        for p, status in plan:
            print(f"{p['date']} {p['ticker']} {p['dim']}: {status.split(' — ')[0].split(' (')[0]}")
        if not args.dry_run and plan:
            PROPOSALS.write_text(apply_expiry(text, plan))
        print(f"{'would retire' if args.dry_run else 'retired'} {len(plan)} proposal(s)")
        return 0
    if args.cmd == 'ask':
        asks = _load(ASKS)
        aid = add_ask(asks, args.kind, args.ticker.upper(), args.text, args.source,
                      args.key, today, args.urgent)
        _save(ASKS, asks)
        print(f'ask:{aid}')
        return 0
    if args.cmd == 'close':
        asks = _load(ASKS)
        close_ask(asks, args.id, args.note, today)
        _save(ASKS, asks)
        print(f'closed {args.id}')
        return 0
    if args.cmd == 'notion-record':
        m = _load(NOTION_MAP)
        pri = {i['id']: i['priority'] for i in collect(today=today)['items']}
        for pair in args.created:
            k, _, v = pair.partition('=')
            if not v:
                ap.error(f'--created needs ID=PAGE, got {pair!r}')
            m[k] = {'page': v, 'priority': pri.get(k)}
        for k in args.closed:
            m.pop(k, None)
        _save(NOTION_MAP, m)
        print(f'{len(args.created)} recorded, {len(args.closed)} removed; {len(m)} tracked')
        return 0

    c = collect(today=today)
    if args.cmd == 'build':
        INBOX.write_text(render(c))
        print(summary_line(c))
    elif args.cmd == 'summary':
        print(summary_line(c))
    elif args.cmd == 'list':
        if args.json:
            print(json.dumps(c, indent=2, ensure_ascii=False))
        else:
            for i in c['items']:
                print(f"P{i['priority']}  {i['id']:<34} {i['title']}")
    elif args.cmd == 'notion-plan':
        print(json.dumps(notion_plan(c, _load(NOTION_MAP)), indent=2, ensure_ascii=False))
    for prob in c['problems']:
        print(f'COULD NOT CHECK: {prob}', file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
