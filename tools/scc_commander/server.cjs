// SPDX-License-Identifier: GPL-3.0-or-later
// SCC Windows Commander: an independently owned, loopback-only MCP service.
// No NMBV source, credentials, process ownership or restart logic is used.
'use strict';
const http = require('node:http');
const os = require('node:os');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {execFile} = require('node:child_process');

const IDENTITY = 'SCC.WindowsCommander';
const PROTOCOL = '2025-03-26';
const MAX_BODY = 16384;
const MAX_OUTPUT = 24000;
const MAX_FILE = 16384;
const READ_ONLY_TOOLS = Object.freeze([
  {name:'scc_system_info',description:'Windows hostname, platform, uptime, Node runtime and memory observation.',inputSchema:{type:'object',properties:{},additionalProperties:false},annotations:{readOnlyHint:true}},
  {name:'scc_list_processes',description:'Observe up to 60 Windows processes. No process control.',inputSchema:{type:'object',properties:{},additionalProperties:false},annotations:{readOnlyHint:true}},
  {name:'scc_list_services',description:'Observe a bounded set of Windows services. No start/stop.',inputSchema:{type:'object',properties:{},additionalProperties:false},annotations:{readOnlyHint:true}},
  {name:'scc_list_listeners',description:'Observe local listening TCP ports and owning process IDs.',inputSchema:{type:'object',properties:{},additionalProperties:false},annotations:{readOnlyHint:true}},
  {name:'scc_process_details',description:'Inspect a process using a validated numeric PID.',inputSchema:{type:'object',properties:{pid:{type:'integer',minimum:1,maximum:4294967295}},required:['pid'],additionalProperties:false},annotations:{readOnlyHint:true}},
  {name:'scc_read_project_file',description:'Read a small UTF-8 file under the configured SCC project root, never through symlinks.',inputSchema:{type:'object',properties:{relative_path:{type:'string',minLength:1,maxLength:260}},required:['relative_path'],additionalProperties:false},annotations:{readOnlyHint:true}},
  {name:'scc_runtime_status',description:'Observe dedicated Commander identity, uptime, root and read-only MCP capabilities.',inputSchema:{type:'object',properties:{},additionalProperties:false},annotations:{readOnlyHint:true}},
]);

