from pathlib import Path
from shiny import App, render, ui, reactive
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from datasets import DATASETS, Metadata

I18N = {
    "sv": {
        "subtitle": "Interagera med data från SOM-institutet! ❤️ Detta är ett projekt under konstruktion.",
        "survey_label": "Välj undersökning:",
        "source_label": "Källa till data:",
        "github_text": "Lämna feedback och förslag på projektet här",
        "year_label": "Välj tidsperiod:",
        "toggle_labels": "Visa dataetiketter",
        "chart_type_label": "Välj diagramtyp:",
        "bar_label": "Staplat stapeldiagram",
        "line_label": "Linjediagram",
        "filter_answers_label": "Visa/dölj svar:",
        "toggle_insert_missing_years": "Lägg till saknade år",
        "disclaimer": "Detta projekt är fristående och har ingen koppling till eller godkännande från SOM-institutet.",
    },
    "en": {
        "subtitle": "Interact with data from the SOM-institute! ❤️ This project is Work-in-Progress.",
        "survey_label": "Select survey:",
        "source_label": "Data source:",
        "github_text": "Leave feedback and suggestions on the project here",
        "year_label": "Select time period:",
        "toggle_labels": "Show data labels",
        "chart_type_label": "Select chart type:",
        "bar_label": "Stacked bar chart",
        "line_label": "Line chart",
        "filter_answers_label": "Show/hide answers:",
        "toggle_insert_missing_years": "Insert missing years",
        "disclaimer": "This project is an independent project and is not affiliated, associated nor endorsed by the SOM-institute.",
    }
}

