from datetime import datetime
from typing import List, NamedTuple
from web3 import Web3
import json
import math
import os
import sys
import time

import slp_utils

RONIN_ADDRESS_PREFIX = "ronin:"

# Data types


class Transaction(NamedTuple):
    from_address: str
    to_address: str
    amount: int


class Payout(NamedTuple):
    name: str
    private_key: str
    nonce: int
    slp_balance: int
    scholar_transaction: Transaction
    academy_transaction: Transaction


class SlpClaim(NamedTuple):
    name: str
    address: str
    private_key: str
    slp_claimed_balance: int
    slp_unclaimed_balance: int
    slp_total_claim: int
    state: dict


def parseRoninAddress(address):
    assert(address.startswith(RONIN_ADDRESS_PREFIX))
    return Web3.toChecksumAddress(address.replace(RONIN_ADDRESS_PREFIX, "0x"))


def formatRoninAddress(address):
    return address.replace("0x", RONIN_ADDRESS_PREFIX)


def log(message="", end="\n"):
    print(message, end=end, flush=True)
    sys.stdout = log_file
    print(message, end=end)  # print to log file
    sys.stdout = original_stdout  # reset to original stdout
    log_file.flush()


def wait(seconds):
    for i in range(0, seconds):
        time.sleep(1)
        log(".", end="")
    log()


web3 = Web3(Web3.HTTPProvider('https://proxy.roninchain.com/free-gas-rpc'))

today = datetime.now()
log_path = f"logs/logs-{today.year}-{today.month:02}-{today.day:02}.txt"

if not os.path.exists(os.path.dirname(log_path)):
    os.makedirs(os.path.dirname(log_path))
log_file = open(log_path, "a", encoding="utf-8")
original_stdout = sys.stdout

log(f"*** Welcome to the SLP Payout program *** ({today})")

# Load accounts data.
if (len(sys.argv) != 2):
    log("Please specify the path to the json config file as parameter.")
    exit()

nonces = {}

with open(sys.argv[1]) as f:
    accounts = json.load(f)

academy_payout_address = parseRoninAddress(
    accounts["Academy"]["AccountAddress"])

# Check for unclaimed SLP
log("Checking for unclaimed SLP", end="")
slp_claims: List[SlpClaim] = []
new_line_needed = False
for scholar in accounts["Scholars"]:
    scholarName = scholar["Name"]
    account_address = parseRoninAddress(scholar["AccountAddress"])

    slp_unclaimed_balance = slp_utils.get_unclaimed_slp(account_address)

    nonce = nonces[account_address] = web3.eth.get_transaction_count(
        account_address)

    if (slp_unclaimed_balance > 0):
        if (new_line_needed):
            new_line_needed = False
            log()
        log(f"Account '{scholarName}' (nonce: {nonce}) has "
            f"{slp_unclaimed_balance} unclaimed SLP.")

        slp_claimed_balance = slp_utils.get_claimed_slp(account_address)
        slp_claims.append(SlpClaim(
            name=scholarName,
            address=account_address,
            private_key=scholar["PrivateKey"],
            slp_claimed_balance=slp_claimed_balance,
            slp_unclaimed_balance=slp_unclaimed_balance,
            slp_total_claim=slp_claimed_balance+slp_claimed_balance,
            state={"signature": None}))
    else:
        log(".", end="")
        new_line_needed = True

if (new_line_needed):
    new_line_needed = False
    log()

if (len(slp_claims) > 0):
    log("Would you like to claim SLP?", end=" ")

while (len(slp_claims) > 0):
    if (input() == "y"):
        for slp_claim in slp_claims:
            log(f"   Claiming {slp_claim.slp_unclaimed_balance} SLP "
                f"for '{slp_claim.name}'...", end="")
            slp_utils.execute_slp_claim(slp_claim, nonces)
            time.sleep(0.250)
            log("DONE")
        log("Waiting 30 seconds", end="")
        wait(30)

        completed_claims: List[SlpClaim] = []
        for slp_claim in slp_claims:
            if slp_claim.state["signature"] is None:
                continue

            slp_total_balance = slp_utils.get_claimed_slp(account_address)
            print(slp_total_balance)
            print(slp_claim.slp_claimed_balance)
            print(slp_claim.slp_unclaimed_balance)

            if (slp_total_balance >= slp_claim.slp_total_claim):
                completed_claims.append(slp_claim)

        for completed_claim in completed_claims:
            slp_claims.remove(completed_claim)

        if (len(slp_claims) > 0):
            log("The following claims didn't complete successfully:")
            for slp_claim in slp_claims:
                log(f"  - Account '{slp_claim.name}' has "
                    f"{slp_claim.slp_unclaimed_balance} unclaimed SLP.")
            log("Would you like to retry claim process? ", end="")
        else:
            log("All claims completed successfully!")
    else:
        break

