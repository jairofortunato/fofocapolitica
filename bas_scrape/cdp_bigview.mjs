const TARGET=process.argv[2], NAV=process.argv[3], OUT=process.argv[4];
import {writeFileSync} from 'fs';
const ws=new WebSocket(TARGET); let id=0; const pend=new Map();
const send=(m,p={})=>{const _id=++id;ws.send(JSON.stringify({id:_id,method:m,params:p}));return new Promise(r=>pend.set(_id,r));};
const reqs=new Map(); const bodies=[]; let TOTAL=null;
ws.onmessage=async e=>{const m=JSON.parse(e.data);
  if(m.id&&pend.has(m.id)){pend.get(m.id)(m.result);pend.delete(m.id);return;}
  const {method,params}=m;
  if(method==='Network.requestWillBeSent'&&params.request.url.includes('atende.php')){
    const qs=new URL(params.request.url).searchParams; reqs.set(params.requestId,qs.get('processo')+'|'+qs.get('rot'));}
  if(method==='Network.loadingFinished'){const r=reqs.get(params.requestId); if(r&&r.startsWith('processaDados')&&!r.endsWith('|1')){
    try{const resp=await send('Network.getResponseBody',{requestId:params.requestId}); const b=JSON.parse(resp.body); if(b&&b.dados){bodies.push(b.dados); if(b.total)TOTAL=b.total;}}catch(e){}}}
};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
ws.onopen=async()=>{
  await send('Network.enable'); await send('Page.enable'); await send('Runtime.enable');
  await send('Emulation.setDeviceMetricsOverride',{width:1400,height:50000,deviceScaleFactor:1,mobile:false});
  await send('Page.navigate',{url:NAV});
  await sleep(9000);
  const seen=new Set(),rows=[];
  const collect=()=>{for(const arr of bodies)for(const it of arr){const v=it.valor||it;const k=JSON.stringify(v);if(!seen.has(k)){seen.add(k);rows.push(v);}}};
  collect();
  for(let i=0;i<60;i++){const before=rows.length;
    await send('Runtime.evaluate',{expression:`(()=>{document.querySelectorAll('*').forEach(el=>{if(el.scrollHeight>el.clientHeight+50)el.scrollTop=el.scrollHeight});window.scrollTo(0,document.body.scrollHeight);})()`});
    await sleep(900); collect();
    if(TOTAL&&rows.length>=Number(TOTAL))break;
    if(rows.length===before&&i>5)break;
  }
  writeFileSync(OUT,JSON.stringify({total:TOTAL,collected:rows.length,rows}));
  console.log('TOTAL',TOTAL,'collected',rows.length);
  ws.close();process.exit(0);
};
ws.onerror=e=>{console.error(e.message);process.exit(1);};
