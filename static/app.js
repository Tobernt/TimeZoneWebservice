// Auto-detect browser timezone and set the "Your timezone" dropdown on first load.
(function initAutoDetect() {
  try {
    const detected = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const url = new URL(window.location.href);
    if (!url.searchParams.get('my_tz') && detected) {
      // Only redirect once; add my_tz while preserving other params
      url.searchParams.set('my_tz', detected);
      if (!url.searchParams.get('other_tz')) {
        // default to UTC if user is already UTC, else compare with UTC for clarity
        url.searchParams.set('other_tz', detected === 'Etc/UTC' ? 'Europe/Stockholm' : 'Etc/UTC');
      }
      window.location.replace(url.toString());
    }
  } catch (e) { /* ignore */ }
})();

// Client-side filter for the big time zone table
(function tableSearch() {
  const input = document.getElementById('search');
  const table = document.getElementById('zones-table');
  if (!input || !table) return;
  input.addEventListener('input', () => {
    const q = input.value.toLowerCase();
    for (const row of table.tBodies[0].rows) {
      const zone = row.cells[0].textContent.toLowerCase();
      row.style.display = zone.includes(q) ? '' : 'none';
    }
  });
})();

// Swap selected time zones and submit the form
(function swapZones() {
  const btn = document.getElementById('swap');
  const form = document.getElementById('compare-form');
  if (!btn || !form) return;
  btn.addEventListener('click', () => {
    const a = document.getElementById('my_tz');
    const b = document.getElementById('other_tz');
    if (a && b) {
      const tmp = a.value;
      a.value = b.value;
      b.value = tmp;
      form.submit();
    }
  });
})();
