"""manage.py onboard_user EMAIL [--first NAME] [--last NAME] [--group NAME] [--no-email]

Creates a staff user in the Content Editor group and emails them a set-password link
(docs/users.md §7). With --no-email, or if the email fails, the link is printed instead so it can
be passed on by hand (for example before the Resend domain is verified).
"""

from django.core.management.base import BaseCommand, CommandError

from apps.core.exceptions import ValidationError
from apps.users.permissions import CONTENT_EDITOR
from apps.users.services.user_service import UserService


class Command(BaseCommand):
    help = "Create a staff user and send them a link to set their password."

    def add_arguments(self, parser):
        parser.add_argument("email")
        parser.add_argument("--first", default="", help="First name")
        parser.add_argument("--last", default="", help="Last name")
        parser.add_argument("--group", default=CONTENT_EDITOR, help=f"Default: {CONTENT_EDITOR}")
        parser.add_argument("--no-email", action="store_true", help="Print the link instead")

    def handle(self, *args, **opts):
        try:
            result = UserService().onboard_user(
                opts["email"],
                first_name=opts["first"],
                last_name=opts["last"],
                group=opts["group"],
                send_email=not opts["no_email"],
            )
        except ValidationError as exc:
            raise CommandError("; ".join(m for msgs in exc.errors.values() for m in msgs)) from exc

        user = result.user
        self.stdout.write(self.style.SUCCESS(f"Created {user.email} (group: {opts['group']})."))
        if result.email_sent:
            self.stdout.write(f"A set-password link was emailed to {user.email}.")
        else:
            if not opts["no_email"]:
                self.stdout.write(self.style.WARNING("The email could not be sent (see the log)."))
            self.stdout.write("Send them this set-password link (it works once):")
            self.stdout.write(result.set_password_link)
