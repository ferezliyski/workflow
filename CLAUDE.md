# Workflow: notes for Claude

**Always reply to the owner in Bulgarian.** Keep replies short. He works mostly from his phone and is not a programmer: explain in plain words, not code. All UI text is Bulgarian.

Read HISTORY.md too: it has the history of the work and the open items.

## What this is

An internal phone web app for a small company. The team is 4 people, soon 7–8. The company has two brands:
- **Slash**: t-shirts.
- **Meivi**: t-shirts, special books, mini albums, car ornaments, 3D pictures, numbers, hoodies.

The company also has a UV printer, a CO2 laser and a 3D printer.

Orders come in manually from TikTok, Instagram, Messenger, Viber, the website and the phone. The app tracks each product through its production stages, from entry to sending.

- Live at GitHub Pages: https://ferezliyski.github.io/workflow/ (repo `ferezliyski/workflow`, branch `main`, served from the root). People use it from the phone home screen and from the computer (Safari and Opera on a Mac).
- Data and login: Supabase project `aetwuxgetazirjnacnuu` in the separate org **"Workflow"**, on the free plan. See `supabase/schema.md`. Change the schema only through migrations, and check advisors after each change.
- Owner = the only admin (`members.is_admin`). Everyone else is a member.

## Repo layout

```
src/app.html        ← THE SOURCE. One file: HTML + CSS + JS (no framework).
build/build.py      → writes index.html (inlines supabase-js + version stamp) and version.txt
build/mock.js       in-browser fake Supabase used by the tests (window.__db, __asUser for a 2nd user)
build/tests/*.py    Playwright scripts against index.html + mock.js (test_sync.py = sync/traffic)
supabase/schema.md  database reference
index.html, version.txt   BUILT FILES, published as-is. Never edit by hand.
```

Setup:

```
cd build && npm install && pip install playwright && playwright install chromium
```

Release (every change):
1. Edit `src/app.html`.
2. Run `python3 build/build.py`.
3. Run the relevant tests, at least `python3 build/tests/test_sync.py`, and check that `errors: []` is printed.
4. Commit and push to `main`.

Open phones reload themselves. They compare `version.txt` with their own version when the app comes back into view. Always tell the owner the new version number.

## Architecture

- **One page.**
  - `D` holds the loaded data and `UI` holds the view state.
  - `render()` rebuilds `#app`. One delegated click handler dispatches on `data-act`.
  - `data-field` inputs save on change.
- **Loading and sync**, designed to keep traffic far under the free 5 GB/month:
  - The app does one full load on open.
  - After that it uses incremental sync. Realtime events trigger a fetch of only the changed orders, by `updated_at`.
  - A light `syncSince` catch-up runs when the app comes back into view, on reconnect, when the phone comes back online, and every 3 minutes.
  - **Do not add periodic full reloads.**
- `redraw()` waits while the user is typing in an input, except the search box.
- The tracking field is saved quietly, without a redraw. Otherwise the tap on "Изпрати" right after it gets lost.
- **Popups:** the body is pinned with `position:fixed` while a popup is open; iPhone otherwise scrolls the list behind it. The scroll position is kept on every re-render. No sideways wobble: overflow-x and touch-action rules.
- Theme: `localStorage['wf-theme']` → `data-theme` on the root element. Use CSS vars `--bg --surface --ink --soft --line`. There is **no `--card` and no `--muted`**.

## Business rules

- **Order source:**
  - brand: Slash or Meivi;
  - channel: TikTok, Instagram, Messenger, Viber, Сайт, Телефон;
  - account: for Meivi TikTok only (Meivi, Auto, Inlove, Zodiac).
- **Products and stages:**
  - Each product type has default stages (`product_type_stages`), copied into `item_stages` per item.
  - Stage kind is 'work' or 'wait' (waiting for the customer, shown as "Чака клиента").
  - Finishing a stage also finishes the earlier ones; undoing one undoes the later ones.
  - "Custom task": a product name typed by hand, with the stages picked by hand.
