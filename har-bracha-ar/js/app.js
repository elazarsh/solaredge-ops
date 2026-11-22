import * as G from './geo.js';
import { Orientation } from './sensors.js';

const $ = (s) => document.querySelector(s);
const mk = (tag, cls, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; };
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const store = {
  get(k) { try { return JSON.parse(localStorage.getItem(k)); } catch { return null; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* private mode */ } },
};
const query = new URLSearchParams(location.search);

const LAYERS = [
  { id: 'view', name: 'נופים' },
  { id: 'bible', name: 'תנ״ך' },
  { id: 'history', name: 'היסטוריה' },
  { id: 'future', name: 'חזון הישוב' },
];
const STORY_ICON = { bible: '📖', history: '🏛' };
const STORY_NAME = { bible: 'תנ״ך', history: 'היסטוריה' };
const COMPASS = ['צפון', 'צפון־מזרח', 'מזרח', 'דרום־מזרח', 'דרום', 'דרום־מערב', 'מערב', 'צפון־מערב'];
const bearingName = (az) => COMPASS[Math.round(az / 45) % 8];
const fmtDist = (m) => (m < 1000 ? `${Math.round(m / 10) * 10} מ׳` : m < 10000 ? `${(m / 1000).toFixed(1)} ק״מ` : `${Math.round(m / 1000)} ק״מ`);

const video = $('#cam'), fx = $('#fx').getContext('2d'), tape = $('#tape').getContext('2d');
const labelsEl = $('#labels');

const orient = new Orientation();
let data, station, mode = null; // mode: 'ar' | 'sim'
let W = 0, H = 0, DPR = 1;
const S = {
  layers: { view: true, bible: true, history: false, future: false },
  year: 2030, fov: 65, yaw: 0, pitch: 2,
  off: { h: 0, p: 0 }, calibrating: false,
  items: [], buildings: [],
};

// ---------------------------------------------------------------- setup
async function init() {
  data = await (await fetch('content/har-bracha.json')).json();
  if ('serviceWorker' in navigator && (location.protocol === 'https:' || location.hostname === 'localhost')) navigator.serviceWorker.register('sw.js').catch(() => {});
  buildChips();
  addEventListener('resize', resize); resize();
  requestAnimationFrame(frame);

  $('#go').onclick = startAR;
  $('#goSim').onclick = () => startSim();
  $('#btnStation').onclick = () => openPicker();
  $('#btnCalib').onclick = () => startCalibration();
  $('#btnMode').onclick = () => (mode === 'sim' ? startAR() : startSim(true));
  $('#sheetClose').onclick = () => ($('#sheet').hidden = true);
  $('#year').oninput = (e) => { S.year = +e.target.value; $('#yearOut').textContent = S.year; };
  $('#fov').oninput = (e) => { S.fov = +e.target.value; $('#fovOut').textContent = S.fov + '°'; };
  $('#calibOk').onclick = () => endCalibration(true);
  $('#calibSkip').onclick = () => endCalibration(false);
  $('#calibReset').onclick = () => { S.off.h = station.declination ?? 0; S.off.p = 0; };
  bindDrag();

  if (query.has('layers')) for (const l of LAYERS) S.layers[l.id] = query.get('layers').split(',').includes(l.id);
  if (query.has('fov')) S.fov = +query.get('fov');
  if (query.has('year')) { S.year = +query.get('year'); $('#year').value = S.year; $('#yearOut').textContent = S.year; }
  if (query.has('sim')) startSim(false, query.get('station'));
}

function resize() {
  W = innerWidth; H = innerHeight; DPR = Math.min(devicePixelRatio || 1, 2);
  for (const [c, h] of [[$('#fx'), H], [$('#tape'), 46]]) { c.width = W * DPR; c.height = h * DPR; }
}

// ---------------------------------------------------------------- start flows
function toast(msg, ms = 2600) { const t = $('#toast'); t.textContent = msg; t.classList.add('on'); clearTimeout(toast.t); toast.t = setTimeout(() => t.classList.remove('on'), ms); }

