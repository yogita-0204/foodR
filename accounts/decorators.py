from functools import wraps

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


ROLE_COLLEGE_USER = "college_user"
ROLE_SHOP_OWNER = "shop_owner"


def get_user_role(user):
    profile = getattr(user, "profile", None)
    return getattr(profile, "role", None)


def user_has_role(user, roles):
    if user.is_superuser or user.is_staff:
        return True
    return get_user_role(user) in roles


def role_required(roles):
    allowed_roles = tuple(roles)

    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if user_has_role(request.user, allowed_roles):
                return view_func(request, *args, **kwargs)

            return HttpResponseForbidden("You do not have access to this page.")

        return wrapper

    return decorator


def shop_owner_required(view_func):
    return role_required([ROLE_SHOP_OWNER])(view_func)


def college_user_required(view_func):
    return role_required([ROLE_COLLEGE_USER])(view_func)
