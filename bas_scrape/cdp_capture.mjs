// Drive headless Chrome via CDP: load the transparency portal, capture every
// atende.php RPC (rot/aca/processo + POST body + response). Then dump the menu.
const TARGET = process.argv[2]; // ws url
const NAV = process.argv[3] || 'https://balnearioarroiodosilva.atende.net/transparencia';
const WAIT = parseInt(process.argv[4] || '12000', 10);

const ws = new WebSocket(TARGET);
let id = 0;
const pending = new Map();
const send = (method, params = {}) => {
  const _id = ++id;
  ws.send(JSON.stringify({ id: _id, method, params }));
  return new Promise((res) => pending.set(_id, res));
};

const reqs = new Map();   // requestId -> {url, postData, rot, aca, processo}
const captured = [];

ws.onmessage = (ev) => {
  const msg = JSON.parse(ev.data);
  if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg.result); pending.delete(msg.id); return; }
  const { method, params } = msg;
  if (method === 'Network.requestWillBeSent') {
    const u = params.request.url;
    if (u.includes('atende.php')) {
      const qs = new URL(u).searchParams;
      reqs.set(params.requestId, {
        url: u, rot: qs.get('rot'), aca: qs.get('aca'), processo: qs.get('processo'),
        postData: params.request.postData || null,
      });
    }
  }
  if (method === 'Network.loadingFinished') {
    const r = reqs.get(params.requestId);
    if (r) captured.push(params.requestId);
  }
};

ws.onopen = async () => {
  await send('Network.enable');
  await send('Page.enable');
  await send('Page.navigate', { url: NAV });
  await new Promise((r) => setTimeout(r, WAIT));
  // pull response bodies for atende.php calls
  const out = [];
  for (const reqId of captured) {
    const r = reqs.get(reqId);
    let body = '';
    try {
      const resp = await send('Network.getResponseBody', { requestId: reqId });
      body = resp && resp.body ? resp.body.slice(0, 4000) : '';
    } catch (e) {}
    out.push({ rot: r.rot, aca: r.aca, processo: r.processo, postData: r.postData, bodyPreview: body });
  }
  console.log(JSON.stringify(out, null, 1));
  ws.close();
  process.exit(0);
};
ws.onerror = (e) => { console.error('WS error', e.message || e); process.exit(1); };
