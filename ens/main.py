
import idna
from web3utils import web3, STRING_ENCODING
from web3utils.hex import EMPTY_SHA3_BYTES

from ens import abis
from ens.registrar import Registrar

DEFAULT_TLD = 'eth'
RECOGNIZED_TLDS = [DEFAULT_TLD, 'reverse']

ENS_MAINNET_ADDR = '0x314159265dd8dbb310642f98f50c066173c1259b'

REVERSE_REGISTRAR_DOMAIN = '.addr.reverse'


class ENS:

    def __init__(self, custom_web3=None, addr=None):
        '''
        if you pass a custom_web3, make sure it is web3utils-style web3
        '''
        self.web3 = custom_web3 if custom_web3 else web3
        assert hasattr(self.web3.eth, 'original_contract')
        self._contract = self.web3.eth.contract

        ens_addr = addr if addr else ENS_MAINNET_ADDR
        self.ens = self._contract(abi=abis.ENS, address=ens_addr)
        self._resolverContract = self._contract(abi=abis.RESOLVER)
        self.registrar = Registrar(self)

    def address(self, name):
        return self.resolve(name, 'addr')

    def name(self, address):
        reversed_domain = self.reverse_domain(address)
        return self.resolve(reversed_domain, get='name')
    reverse = name

    def resolve(self, name, get='addr'):
        resolver = self.resolver(name)
        if resolver:
            lookup_function = getattr(resolver, get)
            return lookup_function(self.namehash(name))
        else:
            return None

    def namehash(self, name):
        name = self._full_name(name)
        node = EMPTY_SHA3_BYTES
        if name:
            labels = name.split(".")
            for label in reversed(labels):
                labelhash = self.labelhash(label)
                assert type(labelhash) == bytes
                assert type(node) == bytes
                node = self.web3.sha3(node + labelhash)
        return node

    def resolver(self, name):
        name = self._full_name(name)
        resolver_addr = self.ens.resolver(self.namehash(name))
        if not resolver_addr:
            return None
        return self._resolverContract(address=resolver_addr)

    def reverser(self, target_address):
        reversed_domain = self.reverse_domain(target_address)
        return self.resolver(reversed_domain)

    def owner(self, name):
        node = self.namehash(name)
        return self.ens.owner(node)

    def labelhash(self, label):
        prepped = self.nameprep(label)
        label_bytes = prepped.encode(STRING_ENCODING)
        return self.web3.sha3(label_bytes)

    @staticmethod
    def nameprep(name):
        if not name:
            return name
        return idna.decode(name, uts46=True, std3_rules=True)

    def _reverse_node(self, address):
        domain = self.reverse_domain(address)
        return self.namehash(domain)

    @staticmethod
    def _full_name(name):
        if isinstance(name, (bytes, bytearray)):
            name = str(name, encoding=STRING_ENCODING)
        pieces = name.split('.')
        if pieces[-1] not in RECOGNIZED_TLDS:
            pieces.append(DEFAULT_TLD)
        return '.'.join(pieces)

    def reverse_domain(self, address):
        if isinstance(address, (bytes, bytearray)):
            address = self.web3.toHex(address)
        if address.startswith('0x'):
            address = address[2:]
        address = address.lower()
        return address + REVERSE_REGISTRAR_DOMAIN
