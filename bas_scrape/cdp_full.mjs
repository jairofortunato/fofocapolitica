const TARGET=process.argv[2], NAV=process.argv[3], WAIT=parseInt(process.argv[4]||'15000'), OUT=process.argv[5]||'full.json';
import {writeFileSync} from 'fs';
const ws=new WebSocket(TARGET); let id=0; const pend=new Map();
const send=(m,p={})=>{const _id=++id;ws.send(JSON.stringify({id:_id,method:m,params:p}));return new Promise(r=>pend.set(_id,r));};
const reqs=new Map(); const done=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);
  if(m.id&&pend.has(m.id)){pend.get(m.id)(m.result);pend.delete(m.id);return;}
  const {method,params}=m;
  if(method==='Network.requestWillBeSent'&&params.request.url.includes('atende.php')){
    const qs=new URL(params.request.url).searchParams;
    reqs.set(params.requestId,{rot:qs.get('rot'),aca:qs.get('aca'),processo:qs.get('processo')});
  }
  if(method==='Network.loadingFinished'){const r=reqs.get(params.requestId); if(r&&r.processo==='processaDados') done.push(params.requestId);}
};
ws.onopen=async()=>{
  await send('Network.enable'); await send('Page.enable');
  await send('Page.navigate',{url:NAV});
  await new Promise(r=>setTimeout(r,WAIT));
  const out=[];
  for(const id of done){const r=reqs.get(id); try{const resp=await send('Network.getResponseBody',{requestId:id}); out.push({rot:r.rot,aca:r.aca,body:resp.body});}catch(e){}}
  writeFileSync(OUT,JSON.stringify(out));
  console.log('captured processaDados bodies:',out.length);
  ws.close(); process.exit(0);
};
ws.onerror=e=>{console.error(e.message);process.exit(1);};
