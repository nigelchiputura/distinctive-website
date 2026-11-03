# Contact form emails refused: sender on an unverified domain

> **Worked example, not a real error.** Kept permanently to show the format
> (`../../Errors_And_Exceptions.md` §6).

- **Logged:** 2026-01-01 00:00 (first encountered)
- **Environment:** VPS preview
- **Layer/Area:** Email
- **Severity:** High
- **Phase / day / card:** Phase 1 · Day 10 · Deploy to the VPS preview host

## What I was trying to do

Submit the contact form on the preview host after the first deploy, to check that an enquiry
reaches `enquiries@distinctive.co.zw`.

## Exact error / stack trace

The page showed "Thank you, we'll be in touch". Nothing arrived in the mailbox. The container
log had:

```text
WARNING apps.contact.services.contact_service: enquiry 3 saved; email failed:
anymail.exceptions.AnymailRequestsAPIError: Resend API response 403:
{"name":"validation_error","message":"The website.localhost domain is not verified."}
```

The admin listed the submission with **Email sent: No**.

## Steps to reproduce

1. Deploy with `EMAIL_PROVIDER=resend` and `RESEND_API_KEY` set, but without
   `DEFAULT_FROM_EMAIL` in the server's `.env`.
2. Submit the contact form.
3. Check the mailbox and `docker compose logs web`.

## Initial suspected cause

The Resend API key was created with the wrong permission, or the DNS records for the sending
domain hadn't propagated yet.
