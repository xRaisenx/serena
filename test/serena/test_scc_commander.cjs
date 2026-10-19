// SPDX-License-Identifier: GPL-3.0-or-later
'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const crypto=require('node:crypto');
const {createServer,READ_ONLY_TOOLS,IDENTITY}=require('../../tools/scc_commander/server.cjs');
const TOKEN='scc-test-token-only-not-a-real-secret-'+('1'.repeat(40));
const challenge='1'.repeat(40);
let server,base,root;

test.before(async()=>{
  root=fs.mkdtempSync(path.join(os.tmpdir(),'scc-commander-spec-'));
  fs.mkdirSync(path.join(root,'docs'));
  fs.writeFileSync(path.join(root,'docs','fixture.txt'),'SCC owns its service\n');
  fs.writeFileSync(path.join(root,'.env'),'secret-not-for-mcp');
  server=createServer({token:TOKEN,projectRoot:root,port:0});
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  base='http://127.0.0.1:'+server.address().port;
});
test.after(async()=>{
  if(server)await new Promise(resolve=>server.close(resolve));
  if(root)fs.rmSync(root,{recursive:true,force:true});
});
function getHeaders(extra={}){return {Authorization:'Bearer '+TOKEN,...extra};}
async function rpc(method,params={},id=1){
  const response=await fetch(base+'/mcp',{method:'POST',headers:{...getHeaders(), 'Content-Type':'application/json','Accept':'application/json, text/event-stream'},body:JSON.stringify({jsonrpc:'2.0',id,method,params})});
  assert.equal(response.status,200);
  return response.json();
}
test('SCC service has independent local-only identity and seven read-only tools',()=>{
  assert.equal(IDENTITY,'SCC.WindowsCommander');
  assert.equal(READ_ONLY_TOOLS.length,7);
  assert.ok(READ_ONLY_TOOLS.every(t=>t.annotations.readOnlyHint===true));
  assert.ok(READ_ONLY_TOOLS.every(t=>t.name.startsWith('scc_')));
  assert.ok(!READ_ONLY_TOOLS.some(t=>/execute|shell|restart|delete|write/i.test(t.name)));
});
test('health proof uses nonce, SCC domain, HMAC-SHA256 and no shared NMBV key',async()=>{
  const response=await fetch(base+'/codemind/health',{headers:getHeaders({'X-Codemind-Challenge':challenge})});
  assert.equal(response.status,200);
  const result=await response.json();
  assert.deepEqual({service:result.service,ready:result.ready,mcp_initialize:result.mcp_initialize,nonce:result.nonce},
    {service:IDENTITY,ready:true,mcp_initialize:true,nonce:challenge});
  const expected=crypto.createHmac('sha256',TOKEN).update(challenge+':'+IDENTITY+':v1').digest('hex');
  assert.equal(result.proof,expected);
  assert.notEqual(result.proof,crypto.createHmac('sha256',TOKEN).update(challenge+':WindowsCommander.McpServer:v1').digest('hex'));
});
test('invalid token, missing challenge and untrusted path fail closed',async()=>{
  assert.equal((await fetch(base+'/codemind/health',{headers:{Authorization:'Bearer bad','X-Codemind-Challenge':challenge}})).status,401);
  assert.equal((await fetch(base+'/codemind/health',{headers:getHeaders()})).status,400);
  assert.equal((await fetch(base+'/codemind/health',{headers:getHeaders({'X-Codemind-Challenge':'wrong'})})).status,400);
  assert.equal((await fetch(base+'/codemind/health?nonce=1',{headers:getHeaders({'X-Codemind-Challenge':challenge})})).status,404);
  assert.equal((await fetch(base+'/admin',{headers:getHeaders()})).status,404);
});
test('MCP initialize and tools/list are real JSON-RPC responses',async()=>{
  const init=await rpc('initialize',{protocolVersion:'2025-03-26',capabilities:{},clientInfo:{name:'scc-test',version:'1.0'}});
  assert.equal(init.result.serverInfo.name,IDENTITY);
  assert.deepEqual(init.result.capabilities,{tools:{}});
  const list=await rpc('tools/list',{},2);
  assert.equal(list.result.tools.length,7);
  assert.ok(list.result.tools.every(x=>x.inputSchema?.type==='object'));
});
test('observed read-only tools return structured tool/call data',async()=>{
  for(const name of ['scc_system_info','scc_runtime_status']){
    const response=await rpc('tools/call',{name,arguments:{}},4);
    assert.equal(response.result.isError,false);
    const value=JSON.parse(response.result.content[0].text);
    if(name==='scc_runtime_status'){
      assert.equal(value.service,IDENTITY);assert.equal(value.execution_authorized,false);assert.equal(value.nmbv_shared,false);
    }else assert.ok(value.hostname);
  }
});
test('scoped file reader cannot escape through absolute, parent or oversized paths',async()=>{
  const good=await rpc('tools/call',{name:'scc_read_project_file',arguments:{relative_path:'docs/fixture.txt'}});
  assert.equal(JSON.parse(good.result.content[0].text).content,'SCC owns its service\n');
  for(const path of ['../secret.txt','C:\\Users\\secret.txt','/etc/passwd','\\\\server\\share','.env','.codemind/peer-token.txt','fixture.txt','x'.repeat(300)]){
    const bad=await rpc('tools/call',{name:'scc_read_project_file',arguments:{relative_path:path}});
    assert.equal(bad.result.isError,true,path);
    assert.match(bad.result.content[0].text,/denied|invalid/);
  }
});
test('arbitrary command execution and arbitrary RPC methods cannot be invoked',async()=>{
  const result=await rpc('tools/call',{name:'run_powershell',arguments:{command:'Remove-Item /'}});
  assert.equal(result.result.isError,true);
  assert.match(result.result.content[0].text,/tool_not_found/);
  const method=await rpc('commander/restart',{});
  assert.equal(method.error.code,-32601);
});
test('PID injection, extra arguments, and invalid shapes are rejected',async()=>{
  for(const args of [{pid:'1; Get-Process'},{pid:0},{pid:1,command:'stop'},{pid:1.5}]){
    const r=await rpc('tools/call',{name:'scc_process_details',arguments:args});
    assert.equal(r.result.isError,true);
  }
  const result=await rpc('tools/call',{name:'scc_system_info',arguments:{execute:true}});
  assert.equal(result.result.isError,true);
});
test('MCP requires bearer even for discovery, and rejects large requests',async()=>{
  const unauthorized=await fetch(base+'/mcp',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({jsonrpc:'2.0',id:1,method:'tools/list'})});
  assert.equal(unauthorized.status,401);
  const oversized=await fetch(base+'/mcp',{method:'POST',headers:{...getHeaders(),'Content-Type':'application/json'},body:JSON.stringify({jsonrpc:'2.0',id:2,method:'ping',extra:'x'.repeat(17000)})});
  assert.equal(oversized.status,413);
});
test('weak token and invalid listening port are rejected at construction',()=>{
  assert.throws(()=>createServer({token:'weak',projectRoot:root}),/strong_scc_token_required/);
  assert.throws(()=>createServer({token:TOKEN,projectRoot:root,port:99999}),/invalid_port/);
});
