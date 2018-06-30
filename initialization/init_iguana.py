#!/usr/bin/env python3
import requests
import json
import pprint
import sys
import os
import configparser
import csv


# read configuration file
ENVIRON = 'PROD'
config = configparser.ConfigParser()
config.read('init_iguana.ini')

# configure pretty printer
pp = pprint.PrettyPrinter(width=41, compact=True)

# get list of notaries
notaries = []
for n in  config[ENVIRON]['notaries'].split(','):
    n = n.strip()
    notaries.append(n)

# what shall we rescan
rescan_ac = config[ENVIRON].getboolean('rescan_ac')
rescan_btc = config[ENVIRON].getboolean('rescan_btc')
rescan_kmd = config[ENVIRON].getboolean('rescan_ac')

# get connection options
conn = {}
connection_options = [
    'iguana_ip',
    'iguana_port',
    'bitcoind_ip',
    'bitcoind_port',
    'bitcoind_rpcuser',
    'bitcoind_rpcpassword',
    'komodod_ip',
    'komodod_port',
    'komodod_rpcuser',
    'komodod_rpcpassword',
    'assetchain_ip',
    'assetchain_rpcuser',
    'assetchain_rpcpassword']
for i in connection_options:
    conn[i] = config[ENVIRON][i]

# load coin definition file
with open('coins.json') as file:
    coins = json.load(file)


# define function that posts json data to iguana
def post_rpc(url, payload, auth=None):
    try:
        r = requests.post(url, data=json.dumps(payload), auth=auth)
        return(json.loads(r.text))
    except Exception as e:
        raise Exception("Couldn't connect to " + url + ": ", e)


# read passphrase from environment variable
try:
    passphrase = sys.argv[1]
except:
    print(
        "Error: no passphrase given.\n" +
        "Usage (include the spaces at the beginning, and " +
        "quotes enclosing the passphrase):\n" +
        "  " + sys.argv[0] + " 'this is my secret passphrase'\n")
    sys.exit(0)

# define url's
iguana_url = 'http://' + conn['iguana_ip'] + ':' + conn['iguana_port']
komodod_url = (
    'http://' +
    conn['komodod_ip'] + ':' +
    conn['komodod_port'])
bitcoind_url = (
    'http://' +
    conn['bitcoind_ip'] + ':' +
    conn['bitcoind_port'])

# define credentials
bitcoind_auth = (
    conn['bitcoind_rpcuser'],
    conn['bitcoind_rpcpassword'])
bitcoind_userpass = (
    conn['bitcoind_rpcuser'] + ':' +
    conn['bitcoind_rpcpassword'])
komodod_auth = (
    conn['komodod_rpcuser'],
    conn['komodod_rpcpassword'])
komodod_userpass = (
    conn['komodod_rpcuser'] + ':' +
    conn['komodod_rpcpassword'])
assetchain_auth = (
    conn['assetchain_rpcuser'],
    conn['assetchain_rpcpassword'])
assetchain_userpass = (
    conn['assetchain_rpcuser'] + ':' +
    conn['assetchain_rpcpassword'])

# add my ip
checkip_response = requests.get('http://checkip.amazonaws.com')
my_public_ip = checkip_response.text.strip()
myipaddr = {
    "agent": "SuperNET",
    "method": "myipaddr",
    "ipaddr": my_public_ip
}
response_myipaddr = post_rpc(iguana_url, myipaddr)
print('== response_myipaddr ==')
pp.pprint(response_myipaddr)

# add notaries
print('== response_addnotary ==')
for n in notaries:
    addnotary = {
        "agent": "iguana",
        "method": "addnotary",
        "ipaddr": n
    }
    response_addnotary = post_rpc(iguana_url, addnotary)
    pp.pprint(response_addnotary)

# addcoin method, BTCD and BTC
addcoin_BTCD = {
    "poll": 100,
    "active": 1,
    "agent": "iguana",
    "method": "addcoin",
    "newcoin": "BTCD",
    "startpend": 1,
    "endpend": 1,
    "services": 128,
    "maxpeers": 16,
    "RELAY": 0,
    "VALIDATE": 0,
    "portp2p": 14631,
    "rpc": 14632
}
response_addcoin_BTCD = post_rpc(iguana_url, addcoin_BTCD)
print('== response_addcoin_BTCD ==')
pp.pprint(response_addcoin_BTCD)
# BTC
addcoin_BTC = {
    "userpass": bitcoind_userpass,
    "prefetchlag": -1,
    "poll": 1,
    "active": 1,
    "agent": "iguana",
    "method": "addcoin",
    "newcoin": "BTC",
    "startpend": 64,
    "endpend": 64,
    "services": 0,
    "maxpeers": 512,
    "RELAY": -1,
    "VALIDATE": 0,
    "portp2p": 8333,
    "minconfirms": 1
}
response_addcoin_BTC = post_rpc(iguana_url, addcoin_BTC)
print('== response_addcoin_BTC ==')
pp.pprint(response_addcoin_BTC)


# The encryptwallet RPC encrypts the wallet with a passphrase.
# This is only to enable encryption for the first time.
# After encryption is enabled, you will need to enter the passphrase to use
# private keys.

