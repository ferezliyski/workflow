import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SHOTS = os.path.join(ROOT, 'build', 'shots') + '/'
os.makedirs(SHOTS, exist_ok=True)
from playwright.sync_api import sync_playwright
out=SHOTS
with sync_playwright() as p:
    b = p.chromium.launch(args=['--no-sandbox'])
    page = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True, color_scheme='dark').new_page()
    errs=[]; page.on('pageerror', lambda e: errs.append(str(e))); page.on('console', lambda m: errs.append(m.text) if m.type=='error' else None)
    page.add_init_script(path=os.path.join(ROOT, 'build', 'mock.js'))
    page.goto('file://' + os.path.join(ROOT, 'index.html')); page.wait_for_timeout(300)
    page.fill('#a-email', 'a@b.bg'); page.fill('#a-pass', 'pass123'); page.click('#auth-form button[type=submit]'); page.wait_for_timeout(300)
    # an order to link to
    page.click('[data-act=new]'); page.fill('#f-customer','Иван'); page.click('[data-act=f-brand][data-v=Meivi]'); page.click('[data-act=f-channel][data-v=Messenger]')
    page.select_option('#f-type', label='Oversize Meivi'); page.click('[data-act=f-size][data-v=S]'); page.click('[data-act=f-color][data-v="Бяла"]'); page.uncheck('#f-confirm'); page.click('[data-act=f-save]'); page.wait_for_timeout(250)
    # notes on the order
    page.locator('.card-top').click(); page.wait_for_timeout(150)
    page.fill('#pop textarea[id^=nt-]', 'Клиентът иска L вместо S'); page.click('[data-act=note-add]'); page.wait_for_timeout(300)
    print('notes in popup:', page.locator('.note').all_inner_texts())
    # task from the order
    page.click('[data-act=task-new][data-order]'); page.wait_for_timeout(150)
    page.fill('#t-title', 'Обади се на Иван за адреса'); page.select_option('#t-assignee', 'u2'); page.click('[data-act=task-save]'); page.wait_for_timeout(300)
    print('after save, popup is order again:', page.locator('.pop-in').get_attribute('aria-label'))
    page.click('.pop-x'); page.wait_for_timeout(150)
    print('card badges:', page.locator('.card .badges').inner_text().replace('\n',' '))
    # profile, admin view
    page.click('[data-act=tab][data-v=profile]'); page.wait_for_timeout(200)
    print('team:', [x.replace('\n',' ') for x in page.locator('.person').all_inner_texts()], '| tab:', page.locator('[data-v=profile]').inner_text().replace('\n',' '))
    page.click('.person:has-text("Гошо")'); page.wait_for_timeout(150)
    print('Гошо tasks:', page.locator('.task').all_inner_texts())
    page.click('[data-act=task-new]'); page.fill('#t-title', 'Инвентаризация на заготовки'); page.fill('#t-due', '2026-11-10'); page.check('#t-urgent'); page.click('[data-act=task-save]'); page.wait_for_timeout(300)
    page.screenshot(path=out + 's20-person.png')
    print('Гошо tasks now:', [x.replace('\n',' | ') for x in page.locator('.task').all_inner_texts()])
    page.locator('.tick').first.click(); page.wait_for_timeout(300)
    print('after tick:', page.locator('.group-toggle').inner_text().replace('\n',' '))
    page.click('[data-act=show-done]'); page.wait_for_timeout(150); print('done rows:', len(page.locator('.task.done').all()))
    page.click('.back'); page.wait_for_timeout(150); print('team after:', [x.replace('\n',' ') for x in page.locator('.person').all_inner_texts()])
    page.click('[data-act=tab][data-v=settings]'); page.wait_for_timeout(150); print('settings title:', page.inner_text('.top h1'), '| profile tab active:', page.get_attribute('[data-v=profile]', 'aria-current'))
    page.click('.back'); page.wait_for_timeout(150); print('back to:', page.inner_text('.top h1'))
    page.screenshot(path=out + 's21-team.png')
    print('overflow:', page.evaluate('document.documentElement.scrollWidth > document.documentElement.clientWidth'), '| errors:', errs)
    b.close()
