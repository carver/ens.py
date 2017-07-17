from web3 import Web3

from web3utils import web3
from web3utils.contracts import EthContractSugar
from web3utils.hex import EMPTY_SHA

from ens import abis
from ens.registrar import Registrar

ENS_MAINNET_ADDR = '0x314159265dd8dbb310642f98f50c066173c1259b'

REVERSE_REGISTRAR_DOMAIN = '.addr.reverse'

class ENS:

    def __init__(self, addr=None, custom_web3=None):
        self.web3 = custom_web3 if custom_web3 else web3
        ens_addr = addr if addr else ENS_MAINNET_ADDR
        self._contract = EthContractSugar(self.web3.eth.contract)
        self.ens = self._contract(abi=abis.ENS, address=ens_addr)
        self._resolverContract = self._contract(abi=abis.RESOLVER)
        self.registrar = Registrar(self)

    def resolve(self, name_string, lookup='addr'):
        resolver = self.resolver(name_string)
        if resolver:
            lookup_function = getattr(resolver, lookup)
            return lookup_function(self.namehash(name_string))
        else:
            return None

    def reverse(self, address):
        reversed_domain = self.reverse_domain(address)
        return self.resolve(reversed_domain, lookup='name')

    def namehash(self, name):
        node = EMPTY_SHA
        if name:
            labels = name.split(".")
            for label in reversed(labels):
                labelhash = self.web3.sha3(label, encoding='bytes')
                node = self.web3.sha3(node + labelhash[2:])
        return node

    def resolver(self, name_string):
        resolver_addr = self.ens.resolver(self.namehash(name_string))
        if not resolver_addr:
            return None
        return self._resolverContract(address=resolver_addr)

    def reverser(self, target_address):
        reversed_domain = self.reverse_domain(target_address)
        return self.resolver(reversed_domain)

    def owner(self, full_name):
        node = self.namehash(full_name)
        return self.ens.owner(node)

    def _reverse_node(self, address):
        domain = self.reverse_domain(address)
        return self.namehash(domain)

    @staticmethod
    def reverse_domain(address):
        if address.startswith('0x'):
            address = address[2:]
        address = address.lower()
        return address + REVERSE_REGISTRAR_DOMAIN
