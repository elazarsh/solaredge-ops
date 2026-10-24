// Geodesy + orientation math. Pure functions, no DOM — unit-tested in tests/geo.test.mjs.
export const D2R = Math.PI / 180;
export const R2D = 180 / Math.PI;
const WGS84_A = 6378137;
const WGS84_E2 = 6.69437999014e-3;
const R_EARTH = 6371000;
const REFRACTION_K = 0.13; // standard atmospheric refraction coefficient

const clamp = (x, lo, hi) => Math.min(hi, Math.max(lo, x));
export const norm360 = (d) => ((d % 360) + 360) % 360;
export const norm180 = (d) => ((((d + 180) % 360) + 360) % 360) - 180;

export function ecef({ lat, lon, alt = 0 }) {
  const phi = lat * D2R, lam = lon * D2R;
  const s = Math.sin(phi), c = Math.cos(phi);
  const N = WGS84_A / Math.sqrt(1 - WGS84_E2 * s * s);
  return [(N + alt) * c * Math.cos(lam), (N + alt) * c * Math.sin(lam), (N * (1 - WGS84_E2) + alt) * s];
}

/** East/North/Up (metres) of `t` in the local tangent frame of `obs`. */
export function toENU(obs, t) {
  const o = ecef(obs), p = ecef(t);
  const dx = p[0] - o[0], dy = p[1] - o[1], dz = p[2] - o[2];
  const phi = obs.lat * D2R, lam = obs.lon * D2R;
  const sp = Math.sin(phi), cp = Math.cos(phi), sl = Math.sin(lam), cl = Math.cos(lam);
  return [-sl * dx + cl * dy, -sp * cl * dx - sp * sl * dy + cp * dz, cp * cl * dx + cp * sl * dy + sp * dz];
}

/** Where to look from `obs` to see `t`: azimuth (° clockwise from true north), elevation angle (°), distance (m) and a unit ENU direction. Includes earth curvature (via ECEF) and standard refraction. */
export function lookAt(obs, t) {
  const [e, n, u0] = toENU(obs, t);
  const horiz = Math.hypot(e, n);
  const u = u0 + (REFRACTION_K * horiz * horiz) / (2 * R_EARTH);
  const len = Math.hypot(e, n, u) || 1;
  return {
    az: norm360(Math.atan2(e, n) * R2D),
    el: Math.atan2(u, horiz) * R2D,
    dist: Math.hypot(e, n, u0),
    horiz,
    dir: [e / len, n / len, u / len],
  };
}

/** Angle (°, negative) below the astronomical horizontal at which the true sea/land horizon appears for an observer `h` metres up. */
export function horizonDip(h) {
  const Re = R_EARTH / (1 - REFRACTION_K);
  return -Math.acos(Re / (Re + Math.max(0, h))) * R2D;
}

/** Unit ENU vector for azimuth/elevation in degrees. */
export const dirAE = (az, el) => [Math.sin(az * D2R) * Math.cos(el * D2R), Math.cos(az * D2R) * Math.cos(el * D2R), Math.sin(el * D2R)];

// ---- 3x3 row-major matrices ------------------------------------------------
export const mul = (a, b) => [
  a[0] * b[0] + a[1] * b[3] + a[2] * b[6], a[0] * b[1] + a[1] * b[4] + a[2] * b[7], a[0] * b[2] + a[1] * b[5] + a[2] * b[8],
  a[3] * b[0] + a[4] * b[3] + a[5] * b[6], a[3] * b[1] + a[4] * b[4] + a[5] * b[7], a[3] * b[2] + a[4] * b[5] + a[5] * b[8],
  a[6] * b[0] + a[7] * b[3] + a[8] * b[6], a[6] * b[1] + a[7] * b[4] + a[8] * b[7], a[6] * b[2] + a[7] * b[5] + a[8] * b[8],
];
export const transpose = (m) => [m[0], m[3], m[6], m[1], m[4], m[7], m[2], m[5], m[8]];
export const apply = (m, v) => [m[0] * v[0] + m[1] * v[1] + m[2] * v[2], m[3] * v[0] + m[4] * v[1] + m[5] * v[2], m[6] * v[0] + m[7] * v[1] + m[8] * v[2]];
export const rotZ = (d) => { const c = Math.cos(d * D2R), s = Math.sin(d * D2R); return [c, -s, 0, s, c, 0, 0, 0, 1]; };
export const rotX = (d) => { const c = Math.cos(d * D2R), s = Math.sin(d * D2R); return [1, 0, 0, 0, c, -s, 0, s, c]; };
export const rotY = (d) => { const c = Math.cos(d * D2R), s = Math.sin(d * D2R); return [c, 0, s, 0, 1, 0, -s, 0, c]; };

