renderNav('performance.html');
renderFooter();

(async () => {
  try {
    const perf = await loadJSON('data/performance.json');
    // Alternative builds (2026-11-21; backfilled from 2026-08-12) start
    // mid-history. Re-base each to the Model's value on its first day: the
    // lines start on the Model line and the gap is the difference in return.
    // A build with no prices yet still gets a (disabled) toggle.
    const PENDING = 'starts after the next close';
    const rebase = d => {
      if (!Array.isArray(d)) return null;
      const i0 = d.findIndex(v => v !== null);
      if (i0 < 0 || !perf.model[i0] || !d[i0]) return null;
      const k = perf.model[i0] / d[i0];
      return d.map(v => (v === null ? null : v * k));
    };
    // Backfilled stretch (rebuilt_until = the day live tracking began): drawn
    // dashed. Index of the first bar on or after that date.
    const rebuiltUntil = perf.rebuilt_until || {};
    const liveIdx = key => {
      const d = rebuiltUntil[key];
      if (!d) return 0;
      const i = perf.dates.findIndex(x => x >= d);
      return i < 0 ? perf.dates.length : i;
    };
    const alts = [
      ['MODEL_TOP25', 'Model, top 25',
        'The same score as the Model, holding the top 25 names instead of 15, equal weight.',
        'The dashed stretch uses the top 25 as recorded on each scoring date.'],
      ['VQR70_TOP15', 'V/Q/R floor 70, top 15',
        'Only names with an AI Thesis score of 70 or more, ranked on Value, Quality and Risk alone; top 15, equal weight.',
        'The dashed stretch is rebuilt by re-scoring past data with today’s scoring rules, so it benefits from some hindsight.'],
      ['VQR70_TOP25', 'V/Q/R floor 70, top 25',
        'The same V/Q/R ranking, holding the top 25.',
        'The dashed stretch is rebuilt by re-scoring past data with today’s scoring rules, so it benefits from some hindsight.'],
    ].map(([key, label, desc, rebuiltNote]) => {
      const d = rebase(perf.bench[key]);
      return { key, label, data: d, color: CHART_COLORS[key], live: liveIdx(key),
        desc: `${desc} Re-picked whenever the scores change, with no hold band; starts at the Model’s value on its first day.` +
          (rebuiltUntil[key] ? ` Tracked live from ${rebuiltUntil[key]}. ${rebuiltNote}` : '') +
          (d ? '' : ` Tracking ${PENDING}.`) };
    });
    const started = alts.filter(a => Array.isArray(a.data));
    // [label, data, color, emphasized, visible-by-default, description, pending, live index].
    const series = [
      ['Model', perf.model, CHART_COLORS.model, true, true,
        'The live portfolio — the top 15 names by score, every position equally sized (since 2026-09-08; volatility-based sizing before that).'],
      ['SMH', perf.bench.SMH, CHART_COLORS.SMH, false, true,
        'Semiconductor ETF — the closest off-the-shelf benchmark for AI hardware.'],
      ['QQQ', perf.bench.QQQ, CHART_COLORS.QQQ, false, true,
        'Nasdaq-100 ETF — the big-tech benchmark.'],
      ['S&P 500', perf.bench.SPY, CHART_COLORS.SPY, false, true,
        'The broad US market.'],
      ...alts.map(a => [a.label, a.data || perf.dates.map(() => null), a.color, false, false,
        a.desc, !a.data, a.live]),
    ].filter(([, d]) => Array.isArray(d));
    const chart = new Chart(document.getElementById('chart'), {
      type: 'line',
      data: { labels: perf.dates,
        datasets: series.map(([l, d, c, em, vis, , , live]) => ({
          ...lineDataset(l, d, c, em), hidden: !vis, spanGaps: false,
          ...(live ? { segment: { borderDash: ctx => (ctx.p1DataIndex < live ? [5, 4] : undefined) } } : {}),
        })) },
      options: { ...baseChartOptions(),
        plugins: { legend: { display: false } } },
    });

    document.getElementById('toggles').innerHTML = series.map(([l, , , , vis, , pending], i) =>
      pending
        ? `<label title="Tracking ${PENDING}"><input type="checkbox" data-i="${i}" disabled> ${esc(l)}</label>`
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

    // Build vs Model over the whole tracked period (rebuilt stretch included)
    // and over live tracking only, once it has a bar of its own.
    const altBox = document.getElementById('alt-builds');
    if (altBox && started.length) {
      const ret = (d, i) => d[d.length - 1] / d[i] - 1;
      const cell = v => (v === null ? '<td class="num">—</td>'
        : `<td class="num ${pctClass(v)}">${fmtPct(v)}</td>`);
      altBox.innerHTML =
        '<tr><th>Build</th><th>From</th><th class="num">Build</th>' +
        '<th class="num">Model</th><th class="num">Gap</th>' +
        '<th class="num" title="Build minus Model since live tracking began">Gap, live</th></tr>' +
        started.map(a => {
          const d = a.data;
          const i0 = d.findIndex(v => v !== null);
          const b = ret(d, i0), m = ret(perf.model, i0);
          const iL = Math.max(a.live, i0);
          const liveDiff = iL < d.length - 1 ? ret(d, iL) - ret(perf.model, iL) : null;
          return `<tr><td>${esc(a.label)}</td><td>${esc(perf.dates[i0])}</td>
            ${cell(b)}${cell(m)}${cell(b - m)}${cell(liveDiff)}</tr>`;
        }).join('');
      altBox.closest('.panel').hidden = false;
    }
  } catch (e) { showError('main', e.message); }
})();
