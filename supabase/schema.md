# Database reference (Supabase project `aetwuxgetazirjnacnuu`, org "Workflow")

Snapshot of the live schema on 2026-11-18. The live database is the source of truth. Check it with the Supabase tools before changing anything.

## Tables (public)

- **members**: user_id (= auth.users.id), name, is_admin, created_at
- **options**: id, kind ('brand' | 'channel' | 'account' | 'missing'), value, sort. Unique (kind, value).
  - `missing` = missing sizes. value is `"<product_type_id>|<size>|<colour>"`, where an empty colour means every colour.
- **stage_defs**: key, name, kind ('work' | 'wait'), sort. Defines the stage catalogue.
- **product_types**: id, name, is_tshirt, sizes text[], colors text[], sort, grp. grp groups t-shirt variants in the filter.
- **product_type_stages**: product_type_id, stage_key, sort, optional. Holds the default stages per product.
- **orders**:
  - identity and customer: id, num (sequence), customer, phone, recipient, address, price (cash on delivery)
  - source: brand, channel, account (Meivi TikTok account)
  - notes and flags: note, problem, urgent, due, photo_req
  - confirmation: needs_confirm, confirmed_at/by
  - packing: packed_at/by
  - completion: waybill_at/by (= "Завършена"), tracking
  - record: created_by, created_at, updated_at
- **items**: id, order_id, product_type_id, name, is_tshirt, size, color, qty, price (per piece; null on old orders), custom_design, note, photo_at/by (= on photo shoot), sort, created_at
- **item_stages**: id, item_id, stage_key, name, kind, sort, done_at/by. Each item gets its own copy of its stages.
- **order_notes**: id, order_id, body, author, created_at
- **tasks**: id, title, note, due, urgent, assignee, created_by, order_id, done_at/by, created_at, updated_at
- **leave_allowances** (user_id, year, days, carried), **leaves** (user_id, kind, start_date, end_date, note, status, …), **holidays** (day, name), **app_settings** (key, value; e.g. workweek)
- **private.settings**: holds `invite_code`. The value is secret: never print it or commit it.

## Access (RLS)

- Helper functions `private.is_member()` and `private.is_admin()` are security definer.
- Every member can read and write: orders, items, item_stages, options, product_types, product_type_stages, stage_defs.
- **order_notes**: every member can read. Insert only as yourself. Delete your own notes, or any note if admin.
- **tasks**:
  - Admin sees all. A member sees only tasks assigned to them.
  - A member can create tasks only for themselves.
  - On a task the admin created, a member can change only the done mark. The trigger `private.guard_task_update` enforces this.
- Admin only: leaves, leave_allowances. holidays and app_settings can be read by every member and written only by the admin.
- **members**: every member can read; each person can update only their own row.

## Triggers

- On auth.users:
  - `private.check_signup` rejects a sign-up unless its `invite_code` metadata (digits only) matches private.settings. It also auto-confirms the email.
  - `private.add_member` inserts the new person into members.
- `updated_at`: kept up to date on orders, tasks and leaves.
- `items_sync_order_price` (`private.sync_order_price`): when an order has items with a price, `orders.price` (cash on delivery) = sum of price × qty. Delivery is not included. Orders whose items have no price keep the total typed by hand.
- Change stamps on the order: any change to items, item_stages or order_notes also bumps `orders.updated_at`. Incremental sync relies on this.

## Functions (RPC)

- `create_order(p jsonb)` inserts an order with its items and their stages in one call.
- `save_item(p jsonb)` adds or edits an item. With `reset_stages`, it also replaces the item's stages.
- `work_stats(p_from, p_to)`: work per person. Security invoker, admin only (checked inside).

To read a function's full definition: `select pg_get_functiondef('public.create_order'::regproc);`

## Realtime publication

members, options, product_types, product_type_stages, orders, tasks, order_notes