encryptwallet = {
    "agent": "bitcoinrpc",
    "method": "encryptwallet",
    "passphrase": passphrase
}
response_encryptwallet = post_rpc(iguana_url, encryptwallet)

try:
    # store BTCDwif
    BTCDwif = response_encryptwallet['BTCDwif']
    BTCD = response_encryptwallet['BTCD']
    print('== response_encryptwallet: BTCDwif successfully obtained. ==')
except:
    print("** Error: Could not obtain BTCDwif. **")
    print(response_encryptwallet['error'])
    e = sys.exc_info()[0]
    print(e)
    sys.exit(0)
try:
    # store BTCwif
    BTCwif = response_encryptwallet['BTCwif']
    BTC = response_encryptwallet['BTC']
    print('== response_encryptwallet: BTCwif successfully obtained. ==')
except:
    print("** Error: Could not obtain BTCwif. **")
    print(response_encryptwallet['error'])
    e = sys.exc_info()[0]
    print(e)
    sys.exit(0)


# The walletpassphrase RPC stores the wallet decryption key in memory for the
# indicated number of seconds. Issuing the walletpassphrase command while the
# wallet is already unlocked will set a new unlock time that overrides
# the old one.

walletpassphrase = {
    "method": "walletpassphrase",
    "params": [
        passphrase,
        9999999
    ]
}
response_walletpassphrase = post_rpc(iguana_url, walletpassphrase)

# store btcpubkey
btcpubkey = response_walletpassphrase['btcpubkey']

print('== response_walletpassphrase ==')
pp.pprint(response_walletpassphrase)


# Requires wallet support. Wallet must be unlocked.The importprivkey RPC adds
# a private key to your wallet. The key should be formatted in the wallet
# import format created by the dumpprivkey RPC.
# The private key to import into the wallet encoded in base58check using
# wallet import format (WIF).

btcd_importprivkey = {
    "agent": "bitcoinrpc",
    "method": "importprivkey",
    "params": [BTCDwif, "", rescan_kmd]
}
response_btcd_importprivkey = post_rpc(
    komodod_url,
    btcd_importprivkey,
    komodod_auth)
print('== response_btcd_importprivkey ==')
pp.pprint(response_btcd_importprivkey)
# BTC
btc_importprivkey = {
    "agent": "bitcoinrpc",
    "method": "importprivkey",
    "params": [BTCwif, "", rescan_btc]
}
response_btc_importprivkey = post_rpc(bitcoind_url, btc_importprivkey, bitcoind_auth)
print('== response_btc_importprivkey ==')
pp.pprint(response_btc_importprivkey)


# The validateaddress RPC accepts a block, verifies it is a valid
# addition to the block chain, and broadcasts it to the network.

btcd_validateaddress = {
    "method": "validateaddress",
    "params": [BTCD]
}
response_btcd_validateaddress = post_rpc(
    komodod_url,
    btcd_validateaddress,
    komodod_auth)
print('== response_btcd_validateaddress ==')
pp.pprint(response_btcd_validateaddress)
# BTC
btc_validateaddress = {
    "method": "validateaddress",
    "params": [BTC]
}
response_btc_validateaddress = post_rpc(
    bitcoind_url,
    btc_validateaddress,
    bitcoind_auth)
print('== response_btc_validateaddress ==')
pp.pprint(response_btc_validateaddress)


# importprivkey method, komodod instances
def ac_importprivkey(symbol, url):
    payload = {
        "agent": "bitcoinrpc",
        "method": "importprivkey",
        "params": [BTCDwif, "", rescan_ac]
    }
    try:
        response_importprivkey = post_rpc(url, payload, assetchain_auth)
        return(response_importprivkey)
    except Exception as e:
        raise Exception(e)


# addcoin method, iguana
def addcoin(payload):
    symbol = payload['newcoin']
    response_addcoin = post_rpc(iguana_url, payload)
    print('== response_addcoin ' + symbol + ' ==')
    pp.pprint(response_addcoin)


# dpow
def dpow(symbol):
    payload = {
        "agent": "iguana",
        "method": "dpow",
        "symbol": symbol,
        "pubkey": btcpubkey
    }
    response_dpow = post_rpc(iguana_url, payload)
    print('== response_dpow ' + symbol + ' ==')
    pp.pprint(response_dpow)


# treat KMD first
for index, coin in enumerate(coins):
    symbol = coin['newcoin']
    if symbol == 'KMD':
        coin['userpass'] = komodod_userpass
        addcoin(coin)
        dpow(symbol)
        del coins[index]
    if coin['newcoin'] == 'BTC' or coin['newcoin'] == 'CHIPS':
        del coins[index]

# importprivkey, add and dpow assetchains
for coin in coins:
    # importprivkey, komodod instance
    symbol = coin['newcoin']
    url = (
        'http://' +
        conn['assetchain_ip'] +
        ':' +
        str(coin['rpc']))
    print('== response_importprivkey ' + symbol + ' ==')
    try:
        ac_ipk_response = ac_importprivkey(symbol, url)
        pp.pprint(ac_ipk_response)
    except Exception as e:
        print(
             "Attention: couldn't import private key for " +
             symbol + ":")
        print(e)
        continue
    # addcoin and dpow, iguana
    coin['userpass'] = assetchain_userpass
    addcoin(coin)
    dpow(symbol)

