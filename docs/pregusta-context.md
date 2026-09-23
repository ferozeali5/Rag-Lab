# Pregustà — consolidated context

Compiled 2026-09-23 from earlier Claude sessions, their 9 design artifacts,
and **verified against `ferozeali5/pregusta-app` main @ 944f022 (2026-09-23)**.
The repo's own `docs/FOR-FEROZE.md` (waiting-on-Feroze list), `docs/ROADMAP.md`
and `CLAUDE.md` are the source of truth; this file is a summary. The backend
lives in a separate repo, `~/pregusta-api` (FastAPI on Render, Postgres on
Supabase), not accessible from here.

## Latest state (verified 2026-09-23)
- **Launch target moved:** Dec 2026 – Jan 2027, hard backstop 31 Jan 2027
  (v1 scope decision 2026-09-15: "the bar beats the date"). iOS first, US only.
  Scope rule: scan quality first.
- **Apple developer account is live:** first real build done, `eas.json`
  has the App Store Connect app (f002cb8, 22 Sep); that build found two bugs,
  both fixed (4ff9117: paywall screen-height hole; 5xx wrongly shown as
  "Pregustà is waking up").
- **Deploy of 16 Sep is live** (main at 3831baa then, 940 tests green, 5
  Supabase migrations verified). Render is now always-on, not free tier.
- **Login decided 2026-09-23 (bac33f6), not built:** free-scan count follows the
  account (sign-in never grants a fresh five; each free scan costs ~$0.20);
  v1 is Apple sign-in only (Restore-by-email covers purchase recovery).
  Deliberately not next.
- **Streaming scans:** wired to `/v1/scan-stream` behind `STREAM_SCAN_ENABLED`,
  which is off (6238ba6). Turning it on is still Feroze's call.
- **Done 19–23 Sep:** ☰ menu dim settled at 42% (0f696ae) and Help moved out of
  ☰; sample menu photos regenerated at real-scan quality 1024px (6bddb4b);
  paste-a-menu-link as a second QR door; paste box warns which menus it can't
  read; share sheet redone; Ask Pregustà answers in groups; dish-card
  re-render perf fix; paywall and failure-screen polish; Spanish App Store
  listing; competitor benchmark table.
- **Old app branches** `i18n-latin`, `manage-sub-app`, `rag-phase1-app`
  (all 15 Sep) are still on GitHub; FOR-FEROZE.md asks whether to delete them.

## Waiting on Feroze (from repo `docs/FOR-FEROZE.md`, last updated 16 Sep)
- 🔴 **Security first:** an old admin password was exposed and is reused on
  other accounts — secure email + 2FA, then money accounts, then infra;
  unique passwords everywhere.
- Decisions: origin story for App Store copy; delete the 3 old branches?;
  fetcher user-agent `PregustaBot/1.0` vs retry-as-browser (chain menus);
  approve streaming; pricing / annual plan / free limit / founding perks;
  second dietary ask for people who skipped it.
- Hands: lawyer pass on the privacy-policy diff; human read of ~140 religious
  knowledge-base entries before RAG Phase 1; GitHub token `workflow` scope
  for CI; Sentry `SENTRY_AUTH_TOKEN` EAS secret (and check the project slug);
  allow git in `pregusta-api` (except push to main) so Claude can work there.
- Eyes: "Usually made with" cautions — helpful or noise; 5 screens that may
  ghost list rows under the header (see ROADMAP).
- Queued: 14 non-blocker findings from the deploy review
  (`docs/deploy-review-findings-2026-09-16.md`); PDF menus refused by
  `safe_fetch.ALLOWED_CONTENT_TYPES`; a composition pass over every screen.

## What the product is
- iOS-first menu scanner for travellers. Tagline "KNOW BEFORE YOU ORDER";
  promise line "A menu you can't read, answered."
- Photo or QR-scan any menu → translated dish list, AI preview photos
  (labelled "✦ AI preview"), converted prices ("about $X"), dietary/allergen
  flags from a profile (Halal, Vegetarian, Nuts, Shellfish…; flags only rule
  things out, never claim "safe"), pronunciation, calories, "Ask the Kitchen"
  card, "Ask Pregustà" chat, bundled sample menu, scan history.
- No user accounts: identity = device ID + Support ID. Reinstall resets
  everything; login is planned (would land at the pass-nudge screen).

## Tech
- App: React Native / Expo, expo-router (`app/(tabs)/index.tsx`), components
  in `components/` (AccountScreen, DietaryProfileScreen, PaywallScreen,
  WelcomeScreen, ManageSubscriptionScreen, PassCard), theme in
  `constants/theme.ts`, `lib/subscription.ts`. Tests: vitest + jest
  (418 + 248 passing at 5db08027). URL scheme `pregusta://`.
- Backend: separate Python API (`billing.py`, `billing_logic.py`,
  `subscription_logic.py`, `db.py`, `smoke.py`) on Postgres. Can cold-start
  ("Pregustà is waking up").
- Payments: Stripe Checkout + billing portal, access granted only by webhook.
  Apple IAP scaffolded; Apple developer account now live (see above).

## Monetization
- `FREE_SCAN_LIMIT = 5` per device, lifetime (never resets);
  `IP_FREE_SCAN_LIMIT = 25` per 24h. Scan rows are written before the model call.
- 6th scan hits a half-menu paywall ("Your menu, finished" / "Unlock this menu").
- Plans: **Trip Pass $2.99 / 14 days, non-renewing**; **Unlimited $3.99/month**.
- Checkout opens in Safari via `Linking.openURL` (no WebView, App Store 3.1.1
  US external-link rules) → `/v1/checkout/return` → `pregusta://checkout-return`.
