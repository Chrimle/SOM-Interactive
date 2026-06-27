# datasets.py
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path


class Category(Enum):
    PROPOSAL = {"sv": "Förslag", "en": "Proposal"}


@dataclass
class Metadata:
    survey_id: str
    titles: dict[str, str]
    file_path: Path = field(init=False)
    category: Category = Category.PROPOSAL
    choice_col_index: int = 1
    value_col_index: int = 2
    value_unit: str = "%"
    time_col_index: int = 0

    def __post_init__(self):
        self.file_path = Path(__file__).parent / "data" / self.survey_id / "data.csv"


_SURVEYS = {
    "byd2RYvlxDRhTo": {
        "sv": "Förslag: Sänka fyraprocentspärren till riksdagen",
        "en": "Proposal: Lower the election threshold to the parliament"
    },
    "dNdVkecX9JRx12": {
        "sv": "Förslag: Sänka rösträttsåldern till 16 år i alla val",
        "en": "Proposal: Lower the voting age to 16 in all elections"
    },
    "DRGRvMStYgAX68": {
        "sv": "Förslag: Minska inkomstskillnaderna i samhället",
        "en": "Proposal: Reduce income differences in society"
    },
    "DtKn8nRSgTxsq8": {
        "sv": "Förslag: Införa sextimmars arbetsdag",
        "en": "Proposal: Introduce six-hour workday"
    },
    "DZPE7JsUS4tTwW": {
        "sv": "Förslag: Höja koldioxidskatten på bensin",
        "en": "Proposal: Increase the CO2 tax on petrol"
    },
    "H21XmkoynT7gjK": {
        "sv": "Förslag: Satsa på miljövänligt samhälle även om det innebär låg tillväxt",
        "en": "Proposal: Strive towards an env. friendly society, even without economic growth"
    },
    "iLRRtxKKzUFOSF": {
        "sv": "Förslag: Satsa på ett samhälle med ökad jämställdhet mellan kvinnor och män",
        "en": "Proposal: Strive towards a society with greater equality between women and men"
    },
    "kNH0jjogKxb2yo": {
        "sv": "Förslag: Höja skatterna",
        "en": "Proposal: Raise taxes"
    },
    "u2FlGAaCPdtXZ0": {
        "sv": "Förslag: Satsa mer på ett miljövänligt samhälle",
        "en": "Proposal: Strive towards an environmentally friendly society"
    },
    "vAkVIwSOFQLy8J": {
        "sv": "Förslag: Stärka djurens rätt",
        "en": "Proposal: Improve the rights of animals"
    },
    "xvNuEbwvtouNOI": {
        "sv": "Förslag: Sänka skatterna",
        "en": "Proposal: Lower taxes"
    },
}

# Dynamically build the final DATASETS dictionary
DATASETS: dict[str, Metadata] = {
    survey_id: Metadata(
        survey_id=survey_id,
        titles=language_map
    )
    for survey_id, language_map in _SURVEYS.items()
}