log()
log("Please review the payouts for each scholar:")

# Generate transactions.
payouts: List[Payout] = []

for scholar in accounts["Scholars"]:
    scholarName = scholar["Name"]
    account_address = parseRoninAddress(scholar["AccountAddress"])
    scholar_payout_address = parseRoninAddress(scholar["ScholarPayoutAddress"])

    slp_balance = slp_utils.get_claimed_slp(account_address)

    if (slp_balance == 0):
        log(f"Skipping account '{scholarName}' "
            f"({formatRoninAddress(account_address)}) "
            "because SLP balance is zero.")
        continue

    scholar_payout_percentage = scholar["ScholarPayoutPercentage"]
    assert(scholar_payout_percentage >= 0 and scholar_payout_percentage <= 1)

    scholar_payout_amount = math.ceil(
        slp_balance * scholar_payout_percentage)
    academy_payout_amount = slp_balance - scholar_payout_amount

    assert(scholar_payout_amount >= 0)
    assert(academy_payout_amount >= 0)
    assert(slp_balance == scholar_payout_amount +
           academy_payout_amount)

    payouts.append(Payout(
        name=scholarName,
        private_key=scholar["PrivateKey"],
        slp_balance=slp_balance,
        nonce=nonces[account_address],
        scholar_transaction=Transaction(
            from_address=account_address,
            to_address=scholar_payout_address,
            amount=scholar_payout_amount),
        academy_transaction=Transaction(
            from_address=account_address,
            to_address=academy_payout_address,
            amount=academy_payout_amount)))

log()

if (len(payouts) == 0):
    exit()


def get_preview_transaction(transaction: Transaction):
    return (f"send {transaction.amount:5} SLP "
            f"from {formatRoninAddress(transaction.from_address)} "
            f"to {formatRoninAddress(transaction.to_address)}")


# Preview transactions.
for payout in payouts:
    log(f"Payout for '{payout.name}'")
    log(f"├─ SLP balance: {payout.slp_balance} SLP")
    log(f"├─ Nonce: {payout.nonce}")
    log(f"├─ Scholar payout: "
        f"{get_preview_transaction(payout.scholar_transaction)}")
    log(f"└─ Academy payout: "
        f"{get_preview_transaction(payout.academy_transaction)}")
    log()

log("Would you like to execute transactions (y/n) ?", end=" ")
if (input() != "y"):
    log("No transaction was executed. Program will now stop.")
    exit()


def get_execute_transaction(transaction: Transaction):
    return (f"sending {transaction.amount:5} SLP "
            f"from {formatRoninAddress(transaction.from_address)} "
            f"to {formatRoninAddress(transaction.to_address)} ...")


# Execute transactions.
log()
log("Executing transactions...")
for payout in payouts:
    log(f"Executing payout for '{payout.name}'")
    log(f"├─ Scholar payout: "
        f"{get_execute_transaction(payout.scholar_transaction)}", end="")
    hash = slp_utils.transfer_slp(
        payout.scholar_transaction, payout.private_key, payout.nonce)
    time.sleep(0.250)
    log("DONE")
    log(f"│  Hash: {hash} - "
        f"Explorer: https://explorer.roninchain.com/tx/{str(hash)}")
    log(f"├─ Academy payout: "
        f"{get_execute_transaction(payout.academy_transaction)}", end="")
    hash = slp_utils.transfer_slp(
        payout.academy_transaction, payout.private_key, payout.nonce + 1)
    time.sleep(0.250)
    log("DONE")
    log(f"└─  Hash: {hash} - Explorer: "
        f"https://explorer.roninchain.com/tx/{str(hash)}")

    log()
