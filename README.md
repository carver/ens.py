
## Ethereum Name Service

Access the Ethereum Name Service using this python library. Note: **this is a work in progress**

#### Look up information

Get a name, defaulting to .eth:

```
import ens

eth_address = ens.resolve('tickets.eth')

assert ens.resolve('tickets') == eth_address 
```


Find the name for an address:

```
domain = ens.reverse('0xfdb33f8ac7ce72d7d4795dd8610e323b4c122fbb')
```


Find the owner of a name:

```
eth_address = ens.owner('exchange.eth')
```

#### FAQ

*Why might the owner be different than the resolved name?*

The owner is like an administrator for the name, and the administrator might direct it elsewhere.
This might even be common for anything other than personal addresses.
