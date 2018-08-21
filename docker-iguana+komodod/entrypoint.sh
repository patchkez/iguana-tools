#!/bin/bash

nohup redir --lport 7771 --laddr 127.0.0.1 --caddr 172.17.0.1 --cport 7771 >/dev/null 2>&1 &

cp -p /SuperNET/iguana/elected .

/SuperNET/agents/iguana "$@"

