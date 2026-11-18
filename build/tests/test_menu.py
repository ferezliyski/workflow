# "Склад" as a tab of the bottom menu, and the order window: "Платена" next to the sum, "Още" with the rare actions.
import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SHOTS = os.path.join(ROOT, 'build', 'shots') + '/'
os.makedirs(SHOTS, exist_ok=True)
from playwright.sync_api import sync_playwright

SEED = r"""
async () => {
  const A = window.__mockApi, db = window.__db;
  const S6 = ['XS','S','M','L','XL','2XL'];
  for (const c of ['Черна', 'Бяла']) await A.addStock(S6.map((sz, i) => ({ product_type_id: 't0', size: sz, color: c, delta: [6, 14, 22, 20, 12, 5][i], kind: 'load', created_by: 'u1' })));
  const tee = (design, size, color, price) => ({ product_type_id: 't0', name: 'Oversize Slash', is_tshirt: true, size, color, qty: 1, price: price == null ? '' : String(price), design, custom_design: false, note: '',
    stages: [{ key: 'print', name: 'Печат', kind: 'work' }, { key: 'press', name: 'Щамповане', kind: 'work' }] });
  const order = (customer, items, extra) => A.createOrder(Object.assign({ customer, phone: '0888 123 456', recipient: '', address: 'София, Еконт офис Младост 1', price: '', brand: 'Slash', channel: 'TikTok', account: '', note: '', urgent: false, due: '', needs_confirm: false, items }, extra || {}));
  await order('Мария Георгиева', [tee('Gojo Satoru „Infinity“', 'L', 'Бяла', 39), tee('Sasuke', 'S', 'Черна', 39)]);     // prices per product
  await order('Стара Поръчка', [tee('Sasuke', 'M', 'Черна', null)], { price: '45' });                                      // one total typed by hand
  const card = await order('Карта Сайт', [tee('Sasuke', 'XL', 'Черна', 39)], { channel: 'Сайт' });                         // paid by card in the store
  Object.assign(db.orders.find(o => o.id === card), { paid: true, shop_name: '#1012' });
  const sent = await order('Изпратена Вече', [tee('Sasuke', 'L', 'Черна', 39)]);
  Object.assign(db.orders.find(o => o.id === sent), { packed_at: new Date().toISOString(), packed_by: 'u1', waybill_at: new Date().toISOString(), waybill_by: 'u1', tracking: '123' });
  await order('Чака Размер', [{ ...tee('Sasuke', 'M', 'Черна', 35), product_type_id: 't1', name: 'Oversize Meivi' }]);    // no blanks of this type: waits for a size
  await A.insert('returns', { product_type_id: 't0', design: 'Gojo Satoru „Infinity“', size: 'XL', color: 'Бяла', created_by: 'u1', used_item_id: null, used_at: null, used_by: null });
  await A.insert('tasks', { title: 'Провери принтера', note: '', due: null, urgent: false, assignee: 'u1', order_id: null });
}
"""

def start(p, as_user='u1', theme='dark', seed=True):
    b = p.chromium.launch(args=['--no-sandbox'])
    page = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True).new_page()
    page.set_default_timeout(6000)
    errs = []; page.on('pageerror', lambda e: errs.append(str(e))); page.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    page.add_init_script(f"window.__noStock = true; window.__asUser = '{as_user}'; try {{ localStorage.setItem('wf-theme', '{theme}'); }} catch (x) {{}}")
    page.add_init_script(path=os.path.join(ROOT, 'build', 'mock.js'))
    page.goto('file://' + os.path.join(ROOT, 'index.html')); page.wait_for_timeout(300)
    if seed: page.evaluate(SEED)
    page.fill('#a-email', 'a@b.bg'); page.fill('#a-pass', 'pass123'); page.click('#auth-form button[type=submit]'); page.wait_for_timeout(800)
    return b, page, errs

