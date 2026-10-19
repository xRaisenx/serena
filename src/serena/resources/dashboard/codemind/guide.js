/* CODEMIND guide search: read-only, deterministic, no network or stored prompts. */
'use strict';
function matchingIndices(items,query){
  const clean = value=>String(value||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();
  const terms=clean(query).split(/\s+/).filter(Boolean);
  return items.flatMap((item,index)=>terms.every(term=>clean(item).includes(term))?[index]:[]);
}
if(typeof document!=='undefined'){
  const search=document.getElementById('guide-search');
  const status=document.getElementById('guide-results');
  if(search&&status){
    const items=Array.from(document.querySelectorAll('[data-guide-item]'));
    const labels=items.map(item=>item.textContent);
    const refresh=()=>{
      const matches=new Set(matchingIndices(labels,search.value));
      items.forEach((item,index)=>{item.hidden=!matches.has(index);});
      status.textContent=matches.size===items.length?'Showing all '+items.length+' scenarios and FAQs.':
        'Showing '+matches.size+' of '+items.length+' scenarios and FAQs.';
    };
    search.addEventListener('input',refresh);
    refresh();
  }
}
if(typeof module!=='undefined'&&module.exports)module.exports={matchingIndices};