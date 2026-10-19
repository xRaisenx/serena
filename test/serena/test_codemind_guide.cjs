'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname,'../../src/serena/resources/dashboard/codemind');
const doc = name=>fs.readFileSync(path.join(root,name),'utf8');

test('operator guide exposes accessible How-To, About, scenarios and FAQ destinations',()=>{
 const h=doc('guide.html');
 for(const id of ['howto','about','scenarios','faqs','readiness'])assert.match(h,new RegExp('id="'+id+'"'));
 assert.match(h,/<a[^>]+href="#howto"/); assert.match(h,/<a[^>]+href="#faqs"/);
 assert.match(h,/<main\b[^>]*id="main"/);
 assert.match(h,/<label[^>]*for="guide-search"/);
 assert.match(h,/<input[^>]+id="guide-search"[^>]*type="search"/);
 assert.match(h,/<p[^>]+id="guide-results"[^>]*role="status"/);
 assert.match(h,/<details\b[^>]*data-guide-item/g);
 assert.match(h, /href="index.html"/);
});

test('deployment matrix requires all five verified gates and never offers a fake start button',()=>{
 const h=doc('guide.html');
 for(const name of ['G1','G2','G3','G4','G5']) assert.match(h,new RegExp('data-gate="'+name+'"'));
 assert.equal((h.match(/data-gate="G[1-5]"/g)||[]).length,5);
 assert.match(h,/NOT VERIFIED/);
 assert.match(h,/at most three active/);
 assert.match(h,/source configured is not host trusted/);
 assert.doesNotMatch(h,/data-action="deploy-all"/);
});

test('FAQ cases cover realistic workflows and distinguish selected from executed',()=>{
 const h=doc('guide.html');
 for(const x of ['Bug fix','Feature implementation','New file type','Hook installation','Subagent queue','failed verification','Learning'])assert.ok(h.includes(x),x);
 assert.match(h,/selected ≠ loaded ≠ executed/);
 assert.match(h,/no LLM call for metadata routing/);
 assert.match(h,/not the same as an autonomous repair/);
});

test('search matching is deterministic, accent-insensitive, and empty-query restores all',()=>{
 const {matchingIndices}=require(path.join(root,'guide.js'));
 const items=['Hooks · Install and trust','Symbol-level résumé indexing','Three subagents: queue and recycle'];
 assert.deepEqual(matchingIndices(items,'HOOKS'),[0]);
 assert.deepEqual(matchingIndices(items,'resume'),[1]);
 assert.deepEqual(matchingIndices(items,'QUEUE'),[2]);
 assert.deepEqual(matchingIndices(items,'  '),[0,1,2]);
 assert.deepEqual(matchingIndices(items,'inexistent'),[]);
});

test('style retains keyboard focus, responsive layout and reduced-motion path',()=>{
 const css=doc('guide.css');
 assert.match(css,/:focus-visible/); assert.match(css,/@media\s*\(max-width:\s*700px\)/);
 assert.match(css,/prefers-reduced-motion/); assert.match(css,/min-width:\s*0/);
});