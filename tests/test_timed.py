# Copyright (c) pallets/itsdangerous
# Copyright (C) 2024 Graz University of Technology.
# copy pasted over to invenio-base because of removable from itsdangerous with version 2.1.0
# https://raw.githubusercontent.com/pallets/itsdangerous/refs/tags/2.0.1/tests/test_itsdangerous/test_timed.py

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


from datetime import datetime, timedelta, timezone
from functools import partial

import pytest
from freezegun import freeze_time
from itsdangerous.exc import BadTimeSignature, SignatureExpired
from itsdangerous.signer import Signer
from itsdangerous.timed import TimedSerializer, TimestampSigner
from test_serializer import TestSerializer
from test_signer import TestSigner


class FreezeMixin:
    @pytest.fixture()
    def ts(self):
        return datetime(2011, 6, 24, 0, 9, 5, tzinfo=timezone.utc)

    @pytest.fixture(autouse=True)
    def freeze(self, ts):
        with freeze_time(ts) as ft:
            yield ft


class TestTimestampSigner(FreezeMixin, TestSigner):
    @pytest.fixture()
    def signer_factory(self):
        return partial(TimestampSigner, secret_key="secret-key")

    def test_max_age(self, signer, ts, freeze):
        signed = signer.sign("value")
        freeze.tick()
        assert signer.unsign(signed, max_age=10) == b"value"
        freeze.tick(timedelta(seconds=10))

        with pytest.raises(SignatureExpired) as exc_info:
            signer.unsign(signed, max_age=10)

        assert exc_info.value.date_signed == ts

    def test_return_timestamp(self, signer, ts):
        signed = signer.sign("value")
        assert signer.unsign(signed, return_timestamp=True) == (b"value", ts)

    def test_timestamp_missing(self, signer):
        other = Signer("secret-key")
        signed = other.sign("value")

        with pytest.raises(BadTimeSignature) as exc_info:
            signer.unsign(signed)

        assert "missing" in str(exc_info.value)
        assert exc_info.value.date_signed is None

    def test_malformed_timestamp(self, signer):
        other = Signer("secret-key")
        signed = other.sign(b"value.____________")

        with pytest.raises(BadTimeSignature) as exc_info:
            signer.unsign(signed)

        assert "Malformed" in str(exc_info.value)
        assert exc_info.value.date_signed is None

    def test_malformed_future_timestamp(self, signer):
        signed = b"value.TgPVoaGhoQ.AGBfQ6G6cr07byTRt0zAdPljHOY"

        with pytest.raises(BadTimeSignature) as exc_info:
            signer.unsign(signed)

        assert "Malformed" in str(exc_info.value)
        assert exc_info.value.date_signed is None

    def test_future_age(self, signer):
        signed = signer.sign("value")

        with freeze_time("1971-05-31"):
            with pytest.raises(SignatureExpired) as exc_info:
                signer.unsign(signed, max_age=10)

        assert isinstance(exc_info.value.date_signed, datetime)

    def test_sig_error_date_signed(self, signer):
        signed = signer.sign("my string").replace(b"my", b"other", 1)

        with pytest.raises(BadTimeSignature) as exc_info:
            signer.unsign(signed)

        assert isinstance(exc_info.value.date_signed, datetime)


class TestTimedSerializer(FreezeMixin, TestSerializer):
    @pytest.fixture()
    def serializer_factory(self):
        return partial(TimedSerializer, secret_key="secret_key")

    def test_max_age(self, serializer, value, ts, freeze):
        signed = serializer.dumps(value)
        freeze.tick()
        assert serializer.loads(signed, max_age=10) == value
        freeze.tick(timedelta(seconds=10))

        with pytest.raises(SignatureExpired) as exc_info:
            serializer.loads(signed, max_age=10)

        assert exc_info.value.date_signed == ts
        assert serializer.load_payload(exc_info.value.payload) == value

    def test_return_payload(self, serializer, value, ts):
        signed = serializer.dumps(value)
        assert serializer.loads(signed, return_timestamp=True) == (value, ts)
