from core.extensions.authentication import AscenderAuthenticationFramework


def use_authentication():
    """
    ## Authentication Provider Hook

    Authentication Provider hook can be called from any places of code
    Hook was made to access the framework authentication provider.
    Authentication provider can be set in bootstrap.py and can be also customized.
    Authentication provider allows developers to make operations related to authentication system.
    For example: Authenticating users, getting information about users, accessing hashing functions and etc.

    Returns:
        AuthenticationProvider: type[BaseAuthenticationProvider]
    """

    return AscenderAuthenticationFramework.auth_provider

# This is shorter alias for method use_authentication()
use_auth = use_authentication