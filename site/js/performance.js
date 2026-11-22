renderNav('performance.html');
renderFooter();

(async () => {
  try {
    const perf = await loadJSON('data/performance.json');
    // Alternative builds (2026-11-21) are recorded forward only, so each starts
    // mid-history. Re-base each to the Model's value on its first day: the
    // lines start on the Model line and the gap is the difference in return.
    // A build with no prices yet still gets a (disabled) toggle, so the page
    // shows what is being tracked from day one.
    const rebase = d => {
      if (!Array.isArray(d)) return null;
      const i0 = d.findIndex(v => v !== null);
      if (i0 < 0 || !perf.model[i0] || !d[i0]) return null;
      const k = perf.model[i0] / d[i0];
      return d.map(v => (v === null ? null : v * k));
    };
    const alts = [
      ['Model, top 25', rebase(perf.bench.MODEL_TOP25), CHART_COLORS.MODEL_TOP25,
        'The same score as the Model, holding the top 25 names instead of 15, equal weight.'],
      ['V/Q/R floor 70, top 15', rebase(perf.bench.VQR70_TOP15), CHART_COLORS.VQR70_TOP15,
        'Only names with an AI Thesis score of 70 or more, ranked on Value, Quality and Risk alone; top 15, equal weight.'],
      ['V/Q/R floor 70, top 25', rebase(perf.bench.VQR70_TOP25), CHART_COLORS.VQR70_TOP25,
        'The same V/Q/R ranking, holding the top 25.'],
    ];
    const started = alts.filter(([, d]) => Array.isArray(d));
    const PENDING = 'starts after the next close';
    // [label, data, color, emphasized, visible-by-default, description, pending].
    const series = [
      ['Model', perf.model, CHART_COLORS.model, true, true,
        'The live portfolio — the top 15 names by score, every position equally sized (since 2026-09-08; volatility-based sizing before that).'],
      ['SMH', perf.bench.SMH, CHART_COLORS.SMH, false, true,
        'Semiconductor ETF — the closest off-the-shelf benchmark for AI hardware.'],
      ['QQQ', perf.bench.QQQ, CHART_COLORS.QQQ, false, true,
        'Nasdaq-100 ETF — the big-tech benchmark.'],
      ['S&P 500', perf.bench.SPY, CHART_COLORS.SPY, false, true,
        'The broad US market.'],
      ...alts.map(([l, d, c, desc]) => [l, d || perf.dates.map(() => null), c, false, false,
        `${desc} Re-picked whenever the scores change, with no hold band; tracked from its first day, starting at the Model’s value that day.` +
        (d ? '' : ` Tracking ${PENDING}.`), !d]),
    ].filter(([, d]) => Array.isArray(d));
    const chart = new Chart(document.getElementById('chart'), {
      type: 'line',
      data: { labels: perf.dates,
        datasets: series.map(([l, d, c, em, vis]) =>
          ({ ...lineDataset(l, d, c, em), hidden: !vis, spanGaps: false })) },
      options: { ...baseChartOptions(),
        plugins: { legend: { display: false } } },
    });

    document.getElementById('toggles').innerHTML = series.map(([l, , , , vis, , pending], i) =>
      pending
        ? `<label title="Tracking ${PENDING}"><input type="checkbox" data-i="${i}" disabled> ${esc(l)} (${PENDING})</label>`
        : `<label><input type="checkbox" data-i="${i}" ${vis ? 'checked' : ''}> ${esc(l)}</label>`).join('');
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

    const altBox = document.getElementById('alt-builds');
    if (altBox && started.length) {
      const pct = (d, i) => d[d.length - 1] / d[i] - 1;
      altBox.innerHTML =
        '<tr><th>Build</th><th>Tracked since</th><th class="num">Build</th>' +
        '<th class="num">Model</th><th class="num">Difference</th></tr>' +
        started.map(([l, d]) => {
          const i0 = d.findIndex(v => v !== null);
          const b = pct(d, i0), m = pct(perf.model, i0);
          return `<tr><td>${esc(l)}</td><td>${esc(perf.dates[i0])}</td>
            <td class="num ${pctClass(b)}">${fmtPct(b)}</td>
            <td class="num ${pctClass(m)}">${fmtPct(m)}</td>
            <td class="num ${pctClass(b - m)}">${fmtPct(b - m)}</td></tr>`;
        }).join('');
      altBox.closest('.panel').hidden = false;
    }
  } catch (e) { showError('main', e.message); }
})();
