# Copyright (c) pallets/itsdangerous
# Copyright (C) 2024 Graz University of Technology.
# copy pasted over to invenio-base because of removable from itsdangerous with version 2.1.0
# https://github.com/pallets/itsdangerous/blob/2.0.1/src/itsdangerous/jws.py

# Original license
# Copyright 2011 Pallets

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:

# 1.  Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.

# 2.  Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.

# 3.  Neither the name of the copyright holder nor the names of its
#     contributors may be used to endorse or promote products derived from
#     this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""JWS functionality copy pasted from itsdangerous."""

import hashlib
import time
from datetime import datetime, timezone
from decimal import Decimal
from numbers import Real

from itsdangerous._json import _CompactJSON
from itsdangerous.encoding import base64_decode, base64_encode, want_bytes
from itsdangerous.exc import (
    BadData,
    BadHeader,
    BadPayload,
    BadSignature,
    SignatureExpired,
)
from itsdangerous.serializer import Serializer
from itsdangerous.signer import HMACAlgorithm, NoneAlgorithm


class JSONWebSignatureSerializer(Serializer):
    """Class JSONWebSignatureSerializer.

    This serializer implements JSON Web Signature (JWS) support.
    Only supports the JWS Compact Serialization.
    """

    jws_algorithms = {
        "HS256": HMACAlgorithm(hashlib.sha256),
        "HS384": HMACAlgorithm(hashlib.sha384),
        "HS512": HMACAlgorithm(hashlib.sha512),
        "none": NoneAlgorithm(),
    }

    #: The default algorithm to use for signature generation
    default_algorithm = "HS512"

    default_serializer = _CompactJSON

    def __init__(
        self,
        secret_key,
        salt=None,
        serializer=None,
        serializer_kwargs=None,
        signer=None,
        signer_kwargs=None,
        algorithm_name=None,
    ):
        """Construct."""
        super().__init__(
            secret_key,
            salt=salt,
            serializer=serializer,
            serializer_kwargs=serializer_kwargs,
            signer=signer,
            signer_kwargs=signer_kwargs,
        )

        if algorithm_name is None:
            algorithm_name = self.default_algorithm

        self.algorithm_name = algorithm_name
        self.algorithm = self.make_algorithm(algorithm_name)

    def load_payload(self, payload, serializer=None, return_header=False):
        """Load payload."""
        payload = want_bytes(payload)

        if b"." not in payload:
            raise BadPayload('No "." found in value')

        base64d_header, base64d_payload = payload.split(b".", 1)

        try:
            json_header = base64_decode(base64d_header)
        except Exception as e:
            raise BadHeader(
                "Could not base64 decode the header because of an exception",
                original_error=e,
            )

        try:
            json_payload = base64_decode(base64d_payload)
        except Exception as e:
            raise BadPayload(
                "Could not base64 decode the payload because of an exception",
                original_error=e,
            )

        try:
            header = super().load_payload(json_header, serializer=_CompactJSON)
        except BadData as e:
            raise BadHeader(
                "Could not unserialize header because it was malformed",
                original_error=e,
            )

        if not isinstance(header, dict):
            raise BadHeader("Header payload is not a JSON object", header=header)

        payload = super().load_payload(json_payload, serializer=serializer)

        if return_header:
            return payload, header

        return payload

    def dump_payload(self, header, obj):
        """Dump payload."""
        base64d_header = base64_encode(
            self.serializer.dumps(header, **self.serializer_kwargs)
        )
        base64d_payload = base64_encode(
            self.serializer.dumps(obj, **self.serializer_kwargs)
        )
        return base64d_header + b"." + base64d_payload

    def make_algorithm(self, algorithm_name):
        """Make algorithm."""
        try:
            return self.jws_algorithms[algorithm_name]
        except KeyError:
            raise NotImplementedError("Algorithm not supported")

    def make_signer(self, salt=None, algorithm=None):
        """Make signer."""
        if salt is None:
            salt = self.salt

        key_derivation = "none" if salt is None else None

        if algorithm is None:
            algorithm = self.algorithm

        return self.signer(
            self.secret_keys,
            salt=salt,
            sep=".",
            key_derivation=key_derivation,
            algorithm=algorithm,
        )

    def make_header(self, header_fields):
        """Make header."""
        header = header_fields.copy() if header_fields else {}
        header["alg"] = self.algorithm_name
        return header

    def dumps(self, obj, salt=None, header_fields=None):
        """Dumps.

        Like :meth:`.Serializer.dumps` but creates a JSON Web
        Signature. It also allows for specifying additional fields to be
        included in the JWS header.
        """
        header = self.make_header(header_fields)
        signer = self.make_signer(salt, self.algorithm)
        return signer.sign(self.dump_payload(header, obj))

    def loads(self, s, salt=None, return_header=False):
        """Loads.

        Reverse of :meth:`dumps`. If requested via ``return_header``
        it will return a tuple of payload and header.
        """
        payload, header = self.load_payload(
            self.make_signer(salt, self.algorithm).unsign(want_bytes(s)),
            return_header=True,
        )

        if header.get("alg") != self.algorithm_name:
            raise BadHeader("Algorithm mismatch", header=header, payload=payload)

        if return_header:
            return payload, header

        return payload

    def loads_unsafe(self, s, salt=None, return_header=False):
        """Loads unsafe."""
        kwargs = {"return_header": return_header}
        return self._loads_unsafe_impl(s, salt, kwargs, kwargs)


