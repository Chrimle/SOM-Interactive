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
        # Pivot the dataframe so Years are the index and Categories are the columns.
        plot_df = df.pivot(index="År", columns="Svarsalternativ", values="Procent")

        fig, ax = plt.subplots(figsize=(8, 5))

        # Plot as Stacked Bar-graph
        plot_df.plot(kind="bar", stacked=True, ax=ax, edgecolor="black", colormap="tab10")

        # Add labels and styling
        ax.set_ylabel("Procent (%)")
        ax.set_xlabel("År")
        ax.set_ylim(0, 100)
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        # Move the legend outside the plot area so it doesn't cover the bars
        ax.legend(title="Svarsalternativ", bbox_to_anchor=(1.05, 1), loc='upper left')

        # Add percentage values inside each stacked section
        for container in ax.containers:
            # label_type='center' puts the text in the middle of that specific block
            ax.bar_label(container, fmt='%d%%', label_type='center')

        # Ensure the external legend doesn't get cut off when rendered in Shiny
        fig.tight_layout()

        return fig

app = App(app_ui, server)
