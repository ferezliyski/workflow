import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SHOTS = os.path.join(ROOT, 'build', 'shots') + '/'
os.makedirs(SHOTS, exist_ok=True)
from playwright.sync_api import sync_playwright
out = SHOTS
with sync_playwright() as p:
    b = p.chromium.launch(args=['--no-sandbox'])
    page = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True).new_page()
    errs = []
    page.on('pageerror', lambda e: errs.append(str(e)))
    page.add_init_script(path=os.path.join(ROOT, 'build', 'mock.js'))
    page.goto('file://' + os.path.join(ROOT, 'index.html')); page.wait_for_timeout(300)
    page.click('[data-act=auth-mode][data-v=up]')
    page.fill('#a-name', 'Мартин'); page.fill('#a-email', 'a@b.bg'); page.fill('#a-pass', 'pass123'); page.fill('#a-code', '111111')
    page.click('#auth-form button[type=submit]'); page.wait_for_timeout(250)
    print('wrong code ->', page.inner_text('.err'), '| sent:', page.evaluate('window.__signup'))
    print('fields kept:', page.input_value('#a-name'), page.input_value('#a-email'), page.input_value('#a-code'))
    page.fill('#a-code', '249 708'); page.click('#auth-form button[type=submit]'); page.wait_for_timeout(300)
    print('sent:', page.evaluate('window.__signup'), '| in app:', page.locator('.top h1').inner_text())
    print('errors:', errs)
    b.close()