class TimedJSONWebSignatureSerializer(JSONWebSignatureSerializer):
    """Class TimedJSONWebSignatureSerializer.

    Works like the regular :class:`JSONWebSignatureSerializer` but
    also records the time of the signing and can be used to expire
    signatures.

    JWS currently does not specify this behavior but it mentions a
    possible extension like this in the spec. Expiry date is encoded
    into the header similar to what's specified in `draft-ietf-oauth
    -json-web-token <http://self-issued.info/docs/draft-ietf-oauth-json
    -web-token.html#expDef>`_.
    """

    DEFAULT_EXPIRES_IN = 3600

    def __init__(self, secret_key, expires_in=None, **kwargs):
        """Construct."""
        super().__init__(secret_key, **kwargs)

        if expires_in is None:
            expires_in = self.DEFAULT_EXPIRES_IN

        self.expires_in = expires_in

    def make_header(self, header_fields):
        """Make header."""
        header = super().make_header(header_fields)
        iat = self.now()
        exp = iat + self.expires_in
        header["iat"] = iat
        header["exp"] = exp
        return header

    def loads(self, s, salt=None, return_header=False):
        """Loads."""
        payload, header = super().loads(s, salt, return_header=True)

        if "exp" not in header:
            raise BadSignature("Missing expiry date", payload=payload)

        int_date_error = BadHeader("Expiry date is not an IntDate", payload=payload)

        try:
            header["exp"] = int(header["exp"])
        except ValueError:
            raise int_date_error

        if header["exp"] < 0:
            raise int_date_error

        if header["exp"] < self.now():
            raise SignatureExpired(
                "Signature expired",
                payload=payload,
                date_signed=self.get_issue_date(header),
            )

        if return_header:
            return payload, header

        return payload

    def get_issue_date(self, header):
        """Get issue date.

        If the header contains the ``iat`` field, return the date the
        signature was issued, as a timezone-aware
        :class:`datetime.datetime` in UTC.

        .. versionchanged:: 2.0
            The timestamp is returned as a timezone-aware ``datetime``
            in UTC rather than a naive ``datetime`` assumed to be UTC.
        """
        rv = header.get("iat")

        if isinstance(rv, (Real, Decimal)):
            return datetime.fromtimestamp(int(rv), tz=timezone.utc)

    def now(self):
        """Get now."""
        return int(time.time())
