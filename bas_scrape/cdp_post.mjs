const TARGET=process.argv[2], NAV=process.argv[3], WAIT=parseInt(process.argv[4]||'15000');
import {writeFileSync} from 'fs';
const ws=new WebSocket(TARGET); let id=0; const pend=new Map();
const send=(m,p={})=>{const _id=++id;ws.send(JSON.stringify({id:_id,method:m,params:p}));return new Promise(r=>pend.set(_id,r));};
const reqs=new Map(); const found=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);
  if(m.id&&pend.has(m.id)){pend.get(m.id)(m.result);pend.delete(m.id);return;}
  const {method,params}=m;
  if(method==='Network.requestWillBeSent'&&params.request.url.includes('atende.php')){
    const qs=new URL(params.request.url).searchParams;
    if(qs.get('processo')==='processaDados'){found.push({rot:qs.get('rot'),aca:qs.get('aca'),post:params.request.postData});}
  }
};
ws.onopen=async()=>{
  await send('Network.enable'); await send('Page.enable');
  await send('Page.navigate',{url:NAV});
  await new Promise(r=>setTimeout(r,WAIT));
  writeFileSync('post45089.json',JSON.stringify(found));
  console.log('processaDados requests:',found.length,'rots:',found.map(f=>f.rot));
  ws.close(); process.exit(0);
};
ws.onerror=e=>{console.error(e.message);process.exit(1);};
