const TARGET=process.argv[2], NAV=process.argv[3], EXPR=process.argv[4], WAIT=parseInt(process.argv[5]||'9000');
const ws=new WebSocket(TARGET); let id=0; const pend=new Map();
const send=(m,p={})=>{const _id=++id;ws.send(JSON.stringify({id:_id,method:m,params:p}));return new Promise(r=>pend.set(_id,r));};
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&pend.has(m.id)){pend.get(m.id)(m.result);pend.delete(m.id);}};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
ws.onopen=async()=>{
  await send('Page.enable'); await send('Runtime.enable');
  if(NAV!=='-'){await send('Page.navigate',{url:NAV}); await sleep(WAIT);}
  const r=await send('Runtime.evaluate',{expression:EXPR,returnByValue:true});
  console.log(JSON.stringify(r.result.value,null,1));
  ws.close(); process.exit(0);
};
ws.onerror=e=>{console.error(e.message);process.exit(1);};
