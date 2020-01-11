from django.core.cache import cache
from django.conf import settings
from rest_framework import status
from django.http import HttpResponse


class IdempotencyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST':

            ival = request.META.get('HTTP_X_IDEMPOTENCY_KEY')
            if ival is not None:
                ival = ival[:128]
                key = 'idemp-{}-{}'.format(request.user.pk, ival)

                is_idempotent = bool(cache.add(key, 'yes', settings.IDEMPOTENCY_TIMEOUT))
                if not is_idempotent:
                    return HttpResponse(
                        f'Error:Duplicate request (non-idempotent): {key}',
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        response = self.get_response(request)
        return response
