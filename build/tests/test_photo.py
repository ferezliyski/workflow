# Photo shoot: no manual "Изпрати за снимане" on the products; "Заяви за снимане" is the only way and works only while the order is not packed.
import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SHOTS = os.path.join(ROOT, 'build', 'shots') + '/'
os.makedirs(SHOTS, exist_ok=True)
from playwright.sync_api import sync_playwright

SEED = r"""
async () => {
  const A = window.__mockApi, db = window.__db;
  const tee = (size) => ({ product_type_id: 't0', name: 'Oversize Slash', is_tshirt: true, size, color: 'Черна', qty: 1, price: '39', design: 'Sasuke', custom_design: false, note: '',
    stages: [{ key: 'print', name: 'Печат', kind: 'work' }, { key: 'press', name: 'Щамповане', kind: 'work' }] });
  const order = (customer, items) => A.createOrder({ customer, phone: '0888 123 456', recipient: '', address: 'София', price: '', brand: 'Slash', channel: 'TikTok', account: '', note: '', urgent: false, due: '', needs_confirm: false, items });
  const done = async (oid, n) => { const its = db.items.filter(i => i.order_id === oid).map(i => i.id);
    for (const s of db.item_stages.filter(x => its.includes(x.item_id)).slice(0, n)) await A.update('item_stages', s.id, { done_at: new Date().toISOString(), done_by: 'u2' }); };
  await order('В Производство', [tee('M')]);
  await done(await order('Готова Поръчка', [tee('L')]), 2);
  const c = await order('Опакована Поръчка', [tee('S')]); await done(c, 2);
  Object.assign(db.orders.find(o => o.id === c), { packed_at: new Date().toISOString(), packed_by: 'u1', photo_req: true });   // requested, then packed
  await done(await order('Два Продукта', [tee('XL'), tee('2XL')]), 3);   // only the last stage of the second product is left
}
"""
STATE = "(name) => { const o = __db.orders.find(o => o.customer === name), its = __db.items.filter(i => i.order_id === o.id); return { req: !!o.photo_req, packed: !!o.packed_at, photo: its.map(i => !!i.photo_at) }; }"

with sync_playwright() as p:
    b = p.chromium.launch(args=['--no-sandbox'])
    page = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True).new_page()
    page.set_default_timeout(6000)
    errs = []; page.on('pageerror', lambda e: errs.append(str(e))); page.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    page.add_init_script("try { localStorage.setItem('wf-theme', 'dark'); } catch (x) {}")
    page.add_init_script(path=os.path.join(ROOT, 'build', 'mock.js'))
    page.goto('file://' + os.path.join(ROOT, 'index.html')); page.wait_for_timeout(300)
    page.evaluate(SEED)
    page.fill('#a-email', 'a@b.bg'); page.fill('#a-pass', 'pass123'); page.click('#auth-form button[type=submit]'); page.wait_for_timeout(800)
    state = lambda name: page.evaluate(STATE, name)
    card = lambda name: page.locator('.card').filter(has_text=name).first
    acts = lambda: page.locator('.pop-in .actions').last.locator('button').all_inner_texts()
    toast = lambda: page.inner_text('#toast').replace('\n', ' | ')
    def open_(name): card(name).locator('.who').click(); page.wait_for_timeout(350)
    def close(): page.click('.pop-x'); page.wait_for_timeout(200)

    # 1. an order in production: no manual send
    open_('В Производство')
    print('1 yellow button on the product:', page.locator('.pop-in .step.photo').count(), '| "Изпрати за снимане" anywhere:', 'Изпрати за снимане' in page.inner_text('.pop-in'), '| bottom:', acts())
    page.screenshot(path=SHOTS + 'photo-order.png')

    # 2. request, remove the request, request again
    page.click('.pop-in [data-act=photo-req]'); page.wait_for_timeout(400)
    print('2 requested:', state('В Производство'), '| toast:', toast(), '| button:', acts()[0])
    page.click('.pop-in [data-act=photo-req]'); page.wait_for_timeout(400)
    print('  removed:', state('В Производство')['req'], '| toast:', toast())
    page.click('.pop-in [data-act=photo-req]'); page.wait_for_timeout(400); close()
    print('  badge on the card:', '📷 Заявена за снимане' in card('В Производство').inner_text())

    # 3. the last stage is finished -> it goes to the photo shoot by itself
    open_('В Производство')
    page.locator('.pop-in [data-act=stage]', has_text='Щамповане').click(); page.wait_for_timeout(500)
    print('3 last stage done:', state('В Производство'), '| notice:', page.locator('#notice h2').inner_text() if page.locator('#notice').count() else None)
    page.click('[data-act=notice-ok]'); page.wait_for_timeout(200)
    print('  in the order:', page.locator('.pop-in .step.photo').all_inner_texts(), '| bottom:', acts())
    page.evaluate("document.querySelector('.pop-in .step.photo').scrollIntoView({ block: 'center' })"); page.screenshot(path=SHOTS + 'photo-at-shoot.png')

    # 4. bring it back, undo, bring it back from the card
    page.click('.pop-in .step.photo'); page.wait_for_timeout(400)
    print('4 returned:', state('В Производство'), '| toast:', toast(), '| yellow button:', page.locator('.pop-in .step.photo').count(), '| bottom:', acts())
    page.click('#toast [data-undo]'); page.wait_for_timeout(400)
    print('  undo -> at the shoot again:', state('В Производство')['photo'])
    close()
    print('  card:', card('В Производство').locator('.now-txt').inner_text().replace('\n', ' '), '/', card('В Производство').locator('.go').inner_text())
    card('В Производство').locator('.go').click(); page.wait_for_timeout(400)
    print('  "Върната" on the card:', state('В Производство')['photo'])

    # 5. the order is already made when it is requested -> right away
    open_('Готова Поръчка')
    print('5 made order, bottom:', acts())
    page.click('.pop-in [data-act=photo-req]'); page.wait_for_timeout(500)
    print('  requested:', state('Готова Поръчка'), '| toast:', toast(), '| in the order:', page.locator('.pop-in .step.photo').all_inner_texts(), '| bottom:', acts())
    close()

    # 6. two products: the request waits for the last stage of the last product
    open_('Два Продукта'); page.click('.pop-in [data-act=photo-req]'); page.wait_for_timeout(400); close()
    card('Два Продукта').locator('.go').click(); page.wait_for_timeout(500)
    print('6 two products after the last stage:', state('Два Продукта'), '| notice:', page.locator('#notice').count())
    page.click('[data-act=notice-ok]'); page.wait_for_timeout(200)

    # 7. a packed order cannot be called for photos
    page.click('.bar .tab:has-text("Готови")'); page.wait_for_timeout(300)
    print('7 packed: badge on the card:', '📷' in card('Опакована Поръчка').inner_text())
    open_('Опакована Поръчка')
    print('  bottom:', acts(), '| request kept in the data:', state('Опакована Поръчка')['req'])
    page.screenshot(path=SHOTS + 'photo-packed.png')
    page.click('.pop-in [data-act=pack]'); page.wait_for_timeout(500)   # unpack
    print('  unpacked:', state('Опакована Поръчка'))
    print('  the request can be removed again:', acts()); close()
    page.click('.bar .tab:has-text("Поръчки")'); page.wait_for_timeout(300)
    print('  the request is back on the card:', '📷 Заявена за снимане' in card('Опакована Поръчка').inner_text())
    print('  overflow:', page.evaluate("document.documentElement.scrollWidth > window.innerWidth"))
    print('errors:', errs); b.close()
