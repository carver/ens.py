
## Ethereum Name Service via Python

[![Join the chat at https://gitter.im/ens-py/Lobby](https://badges.gitter.im/ens-py/Lobby.svg)](https://gitter.im/ens-py/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Access the Ethereum Name Service using this python library. Note: **this is a work in progress**

Using this library is not a way to skip learning how ENS works. A small misunderstanding can cause
you to lose **all** your deposit. Go [read about ENS](http://docs.ens.domains/en/latest/userguide.html) first. Your funds are your responsibility.

### Alpha-quality warning

This is a preview for developers, and an invitation for contributions. Please do not use this in
production until this warning is removed, especially when putting funds at risk. Examples of funds
being at risk include: sending ether/tokens to resolved addresses and participating in name
auctions.

The [nameprep algorithm](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-137.md#name-syntax)
is not well tested, please be cautious and double-check the result through another channel. If you
supply the name in `bytes`, it will be assumed to be UTF-8 encoded, like in
[Ethereum contracts](https://github.com/ethereum/wiki/wiki/Ethereum-Contract-ABI#argument-encoding).
Currently, several of the convenience methods only split on '.' and not other similar dot
characters, as defined in ut-46.


### Look up information

Look up a name, defaulting to .eth:

```
from ens import ens


# look up the hex representation of the address for a name

eth_address = ens.resolve('jasoncarver.eth')


# ens.py will assume you want a .eth name if you don't specify a full name

assert ens.resolve('jasoncarver') == eth_address
```


Find the name for an address:

```
domain = ens.reverse('0xfdb33f8ac7ce72d7d4795dd8610e323b4c122fbb')


# reverse() also accepts the bytes version of the address

assert ens.reverse(b'\xfd\xb3?\x8a\xc7\xcer\xd7\xd4y]\xd8a\x0e2;L\x12/\xbb') == domain


# confirm that the name resolves back to the address that you looked up:

assert ens.resolve(domain) == '0xfdb33f8ac7ce72d7d4795dd8610e323b4c122fbb'
```


Find the owner of a name:

```
eth_address = ens.owner('exchange.eth')
```

### Auctions for names ending in .eth

Look up auction status for the domain 'payment.eth':

```
from ens.registrar import Status


status = ens.registrar.status('payment')


# if you forget to strip out .eth, ens.py will do it for you

assert ens.registrar.status('payment.eth') == status


# these are the possible statuses

assert status in (
  Status.Open,
  Status.Auction,
  Status.Owned,
  Status.Forbidden,
  Status.Reveal,
  Status.NotYetAvailable
  )


# if you get the integer status from another source, you can compare it directly

assert Status.Owned == 2
```

Start auctions:

```
# start one auction (which tips people off that you're interested)

ens.registrar.start('you_saw_him_repressin_me_didnt_ya')


# start many auctions (which provides a bit of cover)

ens.registrar.start(['exchange', 'tickets', 'payment', 'trading', 'registry'])
```

Bid on a 'trading.eth' with 5211 ETH, and secret "I promise I will not forget my secret":

```
from web3utils import web3

ens.registrar.bid(
      'trading',
      web3.toWei('5211', 'ether'),
      "I promise I will not forget my secret",
      transact={'from': web3.eth.accounts[0]}
      )
```
(if you want to "mask" your bid, set a higher value in the transact dict)

Reveal your bid on a 'registry.eth' with 0.01 ETH, and secret
"For real, though: losing your secret means losing ether":

```
ens.registrar.reveal(
      'registry',
      web3.toWei('0.01', 'ether'),
      "For real, though: losing your secret means losing ether",
      transact={'from': web3.eth.accounts[0]}
      )
```

Finalize an auction that you won:

```
ens.registrar.finalize('gambling')
```

Get various auction details:

```
entries = ens.registrar.entries('ethfinex')


# confirm the auction is closed

assert entries[0] == Status.Owned


# find out the owner of the name

assert entries[1].owner() == '0x9a02ed4ca9ad55b75ff9a05debb36d5eb382e184'


# when was the auction completed? (a timezone-aware datetime object)

assert str(entries[2]) == '2017-06-05 08:10:03+00:00'


# how much is held on deposit?

from decimal import Decimal

assert web3.fromWei(entries[3], 'ether') == Decimal('0.01')


# what was the highest bid?

assert web3.fromWei(entries[4], 'ether') == Decimal('201709.02')
```


### Developer Setup

```
python3 -m venv venv
. venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

#### Why does ens.py require python 3?

Because [web3utils requires python 3](https://github.com/carver/web3utils.py#why-is-python-3-required).
Plus, Ethereum is brand new. You shouldn't have any legacy
code that requires you to use a ~10-year-old python version.
