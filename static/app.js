// Auto-detect browser offset and set the dropdown on first load.
(function initAutoDetect() {
  try {
    const url = new URL(window.location.href);
    if (!url.searchParams.get('my_tz')) {
      const offset = -new Date().getTimezoneOffset(); // minutes east of UTC
      const sign = offset >= 0 ? '+' : '-';
      const abs = Math.abs(offset);
      const h = String(Math.floor(abs / 60)).padStart(2, '0');
      const m = String(abs % 60).padStart(2, '0');
      const code = offset === 0 ? 'UTC' : `UTC${sign}${h}:${m}`;
      url.searchParams.set('my_tz', code);
      if (!url.searchParams.get('other_tz')) {
        url.searchParams.set('other_tz', code === 'UTC' ? 'UTC+01:00' : 'UTC');
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
