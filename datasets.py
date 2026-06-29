# datasets.py
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


class Category(Enum):
    PROPOSAL = {"sv": "Förslag", "en": "Proposal"}


@dataclass
class ValueColumnConfig:
    column_index: int
    display_name: str
    value_unit: Optional[str] = None


@dataclass
class Metadata:
    survey_id: str
    titles: dict[str, str]
    file_path: Path = field(init=False)
    category: Category = Category.PROPOSAL
    choice_col_index: int = 1
    value_columns: list[ValueColumnConfig] = field(
        default_factory=lambda: [
            ValueColumnConfig(column_index=2, display_name="Procent", value_unit="%"),
            ValueColumnConfig(column_index=3, display_name="Antal svar", value_unit=None)
        ]
    )
    time_col_index: int = 0

    def __post_init__(self):
        self.file_path = Path(__file__).parent / "data" / self.survey_id / "data.csv"


_SURVEYS = {
    "5jkTvojUF0ZTIU": {
        "sv": "Förslag: Införa dödstraff för mord",
        "en": "Proposal: Introduce death penalty for murder"
    },
    "ArOo97j4b6ZFpd": {
        "sv": "Förslag: Tillåta aktiv dödshjälp",
        "en": "Proposal: Allow active euthanasia"
    },
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
    "g6xB37wuzX5BZP": {
        "sv": "Förslag: Stärka homo-, bi- och transsexuellas ställning i samhället",
        "en": "Proposal: Strengthen the position of homo-, bi- and transsexuals in society"
    },
    "H21XmkoynT7gjK": {
        "sv": "Förslag: Satsa på miljövänligt samhälle även om det innebär låg tillväxt",
        "en": "Proposal: Strive towards an env. friendly society, even without economic growth"
    },
    "iLRRtxKKzUFOSF": {
        "sv": "Förslag: Satsa på ett samhälle med ökad jämställdhet mellan kvinnor och män",
        "en": "Proposal: Strive towards a society with greater equality between women and men"
    },
    "lLL3Ds0l8KAmIx": {
        "sv": "Förslag: Införa republik med vald president",
        "en": "Proposal: Make Sweden a republic with an elected president"
    },
    "kNH0jjogKxb2yo": {
        "sv": "Förslag: Höja skatterna",
        "en": "Proposal: Raise taxes"
    },
    "lesxqpFKRJ8s0g": {
        "sv": "Förslag: Tillåta homosexuella par att adoptera barn",
        "en": "Proposal: Allow homosexual couples to adopt children"
    },
    "MfMvdbn5VClF9O": {
        "sv": "Förslag: Sverige bör på lång sikt avveckla kärnkraften",
        "en": "Proposal: Sweden should in the long run abolish nuclear power"
    },
    "nkXsAviYMNR566": {
        "sv": "Förslag: Förbjuda ansiktstäckande slöja på allmän plats",
        "en": "Proposal: Ban face-covering veils in public places"
    },
    "NpTHvaNvTjmrB9": {
        "sv": "Förslag: Alltid överlåta beslut i viktiga frågor till experter",
        "en": "Proposal: Delegate decisions in important issues to experts"
    },
    "u2FlGAaCPdtXZ0": {
        "sv": "Förslag: Satsa mer på ett miljövänligt samhälle",
        "en": "Proposal: Strive towards an environmentally friendly society"
    },
    "uZM8ISnRKSbtLH": {
        "sv": "Förslag: Förbjuda forskning som använder befruktade ägg",
        "en": "Proposal: Prohibit research that uses fertilized eggs (embryonic stem cells)"
    },
    "vAkVIwSOFQLy8J": {
        "sv": "Förslag: Stärka djurens rätt",
        "en": "Proposal: Improve the rights of animals"
    },
    "xvNuEbwvtouNOI": {
        "sv": "Förslag: Sänka skatterna",
        "en": "Proposal: Lower taxes"
    },
    "ymzgS99s9eEA7P": {
        "sv": "Förslag: Begränsa rätten till fri abort",
        "en": "Proposal: Limit the right to abortion"
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
