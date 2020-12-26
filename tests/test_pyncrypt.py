#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `pyncrypt` package."""

import pytest


from pyncrypt import pyncrypt


VALLST = ["feefifofum", "1Y#⁄€Ü—&bw!", "mechaLechahiMECKAHINIEho"]


@pytest.fixture(scope="module", params=VALLST)
def onetimevault(request):
    """Create a one-time vault for testing purposes."""
    vault = pyncrypt.KeyStore()
    vault.store(key="foobar", value=request.param)
    yield vault
    vault.destroy()


def test_retrieve(onetimevault, key="foobar"):
    """Retrieve a key-value pair from the vault."""
    vault = onetimevault
    assert vault.retrieve(key) in VALLST


def test_require(onetimevault, key="foobar"):
    """Retrieve a key-value pair from the vault."""
    vault = onetimevault
    assert vault.require(key) in VALLST
