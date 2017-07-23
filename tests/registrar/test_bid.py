
import pytest
from web3 import Web3

from ens.registrar import BidTooLow

def test_bid_requires_from(registrar, name1, secret1):
    with pytest.raises(TypeError):
        registrar.bid(name1, 1, secret1)

def test_bid_nameprep(registrar, mocker, fake_hash, fake_hash_utf8, value1, secret1, addr1):
    mocker.patch.object(registrar.web3, 'sha3', side_effect=fake_hash)
    mocker.patch.object(registrar.core, 'shaBid')
    mocker.patch.object(registrar.core, 'newBid')
    registrar.bid("Öbb.eth", value1, secret1, transact={'from': addr1})
    registrar.core.shaBid.assert_called_once_with(
            fake_hash_utf8("öbb"),
            addr1,
            value1,
            fake_hash_utf8(secret1),
            )

def test_bid_hash(registrar, mocker, fake_hash, fake_hash_utf8, label1, value1, secret1, addr1):
    mocker.patch.object(registrar.web3, 'sha3', side_effect=fake_hash)
    mocker.patch.object(registrar.ens, 'labelhash', side_effect=fake_hash_utf8)
    mocker.patch.object(registrar.core, 'shaBid')
    mocker.patch.object(registrar.core, 'newBid')
    registrar.bid(label1, value1, secret1, transact={'from': addr1})
    registrar.core.shaBid.assert_called_once_with(
            fake_hash_utf8(label1),
            addr1,
            value1,
            fake_hash_utf8(secret1),
            )

def test_bid_convert_to_label(registrar, mocker, fake_hash, fake_hash_utf8, hash1, value1, secret1, addr1):
    mocker.patch.object(registrar.web3, 'sha3', side_effect=fake_hash)
    mocker.patch.object(registrar.core, 'shaBid')
    mocker.patch.object(registrar.core, 'newBid')
    registrar.bid('fullname.eth', value1, secret1, transact={'from': addr1})
    registrar.core.shaBid.assert_called_once_with(
            b"HASH(bfullname)",
            addr1,
            value1,
            fake_hash_utf8(secret1),
            )

def test_new_bid(registrar, mocker, hashbytes1, value1, addr1):
    mocker.patch.object(registrar.core, 'shaBid', return_value=hashbytes1)
    mocker.patch.object(registrar.core, 'newBid')
    registrar.bid('', value1, '', transact={'from': addr1})
    registrar.core.newBid.assert_called_once_with(
            hashbytes1,
            transact={'from': addr1, 'gas': 500000, 'value': value1})

# I'm hoping this is a bug in web3 that will be fixed eventually
# I would expect a Solidity contract that returns bytes32 to return a python `bytes`
def test_new_bid_web3_returning_string(registrar, mocker, hash1, value1, addr1):
    mocker.patch.object(
            registrar.core,
            'shaBid',
            return_value='+jZuWõt/è6*á\rGqK\x9b\x88C*\x14B¸Ün\x18\x14\t´\x11Ýå')
    mocker.patch.object(registrar.core, 'newBid')
    registrar.bid('', value1, '', transact={'from': addr1})
    registrar.core.newBid.assert_called_once_with(
            b'+jZuW\xf5t/\xe86*\xe1\rGqK\x9b\x88C*\x14B\xb8\xdcn\x18\x14\t\xb4\x11\xdd\xe5',
            transact={'from': addr1, 'gas': 500000, 'value': value1})

def test_min_bid(registrar, mocker, value1, addr1):
    with pytest.raises(BidTooLow):
        underbid = Web3.toWei('0.01', 'ether') - 1
        registrar.bid('', underbid, '', transact={'from': addr1})
