from django.contrib.auth.backends import ModelBackend, UserModel
from django.contrib.sites.models import Site


class CustomUserBackend(ModelBackend):
    """
    Custom user model backend.
    """

    def authenticate(self, request, email=None, username=None, password=None, **kwargs):

        if email is None:
            email = request._post.get('username')
        user = UserModel._default_manager.get_by_natural_key(email)
        if user.is_superuser:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        else:
            try:
                user = UserModel._default_manager.get(
                    email=email, site=Site.objects.get(
                        domain=request.META['HTTP_ORIGIN'])
                    )
            except UserModel.DoesNotExist:
                UserModel().set_password(password)
            else:
                if user.check_password(password) and self.user_can_authenticate(user):
                    return user