/** W3C DeviceOrientation (alpha, beta, gamma in degrees) → device-to-world matrix (world = East, North, Up). */
export const deviceMatrix = (alpha, beta, gamma) => mul(mul(rotZ(alpha), rotX(beta)), rotY(gamma));

/** Where the back camera (device −Z) points, in the world frame. */
export function cameraAim(R) {
  const d = apply(R, [0, 0, -1]);
  return { az: norm360(Math.atan2(d[0], d[1]) * R2D), el: Math.asin(clamp(d[2], -1, 1)) * R2D };
}

// ---- quaternions (for sensor smoothing) --------------------------------------
export function matToQuat(m) {
  const t = m[0] + m[4] + m[8];
  let w, x, y, z, s;
  if (t > 0) { s = Math.sqrt(t + 1) * 2; w = s / 4; x = (m[7] - m[5]) / s; y = (m[2] - m[6]) / s; z = (m[3] - m[1]) / s; }
  else if (m[0] > m[4] && m[0] > m[8]) { s = Math.sqrt(1 + m[0] - m[4] - m[8]) * 2; w = (m[7] - m[5]) / s; x = s / 4; y = (m[1] + m[3]) / s; z = (m[2] + m[6]) / s; }
  else if (m[4] > m[8]) { s = Math.sqrt(1 + m[4] - m[0] - m[8]) * 2; w = (m[2] - m[6]) / s; x = (m[1] + m[3]) / s; y = s / 4; z = (m[5] + m[7]) / s; }
  else { s = Math.sqrt(1 + m[8] - m[0] - m[4]) * 2; w = (m[3] - m[1]) / s; x = (m[2] + m[6]) / s; y = (m[5] + m[7]) / s; z = s / 4; }
  return [w, x, y, z];
}
export function quatToMat([w, x, y, z]) {
  return [
    1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w),
    2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w),
    2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y),
  ];
}
export function nlerp(a, b, k) {
  const sign = a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3] < 0 ? -1 : 1;
  const q = a.map((v, i) => v + (sign * b[i] - v) * k);
  const len = Math.hypot(...q) || 1;
  return q.map((v) => v / len);
}

// ---- projection ------------------------------------------------------------
/**
 * Build a world→screen projector.
 * yawOff / pitchOff are the calibration corrections: true camera azimuth = measured + yawOff,
 * true camera elevation = measured + pitchOff. fovDeg is the field of view along the screen's long axis.
 */
export function makeProjector({ R, yawOff = 0, pitchOff = 0, screenAngle = 0, fovDeg = 65, W, H }) {
  const f = (Math.max(W, H) / 2) / Math.tan((fovDeg * D2R) / 2);
  const M = mul(transpose(R), rotZ(yawOff));
  const ca = Math.cos(screenAngle * D2R), sa = Math.sin(screenAngle * D2R);
  const cp = Math.cos(pitchOff * D2R), sp = Math.sin(pitchOff * D2R);
  return {
    f,
    project(dir) {
      const v = apply(M, dir);
      const fw0 = -v[2];
      const sx = v[0] * ca - v[1] * sa, sy0 = v[0] * sa + v[1] * ca;
      const sy = sy0 * cp - fw0 * sp, fw = fw0 * cp + sy0 * sp;
      if (fw <= 1e-3) return null; // behind the camera
      return { x: W / 2 + (f * sx) / fw, y: H / 2 - (f * sy) / fw };
    },
  };
}