async function startAR() {
  const err = $('#startErr'); err.textContent = '';
  try {
    await orient.start(); // first: iOS needs this inside the tap gesture
    video.srcObject = await navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: 'environment' } }, audio: false });
    await video.play().catch(() => {});
  } catch (e) {
    err.textContent = e.message === 'motion-denied' ? 'נדרשת הרשאה לחיישני תנועה.' : 'לא ניתן להפעיל מצלמה (נדרש HTTPS והרשאה). אפשר להמשיך במצב הדגמה.';
    return;
  }
  mode = 'ar'; document.body.classList.remove('sim');
  $('#btnMode span').textContent = 'הדגמה';
  $('#start').hidden = true;
  setTimeout(() => { if (mode === 'ar' && !orient.has) { toast('לא התקבלו נתוני חיישנים — עוברים למצב הדגמה'); startSim(true); } }, 2500);
  if (!station) { await pickStation(); startCalibration(); }
  else if (!S.calibrated) startCalibration();
  showHud();
}

async function startSim(keepStation, stationId) {
  mode = 'sim'; document.body.classList.add('sim');
  if (video.srcObject) { video.srcObject.getTracks().forEach((t) => t.stop()); video.srcObject = null; }
  $('#btnMode span').textContent = 'מצלמה';
  $('#start').hidden = true; endCalibration(false, true);
  if (!station || !keepStation) {
    if (stationId) setStation(data.stations.find((s) => s.id === stationId) || data.stations[0]);
    else await pickStation();
  }
  S.off.h = 0; S.off.p = 0;
  S.yaw = query.has('yaw') ? +query.get('yaw') : calibTarget().look.az - 20; S.pitch = query.has('pitch') ? +query.get('pitch') : 5;
  showHud();
}

function showHud() { for (const id of ['top', 'tools', 'bottom']) $('#' + id).hidden = false; $('#btnCalib').hidden = mode !== 'ar'; }

async function pickStation() {
  if (data.stations.length === 1) return setStation(data.stations[0]);
  // Location is optional. The browser's own `timeout` doesn't start until the permission prompt is answered, so race our own timer.
  const gps = await Promise.race([
    new Promise((res) => (navigator.geolocation ? navigator.geolocation.getCurrentPosition((p) => res(p.coords), () => res(null), { timeout: 3000, maximumAge: 60000 }) : res(null))),
    new Promise((res) => setTimeout(() => res(null), 3500)),
  ]);
  return new Promise((resolve) => openPicker(gps, resolve));
}

function openPicker(gps, resolve) {
  const list = $('#pickList'); list.innerHTML = '';
  const dists = data.stations.map((s) => (gps ? G.lookAt(s, { lat: gps.latitude, lon: gps.longitude, alt: s.alt }).horiz : null));
  const nearest = gps ? dists.indexOf(Math.min(...dists)) : -1;
  data.stations.forEach((s, i) => {
    const b = mk('button', i === nearest && dists[i] < 500 ? 'near' : '', `${esc(s.name)}<small>${dists[i] != null ? 'במרחק ' + fmtDist(dists[i]) + ' ממך' : ''}${s.surveyed === false ? ' · מיקום משוער' : ''}</small>`);
    b.onclick = () => { $('#pick').hidden = true; setStation(s); resolve?.(); };
    list.append(b);
  });
  $('#pick').hidden = false;
}

function setStation(st) {
  station = st;
  const saved = store.get('cal:' + st.id);
  S.calibrated = !!saved;
  S.off.h = saved?.h ?? st.declination ?? 0; S.off.p = saved?.p ?? 0; if (saved?.fov) { S.fov = saved.fov; $('#fov').value = S.fov; $('#fovOut').textContent = S.fov + '°'; }
  $('#stationName').textContent = st.name;
  buildItems();
}

