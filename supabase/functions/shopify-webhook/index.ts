// Receives Shopify webhooks for the stores and hands them to public.shopify_event().
// URL: https://<project>.supabase.co/functions/v1/shopify-webhook?shop=slash   (or ?shop=meivi)
// Secrets (Supabase → Edge Functions → Secrets): SHOPIFY_SECRET_SLASH, SHOPIFY_SECRET_MEIVI
// = the signing secret Shopify shows under Settings → Notifications → Webhooks.
import { createClient } from "jsr:@supabase/supabase-js@2";

const BRANDS: Record<string, string> = { slash: "Slash", meivi: "Meivi" };

function b64(buf: ArrayBuffer): string {
  let s = "";
  for (const b of new Uint8Array(buf)) s += String.fromCharCode(b);
  return btoa(s);
}
// constant-time comparison
function same(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return d === 0;
}

Deno.serve(async (req) => {
  if (req.method !== "POST") return new Response("ok");
  const shop = (new URL(req.url).searchParams.get("shop") || "").toLowerCase();
  const brand = BRANDS[shop];
  const secret = brand ? Deno.env.get(`SHOPIFY_SECRET_${shop.toUpperCase()}`) : "";
  if (!brand || !secret) return new Response("not configured", { status: 401 });

  const raw = await req.arrayBuffer();
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = b64(await crypto.subtle.sign("HMAC", key, raw));
  if (!same(sig, req.headers.get("x-shopify-hmac-sha256") || "")) return new Response("bad signature", { status: 401 });

  const topic = req.headers.get("x-shopify-topic") || "";
  let body: unknown;
  try { body = JSON.parse(new TextDecoder().decode(raw)); } catch { return new Response("bad json", { status: 400 }); }

  const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);
  const { data, error } = await sb.rpc("shopify_event", { p_brand: brand, p_topic: topic, p: body });
  if (error) {
    console.error(topic, error.message);
    return new Response("error", { status: 500 }); // Shopify will retry
  }
  return new Response(String(data));
});
