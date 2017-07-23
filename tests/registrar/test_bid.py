
import pytest
from web3 import Web3


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

def test_new_bid(registrar, mocker, hash1, value1, addr1):
    mocker.patch.object(registrar.core, 'shaBid', return_value=hash1)
    mocker.patch.object(registrar.core, 'newBid')
    registrar.bid('', value1, '', transact={'from': addr1})
    registrar.core.newBid.assert_called_once_with(hash1, transact={'from': addr1, 'gas': 500000})

def test_min_bid(registrar, mocker, value1, addr1):
    with pytest.raises(ValueError):
        underbid = Web3.toWei('0.01', 'ether') - 1
        registrar.bid('', underbid, '', transact={'from': addr1})
