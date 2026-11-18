(() => {
  let n = 0; const id = () => 'id' + (++n);
  const user = { id: window.__asUser || 'u1' };
  const now = () => new Date().toISOString();
  const sd = [['design','Дизайн','work',10],['approval','Одобрение от клиента','wait',20],['cutfile','Файл за рязане','work',30],['cut','Изрязване','work',40],['print_pages','Печат на страници','work',50],['print_covers','Печат на корици','work',60],['print','Печат','work',70],['press','Щамповане','work',80],['assemble','Сглобяване','work',90]].map(a => ({ key: a[0], name: a[1], kind: a[2], sort: a[3] }));
  const types = [['Oversize Slash',1,'XS,S,M,L,XL,2XL'],['Oversize Meivi',1,'XS,S,M,L,XL,2XL'],['Мъжка Meivi',1,'S,M,L,XL,2XL,3XL'],['Дамска Meivi',1,'S,M,L,XL,2XL,3XL'],['Худи',1,'XS,S,M,L,XL,2XL,3XL'],['Специална книга',0,''],['Мини албум',0,''],['Украшение за автомобил',0,''],['3D картина',0,''],['Цифри',0,'']]
    .map((a, i) => ({ id: 't' + i, name: a[0], is_tshirt: !!a[1], grp: a[1] && a[0] !== 'Худи' ? 'Тениски' : '', sizes: a[2] ? a[2].split(',') : [], colors: a[0] === 'Худи' ? ['Черно', 'Бяло'] : a[1] ? ['Черна', 'Бяла'] : [], sort: i }));
  const ts = [];
  const add = (t, list) => list.forEach((s, i) => ts.push({ product_type_id: t, stage_key: s.replace('?', ''), sort: i, optional: s.endsWith('?') }));
  ['t0','t1','t2','t3','t4'].forEach(t => add(t, ['design?', 'approval?', 'print', 'press']));
  add('t5', ['design','approval','print_pages','print_covers','assemble']); add('t6', ['design','assemble']); add('t7', ['design','print']);
  add('t8', ['design','approval','cutfile','cut','print']); add('t9', ['design','cutfile','cut','print']);
  const db = { stock_moves: [], leave_allowances: [], leaves: [], holidays: [{ day: '2026-12-24', name: 'Бъдни вечер' }, { day: '2026-12-25', name: 'Коледа' }, { day: '2026-12-28', name: 'Коледа (почивен ден вместо 26 декември)' }, { day: '2027-01-01', name: 'Нова година' }], app_settings: [{ key: 'workweek', value: '5' }], tasks: [], order_notes: [], members: [{ user_id: 'u1', name: 'Мартин', is_admin: true }, { user_id: 'u2', name: 'Гошо', is_admin: false }], options: [], orders: [], items: [], item_stages: [], product_types: types };
  [['brand','Slash'],['brand','Meivi'],['channel','TikTok'],['channel','Instagram'],['channel','Messenger'],['channel','Viber'],['channel','Сайт'],['channel','Телефон'],['account','Meivi'],['account','Auto'],['account','Inlove'],['account','Zodiac']].forEach((o, i) => db.options.push({ id: id(), kind: o[0], value: o[1], sort: i }));
  let logged = false, num = 0, rt = null;
  const calls = { load: 0, syncSince: 0, loadOrders: 0, loadConfig: 0, loadAll: 0, bytes: 0 };
  const sent = v => { calls.bytes += JSON.stringify(v).length; return v; };
  const num0 = v => v === '' || v == null ? null : Number(v);
  const syncPrice = oid => { const l = db.items.filter(i => i.order_id === oid && i.price != null); if (l.length) db.orders.find(o => o.id === oid).price = l.reduce((a, i) => a + i.price * i.qty, 0); };
  let mv = 0;
  const levels = () => { const m = new Map(); db.stock_moves.forEach(x => { const k = x.product_type_id + '|' + x.size + '|' + x.color; const r = m.get(k) || { product_type_id: x.product_type_id, size: x.size, color: x.color, qty: 0, loaded: false }; r.qty += x.delta; r.loaded = r.loaded || x.kind === 'load'; m.set(k, r); }); return [...m.values()]; };
  const full = o => ({ ...o, items: db.items.filter(i => i.order_id === o.id).map(i => ({ ...i, item_stages: db.item_stages.filter(s => s.item_id === i.id) })) });
  // same rules as the database triggers: any change inside an order marks the order as changed
  const touch = (orderId, silent) => { const o = db.orders.find(x => x.id === orderId); if (!o) return; o.updated_at = now(); if (!silent && rt) setTimeout(() => rt.orders({ eventType: 'UPDATE', new: { ...o } }), 30); };
  const orderOf = (t, row) => t === 'orders' ? row.id : t === 'items' ? row.order_id : t === 'item_stages' ? (db.items.find(i => i.id === row.item_id) || {}).order_id : t === 'order_notes' ? row.order_id : null;
  window.__db = db; window.__calls = calls;
  window.__silent = false;                       // true = changes happen but no live event arrives (dropped connection)
  window.__remote = fn => { const before = window.__silent; fn(db, { touch, now, id }); window.__silent = before; };
  window.__mockApi = {
    async session() { return logged ? user : null; },
    async signIn(e, p) { if (p !== 'pass123') throw new Error('Invalid login credentials'); logged = true; return user; },
    async signUp(e, p, name, code) { window.__signup = { e, p, name, code }; if (code.replace(/\D/g,'') !== '249708' || !name) throw new Error('Database error saving new user'); logged = true; return user; },
    async signOut() { logged = false; },
    async load() {
      calls.load++;
      const c = JSON.parse(JSON.stringify(db));
      return sent({ stock: levels(), designs: [{ id: 'd1', brand: 'Slash', name: 'Gojo Satoru „Infinity“', category: 'Jujutsu Kaizen', active: true, kind: 'single', product_type_id: 't0' }, { id: 'd2', brand: 'Slash', name: 'Sasuke', category: 'Naruto', active: true, kind: 'single', product_type_id: 't0' }, { id: 'd3', brand: 'Slash', name: 'Един отбор', category: 'Любов', active: true, kind: 'set', product_type_id: 't0' }], members: c.members, options: c.options, stageDefs: sd, types: c.product_types, typeStages: ts,
        tasks: c.tasks, notes: c.order_notes,
        history: db.orders.map(o => ({ ...o, items: db.items.filter(i => i.order_id === o.id).map(i => ({ name: i.name, qty: i.qty, is_tshirt: i.is_tshirt, price: i.price })) })),
        orders: JSON.parse(JSON.stringify(db.orders.map(full))) });
    },
    async syncSince(iso) {
      calls.syncSince++;
      return sent(JSON.parse(JSON.stringify({ orders: db.orders.filter(o => o.updated_at >= iso).map(full), tasks: db.tasks.filter(t => t.updated_at >= iso), notes: db.order_notes.filter(x => x.created_at >= iso) })));
    },
    async loadOrders(ids) { calls.loadOrders++; return sent(JSON.parse(JSON.stringify(db.orders.filter(o => ids.includes(o.id)).map(full)))); },
    async loadConfig() { calls.loadConfig++; return sent(JSON.parse(JSON.stringify({ members: db.members, options: db.options, stageDefs: sd, types: db.product_types, typeStages: ts }))); },
    async workStats(from, to) {
      if (!db.members.find(x => x.user_id === user.id).is_admin) throw new Error('not allowed');
      const inR = d => d && (!from || d >= from) && (!to || d < to), out = new Map();
      const addRow = (u, kind, label, qty) => { const k = u + '|' + kind + '|' + label; const r = out.get(k) || { user_id: u, kind, label, n: 0, qty: 0 }; r.n++; r.qty += qty; out.set(k, r); };
      db.item_stages.forEach(s => { if (s.done_by && s.kind === 'work' && inR(s.done_at)) addRow(s.done_by, 'stage', s.name, (db.items.find(i => i.id === s.item_id) || {}).qty || 1); });
      db.orders.forEach(o => { if (o.packed_by && inR(o.packed_at)) addRow(o.packed_by, 'pack', 'Опаковани', 1); if (o.waybill_by && inR(o.waybill_at)) addRow(o.waybill_by, 'waybill', 'Товарителници', 1); if (o.confirmed_by && inR(o.confirmed_at)) addRow(o.confirmed_by, 'confirm', 'Потвърждения', 1); if (o.created_by && inR(o.created_at)) addRow(o.created_by, 'created', 'Въведени поръчки', 1); });
      db.tasks.forEach(x => { if (x.done_by && inR(x.done_at)) addRow(x.done_by, 'task', 'Изпълнени задачи', 1); });
      calls.bytes += JSON.stringify([...out.values()]).length;
      return [...out.values()];
    },
    async loadStock() { return levels(); },
    async stockMoves() { return db.stock_moves.filter(m => m.kind === 'load' || m.kind === 'scrap').slice().reverse().slice(0, 15).map(m => ({ ...m })); },
    async addStock(rows) { rows.forEach(r => db.stock_moves.push({ id: ++mv, created_at: now(), ...r })); if (rt && rt.stock && !window.__silent) setTimeout(() => rt.stock({}), 30); },
    async removeStockMove(i) { db.stock_moves = db.stock_moves.filter(m => m.id !== i); if (rt && rt.stock && !window.__silent) setTimeout(() => rt.stock({}), 30); },
    async loadLeave() { return JSON.parse(JSON.stringify({ allowances: db.leave_allowances, leaves: db.leaves, holidays: db.holidays.slice().sort((a, b) => a.day < b.day ? -1 : 1), settings: db.app_settings })); },
    async upsert(t, row) { const key = t === 'leave_allowances' ? r => r.user_id === row.user_id && r.year === row.year : t === 'holidays' ? r => r.day === row.day : r => r.key === row.key; const i = db[t].findIndex(key); if (i >= 0) db[t][i] = { ...db[t][i], ...row }; else db[t].push({ ...row }); },
    async removeBy(t, col, val) { db[t] = db[t].filter(r => r[col] !== val); },
    async loadAll() { calls.loadAll++; return sent(JSON.parse(JSON.stringify(db.orders.map(full)))); },
    async saveItem(p) {
      let iid = p.id;
      if (!iid) { iid = id(); db.items.push({ id: iid, order_id: p.order_id, product_type_id: p.product_type_id || null, name: p.name, is_tshirt: p.is_tshirt, size: p.size, color: p.color, qty: p.qty, custom_design: p.custom_design, note: p.note, price: num0(p.price), design: p.design || '', photo_at: null, sort: db.items.filter(i => i.order_id === p.order_id).length }); }
      else { Object.assign(db.items.find(i => i.id === iid), { product_type_id: p.product_type_id || null, name: p.name, is_tshirt: p.is_tshirt, size: p.size, color: p.color, qty: p.qty, custom_design: p.custom_design, note: p.note, price: num0(p.price), design: p.design || '' }); if (p.reset_stages) db.item_stages = db.item_stages.filter(s => s.item_id !== iid); }
      if (!p.id || p.reset_stages) p.stages.forEach((s, j) => db.item_stages.push({ id: id(), item_id: iid, stage_key: s.key, name: s.name, kind: s.kind, sort: j, done_at: null, done_by: null }));
      syncPrice(p.order_id);
      touch(p.order_id, window.__silent);
      return iid;
    },
    async createOrder(p) {
      const o = { id: id(), num: ++num, customer: p.customer, phone: p.phone, recipient: p.recipient || '', address: p.address, price: p.price === '' || p.price == null ? null : Number(p.price), brand: p.brand, channel: p.channel, account: p.account, note: p.note, problem: '', urgent: p.urgent, due: p.due || null, needs_confirm: p.needs_confirm, confirmed_at: null, packed_at: null, waybill_at: null, tracking: '', created_by: user.id, created_at: now(), updated_at: now() };
      db.orders.push(o);
      p.items.forEach((it, i) => { const iid = id(); db.items.push({ id: iid, order_id: o.id, product_type_id: it.product_type_id || null, name: it.name, is_tshirt: it.is_tshirt, size: it.size, color: it.color, qty: it.qty, custom_design: it.custom_design, note: it.note, price: num0(it.price), design: it.design || '', photo_at: null, sort: i });
        it.stages.forEach((s, j) => db.item_stages.push({ id: id(), item_id: iid, stage_key: s.key, name: s.name, kind: s.kind, sort: j, done_at: null, done_by: null })); });
      syncPrice(o.id);
      if (rt && !window.__silent) setTimeout(() => rt.orders({ eventType: 'INSERT', new: { ...o } }), 30);
      return o.id;
    },
    async update(t, i, patch) {
      const row = db[t].find(r => r.id === i); const wasDone = row && row.done_at; Object.assign(row, patch);
      if (t === 'item_stages' && row.stage_key === 'press' && !!wasDone !== !!row.done_at) { const it = db.items.find(x => x.id === row.item_id);
        if (it && it.is_tshirt && it.product_type_id && it.size && it.color) {
          const taken = -db.stock_moves.filter(m => m.item_id === it.id && m.kind === 'press').reduce((x, m) => x + m.delta, 0);
          const loaded = db.stock_moves.some(m => m.product_type_id === it.product_type_id && m.kind === 'load');
          const delta = row.done_at ? (loaded ? -it.qty : 0) : taken;
          if (delta) db.stock_moves.push({ id: ++mv, product_type_id: it.product_type_id, size: it.size, color: it.color, delta, kind: 'press', item_id: it.id, created_at: now() }); } }
      if (t === 'tasks') { row.updated_at = now(); if (rt && !window.__silent) setTimeout(() => rt.tasks({ eventType: 'UPDATE', new: { ...row } }), 30); }
      const oid = orderOf(t, row); if (oid) touch(oid, window.__silent);
      if (['options', 'product_types'].includes(t) && rt && !window.__silent) setTimeout(() => rt.config({}), 30);
    },
    async insert(t, row) {
      const r = { id: id(), created_at: now(), ...row };
      if (t === 'tasks') { r.created_by = r.created_by || user.id; r.done_at = null; r.done_by = null; r.updated_at = now(); }
      if (t === 'order_notes') r.author = user.id;
      if (t === 'leaves') { r.status = r.status || 'approved'; }
      db[t].push(r);
      if (rt && !window.__silent) {
        if (t === 'tasks') setTimeout(() => rt.tasks({ eventType: 'INSERT', new: { ...r } }), 30);
        if (t === 'order_notes') setTimeout(() => rt.notes({ eventType: 'INSERT', new: { ...r } }), 30);
        if (t === 'options') setTimeout(() => rt.config({}), 30);
      }
      const oid = orderOf(t, r); if (oid) touch(oid, window.__silent);
    },
    async remove(t, i) {
      const row = db[t].find(r => r.id === i); if (!row) return;
      const oid = t === 'orders' ? null : orderOf(t, row);
      db[t] = db[t].filter(r => r.id !== i);
      if (t === 'orders') { const its = db.items.filter(x => x.order_id === i).map(x => x.id); db.items = db.items.filter(x => x.order_id !== i); db.item_stages = db.item_stages.filter(s => !its.includes(s.item_id)); db.order_notes = db.order_notes.filter(x => x.order_id !== i); }
      if (t === 'items') db.item_stages = db.item_stages.filter(s => s.item_id !== i);
      if (rt && !window.__silent) {
        if (t === 'orders') setTimeout(() => rt.orders({ eventType: 'DELETE', old: { id: i } }), 30);
        if (t === 'tasks') setTimeout(() => rt.tasks({ eventType: 'DELETE', old: { id: i } }), 30);
        if (t === 'options') setTimeout(() => rt.config({}), 30);
      }
      if (oid) touch(oid, window.__silent);
    },
    subscribe(h) { rt = h; window.__rt = h; setTimeout(() => h.status('SUBSCRIBED'), 10); }
  };
})();