function equalsSecret(actual, expected) {
  const a = Buffer.from(actual||'', 'utf8'), b = Buffer.from(expected, 'utf8');
  return a.length === b.length && crypto.timingSafeEqual(a,b);
}
function json(res, code, body) {
  const payload = JSON.stringify(body);
  res.writeHead(code, {'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});
  res.end(payload);
}
function isSafeRelative(raw) {
  return typeof raw==='string' && raw.length>0 && raw.length<=260 &&
    !path.isAbsolute(raw) && !path.win32.isAbsolute(raw) &&
    !raw.includes('\0') && !raw.includes(':') &&
    !raw.split(/[\\/]+/).some(p=>p==='..') && !/^[\\/]/.test(raw);
}
function readProjectFile(root, relative) {
  if(!isSafeRelative(relative))throw Error('project_path_denied');
  const parts=relative.split(/[\\/]+/).filter(Boolean);
  const allowed = new Set(['src','test','scripts','docs']);
  const extensions = new Set(['.py','.js','.cjs','.ts','.tsx','.md','.json','.yaml','.yml','.toml','.ps1','.html','.css','.svg','.txt']);
  if(!parts.length||!allowed.has(parts[0])||!extensions.has(path.extname(relative).toLowerCase()))
    throw Error('project_scope_denied');
  let current=root;
  for(const part of parts){
    current=path.join(current,part);
    const stat=fs.lstatSync(current);
    if(stat.isSymbolicLink())throw Error('symlink_denied');
  }
  const canonical=fs.realpathSync(current);
  if(!canonical.toLowerCase().startsWith(root.toLowerCase()+path.sep.toLowerCase()))throw Error('project_boundary_denied');
  const st=fs.statSync(canonical);
  if(!st.isFile()||st.size>MAX_FILE)throw Error('file_type_or_size_denied');
  return {relative_path:relative,bytes:st.size,content:fs.readFileSync(canonical,'utf8')};
}
function execObserved(command, args) {
  return new Promise((resolve,reject)=>{
    execFile(command,args,{windowsHide:true,timeout:6500,maxBuffer:MAX_OUTPUT,encoding:'utf8',shell:false},(err,stdout,stderr)=>{
      if(err)return reject(Error(err.killed?'observation_timeout':'observation_unavailable'));
      if(Buffer.byteLength(stdout)>MAX_OUTPUT)return reject(Error('observation_too_large'));
      try{resolve(JSON.parse(stdout.trim()||'[]'))}
      catch{reject(Error('observation_invalid'))}
    });
  });
}
async function useTool(name,args,root,startedAt) {
  if(!args||typeof args!=='object'||Array.isArray(args))throw Error('invalid_arguments');
  const empty=()=>{if(Object.keys(args).length)throw Error('unexpected_arguments')};
  const ps=(script)=>execObserved('powershell.exe',['-NoProfile','-NonInteractive','-Command',script]);
  switch(name){
  case 'scc_system_info':
    empty();return {hostname:os.hostname(),platform:os.platform(),release:os.release(),arch:os.arch(),uptime_seconds:Math.round(os.uptime()),memory_total:os.totalmem(),memory_free:os.freemem(),node:process.version};
  case 'scc_list_processes':
    empty();return {items:await ps('$ErrorActionPreference="Stop";@(Get-CimInstance Win32_Process | Select-Object -First 60 ProcessId,Name,ParentProcessId | ConvertTo-Json -Compress -Depth 3)')};
  case 'scc_list_services':
    empty();return {items:await ps('$ErrorActionPreference="Stop";@(Get-Service | Select-Object -First 60 Name,Status,DisplayName | ConvertTo-Json -Compress -Depth 3)')};
  case 'scc_list_listeners':
    empty();return {items:await ps('$ErrorActionPreference="Stop";@(Get-NetTCPConnection -State Listen | Select-Object -First 80 LocalAddress,LocalPort,OwningProcess | ConvertTo-Json -Compress -Depth 3)')};
  case 'scc_process_details':
    if(!Number.isSafeInteger(args.pid)||args.pid<1||args.pid>4294967295||Object.keys(args).length!==1)throw Error('invalid_pid');
    return {process:await ps('$ErrorActionPreference="Stop";Get-Process -Id '+args.pid+' | Select-Object Id,ProcessName,StartTime,CPU,WorkingSet64 | ConvertTo-Json -Compress -Depth 3')};
  case 'scc_read_project_file':
    if(Object.keys(args).length!==1)return Promise.reject(Error('invalid_arguments'));
    return readProjectFile(root,args.relative_path);
  case 'scc_runtime_status':
    empty();return {service:IDENTITY,ready:true,mcp_initialize:true,port:undefined,uptime_seconds:Math.round((Date.now()-startedAt)/1000),project_root:root,capabilities:READ_ONLY_TOOLS.map(t=>t.name),execution_authorized:false,nmbv_shared:false};
  default:throw Error('tool_not_found');
  }
}
function createServer({token,projectRoot,port=8767}={}) {
  if(typeof token!=='string'||token.length<32||/[\r\n]/.test(token))throw Error('strong_scc_token_required');
  if(!Number.isInteger(port)||port<0||port>65535)throw Error('invalid_port');
  const root=fs.realpathSync(projectRoot||path.resolve(__dirname,'../..'));
  const startedAt=Date.now();
  const server=http.createServer(async(req,res)=>{
    const requestURL=new URL(req.url||'/', 'http://127.0.0.1');
    if(req.socket.remoteAddress&&!['127.0.0.1','::1','::ffff:127.0.0.1'].includes(req.socket.remoteAddress)){
      return json(res,403,{error:'loopback_only'});
    }
    const expected='Bearer '+token;
    if(!equalsSecret(req.headers.authorization,expected))return json(res,401,{error:'authentication_required'});
    if(requestURL.search||requestURL.hash)return json(res,404,{error:'not_found'});
    if(req.method==='GET'&&requestURL.pathname==='/codemind/health'){
      const nonce=req.headers['x-codemind-challenge'];
      if(typeof nonce!=='string'||!/^[0-9a-f]{40}$/.test(nonce))return json(res,400,{error:'invalid_challenge'});
      const proof=crypto.createHmac('sha256',Buffer.from(token,'utf8')).update(nonce+':'+IDENTITY+':v1').digest('hex');
      return json(res,200,{service:IDENTITY,ready:true,mcp_initialize:true,nonce,proof});
    }
    if(req.method!=='POST'||requestURL.pathname!=='/mcp')return json(res,404,{error:'not_found'});
    let body='';
    try{
      for await(const chunk of req){
        body+=chunk.toString('utf8');
        if(Buffer.byteLength(body)>MAX_BODY)throw Error('request_too_large');
      }
      const data=JSON.parse(body);
      if(!data||typeof data!=='object'||Array.isArray(data)||data.jsonrpc!=='2.0')throw Error('invalid_jsonrpc');
      if(data.method==='notifications/initialized')return res.writeHead(202,{'Cache-Control':'no-store'}).end();
      if(!Object.prototype.hasOwnProperty.call(data,'id')||typeof data.method!=='string')throw Error('invalid_request');
      let result;
      switch(data.method){
      case 'initialize':
        result={protocolVersion:PROTOCOL,capabilities:{tools:{}},serverInfo:{name:IDENTITY,version:'0.1.0'}};break;
      case 'ping':result={};break;
      case 'tools/list':result={tools:READ_ONLY_TOOLS};break;
      case 'tools/call':
        if(typeof data.params?.name!=='string')throw Error('missing_tool_name');
        try{
          const observed=await useTool(data.params.name,data.params.arguments||{},root,startedAt);
          result={content:[{type:'text',text:JSON.stringify(observed)}],isError:false};
        }catch(error){
          result={content:[{type:'text',text:JSON.stringify({error:error.message})}],isError:true};
        }
        break;
      default:return json(res,200,{jsonrpc:'2.0',id:data.id,error:{code:-32601,message:'Method not found'}});
      }
      return json(res,200,{jsonrpc:'2.0',id:data.id,result});
    }catch(error){
      return json(res,error.message==='request_too_large'?413:400,{jsonrpc:'2.0',error:{code:-32600,message:'Invalid request'}});
    }
  });
  server.maxHeadersCount=30;
  server.requestTimeout=10000;
  server.headersTimeout=8000;
  return server;
}
if(require.main===module){
  const projectRoot=process.env.SCC_COMMANDER_PROJECT_ROOT;
  const token=process.env.SCC_COMMANDER_TOKEN;
  const port=Number(process.env.SCC_COMMANDER_PORT||8767);
  try{
    const server=createServer({token,projectRoot,port});
    server.listen(port,'127.0.0.1',()=>{
      process.stdout.write(JSON.stringify({service:IDENTITY,host:'127.0.0.1',port:server.address().port,health:'/codemind/health',mcp:'/mcp',tools:READ_ONLY_TOOLS.length})+'\n');
    });
  }catch(error){process.stderr.write('SCC Commander startup rejected: '+error.message+'\n');process.exitCode=1;}
}
module.exports={createServer,readProjectFile,READ_ONLY_TOOLS,IDENTITY};
