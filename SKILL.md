---
name: rental-space-revenue
description: Aggregate monthly rental-space revenue on a usage-date basis from connected email and uploaded CSV/PDF statements. Use for platform/space totals, reservation-ID reconciliation, changes, extensions, cancellations, duplicate notifications, fees, and net proceeds across services such as Instabase, SpaceMarket, Yoyappin, and Kashikashi.
---

# Rental-space revenue reconciliation

Produce a traceable monthly report in which every recognized amount is tied to a platform reservation ID or a clearly labeled statement-level fee.

Use the mailbox, file-reading, spreadsheet, and code-execution tools available in the current agent environment. Do not depend on product-specific tool names, so the same skill can run in Codex or Claude.

## Required preflight and questions

1. Before searching, verify that a mail search/read capability exists and that the intended mailbox is actually connected. In Codex, use a harmless profile or read-only mailbox check; do not treat the mere presence of a Gmail tool as proof of connection. In Claude, perform the equivalent connector or MCP check.
2. If mail access is unavailable, unauthenticated, or points to an uncertain account, stop the email portion and tell the user exactly what must be connected or confirmed. Offer exported reservation emails as an alternative input. Never imply that email was checked when it was not.
3. A target year and month is mandatory. If the user has not specified it, ask “What year and month of usage revenue should I aggregate?” before searching any source. Do not choose the current or previous month automatically. Relative requests such as “last month” are sufficient when they resolve unambiguously in the user's timezone.
4. Before calculating, ask the user for any other missing fact that can materially change the result and cannot be established from source evidence. Typical blockers include the timezone, accounts/spaces in scope, ambiguous store matches, unresolved cancellations/refunds, unclear cumulative-versus-incremental extensions, and reservation-specific fee terms. Do not silently guess.
5. Apply documented defaults only when the required classification is known, and disclose each estimate. If a reliable partial total can be produced while some items remain unresolved, separate confirmed and unresolved amounts and ask focused questions that identify the affected reservation IDs.

## Mailbox safety: strictly read-only

- Use only non-mutating mailbox operations needed to verify the account, search messages, read messages or threads, and read attachments.
- Never send or forward mail; create, edit, or send drafts; archive, move, trash, or delete messages; apply, remove, or create labels; mark messages read or unread; star messages; modify threads; or change mailbox settings.
- Do not use a mailbox write operation as a workaround, even if it appears harmless or convenient. This skill has no authority to modify email under any circumstance.
- If the available connector cannot complete the task without a write action, stop and tell the user. Never claim a read-only workflow was followed after invoking a mutating action.

## Scope and period

- Confirm the target year-month before searching, plus the timezone and accounts/spaces in scope. If the user says “last month,” use the immediately preceding completed month in the user’s timezone.
- Select reservations by their usage date. An August report includes usage starting in August regardless of when the booking email arrived. Do not use notification-received month as the default accounting basis; produce it only when explicitly requested.
- Search reservation notifications from 12 months before the target month’s first day through the latest available reconciliation date. This lookback captures bookings made far in advance. Then follow every candidate reservation forward for later changes, extensions, cancellations, refunds, or settlement updates.
- If the requested reporting period spans multiple months, use the requested usage-date range and keep the one-year pre-period notification lookback.
- Read connected mail strictly through the non-mutating operations defined above. Uploaded CSV/PDF statements are source documents, not templates to edit.

## Extraction and reconciliation

1. Search broadly by platform sender/domain and event subjects across the full lookback window. Include reservation confirmed/approved, extension, change request, change accepted, cancellation, refund, payout, and statement messages. Paginate bounded searches; do not stop at the first result page.
2. Normalize each notification to: platform, reservation ID, event type, received timestamp, usage start/end, space name, address, gross/customer amount, host-facing amount, cancellation fee, refund, and source message/file locator.
3. Group only by `(platform, reservation ID)`. Do not use guest name, subject, amount, or time alone as the primary key. Merge host/customer copies and exact duplicate notifications.
4. Apply events chronologically. Ignore unaccepted change requests. Use accepted changes. For cumulative extension totals, use the latest cumulative total; for incremental extensions, add the increment. Do not assume which form a platform uses—verify from the notification wording and amount progression.
5. For cancellations, recognize the final retained cancellation fee or gross less confirmed refund. If the final refund is unknown, exclude the amount from confirmed totals and flag it for review.
6. Preserve a notification audit trail so every final row can be traced to its source IDs.

Use `scripts/reconcile_reservations.py` when normalized event JSON is available.

## Fees and proceeds

Use this evidence order:

1. Actual settlement statement amounts.
2. Booking-specific fee or promotion explicitly shown for that reservation.
3. Account-specific contract terms supplied by the user.
4. Current official standard rate, including tax treatment.

Never apply a promotion to other reservations merely because it appears in the same month. For SpaceMarket, detect `お得意様割` in the same reservation’s accepted/current email and apply the configured 5% rate only to that reservation; use the normal configured rate otherwise. Keep the displayed/base rate and the effective tax-inclusive deduction rate distinct. Label estimates as estimates. “Fee-deducted gross profit” means recognized revenue minus platform/settlement fees; it does not include rent, utilities, cleaning, or other operating costs unless requested.

Read [platform-rules.md](references/platform-rules.md) when identifying platform events or fee treatment.

## Store matching

- Prefer exact address matches, then stable space/listing IDs, then distinctive normalized name tokens and known aliases.
- Allow different platform names to map to one store when the evidence is strong. Record the matched source names and basis.
- Keep uncertain rows as `未分類` or `要確認`; do not force a match.
- Keep statement-level transfer fees as common costs unless the user asks for an allocation method.
- Aggregate both by platform and by normalized space/store. Preserve the original platform listing name in detail so the mapping remains auditable.

## Kashikashi CSV/PDF

Run `scripts/parse_kashikashi.py SOURCE --output normalized.json` for a Kashikashi settlement CSV or PDF. Review warnings and reconcile the parsed sales, booking fees, transfer fees, and scheduled payout to the source totals before combining them with email-derived bookings.

Calculate Kashikashi only from an uploaded Kashikashi CSV or PDF. Do not use scheduling tools or other provisional sources as a substitute. If no Kashikashi statement was supplied, do not block the Instabase, SpaceMarket, or Yoyappin reconciliation, but clearly label the result as excluding Kashikashi and tell the user to upload the relevant Kashikashi CSV or PDF. Never estimate Kashikashi revenue or fees, and never report an all-platform grand total as complete while Kashikashi is expected but missing.

## Deliverable and checks

Create or update one workbook with:

- A usage-date summary by platform and by normalized space/store, with revenue, fees, and fee-deducted proceeds.
- Reservation-ID detail showing status, recognized revenue, fee source/rate, fee, and fee-deducted proceeds.
- A notification/source audit trail.
- Assumptions and unresolved items, including exact booking IDs.

Reconcile detail to platform totals, store totals, and any statement payout. Check duplicate IDs, blank IDs, formula errors, period boundaries, and cancellations. Explicitly state remaining uncertainties and ask the user to resolve any item that materially affects the result before calling it final.

## Public distribution

Keep the skill repository free of customer names, email addresses, reservation IDs, addresses, raw email bodies, credentials, generated reports, sales figures, and settlement documents. Do not commit sample booking or settlement datasets, even when synthetic. When preparing a public GitHub release, read [public-release.md](references/public-release.md). Do not publish or create a public repository without an explicit user request.
