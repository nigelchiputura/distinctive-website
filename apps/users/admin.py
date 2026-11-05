"""User admin (docs/users.md §5, §7). Adding a user asks only for an email and a name: the user
gets no password, joins Content Editor by default, and is emailed a link to set their password.
The admin uses the ORM directly (a documented exception); the welcome email goes through
UserService so it matches `manage.py onboard_user`."""

from django import forms
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import ngettext

from apps.users.managers import UserManager
from apps.users.permissions import CONTENT_EDITOR
from apps.users.services.user_service import UserService

from .models import User


class AddUserForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text=f"{CONTENT_EDITOR} can edit the website's content but not users.",
    )

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "groups")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].help_text = "They sign in with this address."
        editor = Group.objects.filter(name=CONTENT_EDITOR).first()
        if editor and not self.is_bound:
            self.initial["groups"] = [editor.pk]


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    add_form = AddUserForm
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "first_name", "last_name", "groups")}),
    )
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Name", {"fields": ("first_name", "last_name")}),
        ("Access", {"fields": ("is_active", "is_staff", "is_superuser", "groups")}),
        ("History", {"fields": ("last_login", "date_joined", "username")}),
    )
    readonly_fields = ("last_login", "date_joined", "username")
    list_display = ("email", "first_name", "last_name", "is_staff", "is_active", "last_login")
    list_filter = ("is_active", "is_staff", "is_superuser", "groups")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    filter_horizontal = ()
    actions = ("deactivate_users", "send_set_password_link")

    def save_model(self, request, obj: User, form, change: bool) -> None:
        if not change:
            obj.email = obj.email.strip().lower()
            obj.username = UserManager.username_for(User, obj.email)
            obj.is_staff = True
            obj.set_unusable_password()
        super().save_model(request, obj, form, change)

    def response_add(self, request, obj: User, post_url_continue=None):
        result = UserService().welcome(obj)
        if result.email_sent:
            self.message_user(request, f"A set-password link was emailed to {obj.email}.")
        else:
            self.message_user(
                request,
                "The welcome email could not be sent. Send them this set-password link (it "
                f"works once): {result.set_password_link}",
                messages.WARNING,
            )
        return super().response_add(request, obj, post_url_continue)

    @admin.action(description="Deactivate the selected users (they can no longer sign in)")
    def deactivate_users(self, request, queryset):
        service = UserService()
        count = 0
        for user in queryset.exclude(pk=request.user.pk):
            service.deactivate(user)
            count += 1
        self.message_user(
            request, ngettext("%d user deactivated.", "%d users deactivated.", count) % count
        )

    @admin.action(description="Email the selected users a new set-password link")
    def send_set_password_link(self, request, queryset):
        service = UserService()
        for user in queryset.filter(is_active=True):
            result = service.welcome(user)
            if not result.email_sent:
                self.message_user(
                    request,
                    f"Couldn't email {user.email}. Their link: {result.set_password_link}",
                    messages.WARNING,
                )
        self.message_user(request, "Done.")
