const TARGET=process.argv[2], NAV=process.argv[3], OUT=process.argv[4]||'rows.json';
import {writeFileSync} from 'fs';
const ws=new WebSocket(TARGET); let id=0; const pend=new Map();
const send=(m,p={})=>{const _id=++id;ws.send(JSON.stringify({id:_id,method:m,params:p}));return new Promise(r=>pend.set(_id,r));};
const reqs=new Map(); const dataBodies=[]; let TOTAL=null;
ws.onmessage=async e=>{const m=JSON.parse(e.data);
  if(m.id&&pend.has(m.id)){pend.get(m.id)(m.result);pend.delete(m.id);return;}
  const {method,params}=m;
  if(method==='Network.requestWillBeSent'&&params.request.url.includes('atende.php')){
    const qs=new URL(params.request.url).searchParams;
    reqs.set(params.requestId,{processo:qs.get('processo'),rot:qs.get('rot')});
  }
  if(method==='Network.loadingFinished'){const r=reqs.get(params.requestId); if(r&&r.processo==='processaDados'&&r.rot!=='1'){
    try{const resp=await send('Network.getResponseBody',{requestId:params.requestId});
      const b=JSON.parse(resp.body); if(b&&b.dados){dataBodies.push(b.dados); if(b.total)TOTAL=b.total;}
    }catch(e){}
  }}
};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
ws.onopen=async()=>{
  await send('Network.enable'); await send('Page.enable'); await send('Runtime.enable');
  await send('Page.navigate',{url:NAV});
  await sleep(8000);
  const seen=new Set(); const rows=[];
  const collect=()=>{for(const arr of dataBodies){for(const it of arr){const v=it.valor||it; const k=JSON.stringify(v); if(!seen.has(k)){seen.add(k);rows.push(v);}}}};
  collect();
  let stale=0;
  for(let i=0;i<200;i++){
    const before=rows.length;
    // scroll the scrollable result container(s) and window to bottom
    await send('Runtime.evaluate',{expression:`
      (()=>{let n=0;document.querySelectorAll('*').forEach(el=>{if(el.scrollHeight>el.clientHeight+50){el.scrollTop=el.scrollHeight;n++;}});window.scrollTo(0,document.body.scrollHeight);return n;})()`});
    await sleep(700);
    collect();
    if(rows.length===before){stale++;} else {stale=0;}
    if(TOTAL&&rows.length>=Number(TOTAL)) break;
    if(stale>=12) break;
  }
  collect();
  writeFileSync(OUT,JSON.stringify({total:TOTAL,collected:rows.length,rows}));
  console.log('TOTAL',TOTAL,'collected',rows.length);
  ws.close(); process.exit(0);
};
ws.onerror=e=>{console.error(e.message);process.exit(1);};
