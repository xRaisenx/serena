'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'../../src/serena/resources/dashboard/codemind');
const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
const css=fs.readFileSync(path.join(root,'console.css'),'utf8');
const js=fs.readFileSync(path.join(root,'console.js'),'utf8');
const bird=fs.readFileSync(path.join(root,'cuckoo-mark.svg'),'utf8');

test('SCC Secucko branding is visible at unlock, navigation, hero and footer',()=>{
  assert.match(html,/<title>SCC \| Secucko Semantic Command Center<\/title>/);
  assert.match(html,/SCC<span class="subtle"> \/ Secucko<\/span>/);
  assert.match(html,/<strong>SCC<\/strong><small>SECUCKO \/ SERENA<\/small>/);
  assert.equal((html.match(/src="cuckoo-mark\.svg"/g)||[]).length,5);
  assert.match(html,/SCC \/ SECUCKO/);
});

test('bird mark is a standalone, accessible, script-free SVG',()=>{
  assert.match(bird,/<svg xmlns="http:\/\/www\.w3\.org\/2000\/svg" viewBox="0 0 160 160"/);
  assert.match(bird,/<title id="bird-title">Secucko cuckoo bird emblem<\/title>/);
  assert.doesNotMatch(bird,/<script|<foreignObject|<image|\b(?:href|src)\s*=\s*["'](?:https?:|data:)/i);
  assert.match(html,/<link rel="icon" type="image\/svg\+xml" href="cuckoo-mark\.svg">/);
  assert.match(html,/class="hero-bird" src="cuckoo-mark\.svg" alt=""/);
});

test('remove obsolete ornamental elements and cross-project UI text',()=>{
  assert.doesNotMatch(html,/orbit-core|orbit-node|workspace-switch|NMBV Bot/);
  assert.doesNotMatch(css,/\.orbit-core|\.orbit-node|\.workspace-switch/);
  assert.match(html,/Task evidence/);
  assert.match(html,/Task records are observations/);
});

test('preserve authenticated operator controls and legacy API contract',()=>{
  for(const id of ['unlock-form','navigation','skill-route-form','forecast-form','tunnel-key-form','tunnel-doctor','tunnel-start','tunnel-stop','tunnel-remove-key']) {
    assert.ok(html.includes('id="'+id+'"'),id);
  }
  assert.match(js,/\/codemind\/api\/overview/);
  assert.match(js,/data\.application !== "CODEMIND Serena"/);
  assert.match(html,/id="operator-token"[^>]*type="password"/);
});

test('design tokens support two themes, mobile widths and reduced motion',()=>{
  assert.match(css,/:root\{color-scheme:dark;/);
  assert.match(css,/body\.light\{color-scheme:light;/);
  assert.match(css,/body\.light \.button\.primary\{color:#fff\}/);
  assert.match(css,/body\.light \.sidebar\{background:/);
  assert.match(css,/\.hero-bird\{/);
  for(const px of [900,650,360]) assert.ok(css.includes('@media(max-width:'+px+'px)'),px);
  assert.match(css,/@media\(prefers-reduced-motion:reduce\)/);
  assert.match(css,/:focus-visible\{outline:/);
});
