# Platform parsing and fee rules

Use these as starting patterns. Email formats and contracts can change, so verify against current messages and official terms.

## Default fee assumptions

Use these only when a settlement statement or account-specific contract is unavailable. Keep them editable in the report.

| Platform / condition | Base rate | Effective deduction used |
| --- | ---: | ---: |
| Instabase time/person-unit plan | 35% | 35% |
| Instabase daily plan | 20% | 20% |
| SpaceMarket normal booking | 30% equivalent on tax-inclusive sales | 30% |
| SpaceMarket booking explicitly marked `お得意様割` | 5% | 5% |
| Yoyappin | 35% before tax | 38.5% including 10% tax on the fee |
| Kashikashi | Statement amount | Statement amount |

Do not infer a discounted or daily-plan rate from the space name alone. Tie it to the reservation or plan evidence.

## Instabase

- Primary key: `予約ID`.
- Typical events: reservation confirmed, extension reservation, reservation changed, cancellation.
- An extension may have a separate reservation ID. Keep it separate when the platform assigns one.
- Prefer a payout statement when present. Otherwise determine whether the plan is time/person-unit or daily before applying a standard rate.

## SpaceMarket

- Primary key: `予約ID`.
- A change request is not final until acceptance/confirmation is present.
- Extension emails commonly show a new cumulative total. Retain the latest cumulative total for the same ID after verifying the progression.
- If the same reservation’s accepted/current email explicitly includes `お得意様割`, apply the configured 5% discounted rate only to that reservation. Keep the message ID as evidence.
- Standard-rate and individual-contract bookings may coexist. Prefer settlement data over a modeled fee.

## Yoyappin

- Primary key: `予約No`.
- Customer and operator notifications may arrive as separate messages for the same booking. Merge them by reservation number.
- Customer total may include a customer-side charge and must not be mistaken for operator revenue.
- When terms state a 35% system fee plus consumption tax, record base fee 35% and effective deduction 38.5%. If an actual statement shows a different deduction, use the statement and flag the variance.
- A cancellation/refund reminder does not prove the final retained amount. Keep it unresolved until the refund result is known.

## Kashikashi

- Primary key: statement `予約ID`.
- Prefer the statement’s per-booking `売上`, `手数料`, and `支払金額` rather than recomputing them.
- Record `振込手数料` separately as a common fee. Verify: sum of booking payouts minus transfer fee equals scheduled payout.
- PDF and CSV statements can be normalized with `scripts/parse_kashikashi.py`.

## Cross-platform safeguards

- Scope reservation IDs by platform; identical numeric IDs across platforms are unrelated.
- Preserve identifiers as text.
- Round only where the platform rule requires it, and reconcile against a real statement whenever available.
- Report both recognized revenue and net proceeds. Do not label customer payment as host revenue without evidence.
