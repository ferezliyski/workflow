import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SHOTS = os.path.join(ROOT, 'build', 'shots') + '/'
os.makedirs(SHOTS, exist_ok=True)
from playwright.sync_api import sync_playwright
out=SHOTS
SEED = r"""window.addEventListener('DOMContentLoaded', () => {
  const db = window.__db, old = new Date(Date.now() - 200 * 864e5).toISOString();
  for (let i = 0; i < 3000; i++) {
    const active = i >= 2950, oid = 'o' + i, iid = 'it' + i;
    db.orders.push({ id: oid, num: 1000 + i, customer: 'Клиент ' + i, phone: '08' + String(10000000 + i), address: 'София, ул. Тестова ' + i, price: 30 + i % 20, brand: i % 3 ? 'Meivi' : 'Slash', channel: 'TikTok', account: 'Auto', note: '', problem: '', urgent: false, due: null, needs_confirm: false, confirmed_at: null, packed_at: null, waybill_at: active ? null : old, tracking: active ? '' : '10' + i, created_by: 'u1', created_at: old, updated_at: old });
    db.items.push({ id: iid, order_id: oid, product_type_id: 't1', name: 'Oversize Meivi', is_tshirt: true, size: 'L', color: 'Черна', qty: 1, custom_design: false, note: '', photo_at: null, sort: 0 });
    db.item_stages.push({ id: 'sp' + i, item_id: iid, stage_key: 'print', name: 'Печат', kind: 'work', sort: 0, done_at: active ? null : old, done_by: null });
    db.item_stages.push({ id: 'ss' + i, item_id: iid, stage_key: 'press', name: 'Щамповане', kind: 'work', sort: 1, done_at: active ? null : old, done_by: null });
  }
});"""
with sync_playwright() as p:
    b = p.chromium.launch(args=['--no-sandbox'])
    page = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True).new_page()
    errs=[]; page.on('pageerror', lambda e: errs.append(str(e))); page.on('console', lambda m: errs.append(m.text) if m.type=='error' else None)
    page.add_init_script(path=os.path.join(ROOT, 'build', 'mock.js')); page.add_init_script(SEED)
    page.goto('file://' + os.path.join(ROOT, 'index.html')); page.wait_for_timeout(300)
    page.fill('#a-email', 'a@b.bg'); page.fill('#a-pass', 'pass123'); page.click('#auth-form button[type=submit]'); page.wait_for_timeout(800)
    calls = lambda: page.evaluate('({...window.__calls})')
    c0 = calls(); full_bytes = c0['bytes']
    print('open: full loads', c0['load'], '| bytes', full_bytes, '| active shown', page.inner_text('.top span'))
    stage = lambda name, oid: page.evaluate(f"[...__db.item_stages].find(s => s.id === '{('sp' if name=='print' else 'ss')}{oid}').id")
    card = lambda n: page.locator('.card').filter(has_text=f'Клиент {n}').first
    def nowtxt(n): return card(n).locator('.now-txt').inner_text().replace('\n', ' ')
    # 1) another phone marks a stage -> arrives live, only that order is fetched
    before = calls()
    page.evaluate("__mockApi.update('item_stages', 'sp2999', { done_at: new Date().toISOString(), done_by: 'u2' })"); page.wait_for_timeout(600)
    after = calls()
    print('1 live stage:', nowtxt(2999), '| fetched orders calls', after['loadOrders'] - before['loadOrders'], '| bytes', after['bytes'] - before['bytes'])
    # 2) another phone creates an order, adds a note, deletes an order
    page.evaluate("__mockApi.createOrder({ customer: 'Нова Мария', phone: '0888', address: '', price: '20', brand: 'Meivi', channel: 'Viber', account: '', note: '', urgent: true, due: '', needs_confirm: false, items: [{ product_type_id: 't5', name: 'Специална книга', is_tshirt: false, size: '', color: '', qty: 1, custom_design: false, note: '', stages: [{ key: 'design', name: 'Дизайн', kind: 'work' }] }] })")
    page.evaluate("__mockApi.insert('order_notes', { order_id: 'o2998', body: 'смени на XL' })")
    page.evaluate("__mockApi.remove('orders', 'o2997')"); page.wait_for_timeout(700)
    print('2 new order on top:', page.locator('.card .who').first.inner_text(), '| note badge:', 'Бележки: 1' in card(2998).inner_text(), '| deleted gone:', page.locator('.card').filter(has_text='Клиент 2997').count() == 0)
    # 3) a missed change (dropped connection) -> caught up on return to the app
    page.evaluate("window.__silent = true; __mockApi.update('item_stages', 'sp2996', { done_at: new Date().toISOString(), done_by: 'u2' }); __mockApi.update('orders', 'o2995', { urgent: true }); window.__silent = false;")
    page.wait_for_timeout(300); print('3 before catch-up:', nowtxt(2996))
    before = calls()
    page.evaluate("document.dispatchEvent(new Event('visibilitychange'))"); page.wait_for_timeout(500)
    after = calls()
    print('3 after return:', nowtxt(2996), '| urgent picked up:', 'Спешна' in card(2995).inner_text(), '| full loads', after['load'], '| catch-up bytes', after['bytes'] - before['bytes'])
    # 4) reconnect after the live channel dropped
    page.evaluate("window.__silent = true; __mockApi.update('item_stages', 'sp2994', { done_at: new Date().toISOString() }); window.__silent = false; __rt.status('CHANNEL_ERROR'); __rt.status('SUBSCRIBED');"); page.wait_for_timeout(500)
    print('4 after reconnect:', nowtxt(2994))
    # 5) my own actions still show at once
    card(2993).locator('.go').click(); page.wait_for_timeout(400); print('5 own Напред:', nowtxt(2993))
    # 6) 3000-order history still complete for stars and stats
    page.locator('#app .card-top').filter(has_text='Клиент 2999').click(); page.wait_for_timeout(150); print('6 star from old orders works:', page.locator('#pop .prev').count() == 0); page.click('.pop-x'); page.wait_for_timeout(150)
    # 7) typing is not interrupted by a live update
    card(2992).locator('.card-top').click(); page.wait_for_timeout(200)
    page.click('[data-field=address]'); page.keyboard.type('Пловдив')
    page.evaluate("__mockApi.update('item_stages', 'sp2991', { done_at: new Date().toISOString() })"); page.wait_for_timeout(600)
    print('7 still typing:', page.evaluate("document.activeElement.dataset.field"), page.input_value('[data-field=address]')[-7:])
    page.click('.pop-x'); page.wait_for_timeout(400); print('7 after closing, live update shown:', nowtxt(2991))
    # traffic comparison
    c = calls()
    print('TOTAL full loads:', c['load'], '| syncs', c['syncSince'], '| order fetches', c['loadOrders'], '| bytes after open', c['bytes'] - full_bytes)
    print('old way: one full reload =', full_bytes, 'bytes, every 30 s')
    print('errors:', errs)
    b.close()
