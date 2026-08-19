renderNav('performance.html');

(async () => {
  try {
    const perf = await loadJSON('data/performance.json');
    // [label, data, color, emphasized, visible-by-default, one-line description].
    // The v2 shadow series (sizing null + score-band scouts, spec A4/C1) ship
    // hidden so the default view stays clean; they start mid-history (null gap
    // before their deploy date). Filter tolerates data files exported before v2.
    const series = [
      ['Model', perf.model, CHART_COLORS.model, true, true,
        'The live portfolio — the top 15 names by score, with steadier stocks given bigger weights (volatility-based sizing).'],
      ['SMH', perf.bench.SMH, CHART_COLORS.SMH, false, true,
        'Semiconductor ETF — the closest off-the-shelf benchmark for AI hardware.'],
      ['QQQ', perf.bench.QQQ, CHART_COLORS.QQQ, false, true,
        'Nasdaq-100 ETF — the big-tech benchmark.'],
      ['S&P 500', perf.bench.SPY, CHART_COLORS.SPY, false, true,
        'The broad US market.'],
      ['Same picks, equal weight', perf.bench.EW_ROSTER, CHART_COLORS.EW_ROSTER, false, false,
        'The model’s exact stocks and trades, but every position equally sized — the gap vs Model shows what volatility-based sizing adds (or costs).'],
      ['Band 1–15', perf.bench.BAND_TOP, CHART_COLORS.BAND_TOP, false, false,
        'The score’s top 15 names, equal weight, rebalanced mechanically — the raw picks with no sizing or trading rules.'],
      ['Band 16–25', perf.bench.BAND_NEXT, CHART_COLORS.BAND_NEXT, false, false,
        'The next 10 names by score — if this keeps pace with Band 1–15, holding a bigger portfolio would be justified.'],
      ['Band 26–40', perf.bench.BAND_TAIL, CHART_COLORS.BAND_TAIL, false, false,
        'Ranks 26–40 — the control group: if these keep up with the top ranks, the score isn’t adding anything.'],
    ].filter(([, d]) => Array.isArray(d));
    const chart = new Chart(document.getElementById('chart'), {
      type: 'line',
      data: { labels: perf.dates,
        datasets: series.map(([l, d, c, em, vis]) =>
          ({ ...lineDataset(l, d, c, em), hidden: !vis, spanGaps: false })) },
      options: { ...baseChartOptions(),
        plugins: { legend: { display: false } } },
    });

    document.getElementById('toggles').innerHTML = series.map(([l, , , , vis], i) =>
      `<label><input type="checkbox" data-i="${i}" ${vis ? 'checked' : ''}> ${l}</label>`).join('');
    document.getElementById('toggles').addEventListener('change', e => {
      const i = Number(e.target.dataset.i);
      chart.setDatasetVisibility(i, e.target.checked);
      chart.update();
    });

    document.getElementById('series-key').innerHTML = series.map(([l, , c, , , desc]) =>
      `<li><span class="key-dot" style="background:${c}"></span><strong>${esc(l)}</strong> — ${esc(desc)}</li>`).join('');

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
