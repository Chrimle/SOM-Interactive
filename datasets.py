# datasets.py
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Metadata:
    title: str
    file_path: Path
    choice_col_index: int
    value_col_index: int
    value_unit: str
    time_col_index: int
    survey_id: str


DATASETS: dict[str, Metadata] = {
    "DtKn8nRSgTxsq8": Metadata(
        title="Förslag: Införa sextimmars arbetsdag",
        file_path=Path(__file__).parent / "data" / "DtKn8nRSgTxsq8" / "data.csv",
        choice_col_index=1,
        value_col_index=2,
        value_unit="%",
        time_col_index=0,
        survey_id="DtKn8nRSgTxsq8"
    ),
    "DZPE7JsUS4tTwW": Metadata(
        title="Förslag: Höja koldioxidskatten på bensin",
        file_path=Path(__file__).parent / "data" / "DZPE7JsUS4tTwW" / "data.csv",
        choice_col_index=1,
        value_col_index=2,
        value_unit="%",
        time_col_index=0,
        survey_id="DZPE7JsUS4tTwW"
    ),
    "kNH0jjogKxb2yo": Metadata(
        title="Förslag: Höja skatterna",
        file_path=Path(__file__).parent / "data" / "kNH0jjogKxb2yo" / "data.csv",
        choice_col_index=1,
        value_col_index=2,
        value_unit="%",
        time_col_index=0,
        survey_id="kNH0jjogKxb2yo"
    ),
    "xvNuEbwvtouNOI": Metadata(
        title="Förslag: Sänka skatterna",
        file_path=Path(__file__).parent / "data" / "xvNuEbwvtouNOI" / "data.csv",
        choice_col_index=1,
        value_col_index=2,
        value_unit="%",
        time_col_index=0,
        survey_id="xvNuEbwvtouNOI"
    ),
}
