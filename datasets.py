# datasets.py
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Metadata:
    title: str
    file_path: Path
    choice_col: str
    value_col: str
    value_unit: str
    time_col: str


DATASETS: dict[str, Metadata] = {
    "DtKn8nRSgTxsq8": Metadata(
        title="Förslag: Införa sextimmars arbetsdag",
        file_path=Path(__file__).parent / "data" / "DtKn8nRSgTxsq8" / "data.csv",
        choice_col="Svarsalternativ",
        value_col="Procent",
        value_unit="%",
        time_col="År"
    )
}
