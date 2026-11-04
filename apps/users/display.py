"""How allauth names a user in messages ("Successfully signed in as …"): their email, which is
what they sign in with. The username is internal (docs/users.md §1)."""


def user_display(user) -> str:
    return user.email