ANSWER_MAP = {
    "Mycket bra förslag": {
        "sv": "Mycket bra förslag",
        "en": "Very good proposal",
        "color": "#2e7d32"  # Dark Green
    },
    "Ganska bra förslag": {
        "sv": "Ganska bra förslag",
        "en": "Rather good proposal",
        "color": "#81c784"  # Light Green
    },
    "Varken bra eller dåligt förslag": {
        "sv": "Varken bra eller dåligt förslag",
        "en": "Neither good nor bad proposal",
        "color": "#b0bec5"  # Gray
    },
    "Ganska dåligt förslag": {
        "sv": "Ganska dåligt förslag",
        "en": "Rather bad proposal",
        "color": "#ef9a9a"  # Light Red
    },
    "Mycket dåligt förslag": {
        "sv": "Mycket dåligt förslag",
        "en": "Very bad proposal",
        "color": "#c62828"  # Dark Red
    }
}

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
        ui.output_ui("disclaimer_ui"),
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
    ui.div(
        ui.output_ui("survey_selector_container"),
        ui.hr(),
        ui.div(
            ui.div(
                ui.output_ui("year_slider_container"),
                style="min-width: 250px;"
            ),
            ui.output_ui("chart_type_ui"),
            ui.output_ui("toggle_labels_ui"),
            ui.output_ui("toggle_insert_missing_years_ui"),
            class_="d-flex flex-wrap gap-4 align-items-center mb-3"
        ),
        ui.output_ui("answer_filter_container"),
        class_="p-3 mb-3 bg-light rounded shadow-sm",
        style="border-left: 5px solid #2c3e50;"
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

    def translate_answer(ans: str) -> str:
        return ANSWER_MAP.get(ans, {}).get(input.lang(), ans)

    @reactive.calc
    def current_dataset() -> tuple[pd.DataFrame, Metadata]:
        meta = DATASETS[input.selected_survey()]
        df = pd.read_csv(meta.file_path, encoding="utf-8")
        return df, meta

    @render.ui
    def sidebar_subtitle():
        return ui.p(translate("subtitle"))

    @render.ui
    def disclaimer_ui():
        return ui.div(
            ui.tags.small(
                translate("disclaimer"),
                class_="text-muted"
            ),
            class_="border-start border-warning ps-2 my-2 bg-light"
        )

    @render.ui
    def selected_survey_ui():
        df, meta = current_dataset()
        return ui.h5(meta.titles.get(input.lang(), meta.titles.get("sv")), class_="m-0")

    @render.ui
    def survey_selector_container():
        lang = input.lang()
        choices = {key: meta.titles.get(lang, meta.titles.get("sv")) for key, meta in DATASETS.items()}

        try:
            current_selection = input.selected_survey()
        except Exception:
            current_selection = None

        return ui.input_select(
            "selected_survey",
            translate("survey_label"),
            choices=choices,
            selected=current_selection
        )

    @render.ui
    def chart_type_ui():
        return ui.input_radio_buttons(
            "chart_type",
            translate("chart_type_label"),
            choices={"bar": translate("bar_label"), "line": translate("line_label")},
            selected="bar"
        )

    @render.ui
    def toggle_labels_ui():
        return ui.input_switch(
            "show_labels",
            translate("toggle_labels"),
            value=True
        )

    @render.ui
    def toggle_insert_missing_years_ui():
        chart_type = input.chart_type()
        if chart_type == "bar":
            return ui.input_switch(
                "insert_missing_years",
                translate("toggle_insert_missing_years"),
                value=True
            )
        else:
            return None

    @render.ui
    def year_slider_container():
        df, meta = current_dataset()
        time_col_label = df.columns[meta.time_col_index]

        # Determine the min and max years in the current dataset
        min_year = int(df[time_col_label].min())
        max_year = int(df[time_col_label].max())

        # Don't show a slider if there is only one year of data
        if min_year == max_year:
            return None

        return ui.input_slider(
            "year_range",
            translate("year_label"),
            min=min_year,
            max=max_year,
            value=(min_year, max_year),
            step=1,
            sep=""
        )

    @render.ui
    def answer_filter_container():
        df, meta = current_dataset()
        choice_col_label = df.columns[meta.choice_col_index]

        # Get all unique choices present in the data
        unique_choices = df[choice_col_label].dropna().unique().tolist()

        # Generate order dynamically using dict keys
        correct_order = list(ANSWER_MAP.keys())
        existing_choices = [cat for cat in correct_order if cat in unique_choices]

        # Fallback for unexpected choices
        other_choices = [cat for cat in unique_choices if cat not in correct_order]
        final_choices = existing_choices + other_choices

        return ui.input_select(
            "selected_answers",
            translate("filter_answers_label"),
            choices={c: translate_answer(c) for c in final_choices},
            selected=final_choices,
            multiple=True,
            selectize=True
        )

    @render.ui
    def github_link():
        return ui.p(
            f"{translate('github_text')} - ",
            ui.a("GitHub", href="https://github.com/Chrimle/SOM-Interactive", target="_blank", class_="fw-bold text-decoration-none"),
            class_="text-muted small"
        )

    @render.ui
    def survey_source_ui():
        df, meta = current_dataset()
        return ui.p(
            f"{translate('source_label')} ",
            ui.a(
                "SOM-institutet",
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

        chart_type = input.chart_type()

        # Filter the dataframe based on the slider input (if it exists)
        year_range = input.year_range()
        if year_range is not None:
            df = df[(df[time_col_label] >= year_range[0]) & (df[time_col_label] <= year_range[1])]

        # Pivot the dataframe
        plot_df = df.pivot_table(index=time_col_label, columns=choice_col_label, values=value_col_label)

        # - Insert Missing Years & Re-index -
        plot_df.index = plot_df.index.astype(int)
        # Only re-index to add empty years if the toggle is checked
        if input.insert_missing_years() and chart_type == "bar":
            if year_range is not None:
                full_years = range(year_range[0], year_range[1] + 1)
            elif not plot_df.empty:
                full_years = range(plot_df.index.min(), plot_df.index.max() + 1)
            else:
                full_years = []
            plot_df = plot_df.reindex(full_years)
        # ------------------------------------

        fig, ax = plt.subplots(figsize=(8, 5))

        # Dynamically retrieve sorting order from map keys
        correct_order = list(ANSWER_MAP.keys())
        existing_order = [cat for cat in correct_order if cat in plot_df.columns]

        # Apply the user's active answer selections
        selected_answers = input.selected_answers()
        if selected_answers:
            existing_order = [cat for cat in existing_order if cat in selected_answers]

        # Reorder/Filter the dataframe columns
        plot_df = plot_df[existing_order]

        # Extract matching color mappings dynamically
        custom_colors = [ANSWER_MAP.get(cat, {}).get("color", "#757575") for cat in plot_df.columns]

        # Rename columns using the translation map before plotting
        plot_df = plot_df.rename(columns={col: translate_answer(col) for col in plot_df.columns})

        if chart_type == "bar":
            # Plot as Stacked Bar-graph
            plot_df.plot(kind="bar", stacked=True, ax=ax, edgecolor="black", color=custom_colors)
        else:
            plot_df.plot(kind="line", marker="o", linewidth=2, ax=ax, color=custom_colors)
            # Ensure index integers display cleanly as X axis ticks instead of floats
            ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

        # Add labels and styling
        ax.set_ylabel(value_col_label + " (" + meta.value_unit + ")")
        ax.set_xlabel(time_col_label)

        # Only lock y-limit to 100 if it's a stacked bar chart (as values total up to 100%)
        if chart_type == "bar":
            ax.set_ylim(0, 100)
        else:
            ax.set_ylim(0, None)

        ax.grid(axis='y', linestyle='--', alpha=0.7)

        # Move the legend outside the plot area
        ax.legend(title=choice_col_label, bbox_to_anchor=(1.05, 1), loc='upper left')

        show_labels = input.show_labels()
        if show_labels:
            if chart_type == "bar":
                # Add percentage values inside each stacked section
                for container in ax.containers:
                    labels = [f"{int(v.get_height())}%" if v.get_height() > 0 else "" for v in container]
                    ax.bar_label(container, labels=labels, label_type='center')
            else:
                # Add data labels slightly above line points (skipping NaN entries)
                for col in plot_df.columns:
                    for x, y in zip(plot_df.index, plot_df[col]):
                        if pd.notna(y):
                            ax.text(x, y + 1.5, f"{int(y)}%", ha='center', va='bottom', fontsize=8)

        # Ensure the external legend doesn't get cut off when rendered in Shiny
        fig.tight_layout()

        return fig


app = App(app_ui, server)
