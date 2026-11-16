---
name: threejs-postprocessing
description: >
  Three.js post-processing with EffectComposer: render the scene to a buffer, then apply passes such as
  bloom, glitch, film grain, depth of field or anti-aliasing before output. Use for "post processing",
  "EffectComposer", "bloom / glow", "glitch", "ShaderPass", "custom shader pass", or adding effects to a
  three.js scene or a three.js-based video/HyperFrames composition.
---

# Three.js post-processing (EffectComposer)

Source: https://threejs.org/manual/#en/how-to-use-post-processing (page body: https://threejs.org/manual/pages/how-to-use-post-processing.html)

Scene → render target → chain of passes → screen. Passes run in the order added; the last enabled pass renders to the screen.

## Setup
```js
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { GlitchPass } from 'three/addons/postprocessing/GlitchPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const composer = new EffectComposer( renderer );
composer.addPass( new RenderPass( scene, camera ) ); // first: provides the scene as input
composer.addPass( new GlitchPass() );                // any effect pass(es)
composer.addPass( new OutputPass() );                // last: sRGB conversion + tone mapping
```

## Render loop
Call `composer.render()` instead of `renderer.render( scene, camera )`:
```js
function animate() {
  requestAnimationFrame( animate );
  composer.render();
}
```

## Rules
- `RenderPass` first, `OutputPass` last.
- Use the `three/addons/...` import path (official npm package); built-in passes live in `examples/jsm/postprocessing`.
- Custom effect: wrap a shader in `ShaderPass`.
  ```js
  import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
  import { LuminosityShader } from 'three/addons/shaders/LuminosityShader.js';
  composer.addPass( new ShaderPass( LuminosityShader ) );
  ```
  `CopyShader` (`three/addons/shaders/CopyShader.js`) is the minimal template for your own shader.
- Live example: https://threejs.org/examples/webgl_postprocessing_glitch

## Not covered by the source page (verify in the docs before relying on it)
Resizing (`composer.setSize`), pixel ratio, and WebGPU post-processing (separate manual page "Post-Processing" / `webgpu-postprocessing`).
