'use strict';
const test=require('node:test'), assert=require('node:assert/strict'), fs=require('node:fs'), path=require('node:path');
const js=fs.readFileSync(path.resolve(__dirname,'../../src/serena/resources/dashboard/codemind/console.js'),'utf8');
const start=js.indexOf('  function renderMethodCatalog() {');
const end=js.indexOf('\n  async function loadMethodCatalog()',start);
assert.ok(start>=0&&end>start,'Expected a bounded renderMethodCatalog source function');
const functionCode=js.slice(start,end);
const methods=[
 {id:'codemind-bug-triage',description:'First failure triage',source_name:'bug-triage'},
 {id:'codemind-repository-audit',description:'Read-only audit',source_name:'repository-audit'}
];
function setup(skills,q=''){
 const widgets={
   'method-list':{children:[],replaceChildren(){this.children=[]},append(...xs){this.children.push(...xs)}},
   'method-search':{value:q},
   'method-count':{textContent:''}
 };
 const byId=name=>widgets[name];
 const element=(tag,cls='',content)=>({tag,cls,content,children:[],append(...xs){this.children.push(...xs)}});
 const text=(name,value)=>{widgets[name].textContent=String(value)};
 const state={catalog:{schema:2,state:'REFERENCE_ONLY',count:2,methods},snapshot:skills};
 const render=new Function('byId','state','element','text',functionCode+';return renderMethodCatalog;')(byId,state,element,text);
 render();
 const cards=widgets['method-list'].children;
 return {cards,count:widgets['method-count'].textContent};
}
test('installed reference is rendered as an installed project skill, not an executing worker',()=>{
 const r=setup({skills:{state:'available',items:[{id:'codemind-bug-triage',version:'1.0'}]}});
 assert.equal(r.count,'2 OF 2 REFERENCES • 1 INSTALLED');
 assert.equal(r.cards.length,2);
 assert.equal(r.cards[0].children[0].content,'PROJECT SKILL INSTALLED • NOT EXECUTED');
 assert.equal(r.cards[1].children[0].content,'REFERENCE ONLY • NOT INSTALLED');
});
test('unverified skill snapshot never implies a negative installation status',()=>{
 const r=setup(null);
 assert.match(r.count,/INSTALLATION UNVERIFIED/);
 assert.ok(r.cards.every(card=>card.children[0].content==='INSTALLATION UNVERIFIED'));
});
test('available but empty project reports methods as reference-only',()=>{
 const r=setup({skills:{state:'available',items:[]}});
 assert.equal(r.count,'2 OF 2 REFERENCES • 0 INSTALLED');
 assert.ok(r.cards.every(card=>card.children[0].content==='REFERENCE ONLY • NOT INSTALLED'));
});
test('search filters method entries without claiming unrelated methods are loaded',()=>{
 const r=setup({skills:{state:'available',items:[{id:'codemind-bug-triage'}]}},'audit');
 assert.equal(r.cards.length,1);
 assert.equal(r.cards[0].children[1].content,'codemind-repository-audit');
 assert.equal(r.cards[0].children[0].content,'REFERENCE ONLY • NOT INSTALLED');
});
