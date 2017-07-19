
from web3utils.hex import is_empty_hex

from ens import abis

REGISTRAR_NAME = 'eth'

GAS_DEFAULT = {
    'bid': 500000,
    'reveal': 150000,
    'finalize': 120000,
    }

START_GAS_CONSTANT = 25000
START_GAS_MARGINAL = 39000

class Registrar:
    """
    Terminology:
        Name: a fully qualified ENS name, for example: 'tickets.eth'
        Label: a label that the registrar auctions, for example: 'tickets'

    The registrar does not directly manage subdomains multiple layers down, like: 'fotc.tickets.eth'
    """

    def __init__(self, ens):
        self.ens = ens
        self.web3 = ens.web3
        self._coreContract = ens._contract(abi=abis.AUCTION_REGISTRAR)
        # delay generating this contract so that this class can be created before web3 is online
        self._core = None
        self._deedContract = ens._contract(abi=abis.DEED)

    def entries(self, name):
        label = self._to_label(name)
        label_hash = self.web3.sha3(label, encoding='bytes')
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
        labels = [self._to_label(name) for name in names]
        label_hashes = [self.web3.sha3(label, encoding='bytes') for label in labels]
        return self.core.startAuctions(label_hashes, **modifier_dict)

    def bid(self, name, amount, secret, **modifier_dict):
        """
        @param amount (in wei) to bid
        @param secret you MUST keep a copy of this to avoid burning your entire bid
        """
        if not modifier_dict:
            modifier_dict = {'transact': {}}
        if 'transact' in modifier_dict:
            self.__default_gas(modifier_dict['transact'], 'reveal')
        # Enforce that sending account must be specified, to create the sealed bid
        modifier_vals = modifier_dict[list(modifier_dict).pop()]
        if 'from' not in modifier_vals:
            raise ValueError("You must specify the sending account when creating a bid")
        label = self._to_label(name)
        bid_hash = self._bid_hash(label, modifier_vals['from'], amount, secret)
        return self.core.newBid(bid_hash, **modifier_dict)

    def reveal(self, name, value, secret, **modifier_dict):
        if not modifier_dict:
            modifier_dict = {'transact': {}}
        if 'transact' in modifier_dict:
            self.__default_gas(modifier_dict['transact'], 'reveal')
        label = self._to_label(name)
        label_hash = self.web3.sha3(label, encoding='bytes')
        secret_hash = self.web3.sha3(secret, encoding='bytes')
        return self.core.unsealBid(label_hash, value, secret_hash, **modifier_dict)
    unseal = reveal

    def finalize(self, name, **modifier_dict):
        if not modifier_dict:
            modifier_dict = {'transact': {}}
        if 'transact' in modifier_dict:
            self.__default_gas(modifier_dict['transact'], 'finalize')
        label_hash = self.web3.sha3(name, encoding='bytes')
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
        last_block = self.web3.eth.getBlock('latest')
        return last_block.gasLimit

    def _bid_hash(self, label, bidder, bid_amount, secret):
        label_hash = self.web3.sha3(label, encoding='bytes')
        secret_hash = self.web3.sha3(secret, encoding='bytes')
        return self.core.shaBid(label_hash, bidder, bid_amount, secret_hash)

    def _to_label(self, name):
        label = name
        if '.' in label:
            pieces = label.split('.')
            if len(pieces) < 2:
                raise TypeError(
                        "You must specify a label, like 'tickets' "
                        "or a fully-qualified name, like 'tickets.eth'")
            if pieces[-1] != REGISTRAR_NAME:
                raise TypeError("This registrar only manages names under .%s " % REGISTRAR_NAME)
            label = pieces[-2]
        return label
