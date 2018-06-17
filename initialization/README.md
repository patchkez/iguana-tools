#### Pre-requisite:
All of your daemons must be running and synched and using the same rpc user and password.

#### Dependencies:
* `python3`
* `requests` library (`pip3 install requests`)

#### Configuration:
The `.ini` configuration file is not supported yet, you need to configure on the script's code itself.

#### First time run:
You can configure `init_iguana.py` to rescan the blockchain after importing private keys. But it takes a lot of time, specially for KMD and BTC. It's disabled by default in `init_iguana.py`.

A more convenient method is: 
1. Use `init_iguana.py` script to import the private key to all daemons,
2. then stop _iguana_,
3. send your funds to yourself ([Agama](https://www.atomicexplorer.com/wallet/#/) is useful for this) for each chain,
4. then start _iguana_ again,
5. and finally run `init_iguana.py` again for normal start.

#### Recharge:
_Iguana_ might comply about utxos. That's because you also need to install and use [`recharge.py`](https://github.com/emmnx/iguana-tools/tree/master/recharge) to take care of utxos.

### Usage:
```
./init_iguana.py <your_passphrase>
```

_Note: Ask me to update the `coins.json` file if it's outdated._
