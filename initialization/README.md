The _.ini_ configuration file is not supported yet, you need to configure on the script's code itself.

Ask me to update the _coins.json_ file if it's outdated.

#### Pre-requisite:
all of your daemons must be running and synched.

You can use _init_iguana.py_ script to import the private key to all daemons, then stop _iguana_, send your funds to yourself (Agama is usefuls for this), and then start _iguana_ again, run _init_iguana.py_ again.

It might comply about utxos. You need to install and use _recharge.py_ to take care of utxos.



### Usage:
```
./init_iguana.py <your_passphrase>
```
