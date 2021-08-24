import json
from pathlib import Path
from typing import NamedTuple


class ScholarInfo(NamedTuple):
    Name: str
    PrivateKey: str
    AccountAddress: str
    ScholarPayoutAddress: str
    ScholarPayoutPercentage: float

    @classmethod
    def load(cls, scholar_dict: dict):
        return cls(scholar_dict['Name'],
                   scholar_dict['PrivateKey'],
                   scholar_dict['AccountAddress'],
                   scholar_dict['ScholarPayoutAddress'],
                   scholar_dict['ScholarPayoutPercentage'])


class AcademyInfo(NamedTuple):
    Name: str
    PrivateKey: str
    AccountAddress: str

    @classmethod
    def load(cls, scholar_dict: dict):
        return cls(scholar_dict['Name'],
                   scholar_dict['PrivateKey'],
                   scholar_dict['AccountAddress'])


class PayoutInfo:
    def __init__(self) -> None:
        self._payout_path = Path("slp-payout-config.json")
        self.load()

    def load(self):
        with open(self._payout_path) as f:
            payout_dict = json.load(f)

        self.academy = AcademyInfo.load(payout_dict["Academy"])
        self.scholar_list = \
            tuple([ScholarInfo.load(scholar_dict)
                   for scholar_dict in payout_dict['Scholars']])

    def to_dict(self):
        return {
            "Academy": self.academy._asdict(),
            "Scholars": [scholar._asdict() for scholar in self.scholar_list]
        }

    def rewrite_academy(self, academy_dict: dict):
        payout_dict = self.to_dict()
        payout_dict["Academy"] = academy_dict

        with open(self._payout_path, 'w') as f:
            json.dump(payout_dict, f, indent=2)

    def rewrite_scholar(self, scholar_dict: dict, index: int):
        payout_dict = self.to_dict()
        payout_dict["Scholars"][index] = scholar_dict

        with open(self._payout_path, 'w') as f:
            json.dump(payout_dict, f, indent=2)
