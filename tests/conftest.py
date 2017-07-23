
import pytest
from unittest.mock import Mock

from web3.providers.tester import EthereumTesterProvider
from web3utils import web3 as REAL_WEB3

from ens import ENS

def mkhash(num, digits=40):
    return '0x' + str(num) * digits

@pytest.fixture
def addr1():
    return mkhash(1)

@pytest.fixture
def addr2():
    return mkhash(2)

@pytest.fixture
def addr9():
    return mkhash(9)

@pytest.fixture
def addrbytes1():
    return b'\x11' * 20

@pytest.fixture
def hash1():
    return mkhash(1, digits=64)

@pytest.fixture
def hash9():
    return mkhash(9, digits=64)

@pytest.fixture
def name1():
    return 'dennis.the.peasant'

@pytest.fixture
def label1():
    return 'peasant'

@pytest.fixture
def label2():
    return 'dennis'

@pytest.fixture
def value1():
    return 1000000000000000000000002

@pytest.fixture
def secret1():
    return 'SUCH_SAFE_MUCH_SECRET'

@pytest.fixture
def ens():
    web3 = REAL_WEB3
    web3.setProvider(EthereumTesterProvider())
    web3 = Mock(wraps=REAL_WEB3)
    return ENS(web3)

@pytest.fixture
def registrar(ens, monkeypatch, addr9):
    monkeypatch.setattr(ens, 'owner', lambda namehash: addr9)
    return ens.registrar

@pytest.fixture
def fake_hash():
    def _fake_hash(tohash, encoding=None):
        if type(tohash) == bytes and not encoding:
            encoding = 'bytes'
        assert encoding == 'bytes'
        if isinstance(tohash, str):
            tohash = tohash.encode('utf-8')
        tohash = b'b'+tohash
        return b'HASH(%s)' % tohash
    return _fake_hash

@pytest.fixture
def fake_hash_utf8(fake_hash):
    return lambda name: fake_hash(name, encoding='bytes')
