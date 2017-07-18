
import pytest

from web3utils import web3

from ens import ens

TEST_NAME = 'arachnid.eth'
TEST_NAME_2 = 'jasoncarver.eth'


def test_reverse():
    assert ens.reverse(ens.resolve(TEST_NAME)) == TEST_NAME

def test_contract_equality():
    assert ens.resolver(TEST_NAME) == ens.resolver(TEST_NAME)
    assert ens.resolver(TEST_NAME) != ens.resolver(TEST_NAME_2)

@pytest.mark.parametrize(
    'name,deed_addr',
    [
        ('arachnid.eth', '0xb1c10e0a6c5342105c82763202cebab4f1472102'),
        ('jasoncarver.eth', '0x7cce8bf2e68c463dc69ec34e0a0a5dad14f28a97'),
    ])
def test_registry_entries(name, deed_addr):
    entries = ens.registrar.entries(name)
    assert entries[:2] == [
            2,
            web3.eth.contract(address=deed_addr),
            ]
    assert entries[1].owner() == ens.owner(name)
    # ^ this isn't true for all names, just for the selected tests
