/**
 * Note: When using the Node.JS APIs, the config file
 * doesn't apply. Instead, pass options directly to the APIs.
 *
 * All configuration options: https://remotion.dev/docs/config
 */

import { Config } from "@remotion/cli/config";
import { enableTailwind } from '@remotion/tailwind-v4';
import { existsSync } from 'node:fs';

// remotion.media (Remotion's Chrome download host) is blocked in the cloud sandbox,
// so reuse a Chrome that is already on disk.
const CHROME_CANDIDATES = [
  process.env.REMOTION_CHROME,
  '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell',
];
const chrome = CHROME_CANDIDATES.find((p) => p && existsSync(p));

Config.setRspack(true);
Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
Config.overrideBundlerConfig(enableTailwind);
if (chrome) {
  Config.setBrowserExecutable(chrome);
}
