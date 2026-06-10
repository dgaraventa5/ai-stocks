renderNav('index.html');

(async () => {
  try {
    const [meta, perf, positions, changes] = await Promise.all([
      loadJSON('data/meta.json'), loadJSON('data/performance.json'),
      loadJSON('data/positions.json'), loadJSON('data/changes.json'),
    ]);

    const value = perf.model[perf.model.length - 1];
    const s = perf.summary;
    document.getElementById('stats').innerHTML = [
      [fmtMoney(value), 'Model value ($10k base)', pctClass(s.total_return)],
      [fmtPct(s.total_return), 'Since inception', pctClass(s.total_return)],
      [fmtPct(s.vs_smh), 'vs SMH', pctClass(s.vs_smh)],
      [String(meta.holdings), 'Holdings', ''],
      [meta.as_of, 'Data as of', 'dim'],
    ].map(([v, k, cls]) =>
      `<div class="stat"><div class="v ${cls}">${v}</div><div class="k">${k}</div></div>`
    ).join('');

    new Chart(document.getElementById('chart'), {
      type: 'line',
      data: { labels: perf.dates, datasets: [
        lineDataset('Model', perf.model, CHART_COLORS.model, true),
        lineDataset('SMH', perf.bench.SMH, CHART_COLORS.SMH),
      ]},
      options: baseChartOptions(),
    });

    const top = [...positions].sort((a, b) => b.weight - a.weight).slice(0, 5);
    document.getElementById('top-positions').innerHTML =
      '<tr><th>Ticker</th><th>Layer</th><th class="num">Weight</th>' +
      '<th class="num">Score</th><th>Tier</th></tr>' +
      top.map(p => `<tr>
        <td><b>${esc(p.ticker)}</b> <span class="dim">${esc(p.company)}</span></td>
        <td><span class="badge" data-layer="${p.layer_num}">${esc(p.layer)}</span></td>
        <td class="num">${p.weight.toFixed(1)}%</td>
        <td class="num">${p.score.toFixed(1)}</td><td>${esc(p.tier)}</td></tr>`).join('');

    document.getElementById('recent-changes').innerHTML =
      changes.slice(0, 3).map(c => `<tr>
        <td class="dim">${c.date}</td><td><b>${esc(c.ticker || '—')}</b></td>
        <td>${esc(c.type)}${c.detail ? ' <span class="dim">' + esc(c.detail) + '</span>' : ''}</td>
        <td class="dim">${esc(c.note || '')}</td></tr>`).join('');

    document.getElementById('footer').textContent =
      `$10,000 notional base · not investment advice · generated ${meta.generated_at}`;
  } catch (e) {
    showError('main', e.message);
  }
})();
