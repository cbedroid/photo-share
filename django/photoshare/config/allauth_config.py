# **************************************#
# ****** Authentication Settings ****** #
# **************************************#

# --- Urls Configuration --#
# https://django-allauth.readthedocs.io/en/latest/forms.html

ACCOUNT_FORMS = {
    "login": "users.forms.UserLoginForm",
    "signup": "users.forms.UserSignUpForm",
    "add_email": "allauth.account.forms.AddEmailForm",
    "change_password": "allauth.account.forms.ChangePasswordForm",
    "set_password": "allauth.account.forms.SetPasswordForm",
    "reset_password": "allauth.account.forms.ResetPasswordForm",
    "reset_password_from_key": "allauth.account.forms.ResetPasswordKeyForm",
    "disconnect": "allauth.socialaccount.forms.DisconnectForm",
}

# ***************************** #
# ---------- ADAPTERS --------- #
# ***************************** #

# --- Sign Up Configuration --#
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_USERNAME_MIN_LENGTH = 3
ACCOUNT_USERNAME_MAX_LENGTH = 60
ACCOUNT_PRESERVE_USERNAME_CASING = True

# allow user to sign in with either username or email
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_USERNAME_BLACKLIST = [
    "admin",
    "administrator",
    "owner",
    "photoshare",
    "techsupport",
    "moderator",
    "staff",
]

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "optional"  # "mandatory", "optional", or "none".
ACCOUNT_EMAIL_CONFIRMATION_HMAC = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True

# This is ignored when ACCOUNT_EMAIL_CONFIRMATION_HMAC = True
ACCOUNT_EMAIL_CONFIRMATION_COOLDOWN = 60 * 3
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = "account_login"
ACCOUNT_EMAIL_SUBJECT_PREFIX = " "

# See  https://django-allauth.readthedocs.io/en/latest/configuration.html
# TODO: Delete non-primary email after a given period ... not decided yet, but it's something to keep in mind
ACCOUNT_MAX_EMAIL_ADDRESSES = 2


# Protection from brute force attack -
# Note that this ONLY fires AFTER a user is locked out due to too many failed attempts
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 60 * 5
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5

# It is crucial that this is set to "False" to prevent malicious attacks on login users
# See explanation here - https://django-allauth.readthedocs.io/en/latest/views.html#logout-account-logout
ACCOUNT_LOGOUT_ON_GET = False
