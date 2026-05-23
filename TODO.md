# TODO

## Auth

- [ ] **Password recovery.** `Forgot password?` on `/login` currently shows atoast. Needs:
  - Backend: `POST /api/auth/forgot-password` issues a single-use reset token; `POST /api/auth/reset-password` consumes it.
  - Frontend: `/reset-password?token=...` route with new-password form.
- [ ] **Two-factor authentication.** Stub UI in `/settings`. Needs TOTP enrollment endpoints + recovery codes + verify-on-login flow.
- [ ] **Active sessions / device list.** Stub UI in `/settings`. Needs a `sessions` table (refresh-token rotation), `GET /api/auth/sessions`, `DELETE /api/auth/sessions/:id`.
- [ ] **Change password.** Stub UI in `/settings`. Needs `POST /api/users/me/password` (re-verify old password, hash new one).

## Settings

- [ ] **Notification preferences.** Stub UI in `/settings`. Needs a `user_preferences` table (email opt-ins per category), wired into the Celery reminder/report tasks.
- [x] **Theme toggle (light/dark).** Stub UI in `/settings`. tokens already wired in `tailwind.css` — needs a Pinia store + persisted preference + `<html data-theme>` switch.
- [ ] **Density preference.** Stub UI. Compact vs. comfortable spacing for tables and forms.

## Marketplace

- [ ] **Ratings & reviews.** Customers should be able to rate professionals after a completed booking. Schema scaffolded but write path / display widget not wired.
- [ ] **Service categories filter.** Chip strip exists on `/home/browse`; filtering currently client-side only.
- [ ] **Search across services + professionals.** Global search box in the top bar.

## Operational

- [ ] **Email delivery in production.** Celery tasks log to stdout in the demo. Wire an SMTP / SES provider via env var.
- [ ] **Observability.** Structured logs + a basic health/metrics dashboard.
- [ ] **CSV export of bookings for customers/professionals.** Admin export exists; per-user export does not.

---
