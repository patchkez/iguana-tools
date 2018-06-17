The `.ini` configuration file is not supported yet, you need to configure on the script's code itself.

Ask me to update the `coins.json` file if it's outdated.

#### Pre-requisite:
All of your daemons must be running and synched and using the same rpc user and password.

#### First time run:
You can use _init_iguana.py_ script to import the private key to all daemons, then stop _iguana_, send your funds to yourself ([Agama](https://www.atomicexplorer.com/wallet/#/) is useful for this), then start _iguana_ again, and finally run `init_iguana.py` again.
It might comply about utxos. That's because your also need to install and use `recharge.py` to take care of utxos.

### Usage:
```
./init_iguana.py <your_passphrase>
```
