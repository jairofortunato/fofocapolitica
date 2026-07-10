const TARGET=process.argv[2], NAV=process.argv[3], WAIT=parseInt(process.argv[4]||'10000');
const ws=new WebSocket(TARGET); let id=0; const pend=new Map();
const send=(m,p={})=>{const _id=++id;ws.send(JSON.stringify({id:_id,method:m,params:p}));return new Promise(r=>pend.set(_id,r));};
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&pend.has(m.id)){pend.get(m.id)(m.result);pend.delete(m.id);}};
ws.onopen=async()=>{
  await send('Page.enable');
  await send('Page.navigate',{url:NAV});
  await new Promise(r=>setTimeout(r,WAIT));
  const js=`(()=>{const out=[];document.querySelectorAll('a[href],[data-url],[onclick]').forEach(el=>{const h=el.getAttribute('href')||el.getAttribute('data-url')||'';const t=(el.textContent||'').trim().replace(/\\s+/g,' ').slice(0,50);if((h&&h.length>1)||/transpar|despesa|receita|pessoal|contrato|licita/i.test(t)){out.push((t||'?')+' :: '+h);}});return Array.from(new Set(out)).join('\\n');})()`;
  const r=await send('Runtime.evaluate',{expression:js,returnByValue:true});
  console.log(r.result.value||'(empty)');
  ws.close();process.exit(0);
};
ws.onerror=e=>{console.error(e.message);process.exit(1);};