// ---------------------------------------------------------------- data → items
function buildItems() {
  labelsEl.innerHTML = '';
  S.items = data.pois.map((p) => makeItem({ kind: 'poi', p, look: G.lookAt(station, p) }));
  S.buildings = data.future.map((b) => {
    const verts = (b.footprint ? b.footprint.map(([lat, lon]) => G.toENU(station, { lat, lon, alt: b.baseAlt })) : b.footprintM.map(([e, n]) => [e, n, b.baseAlt - station.alt]))
      .map(([e, n, u0]) => ({ e, n, u0 }));
    const cx = verts.reduce((a, v) => a + v.e, 0) / verts.length, cn = verts.reduce((a, v) => a + v.n, 0) / verts.length;
    const u = verts[0].u0 + b.height;
    const len = Math.hypot(cx, cn, u);
    const look = { az: G.norm360(Math.atan2(cx, cn) * G.R2D), el: Math.asin(u / len) * G.R2D, dist: len, dir: [cx / len, cn / len, u / len] };
    return { b, verts, look, item: makeItem({ kind: 'bld', p: { name: b.name, pri: 2 }, b, look }) };
  });
  S.items.push(...S.buildings.map((x) => x.item));
}

function makeItem(it) {
  it.el = mk('button', 'lbl'); it.w = 0; it.h = 0;
  it.el.onclick = () => openSheet(it);
  labelsEl.append(it.el);
  return it;
}

/** Which layer drives this label right now, and what does it say? */
function describe(it) {
  if (it.kind === 'bld') {
    const show = S.layers.future && it.b.year <= S.year;
    return show ? { cls: 'k-future', sub: `🏗 ${it.b.year} · ${fmtDist(it.look.dist)}`, show: it.b.year === S.year } : { show: false };
  }
  if (it.p.hidden) return { show: false };
  const st = it.p.stories || {}, km = fmtDist(it.look.dist);
  if (S.layers.bible && st.bible) return { cls: 'k-bible', sub: `${km} · 📖 ${st.bible.short}`, show: true };
  if (S.layers.history && st.history) return { cls: 'k-history', sub: `${km} · 🏛 ${st.history.short}`, show: true };
  if (S.layers.view) return { cls: '', sub: `${km}${it.p.blurb ? ' · ' + it.p.blurb : ''}`, show: true };
  return { show: false };
}

// ---------------------------------------------------------------- chips / sheet
function buildChips() {
  const nav = $('#chips');
  for (const l of LAYERS) {
    const b = mk('button', 'chip' + (S.layers[l.id] ? ' on' : ''), l.name); b.dataset.l = l.id;
    b.onclick = () => { S.layers[l.id] = !S.layers[l.id]; b.classList.toggle('on', S.layers[l.id]); $('#yearBar').hidden = !S.layers.future; S.items.forEach((i) => (i.w = 0)); };
    nav.append(b);
  }
  $('#yearBar').hidden = !S.layers.future;
}

function openSheet(it) {
  const look = it.look; let html;
  if (it.kind === 'bld') {
    html = `<h2>${esc(it.b.name)}</h2><div class="meta">צפי אכלוס ${it.b.year} · ${fmtDist(look.dist)} · ${bearingName(look.az)}</div>
      <div class="story future"><h3>🏗 חזון הישוב</h3><p>${esc(it.b.text)}</p></div>`;
  } else {
    const p = it.p;
    html = `<h2>${esc(p.name)}</h2><div class="meta">${fmtDist(look.dist)} · ${bearingName(look.az)} ${Math.round(look.az)}° · גובה ${p.alt} מ׳</div>${p.blurb ? `<p>${esc(p.blurb)}</p>` : ''}`;
    for (const k of ['bible', 'history']) {
      const s = p.stories?.[k]; if (!s) continue;
      html += `<div class="story ${k}"><h3>${STORY_ICON[k]} ${STORY_NAME[k]}</h3><p>${esc(s.text)}</p>${s.ref ? `<cite>${esc(s.ref)}</cite>` : ''}</div>`;
    }
  }
  $('#sheetBody').innerHTML = html; $('#sheet').hidden = false;
}

// ---------------------------------------------------------------- input: drag (sim look-around, calibration nudge)
function bindDrag() {
  const t = $('#touch'); let last = null;
  t.addEventListener('pointerdown', (e) => { last = [e.clientX, e.clientY]; t.setPointerCapture(e.pointerId); });
  t.addEventListener('pointerup', () => (last = null));
  t.addEventListener('pointermove', (e) => {
    if (!last) return;
    const dx = e.clientX - last[0], dy = e.clientY - last[1]; last = [e.clientX, e.clientY];
    const degPerPx = S.fov / Math.max(W, H);
    if (S.calibrating) { S.off.h -= dx * degPerPx; S.off.p += dy * degPerPx; }
    else if (mode === 'sim') { S.yaw = G.norm360(S.yaw - dx * degPerPx); S.pitch = Math.max(-80, Math.min(80, S.pitch + dy * degPerPx)); }
  });
  t.addEventListener('wheel', (e) => { if (mode === 'sim') { S.fov = Math.max(25, Math.min(90, S.fov + e.deltaY * 0.03)); } }, { passive: true });
}

