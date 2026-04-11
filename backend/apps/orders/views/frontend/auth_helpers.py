from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated


def bypass_user_auth_enabled() -> bool:
    return bool(getattr(settings, "TEST_BYPASS_USER_AUTH", False))


def frontend_order_permissions():
    if bypass_user_auth_enabled():
        return [AllowAny()]
    return [IsAuthenticated()]


def resolve_order_user(request):
    if request.user and request.user.is_authenticated:
        return request.user

    if not bypass_user_auth_enabled():
        return request.user

    user_model = get_user_model()
    field_names = {f.name for f in user_model._meta.fields}

    email = getattr(settings, "TEST_GUEST_USER_EMAIL", "guest@test.local")
    username = getattr(settings, "TEST_GUEST_USER_USERNAME", email)

    lookup = {}
    if "username" in field_names:
        lookup["username"] = username
    elif "email" in field_names:
        lookup["email"] = email
    else:
        # 兜底：如果没有 username/email 字段，直接返回当前匿名对象
        return request.user

    user = user_model.objects.filter(**lookup).first()
    if user:
        return user

    create_kwargs = dict(lookup)
    if "email" in field_names:
        create_kwargs.setdefault("email", email)
    if "first_name" in field_names:
        create_kwargs.setdefault("first_name", "Test")
    if "last_name" in field_names:
        create_kwargs.setdefault("last_name", "Guest")

    if hasattr(user_model.objects, "create_user"):
        user = user_model.objects.create_user(password=None, **create_kwargs)
    else:
        user = user_model.objects.create(**create_kwargs)
        if hasattr(user, "set_unusable_password"):
            user.set_unusable_password()
            user.save(update_fields=["password"])

    return user
