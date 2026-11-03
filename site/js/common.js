/* Shared helpers: data loading, formatting, nav, chart defaults. */

async function loadJSON(path) {
  const r = await fetch(path);
  if (!r.ok) throw new Error(`${path}: ${r.status}`);
  return r.json();
}

function fmtMoney(v) {
  return '$' + Math.round(v).toLocaleString('en-US');
}

function fmtPct(v, digits = 2) {
  const s = (v * 100).toFixed(digits);
  return (v >= 0 ? '+' : '') + s + '%';
}

function pctClass(v) { return v >= 0 ? 'pos' : 'neg'; }

function el(tag, attrs = {}, html = '') {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  e.innerHTML = html;
  return e;
}

function esc(s) {
  return String(s).replace(/[&<>"']/g,
    c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function showError(containerId, msg) {
  const c = document.getElementById(containerId);
  if (c) c.innerHTML = `<div class="error-note">data unavailable: ${esc(msg)}</div>`;
}

function renderNav(active) {
  const pages = [['index.html', 'Dashboard'], ['performance.html', 'Performance'],
    ['positions.html', 'Positions'], ['watchlist.html', 'Watchlist'],
    ['changes.html', 'Changes'], ['scans.html', 'Scans']];
  const nav = document.querySelector('nav');
  nav.innerHTML = '<span class="brand">AI SUPPLY CHAIN</span>' + pages.map(
    ([href, label]) =>
      `<a href="${href}" class="${href === active ? 'active' : ''}">${label}</a>`
  ).join('');
}

const STALE_AFTER_DAYS = 5;   // long weekend + one missed refresh is still normal

async function renderFooter({ showScored = false } = {}) {
  const footer = document.getElementById('footer');
  if (!footer) return;
  const base = '$10,000 notional base · not investment advice';
  try {
    const meta = await loadJSON('data/meta.json');
    const age = Math.floor((Date.now() - new Date(`${meta.as_of}T00:00:00`)) / 86400000);
    if (Number.isNaN(age)) throw new Error('bad as_of');
    const stale = age > STALE_AFTER_DAYS
      ? ` · <span class="stale-note">data is ${age} days old, the daily refresh may have stalled</span>`
      : '';
    const scored = showScored ? `${esc(meta.scored)} names scored · ` : '';
    const scoresDate = meta.scores_as_of ? ` · scores as of ${esc(meta.scores_as_of)}` : '';
    footer.innerHTML = `${scored}${base} · data as of ${esc(meta.as_of)}${scoresDate}` +
      ` · generated ${esc(meta.generated_at)}${stale}`;
  } catch (e) {
    footer.innerHTML = `${base} · <span class="stale-note">data date unavailable</span>`;
  }
}

const CHART_COLORS = { model: '#3fb950', SMH: '#58a6ff', QQQ: '#bc8cff', SPY: '#e3b341', EW: '#8b949e',
  EW_ROSTER: '#56d364', INVVOL_ROSTER: '#f778ba', BAND_TOP: '#1f6feb', BAND_NEXT: '#d29922', BAND_TAIL: '#f85149' };

function lineDataset(label, data, color, emphasized = false) {
  return { label, data, borderColor: color, backgroundColor: color,
    borderWidth: emphasized ? 2.2 : 1.2, pointRadius: 0, tension: 0.1 };
}

function baseChartOptions() {
  return {
    responsive: true, maintainAspectRatio: false, animation: false,
    interaction: { mode: 'index', intersect: false },
    plugins: { legend: { labels: { color: '#8b949e', boxWidth: 12,
      font: { family: 'Menlo, monospace', size: 11 } } } },
    scales: {
      x: { ticks: { color: '#8b949e', maxTicksLimit: 8,
             font: { family: 'Menlo, monospace', size: 10 } },
           grid: { color: '#21262d' } },
      y: { ticks: { color: '#8b949e',
             font: { family: 'Menlo, monospace', size: 10 },
             callback: v => '$' + v.toLocaleString() },
           grid: { color: '#21262d' } },
    },
  };
}
