renderNav('watchlist.html');

const TIER_CLASS = { '✓✓✓': 'tier-3', '✓✓': 'tier-2', '✓': 'tier-1',
  '?': 'tier-q', '✗': 'tier-x' };

// Column defs: [key, label, numeric?]. Order drives both header and cells.
const COLS = [
  ['rank', '#', true], ['ticker', 'Ticker', false],
  ['company', 'Company', false], ['layer', 'Layer', false],
  ['value', 'Val', true], ['quality', 'Qual', true], ['growth', 'Grw', true],
  ['ai', 'AI', true], ['momentum', 'Mom', true], ['risk', 'Risk', true],
  ['score', 'TOTAL', true], ['tier', 'Tier', false],
];

function renderExplainer(m) {
  const tiers = m.tiers.map(t =>
    `<span class="tier-chip"><b class="${TIER_CLASS[t.symbol] || ''}">` +
    `${esc(t.symbol)}</b> ${esc(t.label)} ` +
    `<span class="dim">${t.min}–${t.max}</span></span>`).join('');
  const cats = m.categories.map(c => `
    <div class="cat-card">
      <div class="cat-head">
        <span class="cat-name">${esc(c.name)}</span>
        <span class="cat-weight">${Math.round(c.weight * 100)}%</span>
      </div>
      <div class="dim cat-note">${esc(c.note)}</div>
      <ul class="cat-metrics">${c.metrics.map(x =>
        `<li>${esc(x)}</li>`).join('')}</ul>
      <div class="dim cat-kind">${esc(c.kind_note)}</div>
    </div>`).join('');
  document.getElementById('explainer-body').innerHTML =
    `<p class="dim explainer-intro">${esc(m.total_note)}</p>` +
    `<div class="tier-legend">${tiers}</div>` +
    `<div class="cat-grid">${cats}</div>` +
    '<p class="dim explainer-foot">Higher is better on every category and on ' +
    'the Total (0–100). Blank cells (—) mean an input was missing or not ' +
    'meaningful for that name, so it was left out of the average.</p>';
}

(async () => {
  try {
    const [rows, meta, methodology] = await Promise.all([
      loadJSON('data/watchlist.json'), loadJSON('data/meta.json'),
      loadJSON('data/methodology.json')]);

    renderExplainer(methodology);

    // Stable rank by TOTAL (already sorted score-desc by the exporter).
    let rank = 0;
    for (const r of rows) r.rank = r.score === null ? null : ++rank;

    const scored = rows.filter(r => r.score !== null).length;
    const held = rows.filter(r => r.held).length;
    const strong = rows.filter(r => r.tier === '✓✓✓' || r.tier === '✓✓').length;
    document.getElementById('stats').innerHTML = [
      [String(scored), 'Names scored', ''],
      [String(strong), '✓✓ or better', 'pos'],
      [String(held), 'In portfolio', ''],
      [esc(meta.as_of), 'Data as of', 'dim'],
    ].map(([v, k, cls]) =>
      `<div class="stat"><div class="v ${cls}">${v}</div><div class="k">${k}</div></div>`
    ).join('');

    // Populate the layer filter — distinct layers, ordered by layer number.
    const layerSel = document.getElementById('layer-filter');
    [...new Set(rows.map(r => r.layer).filter(Boolean))]
      .sort((a, b) => rows.find(r => r.layer === a).layer_num
        .localeCompare(rows.find(r => r.layer === b).layer_num))
      .forEach(l => layerSel.appendChild(el('option', { value: l }, esc(l))));

    const table = document.getElementById('watchlist');
    const countEl = document.getElementById('result-count');
    let sortKey = 'score', sortDir = -1, layerFilter = '', query = '';

    function render() {
      const q = query.trim().toLowerCase();
      let view = rows.filter(r =>
        (!layerFilter || r.layer === layerFilter) &&
        (!q || r.ticker.toLowerCase().includes(q) ||
               r.company.toLowerCase().includes(q)));
      view = [...view].sort((a, b) => {
        const x = a[sortKey], y = b[sortKey];
        if (x === null) return 1;       // blanks always sink
        if (y === null) return -1;
        if (x < y) return -sortDir;
        if (x > y) return sortDir;
        return 0;
      });

      countEl.textContent = view.length === rows.length
        ? `${rows.length} names`
        : `${view.length} of ${rows.length} names`;

      if (!view.length) {
        table.innerHTML = '<tr><td class="dim" style="padding:14px">' +
          'No matches.</td></tr>';
        return;
      }

      table.innerHTML = '<tr>' + COLS.map(([key, label, num]) => {
        const arrow = key === sortKey
          ? ` <span class="arrow">${sortDir < 0 ? '▼' : '▲'}</span>` : '';
        return `<th class="sortable${num ? ' num' : ''}" data-key="${key}">` +
          `${esc(label)}${arrow}</th>`;
      }).join('') + '</tr>' + view.map(r => {
        const sub = v => v === null
          ? '<td class="num dim">—</td>'
          : `<td class="num subscore">${v.toFixed(0)}</td>`;
        const tierCls = TIER_CLASS[r.tier] || 'dim';
        return `<tr class="${r.held ? 'held' : ''}">
          <td class="num dim">${r.rank ?? '—'}</td>
          <td><b>${esc(r.ticker)}</b>${r.held
            ? '<span class="held-tag">◀ held</span>' : ''}</td>
          <td class="dim">${esc(r.company)}</td>
          <td><span class="badge" data-layer="${r.layer_num}">${esc(r.layer)}</span></td>
          ${sub(r.value)}${sub(r.quality)}${sub(r.growth)}
          ${sub(r.ai)}${sub(r.momentum)}${sub(r.risk)}
          <td class="num"><b>${r.score === null ? '—' : r.score.toFixed(1)}</b></td>
          <td class="${tierCls}">${esc(r.tier || '—')}</td></tr>`;
      }).join('');

      table.querySelectorAll('th.sortable').forEach(th =>
        th.addEventListener('click', () => {
          const key = th.dataset.key;
          if (key === sortKey) { sortDir = -sortDir; }
          // Text columns default A→Z; numeric default high→low.
          else { sortKey = key; sortDir = ['ticker', 'company', 'layer', 'tier']
            .includes(key) ? 1 : -1; }
          render();
        }));
    }

    render();
    layerSel.addEventListener('change', e => {
      layerFilter = e.target.value; render();
    });
    document.getElementById('search').addEventListener('input', e => {
      query = e.target.value; render();
    });

    document.getElementById('footer').textContent =
      `${scored} names scored · $10,000 notional base · not investment advice` +
      ` · generated ${meta.generated_at}`;
  } catch (e) { showError('main', e.message); }
})();
