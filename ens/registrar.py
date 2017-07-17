
from web3utils.hex import is_empty_hex

from ens import abis

REGISTRAR_NAME = 'eth'

class Registrar:

    def __init__(self, ens):
        self.ens = ens
        self._coreContract = ens._contract(abi=abis.AUCTION_REGISTRAR)
        # delay generating this contract so that this class can be created before web3 is online
        self._core = None
        self._deedContract = ens._contract(abi=abis.DEED)

    @property
    def core(self):
        if not self._core:
            self._core = self._coreContract(self.ens.owner(REGISTRAR_NAME))
        return self._core

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
        entries = self.core.entries(label_hash)
        entries[1] = None if is_empty_hex(entries[1]) else self._deedContract(entries[1])
        return entries
