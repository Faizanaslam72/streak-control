/* Streak Control - app logic */
const STORAGE_KEY = 'streak_control_v1';

const $ = (id) => document.getElementById(id);

const state = {
  lastRelapse: null,
  history: [],
  bestStreakMs: 0,
  keepAwake: false,
  wakeLock: null,
  frame: 'on',
};

function load() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const d = JSON.parse(raw);
      state.lastRelapse = d.lastRelapse || null;
      state.history = Array.isArray(d.history) ? d.history : [];
      state.bestStreakMs = d.bestStreakMs || 0;
      state.keepAwake = !!d.keepAwake;
      state.frame = d.frame || 'on';
    }
  } catch (e) { console.warn(e); }
  if (!state.lastRelapse) {
    state.lastRelapse = Date.now();
    save();
  }
}
function save() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({
    lastRelapse: state.lastRelapse,
    history: state.history,
    bestStreakMs: state.bestStreakMs,
    keepAwake: state.keepAwake,
    frame: state.frame,
  }));
}

function fmtMs(ms) {
  if (ms < 0) ms = 0;
  const s = Math.floor(ms / 1000);
  const days = Math.floor(s / 86400);
  const h = Math.floor((s % 86400) / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = s % 60;
  const pad = (n) => String(n).padStart(2, '0');
  if (days > 0) return `${days}d ${pad(h)}:${pad(m)}:${pad(sec)}`;
  return `${pad(h)}:${pad(m)}:${pad(sec)}`;
}
function fmtShort(ms) {
  if (ms < 0) ms = 0;
  const s = Math.floor(ms / 1000);
  const days = Math.floor(s / 86400);
  const h = Math.floor((s % 86400) / 3600);
  const m = Math.floor((s % 3600) / 60);
  if (days > 0) return `${days}d ${h}h`;
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m`;
}
function fmtDate(ts) {
  const d = new Date(ts);
  return d.toLocaleString(undefined, { month:'short', day:'numeric', hour:'2-digit', minute:'2-digit' });
}

const QUOTES = [
  "Discipline is choosing between what you want now and what you want most.",
  "Every streak broken is a lesson, not a failure.",
  "You are stronger than your urges.",
  "The pain of discipline is less than the pain of regret.",
  "One day at a time. One hour at a time.",
  "Your future self is watching. Make them proud.",
  "Mastery is not about never falling, but always rising.",
  "Control the urge, or the urge controls you.",
];
function pickQuote(ms) {
  const days = ms / 86400000;
  if (days < 1) return QUOTES[0];
  if (days < 3) return QUOTES[1];
  if (days < 7) return QUOTES[3];
  if (days < 14) return QUOTES[5];
  return QUOTES[7];
}

async function setKeepAwake(on) {
  state.keepAwake = on;
  if (on) {
    try {
      if ('wakeLock' in navigator) {
        state.wakeLock = await navigator.wakeLock.request('screen');
        state.wakeLock.addEventListener('release', () => { state.wakeLock = null; });
      }
    } catch (e) { console.warn('wakeLock', e); }
  } else {
    if (state.wakeLock) { try { await state.wakeLock.release(); } catch {} state.wakeLock = null; }
  }
  save();
  updateKeepAwakeBtn();
}
function updateKeepAwakeBtn() {
  const b = $('keepAwakeBtn');
  b.textContent = 'Keep screen on: ' + (state.keepAwake ? 'ON' : 'OFF');
}
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible' && state.keepAwake && !state.wakeLock) {
    setKeepAwake(true);
  }
});

function relapse() {
  const now = Date.now();
  const streak = now - state.lastRelapse;
  if (streak > state.bestStreakMs) state.bestStreakMs = streak;
  state.history.unshift(now);
  if (state.history.length > 200) state.history.length = 200;
  state.lastRelapse = now;
  save();
  if (navigator.vibrate) try { navigator.vibrate([60,40,60]); } catch {}
  renderHistory();
  tick();
}
function resetAll() {
  if (!confirm('Reset all streak data? This cannot be undone.')) return;
  state.lastRelapse = Date.now();
  state.history = [];
  state.bestStreakMs = 0;
  save();
  renderHistory();
  tick();
}

const CIRC = 2 * Math.PI * 96;
function tick() {
  const now = Date.now();
  const elapsed = now - state.lastRelapse;
  $('streakTime').textContent = fmtMs(elapsed);
  $('streakSub').textContent = elapsed < 60000 ? 'just started' : (elapsed < 3600000 ? 'keep going' : 'strong streak');
  const q = pickQuote(elapsed);
  $('quote').textContent = '"' + q.replace(/^"|"$/g,'') + '"';

  const best = state.bestStreakMs;
  if (best > 0) {
    $('targetValue').textContent = fmtMs(best);
    const pct = Math.min(100, (elapsed / best) * 100);
    $('progressFill').style.width = pct + '%';
    $('ringFg').style.strokeDashoffset = CIRC * (1 - pct/100);
    if (elapsed >= best) {
      $('targetMeta').textContent = 'New record! You beat your best. 🎉';
    } else {
      const remaining = best - elapsed;
      $('targetMeta').textContent = `${fmtMs(remaining)} left to beat your best.`;
    }
  } else {
    $('targetValue').textContent = 'No best yet';
    $('progressFill').style.width = '0%';
    $('ringFg').style.strokeDashoffset = CIRC;
    $('targetMeta').textContent = 'Your first streak sets the target.';
  }

  $('statRelapses').textContent = state.history.length;
  $('statBest').textContent = best > 0 ? fmtShort(best) : '0d';
  if (state.history.length >= 2) {
    const gaps = [];
    const sorted = [...state.history].sort((a,b)=>a-b);
    for (let i=1;i<sorted.length;i++) gaps.push(sorted[i]-sorted[i-1]);
    const avg = gaps.reduce((a,b)=>a+b,0)/gaps.length;
    $('statAvg').textContent = fmtShort(avg);
  } else {
    $('statAvg').textContent = '--';
  }

  $('lastRelapseText').textContent = 'Last relapse: ' + fmtDate(state.lastRelapse);

  const d = new Date();
  $('statusTime').textContent = d.toLocaleTimeString(undefined,{hour:'2-digit',minute:'2-digit'});
}

function renderHistory() {
  const list = $('historyList');
  if (!state.history.length) {
    list.innerHTML = '<div class="empty">No relapses logged yet.<br>Stay strong.</div>';
    return;
  }
  list.innerHTML = state.history.map((ts, i) => {
    const prev = state.history[i+1];
    const gap = prev ? ts - prev : null;
    return `<div class="history-item">
      <div>
        <div class="hi-date">${fmtDate(ts)}</div>
        <div class="hi-gap">${gap ? 'gap: ' + fmtMs(gap) : 'first entry'}</div>
      </div>
      <span style="color:var(--muted);font-size:12px">#${i+1}</span>
    </div>`;
  }).join('');
}

function showPanel(id) { $(id).hidden = false; }
function hidePanel(id) { $(id).hidden = true; }

function applyFrame() {
  const f = $('deviceFrame');
  if (state.frame === 'off') f.classList.add('frameless'); else f.classList.remove('frameless');
  const sel = $('frameToggle');
  if (sel) sel.value = state.frame;
}

function exportData() {
  const blob = new Blob([JSON.stringify({
    lastRelapse: state.lastRelapse,
    history: state.history,
    bestStreakMs: state.bestStreakMs,
  }, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'streak-control-backup.json';
  document.body.appendChild(a); a.click(); a.remove();
  URL.revokeObjectURL(url);
}

load();
applyFrame();

$('relapseBtn').addEventListener('click', () => {
  if (confirm('Log a relapse now? This resets your current streak.')) relapse();
});
$('historyBtn').addEventListener('click', () => { renderHistory(); showPanel('historyPanel'); });
$('closeHistory').addEventListener('click', () => hidePanel('historyPanel'));
$('settingsBtn').addEventListener('click', () => showPanel('settingsPanel'));
$('closeSettings').addEventListener('click', () => hidePanel('settingsPanel'));
$('resetBtn').addEventListener('click', resetAll);
$('exportBtn').addEventListener('click', exportData);
$('keepAwakeBtn').addEventListener('click', () => setKeepAwake(!state.keepAwake));
const ft = $('frameToggle');
if (ft) ft.addEventListener('change', (e) => { state.frame = e.target.value; save(); applyFrame(); });
$('importFile').addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => {
    try {
      const d = JSON.parse(reader.result);
      if (d.lastRelapse) state.lastRelapse = d.lastRelapse;
      if (Array.isArray(d.history)) state.history = d.history;
      if (typeof d.bestStreakMs === 'number') state.bestStreakMs = d.bestStreakMs;
      save(); renderHistory(); tick();
      alert('Imported successfully.');
    } catch { alert('Invalid file.'); }
  };
  reader.readAsText(file);
  e.target.value = '';
});

updateKeepAwakeBtn();
if (state.keepAwake) setKeepAwake(true);
renderHistory();
tick();
setInterval(tick, 1000);

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('sw.js').catch(()=>{});
  });
}
