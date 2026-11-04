"""The two enquiry forms (docs/frontend.md §4): Contact's "Get In Touch!" and the gold
"Get In Touch With Us" block on Services. Both feed ContactService.submit.

The honeypot is not a form field: ContactController checks the raw `website` value before the
form is validated, so a bot that fills it gets a success reply and nothing is saved.
"""

from typing import Any, ClassVar

from django import forms

HONEYPOT_FIELD = "website"

MESSAGE_MAX = 5000


def _text(label: str, max_length: int, autocomplete: str, required_msg: str) -> forms.CharField:
    return forms.CharField(
        label=label,
        max_length=max_length,
        error_messages={"required": required_msg},
        widget=forms.TextInput(attrs={"autocomplete": autocomplete}),
    )


def _email() -> forms.EmailField:
    return forms.EmailField(
        label="Email Address",
        max_length=254,
        error_messages={
            "required": "Please enter your email address.",
            "invalid": "Please enter a valid email address, like name@example.com.",
        },
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )


def _message() -> forms.CharField:
    return forms.CharField(
        label="Message",
        max_length=MESSAGE_MAX,
        error_messages={
            "required": "Please enter your message.",
            "max_length": f"Please keep your message under {MESSAGE_MAX:,} characters.",
        },
        widget=forms.Textarea(attrs={"rows": 6}),
    )


class EnquiryBaseForm(forms.Form):
    """Shared behaviour: Bootstrap classes, error wiring for screen readers, unique ids."""

    kind: ClassVar[str] = ""
    half_width: ClassVar[frozenset[str]] = frozenset()  # fields shown two to a row from md up

    def __init__(self, *args: Any, **kwargs: Any):
        kwargs.setdefault("auto_id", f"{self.kind}-%s")
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "form-control")
            field.widget.attrs["aria-describedby"] = f"{self.kind}-{name}-error"

    def full_clean(self) -> None:
        super().full_clean()
        for name in self.errors:
            if name in self.fields:
                self.fields[name].widget.attrs["aria-invalid"] = "true"

    def for_service(self) -> dict[str, str]:
        """The cleaned values as ContactService.submit expects them."""
        raise NotImplementedError

    def errors_for_json(self) -> dict[str, list[str]]:
        return {name: [str(e) for e in errors] for name, errors in self.errors.items()}


class ContactForm(EnquiryBaseForm):
    kind = "contact"
    half_width = frozenset({"name", "email"})

    name = _text("Name", 160, "name", "Please enter your name.")
    email = _email()
    message = _message()

    def for_service(self) -> dict[str, str]:
        data = self.cleaned_data
        return {"name": data["name"], "email": data["email"], "message": data["message"]}


class EnquiryForm(EnquiryBaseForm):
    kind = "enquiry"
    half_width = frozenset({"first_name", "last_name"})

    first_name = _text("First Name", 80, "given-name", "Please enter your first name.")
    last_name = _text("Last Name", 80, "family-name", "Please enter your last name.")
    email = _email()
    message = _message()

    def for_service(self) -> dict[str, str]:
        data = self.cleaned_data
        name = f"{data['first_name'].strip()} {data['last_name'].strip()}"
        return {"name": name, "email": data["email"], "message": data["message"]}
