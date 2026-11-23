// usage: node render.js stills 1,12,30 | node render.js full out.mp4
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const FPS = 24, D = 90;

(async () => {
  const mode = process.argv[2];
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.resolve(__dirname, 'video.html'));
  await page.waitForFunction(() => window.__ready === true);
  await page.evaluate(() => Promise.all([...document.images].map(i => i.complete ? 1 : new Promise(r => { i.onload = i.onerror = r; }))));
  await page.evaluate(() => document.fonts.ready);

  if (mode === 'stills') {
    for (const s of process.argv[3].split(',')) {
      const t = parseFloat(s);
      await page.evaluate(([t, f]) => window.seek(t, f), [t, Math.round(t * FPS)]);
      await page.screenshot({ path: `build/still_${String(s).replace('.', '_')}.jpg`, type: 'jpeg', quality: 85 });
    }
  } else {
    const out = process.argv[3] || 'out/drill.mp4';
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
      '-i', 'build/audio.wav', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p',
      '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    const total = D * FPS;
    for (let f = 0; f < total; f++) {
      await page.evaluate(([t, fr]) => window.seek(t, fr), [f / FPS, f]);
      const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (f % 240 === 0) console.log('frame', f, '/', total);
    }
    ff.stdin.end();
    await new Promise(r => ff.on('close', r));
  }
  await browser.close();
})();
