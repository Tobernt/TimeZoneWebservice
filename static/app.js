// Reactive time zone comparison and utilities
(function () {
  const mySel = document.getElementById('my_tz');
  const otherSel = document.getElementById('other_tz');
  const timeInput = document.getElementById('base_time');
  const compareBtn = document.getElementById('compare');
  const swapBtn = document.getElementById('swap');

  function pad(n) {
    return String(n).padStart(2, '0');
  }

  function currentDate() {
    const d = new Date();
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  }

  function update() {
    if (!mySel || !otherSel || !timeInput) return;
    const my = mySel.value;
    const other = otherSel.value;
    const t = timeInput.value || '00:00';
    const time = `${currentDate()}T${t}`;
    fetch(
      `/api/compare?my_tz=${encodeURIComponent(my)}&other_tz=${encodeURIComponent(
        other
      )}&time=${encodeURIComponent(time)}`
    )
      .then((r) => r.json())
      .then((data) => {
        document.getElementById('my_tz_label').textContent = my;
        document.getElementById('other_tz_label').textContent = other;
        document.getElementById('my_time').textContent = data.my_time;
        document.getElementById('other_time').textContent = data.other_time;
        document.getElementById('my_offset').textContent = `UTC ${data.my_offset}`;
        document.getElementById('other_offset').textContent = `UTC ${data.other_offset}`;
        document.getElementById('diff_text').textContent = `${data.description} (${data.pretty})`;
      });
  }

  // Auto-detect browser offset and set the dropdown
  (function autoDetect() {
    try {
      const offset = -new Date().getTimezoneOffset();
      const sign = offset >= 0 ? '+' : '-';
      const abs = Math.abs(offset);
      const h = pad(Math.floor(abs / 60));
      const m = pad(abs % 60);
      const code = offset === 0 ? 'UTC' : `UTC${sign}${h}:${m}`;
      if (mySel) mySel.value = code;
    } catch (e) {
      /* ignore */
    }
  })();

  if (mySel) mySel.addEventListener('change', update);
  if (otherSel) otherSel.addEventListener('change', update);
  if (timeInput) timeInput.addEventListener('input', update);
  if (compareBtn) compareBtn.addEventListener('click', update);
  if (swapBtn)
    swapBtn.addEventListener('click', () => {
      if (!mySel || !otherSel) return;
      const tmp = mySel.value;
      mySel.value = otherSel.value;
      otherSel.value = tmp;
      update();
    });

  // set default time to now and run initial update
  if (timeInput && !timeInput.value) {
    const d = new Date();
    timeInput.value = `${pad(d.getHours())}:${pad(d.getMinutes())}`;
  }
  update();
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

