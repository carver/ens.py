
from web3utils.hex import is_empty_hex

from ens import abis

REGISTRAR_NAME = 'eth'

GAS_DEFAULT = {
    'reveal': 150000,
    'finalize': 120000,
    }

START_GAS_CONSTANT = 25000
START_GAS_MARGINAL = 40000

class Registrar:

    def __init__(self, ens):
        self.ens = ens
        self._coreContract = ens._contract(abi=abis.AUCTION_REGISTRAR)
        # delay generating this contract so that this class can be created before web3 is online
        self._core = None
        self._deedContract = ens._contract(abi=abis.DEED)

    def entries(self, label):
        if '.' in label:
            pieces = label.split('.')
            if len(pieces) < 2: 
                raise TypeError(
                        "entries() takes a label directly, like 'tickets' "
                        "or a fully-qualified name, like 'tickets.eth'")
            if pieces[-1] != REGISTRAR_NAME:
                raise TypeError("This registrar only manages names under .%s " % REGISTRAR_NAME)
            label = pieces[-2]
        label_hash = self.ens.web3.sha3(label, encoding='bytes')
        return self.entries_by_hash(label_hash)

    def start(self, names, **modifier_dict):
        if not names:
            return
        if not modifier_dict:
            modifier_dict = {'transact': {}}
        if 'transact' in modifier_dict:
            transact_dict = modifier_dict['transact']
            if 'gas' not in transact_dict:
                transact_dict['gas'] = START_GAS_CONSTANT + START_GAS_MARGINAL * len(names) 
            if transact_dict['gas'] > self.__last_gaslimit():
                raise ValueError('There are too many auctions to fit in a block -- start fewer.')
        name_hashes = [self.web3.sha3(name, encoding='bytes') for name in names]
        return self.core.startAuctions(name_hashes, **modifier_dict)

    def reveal(self, name, value, secret, **modifier_dict):
        if not modifier_dict:
            modifier_dict = {'transact': {}}
        if 'transact' in modifier_dict:
            self.__default_gas(modifier_dict['transact'], 'reveal')
        label_hash = self.ens.web3.sha3(name, encoding='bytes')
        secret_hash = self.ens.web3.sha3(secret, encoding='bytes')
        return self.core.unsealBid(label_hash, value, secret_hash, **modifier_dict)
    unseal = reveal

    def finalize(self, name, **modifier_dict):
        if not modifier_dict:
            modifier_dict = {'transact': {}}
        if 'transact' in modifier_dict:
            self.__default_gas(modifier_dict['transact'], 'finalize')
        label_hash = self.ens.web3.sha3(name, encoding='bytes')
        return self.core.finalizeAuction(label_hash, **modifier_dict)

    def entries_by_hash(self, label_hash):
        entries = self.core.entries(label_hash)
        entries[1] = None if is_empty_hex(entries[1]) else self._deedContract(entries[1])
        return entries

    @property
    def core(self):
        if not self._core:
            self._core = self._coreContract(self.ens.owner(REGISTRAR_NAME))
        return self._core

    def __default_gas(self, transact_dict, action):
        if 'gas' not in transact_dict:
            transact_dict['gas'] = GAS_DEFAULT[action]

    def __last_gaslimit(self):
        last_block = self.ens.web3.eth.getBlock('latest')
        return last_block.gasLimit
