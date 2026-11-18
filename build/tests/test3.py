import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SHOTS = os.path.join(ROOT, 'build', 'shots') + '/'
os.makedirs(SHOTS, exist_ok=True)
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(args=['--no-sandbox'])
    page = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True).new_page()
    errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
    page.add_init_script(path=os.path.join(ROOT, 'build', 'mock.js'))
    page.goto('file://' + os.path.join(ROOT, 'index.html')); page.wait_for_timeout(300)
    page.fill('#a-email', 'a@b.bg'); page.fill('#a-pass', 'pass123'); page.click('#auth-form button[type=submit]'); page.wait_for_timeout(300)
    page.click('[data-act=new]'); page.fill('#f-customer', 'Иван'); page.click('[data-act=f-brand][data-v=Meivi]'); page.click('[data-act=f-channel][data-v=Messenger]')
    page.select_option('#f-type', label='Oversize Meivi'); page.click('[data-act=f-size][data-v=S]'); page.click('[data-act=f-color][data-v="Бяла"]'); page.uncheck('#f-confirm')
    page.click('[data-act=f-save]'); page.wait_for_timeout(300)
    page.click('.card-head'); page.locator('[data-act=stage]:has-text("Щамповане")').click(); page.wait_for_timeout(300)
    st = lambda: [(s['name'], bool(s['done_at'])) for s in page.evaluate('window.__db.item_stages')]
    print('after tapping Щамповане:', st(), '| badges:', page.inner_text('.badges'))
    page.locator('[data-act=stage]:has-text("Печат")').click(); page.wait_for_timeout(300)
    print('after undoing Печат:', st(), '| badges:', page.inner_text('.badges'))
    print('errors:', errs); b.close()