// ---------------------------------------------------------------- calibration
function calibTarget() { return S.items.find((i) => i.p?.id === station.calibration?.poi) || S.items[0]; }
function startCalibration() {
  if (mode !== 'ar' || !station) return;
  S.calibrating = true; $('#calib').hidden = false; $('#sheet').hidden = true;
  $('#calibHint').textContent = `הזיזו את התמונה עד שהטבעת יושבת על: ${station.calibration?.hint || calibTarget().p.name}`;
  $('#fov').value = S.fov; $('#fovOut').textContent = S.fov + '°';
}
function endCalibration(save, silent) {
  if (!S.calibrating && !silent) return;
  S.calibrating = false; $('#calib').hidden = true;
  if (save && station) { S.calibrated = true; store.set('cal:' + station.id, { h: S.off.h, p: S.off.p, fov: S.fov }); toast('הכיול נשמר ✓'); }
}

// ---------------------------------------------------------------- frame
function screenAngle() { return (screen.orientation && screen.orientation.angle) ?? window.orientation ?? 0; }

function frame() {
  requestAnimationFrame(frame);
  fx.setTransform(DPR, 0, 0, DPR, 0, 0); fx.clearRect(0, 0, W, H);
  if (!station || !mode) return;
  const R = mode === 'sim' ? G.deviceMatrix(-S.yaw, 90 + S.pitch, 0) : orient.matrix();
  if (!R) return;
  const proj = G.makeProjector({ R, yawOff: mode === 'sim' ? 0 : S.off.h, pitchOff: mode === 'sim' ? 0 : S.off.p, screenAngle: mode === 'sim' ? 0 : screenAngle(), fovDeg: S.fov, W, H });
  const aim = G.cameraAim(R);
  const camAz = mode === 'sim' ? aim.az : G.norm360(aim.az + S.off.h);

  if (mode === 'sim') drawSky(proj, camAz);
  drawGrid(proj);
  drawHorizon(proj, camAz);
  if (!S.calibrating) drawBuildings(proj);
  layoutLabels(proj);
  if (S.calibrating) drawCalibration(proj, camAz);
  drawTape(camAz);
}

function drawSky(proj, camAz) {
  const hz = proj.project(G.dirAE(camAz, G.horizonDip(station.alt)));
  const y = hz ? hz.y : (S.pitch > 0 ? H : 0);
  const sky = fx.createLinearGradient(0, 0, 0, Math.max(y, 1)); sky.addColorStop(0, '#05121f'); sky.addColorStop(1, '#2b5b78');
  fx.fillStyle = sky; fx.fillRect(0, 0, W, Math.max(0, y));
  fx.fillStyle = '#0a1a14'; fx.fillRect(0, Math.max(0, y), W, H);
}

function polyline(proj, pts, stroke, width, dash) {
  fx.beginPath(); let pen = false;
  for (const d of pts) { const p = proj.project(d); if (!p || Math.abs(p.x) > 4 * W || Math.abs(p.y) > 4 * H) { pen = false; continue; } pen ? fx.lineTo(p.x, p.y) : fx.moveTo(p.x, p.y); pen = true; }
  fx.strokeStyle = stroke; fx.lineWidth = width; fx.setLineDash(dash || []); fx.stroke(); fx.setLineDash([]);
}

function drawGrid(proj) {
  if (!S.layers.view && mode !== 'sim') return;
  for (let el = -10; el <= 40; el += 10) polyline(proj, Array.from({ length: 73 }, (_, i) => G.dirAE(i * 5, el)), 'rgba(94,231,255,.10)', 1);
  for (let az = 0; az < 360; az += 15) polyline(proj, Array.from({ length: 11 }, (_, i) => G.dirAE(az, -10 + i * 5)), 'rgba(94,231,255,.10)', 1);
}

