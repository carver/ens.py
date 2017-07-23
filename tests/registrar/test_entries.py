
import pytest

from web3utils.hex import EMPTY_ADDR

from ens.registrar import Status

def test_status_passthrough(registrar, mocker, hash1, label1):
    status = object()
    mocker.patch.object(registrar, 'entries', return_value=[status, None, 0, 0, 0])
    assert registrar.status(label1) is status
    registrar.entries.assert_called_once_with(label1)

def test_entries_passthrough(registrar, mocker, hash1, label1):
    result = object()
    mocker.patch.object(registrar, 'entries_by_hash', return_value=result)
    mocker.patch.object(registrar.ens, 'labelhash', return_value=hash1)
    assert registrar.entries(label1) is result
    registrar.ens.labelhash.assert_called_once_with(label1)
    registrar.entries_by_hash.assert_called_once_with(hash1)

def test_entries_use_label(registrar, mocker, addr1, hash1):
    mocker.patch.object(registrar.ens, 'labelhash')
    mocker.patch.object(registrar, 'entries_by_hash')
    registrar.entries('grail.eth')
    registrar.ens.labelhash.assert_called_once_with('grail')

def test_entries_subdomain_meaningless(registrar, mocker, addr1, hash1):
    mocker.patch.object(registrar.web3, 'sha3')
    mocker.patch.object(registrar, 'entries_by_hash')
    with pytest.raises(ValueError):
        registrar.entries('holy.grail.eth')

def test_entries_status(registrar, mocker):
    NUM_ENTRIES_STATUSES = 6
    core_results = [[idx, EMPTY_ADDR, 0, 0, 0] for idx in range(NUM_ENTRIES_STATUSES)]
    mocker.patch.object(registrar.core, 'entries', side_effect=core_results)
    for idx in range(NUM_ENTRIES_STATUSES):
        entries = registrar.entries_by_hash(b'')
        assert entries[0] == Status(idx)
        assert entries[0] == idx

def test_entries_deed_contract(registrar, mocker, addr1):
    mocker.patch.object(registrar.core, 'entries', return_value=[0, addr1, 2, 3, 4])
    entries = registrar.entries_by_hash(b'')
    assert entries[1]._web3py_contract.address == addr1

def test_entries_empty_deed(registrar, mocker):
    mocker.patch.object(registrar.core, 'entries', return_value=[0, EMPTY_ADDR, 0, 0, 0])
    entries = registrar.entries_by_hash(b'')
    assert entries[1] is None

def test_entries_registration_time(registrar, mocker):
    mocker.patch.object(registrar.core, 'entries', return_value=[0, EMPTY_ADDR, 2 * 3600, 0, 0])
    entries = registrar.entries_by_hash(b'')
    assert str(entries[2]) == '1970-01-01 02:00:00+00:00'

def test_entries_registration_empty(registrar, mocker):
    mocker.patch.object(registrar.core, 'entries', return_value=[0, EMPTY_ADDR, 0, 0, 0])
    entries = registrar.entries_by_hash(b'')
    assert entries[2] is None

def test_entries_value_passthrough(registrar, mocker):
    mocker.patch.object(registrar.core, 'entries', return_value=[0, EMPTY_ADDR, 0, 1, 2])
    entries = registrar.entries_by_hash(b'')
    assert entries[-2:] == [1, 2]