- **T-shirts and hoodies:**
  - Oversize Slash XS–2XL (Slash and Meivi oversize are different products).
  - Oversize Meivi XS–2XL.
  - Мъжка/Дамска Meivi S–3XL.
  - Худи XS–3XL.
  - Colours black and white for now. T-shirt variants are grouped in the filters.
- **Confirmation:** `needs_confirm`, then the customer is called. Until then the order counts as waiting for the customer.
- **Photo shoot:**
  - "На снимане": `items.photo_at` can be set at any stage. "Върната" continues from where it stopped.
  - "Заяви за снимане" (`orders.photo_req`) is not a stage. Marketing flags an order. When the last production stage is finished, the person who finished it sees a big "Предай за снимане" notice. All items get `photo_at` automatically, and `photo_req` is cleared.
- **Missing sizes:**
  - Profile → "Липсващи размери". Stored as `options` with kind `missing`.
  - Orders with a not-yet-made item in a missing size leave the main list. They go behind a yellow button at the top of Поръчки, "⚠ Чакат размер (n)", with a ⚠ badge on the card.
  - In "За правене" those cells are yellow with ⚠, plus a note under the table.
  - Pressing "Заредихме" removes the entry and the orders come back.
- **End of the flow:**
  1. All products are made, then "Опаковано" (`packed_at`). The order moves to the **Готови** tab, section "За изпращане".
  2. Type the waybill number, then press **Изпрати**. This sets `waybill_at` (= "Завършена") and opens Viber with this draft:
     `Здравейте, това е номера на Вашата пратка <номер>. Скоро ще бъде при вас.\nБлагодарим ви!`
     The link is `viber://chat?number=%2B359…&draft=…`; `intlPhone` turns 0… into +359…. On a computer the message is also copied to the clipboard.
  3. "Върни" undoes it. Finished orders from the last 30 days are listed in Готови.
- **Known issue:** Opera on Mac quits when a page opens `viber://`. That is an Opera bug. The owner chose to keep opening Viber anyway and uses Safari.
- **Waybills for site orders** will be generated by the **izprati.bg** Shopify app, which writes the tracking number back to Shopify.
- **Other features:**
  - search across all fields;
  - filters: stage, store, product, urgent, late;
  - repeat-customer ★;
  - order notes;
  - copy buttons for name, address and phone;
  - Viber button next to the phone number;
  - cash-on-delivery price.
- **Profile:**
  - Personal tasks: admin sees and assigns everyone's; a member sees only their own and can only tick the admin's tasks.
  - Settings are editable by everyone.
  - Theme switch.
  - Admin only: statistics (today / 7 days / repeat customers), work per person (`work_stats`, popup per person) and leave tracking. The owner will finish leave in December and open it to members from the new year.
- **Sign-up:** needs the invite code, which is in `private.settings`. Never write the code anywhere.

## Owner's UI preferences (follow them)

- Simple and obvious. **No helper or explanation texts.** "Това не е интерфейс за клиенти."
- White, black and red style; mid-strength colours, not harsh and not washed out. Menu at the bottom, taller bar. Smaller fonts and buttons, with clear separation between order cards.
- Next step: thin green outline. Photo: yellow dashed.
- **Nothing may jump:** no scroll-to-top when picking an option, and no horizontal movement.
- Show counts in headers, e.g. "Поръчки (12)".
- Check every visual change with a 390×844 screenshot before publishing.

## Roadmap (agreed, not done)

1. **Shopify sync** for both stores (Slash, Meivi):
   - New site orders arrive automatically.
   - Plan: a Supabase Edge Function receives Shopify webhooks (orders/create, orders/updated, fulfillments/create|update) and verifies the HMAC.
   - Each store gets a custom app with an Admin API token. Keep the tokens and secrets only in Supabase secrets, never in the repo.
   - Map line items and variants to `product_types` and size/colour, with channel 'Сайт'.
   - When izprati.bg creates a fulfilment with tracking, fill `tracking` and decide with the owner whether to auto-complete.
   - Avoid duplicates: store the Shopify order id (new column).
2. Deactivate a member (someone leaves the team) without deleting their history.
3. Backups (the free plan has no point-in-time restore): e.g. a scheduled export.
4. Optional: change name and password; team chat; push notifications (e.g. "Предай за снимане" to the marketing person's phone).
