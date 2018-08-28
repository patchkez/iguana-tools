#!/usr/bin/env python3
import requests
import json
import sys
import os
import configparser
import datetime
import re

# define function that posts json data to daemon
def post_rpc(url, payload, **kwargs):
    try:
        credentials = kwargs['auth']
    except:
        credentials = ''
    try:
        r = requests.post(
            url,
            headers={'Content-type': 'text/plain; charset=utf-8'},
            auth=credentials,
            data=json.dumps(payload))
        return(json.loads(r.text))
    except Exception as e:
        print("Couldn't connect to " + url, e)


# define function that counts utxo's
def count_unspent(url, rpcauth, amount):
    # request list of utxo's
    listunspent_payload = {"method": "listunspent"}
    response_listunspent = post_rpc(url, listunspent_payload, auth=rpcauth)

    # count how many
    counter = 0
    for i, val in enumerate(response_listunspent['result']):
        if val['amount'] == float(amount):
            counter += 1
    print("Filtered by utxo size: " + amount)
    print("Number of relevant utxo's: " + str(counter))
    return(counter)


# define function that splits funds
def splitfunds(coin, utxo_size, number_needed, url):
    satoshis = int(float(utxo_size) * 100000000)
    splitfunds_payload = {
        "coin": coin,
        "agent": "iguana",
        "method": "splitfunds",
        "satoshis": satoshis,
        "sendflag": 1,
        "duplicates": int(number_needed)
    }
    response_splitfunds = post_rpc(url, splitfunds_payload)
    return response_splitfunds


# send to myself my balance
def consolidate(url, rpcauth):
    print("I'll try to send my whole balance to myself.")
    print("Checking if there is no pending transactions...")
    listtransactions_payload = {"method": "listtransactions"}
    response_listtransactions = post_rpc(url, listtransactions_payload, auth=rpcauth)
    # checking for pending transactions
    for tx in response_listtransactions['result']:
        if tx['category'] == 'send' and tx['confirmations'] == 0:
             raise Exception("Pending transaction detected. Cannot continue.")
    listaddressgroupings_payload = {"method": "listaddressgroupings"}
    response_listaddressgroupings = post_rpc(url, listaddressgroupings_payload, auth=rpcauth)
    my_address = response_listaddressgroupings['result'][0][0][0]
    my_balance = response_listaddressgroupings['result'][0][0][1]
    print('My address: ' + my_address)
    print('My balance: ' + str(my_balance))
    sendtoaddress_payload = {
        "method": "sendtoaddress",
        "params": [my_address, my_balance, "", "", True]
    }
    response_sendtoaddress = post_rpc(url, sendtoaddress_payload, auth=rpcauth)
    result = response_sendtoaddress['result']
    print('Transaction id: ' + result)


# this script
def main():
    now = str(datetime.datetime.utcnow())
    print("Starting at " + now + ' (UTC)')

    # read configuration file
    config = configparser.ConfigParser()
    path = os.path.dirname(sys.argv[0])
    if len(path) > 1:
        path += '/'
    path += '/recharge.ini'
    print("Reading configuration from " + path)
    config.read(path)

    # iterate through list of coins
    for i, coin in enumerate(config):
        if coin == 'DEFAULT':
            continue
        print(coin)
        # define daemon url
        try:
            # read from assetchains directory if defined
            ac_dir = config[coin]['assetchains_dir']
            coin_config_file = str(ac_dir + '/' + coin + '/' + coin + '.conf')
            print("Reading config file for credentials:", coin_config_file)
            with open(coin_config_file, 'r') as f:
                for line in f:
                    if re.search('rpcuser', line):
                        l = line.rstrip()
                        rpcuser = l.replace('rpcuser=', '')
                    elif re.search('rpcpassword', line):
                        l = line.rstrip()
                        rpcpassword = l.replace('rpcpassword=', '')
        except:
            # no assetchains directory defined, read from our recharge.ini file
            rpcuser = config[coin]['rpcuser']
            rpcpassword = config[coin]['rpcpassword'].encode('utf-8')
        rpcip = config[coin]['rpcip']
        rpcport = config[coin]['rpcport']
        rpcurl = 'http://' + rpcip + ':' + rpcport
        rpcauth = (rpcuser, rpcpassword)
        # define utxo size to filter by
        utxo_size = config[coin]['utxo_size']
        # ask how many utxo's
        try:
            n_relevant_utxos = count_unspent(rpcurl, rpcauth, utxo_size)
        except:
            print("Couldn't count utxo's.")
        # define number of relevant utxo's threshold and target
        try:
            threshold = config[coin]['threshold']
            target = config[coin]['target']
        except:
            print("Threshold and/or target not found.\n")
            continue
        if int(threshold) > int(target):
            print(
                "Can't process this! " +
                "Target must be greater than threshold!\n")
            continue
        else:
            pass
        print("Threshold: " + threshold)
        # if necessary, generate more utxo's
        if int(n_relevant_utxos) <= int(threshold):
            print("Threshold reached! ")
            print("Target: " + target)
            # define iguana url
            try:
                iguana_ip = config[coin]['iguana_ip']
            except:
                iguana_ip = '127.0.0.1'
            try:
                iguana_port = config[coin]['iguana_port']
            except:
                iguana_port = '7776'
            iguana_url = 'http://' + iguana_ip + ':' + iguana_port
            # calulate how many utxo's needed to reach target
            n_utxos_needed = int(target) - int(n_relevant_utxos)
            # generate needed utxos
            response_splitfunds = splitfunds(
                coin, utxo_size, n_utxos_needed, iguana_url)
            try:
                txid = response_splitfunds['txid']
                print("Success! Transaction id: " + txid)
            except:
                while (n_utxos_needed > 1):
                    n_utxos_needed = round(n_utxos_needed / 2)
                    response_splitfunds = splitfunds(
                        coin, utxo_size, n_utxos_needed, iguana_url)
                    try:
                        txid = response_splitfunds['txid']
                        print("Success! Transaction id: " + txid)
                        break
                    except:
                        print(
                            "Could not split funds into " +
                            str(n_utxos_needed))
                print("I tried all possible amounts.")
                try:
                    consolidate(rpcurl, rpcauth)
                except Exception as e:
                    print(
                        "Couldn't consolidate utxos. " +
                        "I'll try again next time.\n", e)
        print("")


if __name__ == '__main__':
    main()
