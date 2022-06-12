from typing import Sequence, Mapping

from django.core.signing import Signer, BadSignature
from rest_framework.request import Request
from rest_framework.response import Response


class AllowOrderMixin:
    def dispatch(self, request: Request, *args: Sequence, **kwargs: Mapping) -> Response:
        signer = Signer()
        pk = kwargs['pk']
        try:
            signer.unsign(request.session[f'order_{pk}'])
        except BadSignature:
            message = 'Sorry, but we can recognize your request. Please try again'
            return Response({'message': message}, status=401)

        return super().dispatch(request, *args, **kwargs)
