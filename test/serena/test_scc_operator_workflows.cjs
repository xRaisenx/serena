'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '../../src/serena/resources/dashboard/codemind');
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const js = fs.readFileSync(path.join(root, 'console.js'), 'utf8');
const css = fs.readFileSync(path.join(root, 'console.css'), 'utf8');
const pages = ['overview', 'tools', 'skills', 'forecast', 'learning', 'execution', 'commander', 'connections', 'security', 'about'];

test('every SCC navigation destination has one matching page and heading', () => {
  const links = [...html.matchAll(/<button[^>]+data-view="([a-z]+)"[^>]*>/g)].map(m => m[1]);
  const sections = [...html.matchAll(/<section[^>]+data-page="([a-z]+)"[^>]*>/g)].map(m => m[1]);
  assert.deepEqual(links, pages);
  assert.deepEqual(sections, pages);
  for (const page of pages) {
    assert.match(html, new RegExp('id="' + page + '-heading"'));
  }
});

test('each page has a real user action and a bounded proof contract', () => {
  for (const id of ['operator-actions', 'tools-list', 'skill-route-form', 'skill-packet-next',
    'forecast-form', 'packet-download', 'learning-investigate', 'learning-export',
    'task-export', 'task-plan', 'commander-check', 'tunnel-doctor', 'tunnel-start',
    'tunnel-stop', 'tunnel-evidence', 'security-export', 'security-next']) {
    assert.ok(html.includes('id="' + id + '"'), 'missing interface control ' + id);
  }
  for (const id of ['skill-packet-next', 'packet-download', 'learning-investigate',
    'learning-export', 'task-export', 'task-plan', 'commander-check',
    'tunnel-evidence', 'security-export', 'security-next']) {
    assert.ok(js.includes('byId("' + id + '").addEventListener('), 'unwired control ' + id);
  }
  assert.match(js, /data-action-view/);
  assert.match(js, /data-copy-tool/);
});

test('operator task pathway uses authenticated native SCC advisory endpoints', () => {
  assert.match(js, /fetch\("\/codemind\/api\/v2\/skills\/route"/);
  assert.match(js, /fetch\("\/codemind\/api\/v2\/actions\/preview"/);
  assert.match(js, /state\.skillRoute = \{request_text: requestText/);
  assert.match(js, /state\.forecast = result/);
  assert.match(js, /schema:"scc-engineering-packet-v1"/);
  assert.match(js, /status:"ADVISORY_ONLY",authorization_granted:false/);
  assert.match(js, /selected_installed_skills|installed_skills:/);
});

test('locking SCC clears private planning state and stale requests cannot overwrite new session', () => {
  assert.match(js, /state\.epoch \+= 1/);
  assert.match(js, /state\.skillRoute = null; state\.forecast = null; state\.goal = ""/);
  assert.match(js, /state\.token !== routedToken \|\| state\.epoch !== routedEpoch/);
  assert.match(js, /state\.token === currentToken && state\.epoch === currentEpoch/);
  assert.match(js, /packet-download"\)\.disabled = true/);
});

test('NMBV Bot execution is never implied as a connected SCC native bridge', () => {
  assert.doesNotMatch(js, /NMBV Bot worker bridge|nmbv_skill_route|nmbv_next_action/);
  assert.doesNotMatch(html, /nmbv_skill_route|nmbv_next_action/);
  assert.match(html, /reference methods, not literally 100 living coders/);
  assert.match(html, /does not inherit external worker sessions/);
});

test('About SCC records the complete user-supplied naming history and has usable stage navigation', () => {
  for (const word of ['Serena CODEMIND Commander', 'Secoco', 'Secucko', 'cuckoo']) {
    assert.ok(html.includes(word), word);
  }
  assert.match(html, /data-page="about"/);
  assert.match(html, /SECUCKO \/ SCC/);
  for (const page of ['tools', 'skills', 'forecast', 'security']) {
    assert.ok(html.includes('data-go="' + page + '"'));
  }
});

test('exports are bounded observation packets, not fake readiness or secret-bearing snapshots', () => {
  for (const schema of ['scc-guard-observation-v1', 'scc-task-observations-v1',
    'scc-tunnel-observation-v1', 'scc-acceptance-evidence-v1']) {
    assert.ok(js.includes(schema), schema);
  }
  assert.match(js, /No tunnel key or connection secret is exported/);
  assert.match(js, /revision_attested===true/);
  assert.match(js, /c\.ready===true&&c\.authenticated===true/);
  assert.match(js, /No restart was attempted/);
});

test('tunnel client readiness stays distinct from a recent MCP consumer proof', () => {
  assert.ok(html.includes('id="tunnel-consumer-challenge"'));
  assert.ok(html.includes('id="tunnel-consumer-result"'));
  assert.match(js, /managed_process_running === true && tunnel\.client_ready === true/);
  assert.match(js, /MCP CALL SEEN/);
  assert.match(js, /origin is not cryptographically attested/);
  assert.match(js, /\/codemind\/api\/tunnel\/acceptance\/challenge/);
});

test('responsive about and operator widgets have small-screen layout', () => {
  assert.match(css, /\.scc-action-row/);
  assert.match(css, /\.about-steps/);
  assert.match(css, /@media\(max-width:650px\)/);
  assert.match(css, /#skill-route-form\{grid-template-columns:1fr\}/);
});
