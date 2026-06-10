renderNav('changes.html');

(async () => {
  try {
    const changes = await loadJSON('data/changes.json');
    const render = (type) => {
      document.getElementById('changes').innerHTML =
        '<tr><th>Date</th><th>Ticker</th><th>Type</th><th>Detail</th></tr>' +
        changes.filter(c => !type || c.type === type).map(c => `<tr>
          <td class="dim">${c.date}</td><td><b>${esc(c.ticker || '—')}</b></td>
          <td>${esc(c.type)}</td>
          <td class="dim">${c.detail ? esc(c.detail) + ' — ' : ''}${esc(c.note || '')}</td>
        </tr>`).join('');
    };
    render('');
    document.getElementById('filter').addEventListener('change',
      e => render(e.target.value));
  } catch (e) { showError('main', e.message); }
})();