with sync_playwright() as p:
    b, page, errs = start(p)
    tabs = lambda: page.locator('.bar .tab').all_inner_texts()
    cur = lambda: page.locator('.bar .tab[aria-current=page]').inner_text()
    pressed = lambda: page.locator('.seg .chip[aria-pressed=true]').inner_text()
    wide = lambda: page.evaluate("document.documentElement.scrollWidth > window.innerWidth")
    locked = lambda: page.evaluate("document.body.style.position === 'fixed'")
    ask = lambda: page.locator('#ask').count()

    # ---- 1. bottom menu ----
    print('1 tabs:', [t.replace('\n', ' ') for t in tabs()], '| current:', cur())
    fits = {}
    for w in (390, 375, 360, 320):
        page.set_viewport_size({'width': w, 'height': 844}); page.wait_for_timeout(120)
        fits[w] = page.evaluate("""() => { const t = [...document.querySelectorAll('.bar .tab')], bar = document.querySelector('.bar-in');
          return bar.scrollWidth <= bar.clientWidth && new Set(t.map(x => x.offsetHeight)).size === 1 && t.every(x => x.scrollWidth <= x.clientWidth) && t.every(x => x.getBoundingClientRect().right <= window.innerWidth + 0.5); }""")
    page.set_viewport_size({'width': 390, 'height': 844}); page.wait_for_timeout(120)
    print('  one line, nothing cut (with a task badge):', fits)

    # ---- 2. "Склад" ----
    page.click('.bar .tab:has-text("Склад")'); page.wait_for_timeout(500)
    print('2 store:', page.inner_text('.top h1'), '| chips:', page.locator('.seg .chip').all_inner_texts(), '| on:', pressed(), '| menu:', cur(), '| back link:', page.locator('.link.back').count())
    page.screenshot(path=SHOTS + 'menu-store.png')
    segY = [round(page.locator('.seg').bounding_box()['y'], 1)]
    page.evaluate("window.scrollTo(0, 60)"); y0 = page.evaluate("window.scrollY")
    page.click('.seg .chip:has-text("Returns")'); page.wait_for_timeout(300)
    print('  returns:', pressed(), '| add button:', page.locator('[data-act=ret-open]').count(), '| menu:', cur(), '| page moved:', page.evaluate("window.scrollY") != y0 and page.evaluate("document.documentElement.scrollHeight - window.innerHeight") >= y0)
    page.screenshot(path=SHOTS + 'menu-returns.png')
    page.click('.seg .chip:has-text("Материали")'); page.wait_for_timeout(400)
    print('  materials:', pressed(), '| + Материал:', page.locator('.top [data-act=mat-new]').count(), '| menu:', cur())
    page.click('[data-act=mat-new]'); page.wait_for_timeout(150); page.fill('#mat-name', 'Целофанов плик 30×40'); page.fill('#mat-low', '100'); page.click('[data-act=mat-save]'); page.wait_for_timeout(400)
    print('  material added:', page.locator('.mat-row').all_inner_texts())
    page.evaluate("window.scrollTo(0, 0)"); segY.append(round(page.locator('.seg').bounding_box()['y'], 1))
    page.click('.seg .chip:has-text("Returns")'); page.wait_for_timeout(200); segY.append(round(page.locator('.seg').bounding_box()['y'], 1)); page.click('.seg .chip:has-text("Материали")'); page.wait_for_timeout(200)
    print('  chips stay in place between the parts:', len(set(segY)) == 1, segY)
    page.screenshot(path=SHOTS + 'menu-materials.png')
    page.click('.bar .tab:has-text("Поръчки")'); page.wait_for_timeout(200); page.click('.bar .tab:has-text("Склад")'); page.wait_for_timeout(400)
    print('  comes back to the last part:', pressed())
    page.click('.seg .chip:has-text("Наличности")'); page.wait_for_timeout(400)
    page.click('[data-act=stock-open][data-v=load]'); page.wait_for_timeout(200)
    print('  load popup:', page.locator('.pop-in').get_attribute('aria-label'), '| page locked:', locked()); page.click('.pop-x'); page.wait_for_timeout(150)
    print('  overflow:', wide())

    # ---- 3. waiting for a size -> "Наличности" opens the store ----
    page.click('.bar .tab:has-text("Поръчки")'); page.wait_for_timeout(200)
    page.click('.nosize-btn'); page.wait_for_timeout(200); page.click('.top .fbtn:has-text("Наличности")'); page.wait_for_timeout(400)
    print('3 from "Чакат размер":', page.inner_text('.top h1'), '/', pressed(), '| menu:', cur())

    # ---- 4. profile without the store buttons ----
    page.click('.bar .tab:has-text("Профил")'); page.wait_for_timeout(200)
    print('4 admin profile buttons:', [t for t in page.locator('main .btn').all_inner_texts()], '| menu:', cur())
    page.screenshot(path=SHOTS + 'menu-profile.png')

    # ---- 5. "Платена" next to the sum ----
    page.click('.bar .tab:has-text("Поръчки")'); page.wait_for_timeout(200)
    if page.locator('.link.back').count(): page.click('.link.back'); page.wait_for_timeout(200)   # still on "Чакат размер" from step 3
    page.click('.card .who:has-text("Мария Георгиева")'); page.wait_for_timeout(400)
    acts = lambda: page.locator('.pop-in .actions').last.locator('button').all_inner_texts()
    print('5 sum row:', page.inner_text('.pop-in .cod-row').replace('\n', ' | '), '| bottom buttons:', acts())
    page.evaluate("document.querySelector('.pop-in .cod-row').scrollIntoView({ block: 'center' })"); page.screenshot(path=SHOTS + 'menu-order-top.png')
    page.click('.cod-row [data-act=paid]'); page.wait_for_timeout(200)
    print('  window:', page.locator('#ask button').all_inner_texts())
    page.screenshot(path=SHOTS + 'menu-paid-ask.png')
    page.locator('#ask .ask-box').click(position={'x': 4, 'y': 4}); print('  tap inside the window keeps it:', ask() == 1)
    page.locator('#ask').click(position={'x': 4, 'y': 4}); print('  tap outside closes it:', ask() == 0)
    page.click('.cod-row [data-act=paid]'); page.click('#ask [data-act=ask-x][data-x]'); print('  "Откажи" closes it:', ask() == 0, '| still a normal sum:', page.inner_text('.pop-in .cod'))
    page.click('.cod-row [data-act=paid]'); page.click('#ask [data-act=paid][data-v=order]'); page.wait_for_timeout(500)
    print('  paid:', page.inner_text('.pop-in .cod').replace('\n', ' '), '| window gone:', ask() == 0, '| button gone:', page.locator('.pop-in .copy[data-act=paid]').count() == 0, '| db:', page.evaluate("__db.orders[0].paid_manual"))
    page.click('.pop-in .cod [data-act=paid]'); page.wait_for_timeout(500)
    print('  undo:', page.inner_text('.pop-in .cod-row').replace('\n', ' | '), '| db:', page.evaluate("__db.orders[0].paid_manual"))

    # ---- 6. "Още" ----
    page.click('.pop-in [data-act=more]'); page.wait_for_timeout(200)
    print('6 more:', page.locator('#ask button').all_inner_texts(), '| page locked:', locked())
    page.screenshot(path=SHOTS + 'menu-more.png')
    page.click('#ask [data-act=ask-x][data-x]'); print('  "Затвори":', ask() == 0, '| order still open:', page.locator('.pop-in').get_attribute('aria-label'))
    page.click('.pop-in [data-act=more]'); page.click('#ask [data-act=urgent]'); page.wait_for_timeout(500)
    print('  urgent:', page.evaluate("__db.orders[0].urgent"), '| toast:', page.inner_text('#toast'), '| window gone:', ask() == 0)
    page.click('.pop-in [data-act=more]'); page.wait_for_timeout(150); print('  now offers:', page.locator('#ask [data-act=urgent]').inner_text())
    page.click('#ask [data-act=urgent]'); page.wait_for_timeout(500); print('  urgent off:', page.evaluate("__db.orders[0].urgent"), '| toast:', page.inner_text('#toast'))
    page.click('.pop-in [data-act=more]'); page.click('#ask [data-act=task-new]'); page.wait_for_timeout(300)
    print('  task:', page.locator('.pop-in').get_attribute('aria-label'), '| window gone:', ask() == 0)
    page.fill('#t-title', 'Обади се за адреса'); page.click('[data-act=task-save]'); page.wait_for_timeout(400)
    print('  after saving the task:', page.locator('.pop-in').get_attribute('aria-label'), '| task has the order:', page.evaluate("__db.tasks.some(t => t.title === 'Обади се за адреса' && t.order_id === __db.orders[0].id)"))
    # delete: two taps, the first only arms
    n0 = page.evaluate("__db.orders.length")
    page.click('.pop-in [data-act=more]'); page.click('#ask [data-act=delete]'); page.wait_for_timeout(150)
    print('  delete, first tap:', page.locator('#ask [data-act=delete]').inner_text(), '| orders:', page.evaluate("__db.orders.length") == n0)
    page.screenshot(path=SHOTS + 'menu-more-armed.png')
    page.click('#ask [data-act=ask-x][data-x]'); page.click('.pop-in [data-act=more]'); page.wait_for_timeout(150)
    print('  closed and opened again:', page.locator('#ask [data-act=delete]').inner_text())
    page.click('#ask [data-act=delete]'); page.wait_for_timeout(100); page.click('#ask [data-act=delete]'); page.wait_for_timeout(600)
    print('  delete, second tap: orders', n0, '->', page.evaluate("__db.orders.length"), '| window gone:', ask() == 0, '| order closed:', page.locator('.pop-in').count() == 0, '| page unlocked:', not locked(), '| card gone:', page.locator('.card .who:has-text("Мария Георгиева")').count() == 0)

    # ---- 7. other kinds of orders ----
    page.click('.card .who:has-text("Стара Поръчка")'); page.wait_for_timeout(400)
    print('7 hand-typed total:', page.locator('.pop-in .inline:has(input[data-field=price]) button').all_inner_texts(), '| value:', page.input_value('.pop-in input[data-field=price]'))
    page.evaluate("document.querySelector('.pop-in input[data-field=price]').scrollIntoView({ block: 'center' })"); page.screenshot(path=SHOTS + 'menu-order-price.png')
    page.fill('.pop-in input[data-field=price]', '50'); page.dispatch_event('.pop-in input[data-field=price]', 'change'); page.wait_for_timeout(500)
    print('  typing a price still saves:', page.evaluate("__db.orders.find(o => o.customer === 'Стара Поръчка').price"))
    page.click('.pop-in .inline [data-act=paid]'); page.click('#ask [data-act=paid][data-v=all]'); page.wait_for_timeout(500)
    print('  paid:', page.inner_text('.pop-in .cod').replace('\n', ' '))
    page.click('.pop-x'); page.wait_for_timeout(200)
    page.click('.card .who:has-text("Карта Сайт")'); page.wait_for_timeout(400)
    print('  paid by card in the store: label', [t for t in page.locator('.pop-in .lbl').all_inner_texts() if 'лат' in t], '| "Платена" button:', page.locator('.pop-in .copy[data-act=paid]').count())
    page.click('.pop-x'); page.wait_for_timeout(200)
    page.click('.bar .tab:has-text("Готови")'); page.wait_for_timeout(200); page.click('.seg .chip:has-text("Завършени")'); page.wait_for_timeout(200)
    page.click('.card .who:has-text("Изпратена Вече")'); page.wait_for_timeout(400)
    print('  finished order, bottom buttons:', acts())
    page.click('.pop-x'); page.wait_for_timeout(200)
    print('  overflow:', wide(), '| page unlocked:', not locked())
    print('errors:', errs); b.close()

    # ---- 8. a member ----
    b, page, errs2 = start(p, as_user='u2', theme='light')
    page.click('.bar .tab:has-text("Профил")'); page.wait_for_timeout(200)
    print('8 member profile buttons:', page.locator('main .btn').all_inner_texts(), '| tabs:', [t.replace('\n', ' ') for t in page.locator('.bar .tab').all_inner_texts()])
    page.screenshot(path=SHOTS + 'menu-profile-member.png')
    page.click('.bar .tab:has-text("Склад")'); page.wait_for_timeout(400); print('  member sees the store:', page.inner_text('.top h1'), page.locator('.seg .chip').all_inner_texts())
    page.screenshot(path=SHOTS + 'menu-store-light.png')
    print('errors:', errs2); b.close()
