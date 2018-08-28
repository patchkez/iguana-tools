# recharge.py install

As root:
```
apt install python3
pip3 install requests
cd /opt
git clone https://github.com/emmnx/iguana-tools.git
cd iguana-tools/recharge
cp recharge.ini.example recharge.ini
cp cron.recharge.iguana /etc/cron.d/rechargeiguana
service cron reload
vim recharge.ini
```
You can configure default parameters for all coins (under the "DEFAULT" label) or individually (under each coin label.)

Specify `rpcuser` and `rpcpassword` for each (or all) coin(s). 

For assetchains, you can instead specify the directory where all the assetchains read their configurations from, so that the script will take those values from there (generally `/home/<user>/.komodo`, and yes, _recharge.py_ will iterate through the coin folders.)

You can test it now:
```
/opt/iguana-tools/recharge/recharge.py
```

The installed _cron_ file will take care of running the script every 10 minutes.
