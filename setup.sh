#!/bin/bash

set -ex

SCRIPT_DIR=$(cd $(dirname $0); pwd)

wsl sudo apt update
wsl sudo apt -y upgrade

wsl sudo apt install -y python3 python3-pip

wsl pip install -U pip
wsl pip install -r requirements.txt

cp ${SCRIPT_DIR}/slp-payout-config.json.template ${SCRIPT_DIR}/slp-payout-config.json