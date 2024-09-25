# Copyright (c) pallets/itsdangerous
# Copyright (C) 2024 Graz University of Technology.
# copy pasted over to invenio-base because of removable from itsdangerous with version 2.1.0
# https://raw.githubusercontent.com/pallets/itsdangerous/refs/tags/2.0.1/tests/test_itsdangerous/test_jws.py

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

from datetime import timedelta

import pytest
from itsdangerous.exc import (
    BadData,
    BadHeader,
    BadPayload,
    BadSignature,
    SignatureExpired,
)
from test_serializer import TestSerializer
from test_timed import TestTimedSerializer

from invenio_base.jws import JSONWebSignatureSerializer, TimedJSONWebSignatureSerializer


class TestJWSSerializer(TestSerializer):
    @pytest.fixture()
    def serializer_factory(self):
        def factory(secret_key="secret-key", **kwargs):
            return JSONWebSignatureSerializer(secret_key=secret_key, **kwargs)

        return factory

    test_signer_cls = None  # type: ignore
    test_signer_kwargs = None  # type: ignore
    test_fallback_signers = None  # type: ignore
    test_iter_unsigners = None  # type: ignore

    @pytest.mark.parametrize("algorithm_name", ("HS256", "HS384", "HS512", "none"))
    def test_algorithm(self, serializer_factory, algorithm_name):
        serializer = serializer_factory(algorithm_name=algorithm_name)
        assert serializer.loads(serializer.dumps("value")) == "value"

    def test_invalid_algorithm(self, serializer_factory):
        with pytest.raises(NotImplementedError) as exc_info:
            serializer_factory(algorithm_name="invalid")

        assert "not supported" in str(exc_info.value)

    def test_algorithm_mismatch(self, serializer_factory, serializer):
        other = serializer_factory(algorithm_name="HS256")
        other.algorithm = serializer.algorithm
        signed = other.dumps("value")

        with pytest.raises(BadHeader) as exc_info:
            serializer.loads(signed)

        assert "mismatch" in str(exc_info.value)

    @pytest.mark.parametrize(
        ("value", "exc_cls", "match"),
        (
            ("ab", BadPayload, '"."'),
            ("a.b", BadHeader, "base64 decode"),
            ("ew.b", BadPayload, "base64 decode"),
            ("ew.ab", BadData, "malformed"),
            ("W10.ab", BadHeader, "JSON object"),
        ),
    )
    def test_load_payload_exceptions(self, serializer, value, exc_cls, match):
        signer = serializer.make_signer()
        signed = signer.sign(value)

        with pytest.raises(exc_cls) as exc_info:
            serializer.loads(signed)

        assert match in str(exc_info.value)

    def test_secret_keys(self):
        serializer = JSONWebSignatureSerializer("a")

        dumped = serializer.dumps("value")

        serializer = JSONWebSignatureSerializer(["a", "b"])

        assert serializer.loads(dumped) == "value"


class TestTimedJWSSerializer(TestJWSSerializer, TestTimedSerializer):
    @pytest.fixture()
    def serializer_factory(self):
        def factory(secret_key="secret-key", expires_in=10, **kwargs):
            return TimedJSONWebSignatureSerializer(
                secret_key=secret_key, expires_in=expires_in, **kwargs
            )

        return factory

    def test_default_expires_in(self, serializer_factory):
        serializer = serializer_factory(expires_in=None)
        assert serializer.expires_in == serializer.DEFAULT_EXPIRES_IN

    test_max_age = None

    def test_exp(self, serializer, value, ts, freeze):
        signed = serializer.dumps(value)
        freeze.tick()
        assert serializer.loads(signed) == value
        freeze.tick(timedelta(seconds=10))

        with pytest.raises(SignatureExpired) as exc_info:
            serializer.loads(signed)

        assert exc_info.value.date_signed == ts
        assert exc_info.value.payload == value

    test_return_payload = None

    def test_return_header(self, serializer, value, ts):
        signed = serializer.dumps(value)
        payload, header = serializer.loads(signed, return_header=True)
        date_signed = serializer.get_issue_date(header)
        assert (payload, date_signed) == (value, ts)

    def test_missing_exp(self, serializer):
        header = serializer.make_header(None)
        del header["exp"]
        signer = serializer.make_signer()
        signed = signer.sign(serializer.dump_payload(header, "value"))

        with pytest.raises(BadSignature):
            serializer.loads(signed)

    @pytest.mark.parametrize("exp", ("invalid", -1))
    def test_invalid_exp(self, serializer, exp):
        header = serializer.make_header(None)
        header["exp"] = exp
        signer = serializer.make_signer()
        signed = signer.sign(serializer.dump_payload(header, "value"))

        with pytest.raises(BadHeader) as exc_info:
            serializer.loads(signed)

        assert "IntDate" in str(exc_info.value)

    def test_invalid_iat(self, serializer):
        header = serializer.make_header(None)
        header["iat"] = "invalid"
        assert serializer.get_issue_date(header) is None
