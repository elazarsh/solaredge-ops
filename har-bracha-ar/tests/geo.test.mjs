import test from 'node:test';
import assert from 'node:assert/strict';
import * as G from '../js/geo.js';

const near = (a, b, tol, msg) => assert.ok(Math.abs(a - b) <= tol, `${msg || ''} expected ${b}±${tol}, got ${a}`);
const station = { lat: 32.186, lon: 35.237, alt: 860 };

test('cardinal azimuths', () => {
  near(G.lookAt(station, { lat: 32.286, lon: 35.237, alt: 860 }).az, 0, 0.1, 'north');
  near(G.lookAt(station, { lat: 32.186, lon: 35.337, alt: 860 }).az, 90, 0.1, 'east');
  near(G.lookAt(station, { lat: 32.086, lon: 35.237, alt: 860 }).az, 180, 0.1, 'south');
  near(G.lookAt(station, { lat: 32.186, lon: 35.137, alt: 860 }).az, 270, 0.1, 'west');
});

test('distance ~ 1° lat = 111 km', () => {
  near(G.lookAt(station, { lat: 33.186, lon: 35.237, alt: 860 }).dist / 1000, 111, 1);
});

test('Hermon is a sliver above the horizon, ~150 km north-north-east', () => {
  const h = G.lookAt(station, { lat: 33.4161, lon: 35.8575, alt: 2814 });
  near(h.dist / 1000, 149, 4); near(h.az, 25, 4);
  assert.ok(h.el > 0 && h.el < 0.5, `el=${h.el}`);
});

test('Tel Aviv towers sit below the astronomical horizon', () => {
  assert.ok(G.lookAt(station, { lat: 32.0743, lon: 34.7922, alt: 200 }).el < -0.5);
});

test('horizon dip at 860 m is about -1°', () => near(G.horizonDip(860), -0.95, 0.15));

test('device pointing: upright phone facing north / pitched up', () => {
  const north = G.cameraAim(G.deviceMatrix(0, 90, 0));
  near(north.az, 0, 0.01); near(north.el, 0, 0.01);
  const east = G.cameraAim(G.deviceMatrix(-90, 90, 0)); // alpha counter-clockwise → facing east
  near(east.az, 90, 0.01);
  near(G.cameraAim(G.deviceMatrix(0, 110, 0)).el, 20, 0.01);
  near(G.cameraAim(G.deviceMatrix(0, 0, 0)).el, -90, 0.01); // lying flat looks at the ground
});

test('quaternion round trip preserves orientation', () => {
  const m = G.deviceMatrix(123, 77, -15), r = G.quatToMat(G.matToQuat(m));
  m.forEach((v, i) => near(r[i], v, 1e-9));
});

test('projection: aim at a target puts it at the screen centre; up/right land in the right place', () => {
  const W = 400, H = 800;
  const R = G.deviceMatrix(-65, 90, 0); // facing azimuth 65°
  const P = G.makeProjector({ R, W, H, fovDeg: 65 });
  const c = P.project(G.dirAE(65, 0));
  near(c.x, 200, 0.01); near(c.y, 400, 0.01);
  const right = P.project(G.dirAE(75, 0)); assert.ok(right.x > 200, 'east of facing is to the right');
  near(right.y, 400, 0.01);
  const up = P.project(G.dirAE(65, 10)); assert.ok(up.y < 400, 'higher elevation is up the screen');
  assert.equal(P.project(G.dirAE(245, 0)), null, 'behind the camera');
  // 65° across the long axis (height) → a point 32.5° up sits at the top edge
  near(P.project(G.dirAE(65, 32.5)).y, 0, 0.5);
});

test('calibration offsets: yawOff = expected − measured recentres the target', () => {
  const R = G.deviceMatrix(-50, 90, 0); // sensor says 50°, truth is 65°
  const P = G.makeProjector({ R, yawOff: 15, W: 400, H: 800 });
  near(P.project(G.dirAE(65, 0)).x, 200, 0.01);
  const Q = G.makeProjector({ R: G.deviceMatrix(0, 95, 0), pitchOff: -5, W: 400, H: 800 }); // sensor says +5°, truth 0°
  near(Q.project(G.dirAE(0, 0)).y, 400, 0.01);
});

test('landscape screen rotation keeps an aimed-at target centred', () => {
  const R = G.deviceMatrix(-65, 90, 0);
  const P = G.makeProjector({ R, screenAngle: 90, W: 800, H: 400 });
  const c = P.project(G.dirAE(65, 0)); near(c.x, 400, 0.01); near(c.y, 200, 0.01);
});
