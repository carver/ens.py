
# Ethereum Name Service via Python

[![Join the chat at https://gitter.im/ens-py/Lobby](https://badges.gitter.im/ens-py/Lobby.svg)](https://gitter.im/ens-py/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Access the Ethereum Name Service using this python library. Note: **this is a work in progress**

Using this library is not a way to skip learning how ENS works. If you are registering a name, a
small misunderstanding can cause you to lose **all** your deposit.
Go [read about ENS](http://docs.ens.domains/en/latest/userguide.html) first.
Your funds are your responsibility.

## Beta-quality warning

This is a preview for developers, and an invitation for contributions. Please do not use this in
production until this warning is removed, especially when putting funds at risk. Examples of funds
being at risk include: sending ether/tokens to resolved addresses and participating in name
auctions.

If you supply the a domain with type `bytes`, it will be assumed to be UTF-8 encoded, like in
[Ethereum contracts](https://github.com/ethereum/wiki/wiki/Ethereum-Contract-ABI#argument-encoding).

## Setup

```
pip install ens
```

Any issues? See [Setup details](#setup-details)

## Usage

All examples in Python 3

### Name info

#### Get address from name

Default to {name}.eth:

```
from ens import ens


# look up the hex representation of the address for a name

eth_address = ens.address('jasoncarver.eth')

assert eth_address == '0x5b2063246f2191f18f2675cedb8b28102e957458'


# ens.py will assume you want a .eth name if you don't specify a full name

assert ens.address('jasoncarver') == eth_address
```

#### Get name from address

```
domain = ens.name('0x5b2063246f2191f18f2675cedb8b28102e957458')


# name() also accepts the bytes version of the address

assert ens.name(b'[ c$o!\x91\xf1\x8f&u\xce\xdb\x8b(\x10.\x95tX') == domain


# confirm that the name resolves back to the address that you looked up:

assert ens.address(domain) == '0x5b2063246f2191f18f2675cedb8b28102e957458'
```

#### Get owner of name

```
eth_address = ens.owner('exchange.eth')
```

### Set up your name

#### Point your name to your address

Do you want to set up your name so that `ens.address()` will show the address it points to?

```
ens.setup_address('jasoncarver.eth', '0x5b2063246f2191f18f2675cedb8b28102e957458')
```
You must already be the owner of the domain (or its parent).

In the common case where you want to point the name to the owning address, you can skip the address
```
ens.setup_address('jasoncarver.eth')
```

You can claim arbitrarily deep subdomains. *Gas costs scale up with the number of subdomains!*
```
ens.setup_address('supreme.executive.power.derives.from.a.mandate.from.the.masses.jasoncarver.eth')
```

Wait for the transaction to be mined, then:
```
assert ens.address('supreme.executive.power.derives.from.a.mandate.from.the.masses.jasoncarver.eth') == \
    '0x5b2063246f2191f18f2675cedb8b28102e957458'
```

#### Point your address to your name

Do you want to set up your address so that `ens.name()` will show the name that points to it?

This is like Caller ID. It enables you and others to take an account and determine what name points
to it. Sometimes this is referred to as "reverse" resolution.

```
ens.setup_name('jasoncarver.eth', '0x5b2063246f2191f18f2675cedb8b28102e957458')
```

If you don't supply the address, `setup_name` will assume you want the address returned by
`ens.address(name)`.
```
ens.setup_name('jasoncarver.eth')
```
If the name doesn't already point to an address, `ens.setup_name` will call `ens.setup_address` for
you.

Wait for the transaction to be mined, then:
```
assert ens.name('0x5b2063246f2191f18f2675cedb8b28102e957458') == 'jasoncarver.eth'
```

### Auctions for names ending in .eth

#### Get auction status

Example with domain 'payment.eth':

```
from ens.registrar import Status


status = ens.registrar.status('payment')


# if you forget to strip out .eth, ens.py will do it for you

assert ens.registrar.status('payment.eth') == status


# these are the possible statuses

assert status in (
  Status.Open,
  Status.Auctioning,
  Status.Owned,
  Status.Forbidden,
  Status.Revealing,
  Status.NotYetAvailable
  )


# if you get the integer status from another source, you can compare it directly

assert Status.Owned == 2
```

#### Start auctions

```
# start one auction (which tips people off that you're interested)

ens.registrar.start('you_saw_him_repressin_me_didnt_ya')


# start many auctions (which provides a bit of cover)

ens.registrar.start(['exchange', 'tickets', 'payment', 'trading', 'registry'])
```

#### Bid on auction

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

#### Reveal your bid

You must **always** reveal your bid, whether you won or lost.
Otherwise you will lose the full deposit.

Example of revealing your bid on 'registry.eth' with 0.01 ETH, and secret
"For real, though: losing your secret means losing ether":

```
ens.registrar.reveal(
      'registry',
      web3.toWei('0.01', 'ether'),
      "For real, though: losing your secret means losing ether",
      transact={'from': web3.eth.accounts[0]}
      )
```

#### Claim the name you won

aka "Finalize" auction, which makes you the owner in ENS.

```
ens.registrar.finalize('gambling')
```

#### Get detailed information on an auction

Find out the owner of the auction Deed --
see [docs on the difference](http://docs.ens.domains/en/latest/userguide.html#managing-ownership)
between owning the name and the deed

```
deed = ens.registrar.deed('ethfinex')

assert deed.owner() == '0x9a02ed4ca9ad55b75ff9a05debb36d5eb382e184'
```

When was the auction completed? (a timezone-aware datetime object)

```
close_datetime = ens.registrar.close_at('ethfinex')

assert str(close_datetime) == '2017-06-05 08:10:03+00:00'
```

How much is held on deposit?

```
from decimal import Decimal

deposit = ens.registrar.deposit('ethfinex')

assert web3.fromWei(deposit, 'ether') == Decimal('0.01')
```

What was the highest bid?

```
top_bid = ens.registrar.top_bid('ethfinex')

assert web3.fromWei(top_bid, 'ether') == Decimal('201709.02')
```

## Setup details

### Web3.py version

This library only works with v3.* of the web3.py library. v4.* of Web3.py comes with its own ens module, but no auction support. For auction support compatible with web3.py v4, see https://github.com/carver/ensauction.py

### If Python 2 is your default, or you're not sure

In your shell
```
if pip --version | grep "python 2"; then
  python3 -m venv ~/.py3venv
  source ~/.py3venv/bin/activate
fi
```

### Now, with Python 3

In your shell: `pip install ens`

*ens.py* requires an up-to-date Ethereum blockchain, preferably local. If your setup isn't working,
try running `geth --fast` until it's fully-synced. I highly recommend using the default IPC
communication method, for speed and security.

### "No matching distribution found for ens"

If you are seeing something like:
```
Collecting ens
  Could not find a version that satisfies the requirement ens (from versions: )
No matching distribution found for ens
```

Then retry the first Setup section, to make sure you're in Python 3

### Optionally, a custom web3 provider

In Python:

```
from ens import ENS
from web3 import IPCProvider 

ens = ENS(IPCProvider('/your/custom/ipc/path'))
```



## Developer Setup

```
git clone git@github.com:carver/ens.py.git
cd ens.py/

python3 -m venv venv
. venv/bin/activate

pip install -e .
pip install -r requirements-dev.txt
```

### Testing Setup

Re-run flake on file changes:

```
$ when-changed -s -1 -r ens/ tests/ -c "clear; echo; echo \"running flake - $(date)\"; warn()
{
notify-send -t 5000 'Flake8 failure ⚠⚠⚠⚠⚠' 'flake8 on ens.py failed'
}
if ! git diff | flake8 --diff | grep "\.py"; then if ! flake8 ens/ tests/; then warn; fi else warn; fi; echo done"
```

### Why does ens.py require python 3?

*Short version*

It turns out that the distinction between `str` and `bytes` is important. If
you want to write code for the future (Ethereum), don't use a language from the past.

*Long version*

Interacting with the EVM requires clarity on the bits you're using. For example, a sha3 hash expects
to receive a series of bytes to process. Calculating the sha3 hash of a string is (or should be)
a Type Error; the hash algorithm doesn't know what to do with
a series of characters, aka Unicode code points. As the caller, you need to know which thing you're
calculating the hash of:
1. a series of bytes: `b'[ c$o!\x91\xf1\x8f&u\xce\xdb\x8b(\x10.\x95tX'`
2. the bytes represented by a string in hex format: `'0x5b2063246f2191f18f2675cedb8b28102e957458'`
3. the bytes generated by encoding a string using utf-8: **Oops, the bytes from #1 cannot be read using utf-8!**
4. the bytes generated by encoding a string using utf-16: `'⁛④Ⅿ\uf191⚏칵诛ဨ键塴'`

Python 3 doesn't let you ignore a lot of these details. That's good, because precision in dealing
with the EVM is critical. Ether is at stake.

If you are resistant -- I get it, I've been there. It is not intuitive for most people. But it's
seriously worth it to [learn about
encoding](https://www.joelonsoftware.com/2003/10/08/the-absolute-minimum-every-software-developer-absolutely-positively-must-know-about-unicode-and-character-sets-no-excuses/) 
if you're going to develop on top of Ethereum. Your ETH depends on it!
