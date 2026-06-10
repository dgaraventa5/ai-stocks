renderNav('positions.html');

(async () => {
  try {
    const [positions, theses] = await Promise.all([
      loadJSON('data/positions.json'), loadJSON('data/theses.json')]);
    const rows = [...positions].sort((a, b) => b.weight - a.weight);
    const table = document.getElementById('positions');
    table.innerHTML =
      '<tr><th>Ticker</th><th>Company</th><th>Layer</th>' +
      '<th class="num">Weight</th><th class="num">Notional</th>' +
      '<th class="num">Score</th><th>Tier</th></tr>';
    for (const p of rows) {
      const thesis = theses[p.ticker];
      const tr = el('tr', thesis ? { class: 'clickable' } : {}, `
        <td><b>${esc(p.ticker)}</b>${thesis ? ' <span class="dim">▸</span>' : ''}</td>
        <td class="dim">${esc(p.company)}</td>
        <td><span class="badge" data-layer="${p.layer_num}">${esc(p.layer)}</span></td>
        <td class="num">${p.weight.toFixed(1)}%</td>
        <td class="num">${fmtMoney(p.notional)}</td>
        <td class="num">${p.score.toFixed(1)}</td><td>${esc(p.tier)}</td>`);
      table.appendChild(tr);
      if (thesis) {
        const detail = el('tr', { class: 'thesis-row', hidden: '' },
          `<td colspan="7">${esc(thesis)}</td>`);
        table.appendChild(detail);
        tr.addEventListener('click', () => detail.toggleAttribute('hidden'));
      }
    }
  } catch (e) { showError('main', e.message); }
})();
