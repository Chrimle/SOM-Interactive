from pathlib import Path
from shiny import App, render, ui
import pandas as pd
import matplotlib.pyplot as plt

# Load the data
csv_path = Path(__file__).parent / "data" / "DtKn8nRSgTxsq8" / "data.csv"
df = pd.read_csv(csv_path, encoding="utf-8")

# Get unique survey options for the dropdown menu
categories = list(df["Svarsalternativ"].unique())

app_ui = ui.page_fluid(
    ui.h2("SOM Interactive"),
    ui.p("This is a WIP project to interact with SOM-data!"),
    ui.hr(),
    ui.h3("Förslag: Införa sextimmars arbetsdag"),
    ui.input_select("category", "Välj svarsalternativ:", choices=categories),
    ui.output_plot("survey_plot"),
)

def server(input, output, session):
    @render.plot
    def survey_plot():
        # Filter data based on dropdown selection
        filtered_df = df[df["Svarsalternativ"] == input.category()].sort_values("År")

        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(filtered_df["År"].astype(str), filtered_df["Procent"], color="royalblue", edgecolor="black")

        # Add labels and styling
        ax.set_ylabel("Procent (%)")
        ax.set_xlabel("År")
        ax.set_ylim(0, 100)
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        # Add percentage values on top of each bar
        ax.bar_label(bars, fmt='%d%%', padding=3)
        return fig

app = App(app_ui, server)
