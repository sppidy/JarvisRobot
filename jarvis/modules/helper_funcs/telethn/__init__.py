from jarvis import (
    telethn,
    SUDO_USERS,
    WHITELIST_USERS,
    SUPPORT_USERS,
    TECHY_USERS,
    DEV_USERS,
)

IMMUNE_USERS = SUDO_USERS + WHITELIST_USERS + SUPPORT_USERS + TECHY_USERS + DEV_USERS

IMMUNE_USERS = (
    list(SUDO_USERS)
    + list(WHITELIST_USERS)
    + list(SUPPORT_USERS)
    + list(TECHY_USERS)
    + list(DEV_USERS)
)
