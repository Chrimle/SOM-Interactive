from pathlib import Path
from shiny import App, render, ui, reactive
import pandas as pd
import matplotlib.pyplot as plt
from datasets import DATASETS, Metadata

SURVEY_CHOICES = {key: meta.title for key, meta in DATASETS.items()}

app_ui = ui.page_fluid(
    ui.h2("SOM Interactive"),
    ui.p("This is a WIP project to interact with SOM-data!"),
    ui.p(
        "Visit the ",
        ui.a("SOM Interactive", href="https://github.com/Chrimle/SOM-Interactive", target="_blank"),
        " GitHub Project for feedback and/or requests."
    ),
    ui.hr(),
    ui.input_select("selected_survey", "Välj undersökning:", choices=SURVEY_CHOICES),
    ui.h3("Förslag: Införa sextimmars arbetsdag"),
    ui.output_plot("survey_plot"),
)

def server(input, output, session):

    @reactive.calc
    def current_dataset() -> tuple[pd.DataFrame, Metadata]:
        meta = DATASETS[input.selected_survey()]
        df = pd.read_csv(meta.file_path, encoding="utf-8")
        return df, meta

    @render.plot
    def survey_plot():
        df, meta = current_dataset()
        # Pivot the dataframe so Years are the index and Categories are the columns.
        plot_df = df.pivot(index=meta.time_col, columns=meta.choice_col, values=meta.value_col)

        fig, ax = plt.subplots(figsize=(8, 5))

        # Configuring Color-coding answers...
        correct_order = ["Mycket bra förslag", "Ganska bra förslag", "Varken bra eller dåligt förslag", "Ganska dåligt förslag", "Mycket dåligt förslag"]
        existing_order = [cat for cat in correct_order if cat in plot_df.columns]
        plot_df = plot_df[existing_order]
        custom_colors = [
            "#2e7d32",  # Dark Green
            "#81c784",  # Light Green
            "#b0bec5",  # Gray
            "#ef9a9a",  # Light Red
            "#c62828"   # Dark Red
        ]

        # Plot as Stacked Bar-graph
        plot_df.plot(kind="bar", stacked=True, ax=ax, edgecolor="black", color=custom_colors)

        # Add labels and styling
        ax.set_ylabel(meta.value_col + " (" + meta.value_unit + ")")
        ax.set_xlabel(meta.time_col)
        ax.set_ylim(0, 100)
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        # Move the legend outside the plot area so it doesn't cover the bars
        ax.legend(title=meta.choice_col, bbox_to_anchor=(1.05, 1), loc='upper left')

        # Add percentage values inside each stacked section
        for container in ax.containers:
            # label_type='center' puts the text in the middle of that specific block
            ax.bar_label(container, fmt='%d%%', label_type='center')

        # Ensure the external legend doesn't get cut off when rendered in Shiny
        fig.tight_layout()

        return fig

app = App(app_ui, server)
