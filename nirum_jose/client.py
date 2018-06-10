import io
import json
import logging
from typing import Any, Mapping, Sequence, Tuple, Union
import urllib.request

from jose.jws import sign
from nirum.exc import UnexpectedNirumResponseError
from nirum.transport import Transport

__all__ = 'SigningHttpTransport',


class SigningHttpTransport(Transport):

    logger = logging.getLogger(f'{__name__}.SigningHttpTransport')

    def __init__(self, url: str, secret: str, algorithm: str) -> None:
        self.url = url
        self.secret = secret
        self.algorithm = algorithm

    def call(
        self,
        method_name: str,
        payload: Any,
        service_annotations: Mapping[str, Union[str, int, None]],
        method_annotations: Mapping[str, Union[str, int, None]],
        parameter_annotations: Mapping[
            str,
            Mapping[str, Union[str, int, None]]
        ]
    ) -> Tuple[bool, Any]:
        logger = self.logger.getChild('call')
        signed_payload = sign(
            {'_method': method_name, **payload},
            self.secret,
            algorithm=self.algorithm
        )
        request = urllib.request.Request(
            self.url,
            data=signed_payload,
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/jose',
            },
        )
        logger.debug(
            'An HTTP request for %s():\n%s %s\n%s\n\n%s',
            method_name, request.get_method(), request.full_url,
            request.headers, request.data
        )
        response = urllib.request.urlopen(request)
        try:
            content = json.load(
                io.TextIOWrapper(response, 'utf-8')  # type: ignore
            )
        except ValueError:
            response.seek(0)
            raise UnexpectedNirumResponseError(response.read().decode())
        status = response.status  # type: ignore
        return 200 <= status < 400, content
