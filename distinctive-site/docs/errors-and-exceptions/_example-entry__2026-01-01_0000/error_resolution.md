# Resolution — Contact form emails refused: sender on an unverified domain

> **Worked example, not a real error.**

- **Resolved:** 2026-01-01 00:40
- **Time to resolve:** about 40 minutes

## Confirmed root cause

`DEFAULT_FROM_EMAIL` was missing from the server's `.env`, so Django fell back to the dev
default `Distinctive Website <website@website.localhost>`. Resend only sends from verified
domains, so it refused every message with a 403. The key and the DNS records were fine.

The submission itself was safe: `ContactService.submit` saves before it sends, so the enquiry
was in the admin with `email_sent=False`.

## Fix applied (and why it works)

- Added `DEFAULT_FROM_EMAIL=Distinctive Website <website@mail.distinctive.co.zw>` to the VPS
  `.env` and ran `docker compose -f docker-compose.prod.yml up -d`.
- Re-sent the unsent enquiry with the admin action **Resend notification email**.

## Alternatives considered and rejected

- **Regenerating the Resend key:** the key worked; Resend's message named the domain, not the
  key.
- **Falling back to SMTP:** not needed, and the VPS provider may block SMTP ports anyway
  (`deployment.md` §6).

## Prevention (test / lint rule / check / doc)

- The system check `core.W001` warns at start-up when the sender isn't on a real domain, so it
  shows in `docker compose logs web` during `migrate` (`deployment.md` §6).
- `.env.prod.example` lists `DEFAULT_FROM_EMAIL` as required.
- The Day 10 deploy checklist has "submit the form; check the inbox **and** `Email sent: Yes`".

## What this taught me about the stack

A success page proves the save, not the send. Django's email settings fail quietly with defaults,
so every setting that must be real in production needs a start-up check, and logging has to be
configured to see warnings at all when `DEBUG` is off.