- Access rule `db.paid_plan_sql()`:
  `status='active' AND (current_period_end IS NULL OR > now())`.
- Manage-pass endpoints: `GET /v1/subscription`, `/invoices` (last 12),
  `POST /v1/billing/portal`, `/cancel` (cancel_at_period_end only), `/resume`.
  Apple plans return `409 manage_in_apple`.
- Paid members get a numbered gold pass card (№ 0001 = founding member);
  unpaid state is a steel card.

## Brand / visual system
- Ground `#0A0A0C`, cream `#F5F0E8`, gold `#F5C64C`, danger `#E5484D`.
- Text: `TEXT_MUTED #8a8278` (5.2:1), `TEXT_DIM #877c72` (4.9:1),
  `TEXT_FAINT #827768` (4.5:1), `TEXT_TRACE #3a3630` decorative only.
  `TEXT_GHOST` removed. Guard test: `constants/textContrast.test.ts`.
- Fonts: Fredoka (display/wordmark), IBM Plex Sans/Mono, serif for engraving.
- Tone: honest, anti-dark-pattern (no guilt screen on cancel; respect
  reduce-motion; animation never blocks).

## First-run flow (11 screens)
Intro → dietary profile (skippable) → camera permission (upload fallback) →
camera (QR mode, "5 free scans") → wait screen (8 themed scenes) → results →
milestone mosaic after scan 3 → steel pass nudge on scans 4–5 → half-menu
wall on scan 6 → Stripe Checkout in Safari + "Checking with Stripe" →
Welcome ("RESERVED for [name]", gold card strike, "Welcome to the club.").

## Finished / shipped
- WCAG AA contrast fix across theme (commit 5db08027, 16 Sep).
- Full first-run flow, paywall, Stripe checkout + webhooks.
- Manage-your-pass screen and endpoints incl. cancel/resume (18 Sep).
- Stripe `current_period_end` writer fix for API 2025-03-31 (e558d6f in pregusta-api, 14 Sep).
- Support email falls back to a copyable address if the mail app won't open (18 Sep).
- As of 16 Sep, pending deploy: engraved pass Nº, "ready instantly" cached-menu line.

## Open — bugs / hardening
- **Prod data bug:** one device active since 4 Sep with NULL
  `current_period_end` = access forever. Repair the row, stop treating NULL as
  valid in `paid_plan_sql()`, add a `smoke.py` check.
- `past_due` cuts access instantly; add a bounded grace window.
- No notification when a pass ends.
- Lapsed payers get zero free scans forever; consider a few scans/month,
  Stripe `pause_collection`, or seasonal billing.
- QR codes pointing to JS-rendered or PDF menus fail (falls back to photo).
- Apple IAP: account is now live; RevenueCat product setup still to do.

## Open — proposed designs (not built; user to judge on device)
- **Intro:** "Two Ways to Open Pregustà" — Option A "menu in candlelight"
  (typographic foreign menu lines resolving to translation + flag + price)
  recommended. Drop logo glow, close empty space, keep "Try a sample".
- **Account screen:** full-width pass with legible Nº + "Manage your pass ›"
  (the must-do); 4 groups → 2 ("At the table", "What we keep"); help as footer.
- **Your Pass screen:** Apple-Wallet-style restructure — fix title clipped by
  ✕, remove duplicate №, stats band, PLAN / RECEIPTS / MEMBERSHIP groups.
- **Resume/cancel motion:** A "The strike" for resume, C "The cool" for cancel
  (gold cools to 45%, never grey) recommended.
- **Help:** after 2nd identical failure offer prefilled "Still stuck?";
  Help row in ☰ menu; app-help mode in Ask Pregustà; written help sheet.
  Today only billing/restore failures offer "Email us".

## Loose ends from past sessions
- "Gold card issue" (16–19 Sep): the dim question is resolved (☰ dim 42%,
  0f696ae). The sample-row/menu-length question may still be open.
- "Session transcript export" (13–16 Sep, archived): its head 2833d1e **is on
  main**, so those commits did get pushed. Its 6 open items are most likely
  the ones in FOR-FEROZE.md.
- "Pregusta from phone" (19–23 Sep): last task "Reading theme constants";
  its environment was deleted, so it can't be resumed. Check that machine for
  unpushed work.

## Artifacts (design notes)
- Reading Pregustà in the Dark — https://claude.ai/artifact/W9rBn59K2jNrAJWgvbwUVR
- The Account Screen, Rethought — https://claude.ai/artifact/4oX6RdNCMAp9eYqi51LgJ7
- Eleven Screens to a Pass — https://claude.ai/artifact/UUDWqE5UqtLhhUu9UbMPBu
- The First Screen Deserves Better — https://claude.ai/artifact/283vSofjuukWfB4w6yNPuh
- Two Ways to Open Pregustà — https://claude.ai/artifact/1aHFScwpFgDX4yViEWm3Wq
- The Money Path — https://claude.ai/artifact/Ti9Gh9LtyEVmaK1EZJLWAy
- Where Help Runs Out — https://claude.ai/artifact/HpsnCbcNHXkxPWHt9j1u5p
- Two Moments — https://claude.ai/artifact/5ikT8VEJmFUy1A7JoDjnrw
- Your Pass, Restructured — https://claude.ai/artifact/Ee8UE6GF3a4u4Mm4ZKNyGR

## Relation to Rag-Lab
Rag-Lab uses Pregusta-style menu data as a safe playground for a RAG pipeline
(Voyage embeddings → pgvector on Supabase → Claude). Next step there is to
swap `data/pregusta_menu_sample.json` for a real parsed-menu export.
