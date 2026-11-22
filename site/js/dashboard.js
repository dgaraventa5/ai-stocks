renderNav('index.html');
renderFooter();

const TIER_CLASS = { '✓✓✓': 'tier-3', '✓✓': 'tier-2', '✓': 'tier-1',
  '?': 'tier-q', '✗': 'tier-x' };
const INTRO_CLOSED_KEY = 'dashboard-intro-closed';

// Optional data: the dashboard still renders if one of these is missing.
const loadOptional = path => loadJSON(path).catch(() => null);

function fmtLongDate(iso) {
  const d = new Date(`${iso}T00:00:00`);
  return Number.isNaN(d.getTime()) ? iso
    : d.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
}

// "What is this?" panel for first-time visitors. Open by default; once a
// visitor closes it, it stays closed for them (per-browser, best effort).
function renderIntro(meta, perf) {
  const intro = document.getElementById('intro');
  try {
    if (localStorage.getItem(INTRO_CLOSED_KEY) === '1') intro.removeAttribute('open');
  } catch (e) { /* storage blocked: leave it open */ }
  intro.addEventListener('toggle', () => {
    try {
      if (intro.open) localStorage.removeItem(INTRO_CLOSED_KEY);
      else localStorage.setItem(INTRO_CLOSED_KEY, '1');
    } catch (e) { /* storage blocked: nothing to remember */ }
  });

  const scored = meta.scored ? `About ${esc(meta.scored)}` : 'About 200';
  const start = perf.dates && perf.dates.length ? fmtLongDate(perf.dates[0]) : null;
  const steps = [
    ['Score every company',
      `${scored} companies get a 0–100 score each week for value, quality,
       growth, AI exposure, momentum and risk.`],
    ['Buy the top 15',
      'The 15 highest scores are bought, in equal amounts.'],
    ['Sell only on a real drop',
      `A name is sold after ranking below 18th twice in a row, so the
       portfolio often holds a few more than 15.`],
  ];
  document.getElementById('intro-body').innerHTML = `
    <p class="intro-lede">A model portfolio of the companies building AI's
    physical backbone, from power plants to chips to software.</p>
    <ol class="intro-steps">${steps.map(([title, text]) => `
      <li><span class="intro-step-title">${title}</span>
      <span class="intro-step-text">${text}</span></li>`).join('')}
    </ol>
    <p class="intro-foot">Results show $10,000 invested${start
      ? ` on ${esc(start)}` : ' at the start'}, compared with the S&amp;P 500.
    <a href="positions.html">Positions</a> explains why each company is owned.
    Not investment advice.</p>`;
}

function renderTierLegend(methodology) {
  const box = document.getElementById('tier-legend');
  if (!methodology || !Array.isArray(methodology.tiers)) { box.remove(); return; }
  box.innerHTML = '<span class="dim legend-label">Tier:</span>' +
    methodology.tiers.map(t =>
      `<span class="tier-chip"><b class="${TIER_CLASS[t.symbol] || ''}">` +
      `${esc(t.symbol)}</b> ${esc(t.label)} ` +
      `<span class="dim">${esc(t.min)}–${esc(t.max)}</span></span>`).join('');
}

(async () => {
  try {
    const [meta, perf, positions, changes, methodology] = await Promise.all([
      loadJSON('data/meta.json'), loadJSON('data/performance.json'),
      loadJSON('data/positions.json'), loadJSON('data/changes.json'),
      loadOptional('data/methodology.json'),
    ]);

    renderIntro(meta, perf);

    const value = perf.model[perf.model.length - 1];
    const s = perf.summary;
    document.getElementById('stats').innerHTML = [
      [fmtMoney(value), 'Model value ($10k base)', pctClass(s.total_return)],
      [fmtPct(s.total_return), 'Since inception', pctClass(s.total_return)],
      [fmtPct(s.vs_spy), 'vs S&amp;P 500', pctClass(s.vs_spy)],
      [String(meta.holdings), 'Holdings', ''],
      [esc(meta.as_of), 'Performance as of', 'dim'],
      [esc(meta.scores_as_of ?? 'n/a'), 'Scores as of', 'dim'],
    ].map(([v, k, cls]) =>
      `<div class="stat"><div class="v ${cls}">${v}</div><div class="k">${k}</div></div>`
    ).join('');

    new Chart(document.getElementById('chart'), {
      type: 'line',
      data: { labels: perf.dates, datasets: [
        lineDataset('Model', perf.model, CHART_COLORS.model, true),
        lineDataset('S&P 500', perf.bench.SPY, CHART_COLORS.SPY),
      ]},
      options: baseChartOptions(),
    });

    const top = [...positions].sort((a, b) => b.weight - a.weight).slice(0, 5);
    document.getElementById('top-positions').innerHTML =
      '<tr><th>Ticker</th><th>Layer</th><th class="num">Weight</th>' +
      '<th class="num" title="0–100; higher is better">Score</th><th>Tier</th></tr>' +
      top.map(p => `<tr>
        <td><b>${esc(p.ticker)}</b> <span class="dim">${esc(p.company)}</span></td>
        <td><span class="badge" data-layer="${p.layer_num}">${esc(p.layer)}</span></td>
        <td class="num">${p.weight.toFixed(1)}%</td>
        <td class="num">${p.score.toFixed(1)}</td>
        <td class="${TIER_CLASS[p.tier] || ''}">${esc(p.tier)}</td></tr>`).join('');
    renderTierLegend(methodology);

    document.getElementById('recent-changes').innerHTML =
      changes.slice(0, 3).map(c => `<tr>
        <td class="dim">${esc(c.date)}</td><td><b>${esc(c.ticker || '—')}</b></td>
        <td>${esc(c.type)}${c.detail ? ' <span class="dim">' + esc(c.detail) + '</span>' : ''}</td>
        <td class="dim">${esc(c.note || '')}</td></tr>`).join('');
  } catch (e) {
    showError('main', e.message);
  }
})();
