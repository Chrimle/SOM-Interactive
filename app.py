from pathlib import Path
from shiny import App, render, ui, reactive
import pandas as pd
import matplotlib.pyplot as plt
from datasets import DATASETS, Metadata

SURVEY_CHOICES = {key: meta.title for key, meta in DATASETS.items()}

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h3("SOM Interactive"),
        ui.p("This is a WIP project to interact with SOM-data!"),
        ui.hr(),
        ui.input_select("selected_survey", "Välj undersökning:", choices=SURVEY_CHOICES),
        ui.hr(),
        ui.p(
            "Visit the ",
            ui.a("SOM Interactive", href="https://github.com/Chrimle/SOM-Interactive", target="_blank", class_="fw-bold text-decoration-none"),
            " GitHub Project for feedback and/or requests.",
            class_="text-muted small"
        ),
        bg="#f8f9fa"
    ),
    ui.head_content(
        ui.tags.link(
            rel="stylesheet",
            href="https://cdn.jsdelivr.net/npm/bootswatch@5.3.3/dist/flatly/bootstrap.min.css"
        ),
        ui.HTML("""
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-DJPKJ5B6W7"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());

          gtag('config', 'G-DJPKJ5B6W7');
        </script>
        """)
    ),
    ui.card(
        ui.card_header(
            ui.output_ui("selected_survey_ui")
        ),
        ui.output_plot("survey_plot"),
        ui.card_footer(
            ui.output_ui("survey_source_ui")
        ),
        full_screen=True
    ),
    title="SOM Interactive"
)


def server(input, output, session):
    @reactive.calc
    def current_dataset() -> tuple[pd.DataFrame, Metadata]:
        meta = DATASETS[input.selected_survey()]
        df = pd.read_csv(meta.file_path, encoding="utf-8")
        return df, meta

    @render.ui
    def selected_survey_ui():
        df, meta = current_dataset()
        return ui.h5(meta.title, class_="m-0")

    @render.ui
    def survey_source_ui():
        df, meta = current_dataset()
        return ui.p(
            "Källa till data: ",
            ui.a(
                "SOM Institutet",
                href=f"https://som-institutet.se/dataanalys?m=item_{meta.survey_id}",
                target="_blank"
            ),
            class_="m-0 small text-muted"
        )

    @render.plot
    def survey_plot():
        df, meta = current_dataset()
        # Labels
        choice_col_label = df.columns[meta.choice_col_index]
        value_col_label = df.columns[meta.value_col_index]
        time_col_label = df.columns[meta.time_col_index]
        # Pivot the dataframe so Years are the index and Categories are the columns.
        plot_df = df.pivot(index=time_col_label, columns=choice_col_label, values=value_col_label)

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
            "#c62828"  # Dark Red
        ]

        # Plot as Stacked Bar-graph
        plot_df.plot(kind="bar", stacked=True, ax=ax, edgecolor="black", color=custom_colors)

        # Add labels and styling
        ax.set_ylabel(value_col_label + " (" + meta.value_unit + ")")
        ax.set_xlabel(time_col_label)
        ax.set_ylim(0, 100)
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        # Move the legend outside the plot area so it doesn't cover the bars
        ax.legend(title=choice_col_label, bbox_to_anchor=(1.05, 1), loc='upper left')

        # Add percentage values inside each stacked section
        for container in ax.containers:
            # label_type='center' puts the text in the middle of that specific block
            ax.bar_label(container, fmt='%d%%', label_type='center')

        # Ensure the external legend doesn't get cut off when rendered in Shiny
        fig.tight_layout()

        return fig


app = App(app_ui, server)
