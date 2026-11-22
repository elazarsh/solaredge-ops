// Device orientation → smoothed device-to-world matrix. Handles the iOS permission prompt and iOS' relative alpha.
import { deviceMatrix, cameraAim, matToQuat, quatToMat, nlerp, norm180 } from './geo.js';

export class Orientation {
  constructor() { this.q = null; this.has = false; this.iosOff = null; this.lastAbs = 0; }

  static needsPermission() {
    return typeof DeviceOrientationEvent !== 'undefined' && typeof DeviceOrientationEvent.requestPermission === 'function';
  }

  /** Must be called from a user gesture on iOS. */
  async start() {
    if (Orientation.needsPermission()) {
      const r = await DeviceOrientationEvent.requestPermission();
      if (r !== 'granted') throw new Error('motion-denied');
    }
    window.addEventListener('deviceorientationabsolute', (e) => this._on(e, true), true);
    window.addEventListener('deviceorientation', (e) => this._on(e, false), true);
  }

  _on(e, isAbs) {
    if (e.alpha == null || e.beta == null || e.gamma == null) return;
    const now = performance.now();
    if (isAbs) this.lastAbs = now;
    else if (now - this.lastAbs < 500) return; // absolute stream is flowing — ignore the relative duplicate
    let alpha = e.alpha;
    if (typeof e.webkitCompassHeading === 'number' && e.webkitCompassHeading >= 0) {
      // iOS: alpha has an arbitrary zero; webkitCompassHeading is the magnetic heading of the camera when held upright.
      if (e.beta > 50 && e.beta < 130) {
        const aim = cameraAim(deviceMatrix(e.alpha, e.beta, e.gamma));
        const d = norm180(e.webkitCompassHeading - aim.az);
        this.iosOff = this.iosOff == null ? d : this.iosOff + norm180(d - this.iosOff) * 0.1;
      }
      alpha = e.alpha - (this.iosOff || 0);
    }
    const q = matToQuat(deviceMatrix(alpha, e.beta, e.gamma));
    this.q = this.q ? nlerp(this.q, q, 0.3) : q;
    this.has = true;
  }

  matrix() { return this.q ? quatToMat(this.q) : null; }
}
