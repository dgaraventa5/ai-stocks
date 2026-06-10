renderNav('performance.html');

(async () => {
  try {
    const perf = await loadJSON('data/performance.json');
    const series = [
      ['Model', perf.model, CHART_COLORS.model, true],
      ['SMH', perf.bench.SMH, CHART_COLORS.SMH, false],
      ['QQQ', perf.bench.QQQ, CHART_COLORS.QQQ, false],
      ['S&P 500', perf.bench.SPY, CHART_COLORS.SPY, false],
    ];
    const chart = new Chart(document.getElementById('chart'), {
      type: 'line',
      data: { labels: perf.dates,
        datasets: series.map(([l, d, c, em]) => lineDataset(l, d, c, em)) },
      options: { ...baseChartOptions(),
        plugins: { legend: { display: false } } },
    });

    document.getElementById('toggles').innerHTML = series.map(([l], i) =>
      `<label><input type="checkbox" data-i="${i}" checked> ${l}</label>`).join('');
    document.getElementById('toggles').addEventListener('change', e => {
      const i = Number(e.target.dataset.i);
      chart.setDatasetVisibility(i, e.target.checked);
      chart.update();
    });

    document.getElementById('monthly').innerHTML =
      '<tr><th>Month</th><th class="num">Model</th><th class="num">SMH</th>' +
      '<th class="num">QQQ</th><th class="num">S&amp;P 500</th></tr>' +
      perf.monthly.map(m => `<tr><td>${esc(m.month)}</td>
        <td class="num ${pctClass(m.model)}">${fmtPct(m.model)}</td>
        <td class="num ${pctClass(m.SMH)}">${fmtPct(m.SMH)}</td>
        <td class="num ${pctClass(m.QQQ)}">${fmtPct(m.QQQ)}</td>
        <td class="num ${pctClass(m.SPY)}">${fmtPct(m.SPY)}</td></tr>`).join('');
  } catch (e) { showError('main', e.message); }
})();
