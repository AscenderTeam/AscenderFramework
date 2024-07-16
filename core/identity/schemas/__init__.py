from .basic import IdentityBasicScheme
from .oauth2 import IdentityOAuth2Scheme

def get_scheme(scheme_name: str, *scheme_args, **scheme_kargs) -> IdentityBasicScheme | IdentityOAuth2Scheme:
    return {
        "basic": IdentityBasicScheme,
        "oauth2": IdentityOAuth2Scheme
    }.get(scheme_name, "basic")(*scheme_args, **scheme_kargs)