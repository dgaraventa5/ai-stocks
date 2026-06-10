renderNav('scans.html');

(async () => {
  try {
    const scans = await loadJSON('data/scans.json');
    document.getElementById('scans').innerHTML = scans.length
      ? scans.map(s => `<tr><td class="dim">${esc(s.date)}</td>
          <td><a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.title)} ↗</a></td></tr>`).join('')
      : '<tr><td class="dim">no scans linked yet</td></tr>';
  } catch (e) { showError('main', e.message); }
})();
