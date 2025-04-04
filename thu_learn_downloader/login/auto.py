from . import bitwarden


def username() -> str:
    try:
        username_bitwarden: str = bitwarden.username()
        if username_bitwarden:
            return username_bitwarden
    except Exception:
        pass
    return ""


def password() -> str:
    try:
        password_bitwarden: str = bitwarden.password()
        if password_bitwarden:
            return password_bitwarden
    except Exception:
        pass
    return ""