function drawHorizon(proj, camAz) {
  const dip = G.horizonDip(station.alt);
  polyline(proj, Array.from({ length: 73 }, (_, i) => G.dirAE(i * 5, dip)), 'rgba(245,196,107,.7)', 1.5, [8, 6]);
  fx.font = '700 15px system-ui'; fx.textAlign = 'center'; fx.fillStyle = 'rgba(245,196,107,.9)';
  [['צפון', 0], ['מזרח', 90], ['דרום', 180], ['מערב', 270]].forEach(([n, az]) => { const p = proj.project(G.dirAE(az, dip)); if (p && p.x > 0 && p.x < W) fx.fillText(n, p.x, p.y + 18); });
}

function drawBuildings(proj) {
  if (!S.layers.future) return;
  const faces = [];
  for (const { b, verts } of S.buildings) {
    if (b.year > S.year) continue;
    const hot = b.year === S.year, n = verts.length;
    const dist = (v, up) => Math.hypot(v.e, v.n, v.u0 + up);
    const P = (v, up) => { const d = Math.hypot(v.e, v.n, v.u0 + up); return proj.project([v.e / d, v.n / d, (v.u0 + up) / d]); };
    const base = verts.map((v) => P(v, 0)), top = verts.map((v) => P(v, b.height));
    for (let i = 0; i < n; i++) {
      const j = (i + 1) % n, pts = [base[i], base[j], top[j], top[i]];
      if (pts.every(Boolean)) faces.push({ pts, hot, d: (dist(verts[i], 0) + dist(verts[j], 0)) / 2 });
    }
    if (top.every(Boolean)) faces.push({ pts: top, hot, d: dist(verts[0], b.height) - 1, roof: true });
  }
  faces.sort((a, c) => c.d - a.d);
  for (const f of faces) {
    fx.beginPath(); f.pts.forEach((p, i) => (i ? fx.lineTo(p.x, p.y) : fx.moveTo(p.x, p.y))); fx.closePath();
    fx.fillStyle = f.hot ? (f.roof ? 'rgba(255,224,150,.55)' : 'rgba(245,196,107,.32)') : (f.roof ? 'rgba(94,231,255,.30)' : 'rgba(94,231,255,.15)');
    fx.fill(); fx.strokeStyle = f.hot ? '#f5c46b' : 'rgba(94,231,255,.8)'; fx.lineWidth = f.hot ? 1.8 : 1; fx.stroke();
  }
}

const placed = [];
function layoutLabels(proj) {
  placed.length = 0;
  const cands = [];
  for (const it of S.items) {
    const d = S.calibrating ? { show: it === calibTarget(), cls: '', sub: '' } : describe(it);
    const pr = d.show ? proj.project(it.look.dir) : null;
    if (!pr || pr.x < -80 || pr.x > W + 80 || pr.y < 40 || pr.y > H + 40) { it.el.style.display = 'none'; continue; }
    cands.push({ it, d, pr });
  }
  cands.sort((a, b) => (b.it.p.pri - a.it.p.pri) || (a.it.look.dist - b.it.look.dist));
  for (const { it, d, pr } of cands) {
    if (it.cls !== d.cls || it.sub !== d.sub) {
      it.cls = d.cls; it.sub = d.sub; it.el.className = 'lbl ' + d.cls; it.w = 0;
      it.el.innerHTML = `<span class="n">${esc(it.p.name)}</span>${d.sub ? `<span class="s">${esc(d.sub)}</span>` : ''}`;
    }
    it.el.style.display = 'block';
    if (!it.w) { it.w = it.el.offsetWidth; it.h = it.el.offsetHeight; }
    let tier = 0, x = Math.max(72, Math.min(W - it.w - 6, pr.x - it.w / 2)), y;
    for (; tier < 7; tier++) {
      y = pr.y - 16 - it.h - tier * (it.h + 6);
      if (!placed.some((r) => x < r.x + r.w + 4 && x + it.w + 4 > r.x && y < r.y + r.h + 3 && y + it.h + 3 > r.y)) break;
    }
    if (tier >= 7 || y < 52) { it.el.style.display = 'none'; continue; }
    placed.push({ x, y, w: it.w, h: it.h });
    it.el.style.transform = `translate(${x}px,${y}px)`;
    fx.strokeStyle = 'rgba(94,231,255,.55)'; fx.lineWidth = 1; fx.beginPath(); fx.moveTo(pr.x, pr.y); fx.lineTo(Math.max(x + 8, Math.min(x + it.w - 8, pr.x)), y + it.h); fx.stroke();
    fx.fillStyle = d.cls === 'k-bible' ? '#f5c46b' : d.cls === 'k-history' ? '#ff8fa3' : '#5ee7ff';
    fx.beginPath(); fx.arc(pr.x, pr.y, 3.5, 0, 6.3); fx.fill();
  }
}

