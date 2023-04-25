from re import sub

from django.conf import settings
from django.contrib.sites.models import Site
from django.http import Http404

from django.utils.deprecation import MiddlewareMixin
from rest_framework.authtoken.models import Token


class DynamicSiteDomainMiddleware(MiddlewareMixin):
    """
    Middleware that sets `site` attribute to request object.
    """

    def __call__(self, request):
        try:
            if '/admin/' not in request.META['PATH_INFO']:
                if 'HTTP_ORIGIN' in request.META:
                    current_site = Site.objects.get(
                        domain=request.META['HTTP_ORIGIN'])
                    header_token = request.META.get('HTTP_AUTHORIZATION', None)
                    if header_token is not None:
                        try:
                            token = sub('Token ', '', request.META.get(
                                'HTTP_AUTHORIZATION', None))
                            token_obj = Token.objects.get(key=token)
                            request.user = token_obj.user
                            if request.user.site != current_site:
                                raise Http404
                        except Token.DoesNotExist:
                            pass
                    request.site = current_site
                    settings.SITE_ID = current_site.id
        except Site.DoesNotExist:
            raise Http404
        response = self.get_response(request)
        return response
