# Workflow: history of the work so far (chat with Claude, 15–18.11.2026)

This file continues the work from an earlier chat with Claude. Read it together with **CLAUDE.md**: that file has the technical description, the rules and the publishing process. Here are the history, the decisions and the owner's wishes in the order they came up.

**Reply to the owner in Bulgarian, briefly, without technical terms.** He uses the app from his phone and from a Mac (Safari; Opera has a problem with Viber links).

## How we got here

1. **Idea.** A shared phone app for the team, with orders from TikTok, Instagram, Messenger, Viber, the website and the phone, and progress per product. The first version has manual entry only. The stores (Shopify) will be connected later, once real sales start on the sites.
2. **Infrastructure.**
   - Supabase: a separate free organization **"Workflow"** in the same Supabase account, so as not to use up Meivi's projects.
   - Hosting: Netlify at first, then GitHub Pages (`ferezliyski/workflow`), because the Netlify badge covered the menu.
   - The app updates itself through `version.txt`.
   - Sign-up only with an invite code. The code is in the database; do not write it anywhere.
3. **Stages per product**, given by the owner:
   - T-shirts: confirmation (call the customer), print, press, pack, waybill.
   - Special book: design, customer approval, print pages, print covers, assemble, pack, waybill.
   - Mini album: design, assemble, pack, waybill.
   - Car ornament: design, print, pack, waybill.
   - 3D picture: design, approval, cutting file, cut, print, pack, waybill.
   - Numbers (цифри): design, cutting file, cut, print, pack, waybill.
   - Hoodies were added later.
   - "Изпратена за снимане" can happen at any stage. The order continues from where it stopped.
   - Custom task: a product typed by hand, with stages picked by hand.
4. **Source of an order:**
   - brand: Slash or Meivi;
   - channel;
   - for Meivi TikTok, the account: Meivi, Auto, Inlove or Zodiac.
5. **Sizes and colours:**
   - Oversize Slash XS–2XL (Slash and Meivi oversize are different products).
   - Oversize Meivi XS–2XL.
   - Мъжка/Дамска Meivi S–3XL.
   - Худи XS–3XL.
   - Black and white for now.
6. **Look**, after several rounds:
   - menu at the bottom, taller bar;
   - simple; white, black and red; mid-strength colours; smaller fonts;
   - clear separation between orders;
   - next step: thin green outline; photo: yellow dashed;
   - no helper texts ("това не е интерфейс за клиенти");
   - nothing may jump or scroll by itself, and no sideways movement;
   - the background is frozen while a popup is open.
7. **Lists and filters:**
   - "За правене": a table by model, size and colour, plus other products by stage.
   - Filters (a small button with a popup): stage, store, product with t-shirts grouped, urgent, late.
   - Search across everything.
   - Counts in the headers.
8. **Order details:**
   - delivery recipient and address in two fields, with copy buttons;
   - cash-on-delivery price;
   - repeat-customer ★;
   - notes;
   - edit products and phone;
   - Viber button next to the phone.
9. **Profile:**
   - Personal tasks: the owner is the only admin and sees and assigns everyone's. A member sees only their own and can only tick the admin's tasks.
   - Settings are editable by everyone.
   - Light/dark theme.
   - Admin only: statistics (today / 7 days, repeat customers), work per person (popup per person) and leave tracking.
   - The owner will finish leave tracking in December and open it to members from the new year.
10. **Traffic.** The 30-second full reload would have exceeded the free 5 GB/month. It was replaced with incremental sync (see CLAUDE.md). Usage is 4–7 hours a day on 4–5 phones plus a computer.
11. **18.11, the end of the flow:**
    - Packed orders go to "Готови" → "За изпращане".
    - "Изпрати" sits under the waybill field. It marks the order "Завършена" and opens Viber with: "Здравейте, това е номера на Вашата пратка <номер>. Скоро ще бъде при вас. Благодарим ви!"
    - Opera on Mac quits on Viber links (an Opera bug). The owner said: do not block it, better that it works sometimes. He uses Safari. On a computer the message is also copied.
12. **18.11, missing sizes:**
    - Profile → "Липсващи размери": pick type, size and colour.
    - Matching orders leave the main list and go behind "⚠ Чакат размер (n)" at the top of Поръчки, with a ⚠ badge.
    - In "За правене" those cells are yellow with ⚠.
    - "Заредихме" brings the orders back.
13. **18.11, "Заяви за снимане":**
    - A button on the order, not a stage. Marketing picks orders for the photo shoot.
    - When the order is made and packing comes next, a big "Предай за снимане" notice appears on a white background, and the order is automatically marked as on photo shoot.
14. **18.11.** The source code, tests, CLAUDE.md and this file were moved into the repo. Last published version at the move: 20261118-1300.

15. **18.11, moved to Claude Code on the Mac.** Small changes: black profile buttons; statistics split into "Meivi тениски" and "Meivi подаръци".
16. **18.11, prices.** Each product has its own price, typed by hand when adding it (the owner does not want default prices for now). Cash on delivery is the sum of the products, without delivery. Old orders keep their total.
17. **18.11, Slash integration prepared.**
    - The 96 Slash products (87 t-shirts, 9 sets) are loaded as designs. Manual orders pick the design from the same list.
    - Site orders will arrive by themselves, always "за потвърждение" (the team calls every customer), without design/approval stages. Sets become two t-shirts.
    - A cancelled site order is not deleted; it gets the badge "Отказана в сайта".
    - Waiting for the owner: add the webhooks in Shopify and the secret in Supabase (see CLAUDE.md → Roadmap).
18. **18.11, later:** Slash sync live; stock (Наличности), Returns and Материали tabs (see CLAUDE.md → Business rules).
19. **18.11, "Платена" button** in the order (version 20261118-2038): "Само поръчката" or "Поръчката и доставката"; cash on delivery then shows 0 € with that text.

## Still to do (in the owner's order)

1. **Synchronisation with the Shopify stores** (Slash and Meivi). The plan is in CLAUDE.md → Roadmap.
   - Waybills for site orders are generated by the **izprati.bg** Shopify app, which writes the tracking number back to Shopify.
   - The owner needs to be guided step by step in Shopify: creating a custom app and getting a key.
2. Deactivating a member who leaves, without deleting their history.
3. Backups.
4. Optional: change name and password, team chat, push notifications (e.g. "Предай за снимане" on the marketing person's phone).

## Untested

The live link between two real phones. The owner was going to try it on 18.11. Ask him how it went.
