'use strict';
/** CODEMIND deterministic Codex hook bridge. No external packages, no process mutations. */
const fs=require('node:fs'), path=require('node:path'), os=require('node:os'), crypto=require('node:crypto');
const ROOT=path.resolve(__dirname,'..','..');
const STATE=process.env.CODEMIND_HOOK_STATE_DIR||path.join(process.env.LOCALAPPDATA||path.join(os.homedir(),'.local','share'),'CODEMIND-Serena','hooks');
const LEDGER=path.join(STATE,'evidence-v1.jsonl');
const ALLOWED=new Set(['SessionStart','UserPromptSubmit','PreToolUse','PostToolUse','PermissionRequest','Stop','SubagentStart','SubagentStop','PreCompact','PostCompact','SessionEnd']);
const STOPWORDS=new Set(['the','and','for','that','with','this','from','your','into','after','before']);
const sha=s=>crypto.createHash('sha256').update(s).digest('hex');
const bounded=(s,n=1050)=>String(s||'').slice(0,n);
const clean=s=>String(s||'').replace(/sk-(?:proj-|admin-)?[A-Za-z0-9_-]{8,}/gi,'[REDACTED]').replace(/Bearer\s+\S+/gi,'Bearer [REDACTED]').replace(/[\r\n]+/g,' ');
const sid=e=>sha(e.session_id||'').slice(0,14);
const context=(ev,msg)=>({hookSpecificOutput:{hookEventName:ev,additionalContext:bounded(clean(msg))}});
function history(){try{return fs.readFileSync(LEDGER,'utf8').split('\n').filter(Boolean).slice(-100).map(x=>{try{return JSON.parse(x)}catch{return null}}).filter(Boolean)}catch{return []}}
function record(x){
  try{fs.mkdirSync(STATE,{recursive:true});fs.appendFileSync(LEDGER,JSON.stringify(x)+'\n');
    if(fs.statSync(LEDGER).size>256000){let data=fs.readFileSync(LEDGER,'utf8').split('\n').filter(Boolean).slice(-600).join('\n')+'\n';
      let tmp=LEDGER+'.'+process.pid+'.tmp';fs.writeFileSync(tmp,data,{flag:'wx'});fs.renameSync(tmp,LEDGER)}
  }catch{/* Hook must not fail the session over telemetry storage. */}
}
function words(s){return new Set((String(s).toLowerCase().match(/[a-z][a-z0-9]*/g)||[]).filter(x=>!STOPWORDS.has(x)))}
function route(prompt){
  const dir=path.join(ROOT,'.codemind','skills'), matches=[];
  try{const a=words(prompt);
    for(const name of fs.readdirSync(dir).filter(n=>n.endsWith('.json')).slice(0,80)){
      const file=path.join(dir,name);if(fs.lstatSync(file).isSymbolicLink())continue;
      const m=JSON.parse(fs.readFileSync(file,'utf8'));
      if(!m||m.enabled!==true||typeof m.id!=='string'||typeof m.description!=='string')continue;
      const b=words(m.id.replace(/-/g,' ')+' '+m.description),score=[...a].filter(t=>b.has(t)).length;
      if(score>0)matches.push({id:m.id,score});
    }
  }catch{/* No activated manifest registry. */}
  // Same deterministic scoring and top-3 selection as CODEMIND SkillRouter.route.
  return matches.sort((a,b)=>b.score-a.score||a.id.localeCompare(b.id)).slice(0,3);
}
const signature=e=>sha(JSON.stringify([e.cwd||'',e.tool_name||'',e.tool_input||{}]));
function failedTimes(sig,entries){let n=0;for(const x of entries.slice().reverse()){if(x.signature!==sig)continue;if(x.status==='success')break;if(x.status==='error'||x.status==='timeout')n++}return n}
function failureInfo(r){
  if(!r)return null;
  const x=(typeof r==='object')?r:{};
  if(x.timedOut===true||x.timed_out===true)return 'timeout';
  if(typeof x.exitCode==='number'&&x.exitCode!==0||typeof x.exit_code==='number'&&x.exit_code!==0||x.isError===true||x.is_error===true||x.success===false||x.status==='error')return 'error';
  let raw=typeof r==='string'?r:typeof x.text==='string'?x.text:typeof x.stderr==='string'?x.stderr:'';
  if(!raw&&Array.isArray(x.content))raw=x.content.filter(v=>v&&typeof v.text==='string').slice(0,3).map(v=>v.text.slice(0,1400)).join(' ');
  if(raw.startsWith('{')&&raw.length<5000)try{let v=JSON.parse(raw);if(v.timedOut||v.timed_out)return 'timeout';if(v.exitCode!==undefined&&Number(v.exitCode)!==0||v.isError||v.is_error)return 'error'}catch{}
  if(/session terminated|timed out|timeout exceeded|\bprocess exited with code [1-9]\d*\b/i.test(raw.slice(0,3000)))return /timed out|timeout exceeded/i.test(raw.slice(0,3000))?'timeout':'error';
  return null;
}
function destructive(e){
  const s=(typeof e.tool_input==='object'?JSON.stringify(e.tool_input):String(e.tool_input||'')).slice(0,6000),t=String(e.tool_name||'').toLowerCase(),matches=[];
  if(/\b(rm\s+-rf|remove-item\b[^\n]{0,100}-recurse|del\s+\/s|format-volume|diskpart|git\s+reset\s+--hard|git\s+clean\s+-[a-z]*f|drop\s+database|drop\s+table|truncate\s+table)\b/i.test(s))matches.push('destructive filesystem/database operation');
  if(/\b(stop-process|taskkill|kill-process|restart-service|stop-service)\b/i.test(s)&&/commander|serena|python|node|codemind/i.test(s))matches.push('runtime process termination/restart');
  if(/force_delete|delete_symbol|drop_database|reset_database/i.test(t))matches.push('potentially destructive MCP tool');
  return matches;
}
function contradiction(message,records){
  if(!/\b(100%|fully completed|all tests pass(?:ed)?|zero defects|no remaining issues|production[- ]ready|fully fixed)\b/i.test(String(message||'').slice(0,2400)))return false;
  const state=new Map();for(const x of records.slice(-40)){if(x.signature&&['success','error','timeout'].includes(x.status))state.set(x.signature,x.status)}
  return [...state.values()].some(s=>s==='error'||s==='timeout');
}
function run(e){
 const ev=e.hook_event_name;if(!ALLOWED.has(ev))return {};
 const entries=history().filter(x=>x.session===sid(e));
 if(ev==='SessionStart'){
   record({event:ev,at:Date.now(),session:sid(e),source:e.source||'unknown'});
   return context(ev,'CODEMIND-100: bounded task triage and neurosymbolic invariants. Serena symbols/references/diagnostics first; use nmbv_skill_route and nmbv_next_action only if available and authorized. Windows Commander remains independent. Preserve dirty edits; never reset or kill unrelated processes. No timeout/skipped test is PASS. Two identical failures require a different strategy. Hooks cannot grant execution authority.');
 }
 if(ev==='UserPromptSubmit'){
   const selected=route(String(e.prompt||'').slice(0,12000));if(!selected.length)return {};
   return context(ev,'CODEMIND SkillRouter metadata match: '+selected.map(x=>x.id+'('+x.score+')').join(', ')+'. Advisory skill selection only; validate capabilities and authorization before invoking any worker.');
 }
 if(ev==='PreToolUse'){
   const count=failedTimes(signature(e),entries);
   if(count>=2)return {hookSpecificOutput:{hookEventName:ev,permissionDecision:'deny',permissionDecisionReason:'CODEMIND anti-loop: same tool input failed twice; inspect evidence and change strategy before retrying.'}};
   const risk=destructive(e);return risk.length?context(ev,'CODEMIND ADVISORY: '+risk.join('; ')+'. Verify target ownership, explicit authorization, exact scope, rollback and live process identity; preserve Commander/Serena.'): {};
 }
 if(ev==='PermissionRequest'){
   const risk=destructive(e);return risk.length?{systemMessage:'CODEMIND approval review: '+risk.join('; ')+'; require an authorized owner and bounded target.'}:{};
 }
 if(ev==='PostToolUse'){
   const sig=signature(e),f=failureInfo(e.tool_response),r=e.tool_response;
   const success=r&&typeof r==='object'&&(r.exitCode===0||r.exit_code===0||r.isError===false||r.is_error===false||r.success===true||r.status==='success');
   record({at:Date.now(),event:ev,session:sid(e),signature:sig,status:f||(success?'success':'unknown'),tool:sha(e.tool_name||'').slice(0,10)});
   if(!f)return {};
   const count=failedTimes(sig,history().filter(x=>x.session===sid(e)));
   return context(ev,'CODEMIND observed '+f+'; not PASS. Identical consecutive failures: '+count+'. '+(count>=2?'STRATEGY_CHANGE_REQUIRED: stop repeating and inspect root cause.':'Inspect current error evidence before retry.'));
 }
 if(ev==='Stop'||ev==='SubagentStop'){
   return contradiction(e.last_assistant_message,entries)&&!e.stop_hook_active?{decision:'block',reason:'CODEMIND evidence gate: recent failed/timed-out tool contradicts unconditional completion claim. Correct claim or obtain new passing proof; only one continuation.'}:{};
 }
 if(ev==='SubagentStart')return context(ev,'Subagent: preserve assigned scope and evidence; timeout != PASS, no foreign dirty-file edits, no process restarts.');
 if(ev==='PreCompact'||ev==='PostCompact'||ev==='SessionEnd'){record({at:Date.now(),event:ev,session:sid(e),trigger:e.trigger||e.reason||''});return {}}
 return {};
}
if(require.main===module){
 let length=0,chunks=[];
 process.stdin.on('data',b=>{length+=b.length;if(length>262144){process.stdin.destroy();process.stdout.write('{}\n');return}chunks.push(b)});
 process.stdin.on('end',()=>{try{process.stdout.write(JSON.stringify(run(JSON.parse(Buffer.concat(chunks).toString('utf8')||'{}')))+'\n')}catch{process.stdout.write('{}\n')}});
}
module.exports={run,route,signature,failureInfo,destructive,failedTimes,contradiction};
