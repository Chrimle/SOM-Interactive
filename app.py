from pathlib import Path
from shiny import App, render, ui, reactive
import pandas as pd
import matplotlib.pyplot as plt
from datasets import DATASETS, Metadata

I18N = {
    "sv": {
        "subtitle": "Detta är ett pågående projekt för att interagera med SOM-data!",
        "survey_label": "Välj undersökning:",
        "source_label": "Källa till data:",
        "github_text": "Besök projektet på GitHub för feedback och önskemål."
    },
    "en": {
        "subtitle": "This is a WIP project to interact with SOM data!",
        "survey_label": "Select survey:",
        "source_label": "Data source:",
        "github_text": "Visit the GitHub project for feedback and requests."
    }
}

SURVEY_CHOICES = {key: meta.title for key, meta in DATASETS.items()}

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_radio_buttons(
            "lang",
            None,
            choices={"sv": "🇸🇪 Svenska", "en": "🇬🇧 English"},
            selected="sv",
            inline=True
        ),
        ui.hr(),
        ui.output_ui("sidebar_subtitle"),
        ui.hr(),
        ui.output_ui("survey_selector_container"),
        ui.hr(),
        ui.output_ui("github_link"),
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
    # A helper function to quickly look up translations
    def translate(key: str) -> str:
        return I18N[input.lang()][key]

    @reactive.calc
    def current_dataset() -> tuple[pd.DataFrame, Metadata]:
        meta = DATASETS[input.selected_survey()]
        df = pd.read_csv(meta.file_path, encoding="utf-8")
        return df, meta

    @render.ui
    def sidebar_header():
        return ui.h3(translate("title"))

    @render.ui
    def sidebar_subtitle():
        return ui.p(translate("subtitle"))

    @render.ui
    def selected_survey_ui():
        df, meta = current_dataset()
        return ui.h5(meta.title, class_="m-0")

    @render.ui
    def survey_selector_container():
        return ui.input_select(
            "selected_survey",
            translate("survey_label"),
            choices=SURVEY_CHOICES
        )

    @render.ui
    def github_link():
        return ui.p(
            ui.a("GitHub Project", href="https://github.com/Chrimle/SOM-Interactive", target="_blank", class_="fw-bold text-decoration-none"),
            f" - {translate('github_text')}",
            class_="text-muted small"
        )

    # Update your existing footer to use the translated label too!
    @render.ui
    def survey_source_ui():
        df, meta = current_dataset()
        return ui.p(
            f"{translate('source_label')} ",
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
