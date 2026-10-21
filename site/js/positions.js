renderNav('positions.html');

// Growth-of-1 path since entry → a small inline SVG line. The dashed line is
// the entry price, so above it = up since the model bought.
function sparkline(path, up) {
  if (!path || path.length < 2) return '<span class="dim">—</span>';
  const w = 84, h = 22, pad = 2;
  const lo = Math.min(1, ...path), hi = Math.max(1, ...path);
  const span = hi - lo || 1;
  const x = i => (pad + i * (w - 2 * pad) / (path.length - 1)).toFixed(1);
  const y = v => (pad + (hi - v) * (h - 2 * pad) / span).toFixed(1);
  const pts = path.map((v, i) => `${x(i)},${y(v)}`).join(' ');
  const color = up ? 'var(--green)' : 'var(--red)';
  return `<svg class="spark" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" ` +
    `aria-hidden="true"><line x1="${pad}" x2="${w - pad}" y1="${y(1)}" y2="${y(1)}" ` +
    `class="spark-base"/><polyline points="${pts}" fill="none" stroke="${color}" ` +
    `stroke-width="1.4" stroke-linejoin="round"/></svg>`;
}

function fmtSince(d) {
  if (!d) return '—';
  const [yy, mm, dd] = d.split('-').map(Number);
  return new Date(yy, mm - 1, dd).toLocaleDateString('en-US',
    { month: 'short', day: 'numeric' });
}

const COLS = [
  ['ticker', 'Ticker', false], ['company', 'Company', false],
  ['layer', 'Layer', false], ['weight', 'Weight', true],
  ['notional', 'Notional', true], ['since', 'Held since', false],
  ['ret', 'Return', true], ['vs_spy', 'vs S&P', true],
  [null, 'Trend', false], ['score', 'Score', true], ['tier', 'Tier', false],
];

(async () => {
  try {
    const [positions, theses] = await Promise.all([
      loadJSON('data/positions.json'), loadJSON('data/theses.json')]);
    const rows = positions.map(p => ({ since: null, ret: null, vs_spy: null,
      spark: null, ...p }));
    if (rows.some(p => theses[p.ticker])) {
      document.getElementById('positions-title').textContent =
        'All holdings — click a row (▸) for the thesis';
    }
    const table = document.getElementById('positions');
    let sortKey = 'score', sortDir = -1;

    function render() {
      const view = [...rows].sort((a, b) => {
        const x = a[sortKey], y = b[sortKey];
        if (x === null) return 1;       // blanks always sink
        if (y === null) return -1;
        if (x < y) return -sortDir;
        if (x > y) return sortDir;
        return 0;
      });
      table.innerHTML = '<tr>' + COLS.map(([key, label, num]) => {
        if (!key) return `<th>${esc(label)}</th>`;
        const arrow = key === sortKey
          ? ` <span class="arrow">${sortDir < 0 ? '▼' : '▲'}</span>` : '';
        return `<th class="sortable${num ? ' num' : ''}" data-key="${key}">` +
          `${esc(label)}${arrow}</th>`;
      }).join('') + '</tr>';
      const pct = v => v === null
        ? '<td class="num dim">—</td>'
        : `<td class="num ${pctClass(v)}">${fmtPct(v, 1)}</td>`;
      for (const p of view) {
        const thesis = theses[p.ticker];
        const tr = el('tr', thesis ? { class: 'clickable' } : {}, `
          <td style="white-space:nowrap"><b>${esc(p.ticker)}</b>${thesis ? ' <span class="dim">▸</span>' : ''}</td>
          <td class="dim">${esc(p.company)}</td>
          <td><span class="badge" data-layer="${p.layer_num}">${esc(p.layer)}</span></td>
          <td class="num">${p.weight.toFixed(1)}%</td>
          <td class="num">${fmtMoney(p.notional)}</td>
          <td class="dim">${fmtSince(p.since)}</td>
          ${pct(p.ret)}${pct(p.vs_spy)}
          <td>${sparkline(p.spark, (p.ret ?? 0) >= 0)}</td>
          <td class="num">${p.score.toFixed(1)}</td><td>${esc(p.tier)}</td>`);
        table.appendChild(tr);
        if (thesis) {
          const detail = el('tr', { class: 'thesis-row', hidden: '' },
            `<td colspan="${COLS.length}">${esc(thesis)}</td>`);
          table.appendChild(detail);
          tr.addEventListener('click', () => detail.toggleAttribute('hidden'));
        }
      }
      table.querySelectorAll('th.sortable').forEach(th =>
        th.addEventListener('click', () => {
          const key = th.dataset.key;
          if (key === sortKey) { sortDir = -sortDir; }
          // Text columns default A→Z; numeric default high→low.
          else { sortKey = key; sortDir = ['ticker', 'company', 'layer', 'tier',
            'since'].includes(key) ? 1 : -1; }
          render();
        }));
    }
    render();
  } catch (e) { showError('main', e.message); }
})();
