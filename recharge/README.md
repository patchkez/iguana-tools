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
Change your `rpcuser` and `rpcpassword` and save the file. Or, you can specify the directory where all the assetchains read their configurations from, so that the script will take those values from there (generally `/home/<user>/.komodo`)

You can configure default parameters for all coins ("DEFAULT" label) or individually, under each coin label.

You can test it now:
```
/opt/iguana-tools/recharge/recharge.py
```

The installed _cron_ file will take care of running the script every 10 minutes.