function drawCalibration(proj, camAz) {
  const t = calibTarget(), pr = proj.project(t.look.dir), cx = W / 2, cy = H / 2;
  fx.strokeStyle = 'rgba(255,255,255,.7)'; fx.lineWidth = 1; fx.beginPath();
  fx.moveTo(cx - 18, cy); fx.lineTo(cx + 18, cy); fx.moveTo(cx, cy - 18); fx.lineTo(cx, cy + 18); fx.stroke();
  const delta = G.norm180(t.look.az - camAz);
  $('#calibDelta').textContent = !pr || pr.x < 0 || pr.x > W ? `סובבו ${delta > 0 ? 'ימינה' : 'שמאלה'} כ־${Math.abs(Math.round(delta))}° כדי לראות את ${t.p.name}` : '';
  if (!pr) return;
  const pulse = 1 + 0.08 * Math.sin(performance.now() / 250);
  fx.strokeStyle = '#f5c46b'; fx.lineWidth = 3; fx.shadowColor = '#f5c46b'; fx.shadowBlur = 14;
  fx.beginPath(); fx.arc(pr.x, pr.y, 34 * pulse, 0, 6.3); fx.stroke(); fx.shadowBlur = 0;
  fx.beginPath(); fx.moveTo(pr.x - 46, pr.y); fx.lineTo(pr.x - 24, pr.y); fx.moveTo(pr.x + 24, pr.y); fx.lineTo(pr.x + 46, pr.y); fx.stroke();
}

function drawTape(camAz) {
  const w = W, h = 46, ppd = w / 100; // 100° across the strip
  tape.setTransform(DPR, 0, 0, DPR, 0, 0); tape.clearRect(0, 0, w, h);
  tape.fillStyle = 'rgba(6,18,28,.55)'; tape.fillRect(0, 0, w, h);
  tape.textAlign = 'center'; tape.font = '11px system-ui';
  const first = Math.ceil((camAz - 50) / 5) * 5;
  for (let a = first; a <= camAz + 50; a += 5) {
    const x = w / 2 + (a - camAz) * ppd, n = Math.round(G.norm360(a)), major = n % 15 === 0;
    tape.strokeStyle = major ? 'rgba(94,231,255,.9)' : 'rgba(94,231,255,.4)'; tape.beginPath(); tape.moveTo(x, h); tape.lineTo(x, h - (major ? 12 : 6)); tape.stroke();
    if (major) {
      const card = { 0: 'צ׳', 90: 'מז׳', 180: 'ד׳', 270: 'מע׳' }[n];
      tape.fillStyle = card ? '#f5c46b' : '#8fb0c4'; tape.font = card ? '700 14px system-ui' : '11px system-ui'; tape.fillText(card || n, x, h - 16);
    }
  }
  tape.fillStyle = '#f5c46b';
  for (const it of S.items) {
    if (it.kind !== 'poi' || !describe(it).show) continue;
    const dlt = G.norm180(it.look.az - camAz); if (Math.abs(dlt) > 50) continue;
    const x = w / 2 + dlt * ppd; tape.beginPath(); tape.moveTo(x, 3); tape.lineTo(x + 4, 8); tape.lineTo(x, 13); tape.lineTo(x - 4, 8); tape.fill();
  }
  tape.fillStyle = '#5ee7ff'; tape.beginPath(); tape.moveTo(w / 2 - 6, 0); tape.lineTo(w / 2 + 6, 0); tape.lineTo(w / 2, 8); tape.fill();
}

init();
