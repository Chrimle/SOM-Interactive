import numpy as np
from pathlib import Path
from shiny import App, render, ui, reactive
import pandas as pd
import plotly.graph_objects as go
from shinywidgets import output_widget, render_plotly
from datasets import DATASETS, Metadata
from scipy.stats import linregress

I18N = {
    "sv": {
        "subtitle": "Interagera med data från SOM-institutet! ❤️ Detta är ett projekt under konstruktion.",
        "category_label": "Välj kategori:",
        "survey_label": "Välj undersökning:",
        "data_label": "Välj data:",
        "source_label": "Källa till data:",
        "github_text": "Lämna feedback och förslag på projektet här",
        "year_label": "Välj tidsperiod:",
        "toggle_labels": "Visa dataetiketter",
        "chart_type_label": "Välj diagramtyp:",
        "bar_label": "Staplat stapeldiagram",
        "line_label": "Linjediagram",
        "scatter_label": "Punktdiagram med trendlinje",
        "survey_title": "Ingen undersökning vald",
        "default_survey_option": "--- Välj en undersökning ---",
        "disclaimer": "Detta projekt är fristående och har ingen koppling till eller godkännande från SOM-institutet.",
        "quick_stats_header_label": "Snabb Fakta",
        "quick_stats_footer_label": "Inofficiell data, analys av",
        "quick_stats_content_label_part1": "Jämför data från ",
        "quick_stats_content_label_part2": " till ",
        "quick_stats_content_value_diff": "Skillnad",
        "year_abbreviated": "år",
        # SOM Provided translations
        "Antal svar": "Antal svar",
        "Procent": "Procent",
        "År": "År",
    },
    "en": {
        "subtitle": "Interact with data from the SOM-institute! ❤️ This project is Work-in-Progress.",
        "category_label": "Select category:",
        "survey_label": "Select survey:",
        "data_label": "Select data:",
        "source_label": "Data source:",
        "github_text": "Leave feedback and suggestions on the project here",
        "year_label": "Select time period:",
        "toggle_labels": "Show data labels",
        "chart_type_label": "Select chart type:",
        "bar_label": "Stacked bar chart",
        "line_label": "Line chart",
        "scatter_label": "Scatter plot with trend-line",
        "survey_title": "No survey selected",
        "default_survey_option": "--- Select a survey ---",
        "disclaimer": "This project is an independent project and is not affiliated, associated nor endorsed by the SOM-institute.",
        "quick_stats_header_label": "Quick Stats",
        "quick_stats_footer_label": "Inofficial data, analysis by",
        "quick_stats_content_label_part1": "Comparing data from ",
        "quick_stats_content_label_part2": " to ",
        "quick_stats_content_value_diff": "Difference",
        "year_abbreviated": "yr",
        # SOM Provided translations
        "Antal svar": "Response Count",  # TODO: find official translation!
        "Procent": "Percent",
        "År": "Year",
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
    },
    "Ingen uppfattning": {
        "sv": "Ingen uppfattning",
        "en": "No opinion",
        "color": "#37474f"  # Gray
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
        )
    ),
    ui.div(
        ui.div(
            ui.output_ui("category_selector_container"),
            ui.output_ui("survey_selector_container"),
            ui.output_ui("value_selector_container"),
            class_="d-flex flex-wrap gap-4 align-items-center"
        ),
        ui.hr(),
        ui.div(
            ui.div(
                ui.output_ui("year_slider_container"),
                style="min-width: 250px;"
            ),
            ui.output_ui("chart_type_ui"),
            ui.output_ui("toggle_labels_ui"),
            class_="d-flex flex-wrap gap-4 align-items-center mb-3"
        ),
        class_="p-3 mb-3 bg-light rounded shadow-sm",
        style="border-left: 5px solid #2c3e50;"
    ),
    ui.layout_columns(
        ui.card(
            ui.card_header(
                ui.output_ui("quick_stats_header")
            ),
            ui.output_ui("quick_stats_body"),
            ui.card_footer(
                ui.output_ui("quick_stats_footer")
            ),
            full_screen=False
        ),
        ui.card(
            ui.card_header(
                ui.output_ui("selected_survey_ui")
            ),
            output_widget("survey_plot"),
            ui.card_footer(
                ui.output_ui("survey_source_ui")
            ),
            full_screen=True
        ),
        # 2/12 columns for Quick Stats (~17%), 10/12 for Chart (~83%)
        col_widths={"md": (12, 12), "lg": (2, 10)}
    ),
    title="SOM Interactive"
)


def server(input, output, session):
    # A helper function to quickly look up translations
    def translate(key: str) -> str:
        return I18N[input.lang()][key]

    def translate_answer(ans: str) -> str:
        return ANSWER_MAP.get(ans, {}).get(input.lang(), ans)

    def is_valid_survey_selected() -> bool:
        return input.selected_survey() != ""

    @reactive.calc
    def current_dataset() -> tuple[pd.DataFrame, Metadata]:
        if not is_valid_survey_selected():
            return None, None
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
        text = translate("survey_title") if meta is None else meta.titles.get(input.lang(), meta.titles.get("sv"))
        return ui.h5(text, class_="m-0")

    @render.ui
    def category_selector_container():
        lang = input.lang()

        unique_categories = {meta.category for meta in DATASETS.values()}

        choices = {cat.name: cat.value.get(lang, cat.name) for cat in unique_categories}

        try:
            current_selection = input.selected_category()
        except Exception:
            current_selection = None

        return ui.input_select(
            "selected_category",
            translate("category_label"),
            choices=choices,
            selected=current_selection,
            width="max-content"
        )

    @render.ui
    def survey_selector_container():
        lang = input.lang()
        try:
            selected_cat_name = input.selected_category()
        except Exception:
            selected_cat_name = None

        # Filter the survey choices based on the selected category
        choices = {"": translate("default_survey_option")}
        for key, meta in DATASETS.items():
            if selected_cat_name is None or meta.category.name == selected_cat_name:
                choices[key] = meta.titles.get(lang, meta.titles.get("sv"))

        try:
            current_selection = input.selected_survey()
            if current_selection not in choices:
                current_selection = ""
        except Exception:
            current_selection = ""

        return ui.input_select(
            "selected_survey",
            translate("survey_label"),
            choices=choices,
            selected=current_selection,
            width="max-content"
        )

    @render.ui
    def value_selector_container():
        df, meta = current_dataset()
        # Fallback if no survey metadata is loaded yet
        if not meta or not is_valid_survey_selected():
            return None

        choices = {}
        for config in meta.value_columns:
            idx = config.column_index
            display_name = translate(config.display_name)
            unit = config.value_unit

            unit_label = f" ({unit})" if unit else ""
            choices[str(idx)] = f"{display_name}{unit_label}"

        return ui.input_select(
            id="selected_value_col",
            label=translate("data_label"),
            choices=choices,
            selected=list(choices.keys())[0]
        )

    @render.ui
    def chart_type_ui():
        return ui.input_radio_buttons(
            "chart_type",
            translate("chart_type_label"),
            choices={
                "bar": translate("bar_label"),
                "line": translate("line_label"),
                "scatter": translate("scatter_label")
            },
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
    def year_slider_container():
        if not is_valid_survey_selected():
            return None

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
    def github_link():
        return ui.p(
            f"{translate('github_text')} - ",
            ui.a("GitHub", href="https://github.com/Chrimle/SOM-Interactive", target="_blank", class_="fw-bold text-decoration-none"),
            class_="text-muted small"
        )

    @render.ui
    def survey_source_ui():
        if not is_valid_survey_selected():
            return None
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

    @render_plotly
    def survey_plot():
        if not is_valid_survey_selected():
            return None
        df, meta = current_dataset()
        chosen_index = int(input.selected_value_col())
        # Labels
        choice_col_label = df.columns[meta.choice_col_index]
        value_col_label = df.columns[chosen_index]
        value_display_name = translate(df.columns[chosen_index])

        active_config = next((c for c in meta.value_columns if c.column_index == chosen_index), None)
        value_unit_label = active_config.value_unit if active_config else None

        time_col_label = df.columns[meta.time_col_index]
        time_axis_display_name = translate(time_col_label)

        chart_type = input.chart_type()
        show_labels = input.show_labels()

        # Filter the dataframe based on the slider input (if it exists)
        year_range = input.year_range()
        if year_range is not None:
            df = df[(df[time_col_label] >= year_range[0]) & (df[time_col_label] <= year_range[1])]

        # Pivot the dataframe
        plot_df = df.pivot_table(index=time_col_label, columns=choice_col_label, values=value_col_label)

        # - Insert Missing Years & Re-index -
        plot_df.index = plot_df.index.astype(int)
        if year_range is not None:
            full_years = range(year_range[0], year_range[1] + 1)
        elif not plot_df.empty:
            full_years = range(plot_df.index.min(), plot_df.index.max() + 1)
        else:
            full_years = []
        plot_df = plot_df.reindex(full_years)
        # ------------------------------------

        # Dynamically retrieve sorting order from map keys
        correct_order = list(ANSWER_MAP.keys())
        existing_order = [cat for cat in correct_order if cat in plot_df.columns]

        # Reorder/Filter the dataframe columns
        plot_df = plot_df[existing_order]

        # Extract matching color mappings dynamically
        custom_colors = [ANSWER_MAP.get(cat, {}).get("color", "#757575") for cat in plot_df.columns]

        # Rename columns using the translation map before plotting
        plot_df = plot_df.rename(columns={col: translate_answer(col) for col in plot_df.columns})

        fig = go.Figure()

        # Build Plotly Traces
        for col, color in zip(plot_df.columns, custom_colors):
            # Custom hover template ensuring full name alignment alongside its values
            hovertemplate = (
                f"<b>{col}</b><br>"
                f"{value_display_name}: %{{y}} {value_unit_label if value_unit_label is not None else ""}<extra></extra>"
            )

            if chart_type == "bar":
                text_labels = [int(v) if pd.notna(v) and v > 0 else "" for v in plot_df[col]] if show_labels else None
                fig.add_trace(go.Bar(
                    x=plot_df.index,
                    y=plot_df[col],
                    name=col,
                    marker_color=color,
                    marker_line=dict(width=1, color="black"),
                    text=text_labels,
                    textposition="inside" if show_labels else "none",
                    hovertemplate=hovertemplate
                ))
            elif chart_type == "line":
                text_labels = [int(v) if pd.notna(v) else "" for v in plot_df[col]] if show_labels else None

                # TRACE 1: Background dashed line connecting the missing NaN gaps
                fig.add_trace(go.Scatter(
                    x=plot_df.index,
                    y=plot_df[col],
                    mode='lines',
                    line=dict(color=color, width=2, dash='dash'),
                    connectgaps=True,
                    showlegend=False,
                    hoverinfo='skip'
                ))

                # TRACE 2: Foreground solid line + markers that breaks at NaN gaps
                fig.add_trace(go.Scatter(
                    x=plot_df.index,
                    y=plot_df[col],
                    mode='lines+markers+text' if show_labels else 'lines+markers',
                    name=col,
                    line=dict(color=color, width=2),
                    marker=dict(size=8),
                    text=text_labels,
                    textposition="top center",
                    hovertemplate=hovertemplate,
                    connectgaps=False
                ))
            elif chart_type == "scatter":
                text_labels = [int(v) if pd.notna(v) else "" for v in plot_df[col]] if show_labels else None

                # Base Scatter Markers
                fig.add_trace(go.Scatter(
                    x=plot_df.index,
                    y=plot_df[col],
                    mode='markers+text' if show_labels else 'markers',
                    name=col,
                    marker=dict(color=color, size=8),
                    text=text_labels,
                    textposition="top center",
                    hovertemplate=hovertemplate
                ))

                valid_data = plot_df[col].dropna()
                if len(valid_data) > 1:  # Need at least 2 points to draw a line
                    valid_idx = valid_data.index
                    valid_vals = valid_data.values

                    # 1D polynomial fit (linear regression)
                    z = np.polyfit(valid_idx, valid_vals, 1)
                    p = np.poly1d(z)
                    trendline_y = p(plot_df.index)

                    # Add Trendline Trace
                    fig.add_trace(go.Scatter(
                        x=plot_df.index,
                        y=trendline_y,
                        mode='lines',
                        name=f"{col} (Trend)",
                        line=dict(color=color, width=2, dash='dot'),
                        showlegend=False,
                        hoverinfo='skip'
                    ))

        # Layout and Styling
        fig.update_layout(
            barmode='stack' if chart_type == "bar" else 'group',
            yaxis_title=f"{value_display_name} {f"({value_unit_label})" if value_unit_label is not None else ""}",
            xaxis_title=time_axis_display_name,
            yaxis=dict(
                range=[0, None],
                gridcolor='rgba(0,0,0,0.1)',
                griddash='dash'
            ),
            legend_title_text=choice_col_label,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02
            ),
            template="plotly_white",
            hovermode="x unified",
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                align="left"
            ),
            margin=dict(r=30)
        )

        # Force categorical x-axis for bars so reindexed missing years display as gaps,
        # or enforce integer ticks for line charts.
        if chart_type == "bar":
            fig.update_xaxes(type='category')
        else:
            fig.update_xaxes(dtick=1)

        return fig

    @render.ui
    def quick_stats_header():
        return ui.h5(
            translate('quick_stats_header_label'),
            class_="m-0"
        )

    @render.ui
    def quick_stats_body():
        if not is_valid_survey_selected():
            return None

        df, meta = current_dataset()
        chosen_index = int(input.selected_value_col())

        # Labels
        choice_col_label = df.columns[meta.choice_col_index]
        value_col_label = df.columns[chosen_index]
        time_col_label = df.columns[meta.time_col_index]

        # Filter dataframe
        year_range = input.year_range()
        if year_range is not None:
            df = df[(df[time_col_label] >= year_range[0]) & (df[time_col_label] <= year_range[1])]

        if df.empty:
            return ui.p("No data available for the selected range.", class_="text-muted m-0")

        min_year = int(df[time_col_label].min())
        max_year = int(df[time_col_label].max())

        if min_year == max_year:
            return ui.p(
                f"Only one year of data ({min_year}) is available in this range. Select a wider range to see trends.",
                class_="text-muted m-0"
            )

        # Get correct ordering based on your ANSWER_MAP
        correct_order = list(ANSWER_MAP.keys())
        existing_categories = [cat for cat in correct_order if cat in df[choice_col_label].values]

        ui_elements = []

        # Build a UI card for each category
        for cat in existing_categories:
            cat_data = df[df[choice_col_label] == cat].dropna(subset=[time_col_label, value_col_label])

            # Convert to numpy arrays for calculation
            x = cat_data[time_col_label].astype(float).values
            y = cat_data[value_col_label].astype(float).values

            # We need at least 2 distinct data points to calculate a linear regression
            if len(x) < 2 or len(np.unique(x)) < 2:
                continue

            # 1. Calculate Absolute Difference (Start to End point)
            old_val = y[x == x.min()][0]
            new_val = y[x == x.max()][0]
            diff = new_val - old_val
            diff_str = f"+{diff:.1f}" if diff > 0 else f"{diff:.1f}"

            # 2. Calculate Linear Regression (Slope and R²)
            res = linregress(x, y)
            slope = res.slope
            r_squared = res.rvalue ** 2

            # Format Trend (Slope / yr)
            yr_abbr = translate("year_abbreviated")
            if slope > 0:
                text_color = "text-success"
                trend_str = f"+{slope:.2f}/{yr_abbr}"
            elif slope < 0:
                text_color = "text-danger"
                trend_str = f"{slope:.2f}/{yr_abbr}"
            else:
                text_color = "text-muted"
                trend_str = f"±0.00/{yr_abbr}"

            display_name = translate_answer(cat)

            # Construct the Bootstrap Card
            card = ui.div(
                ui.div(display_name, class_="fw-bold mb-1 text-truncate"),
                ui.div(
                    # Row 1: Difference
                    ui.div(
                        ui.span(translate("quick_stats_content_value_diff"), class_="fw-semibold text-muted"),
                        ui.span(diff_str, class_="fw-bold text-muted"),
                        class_="d-flex justify-content-between mb-1"
                    ),
                    # Row 2: Trend (Linear Regression Slope)
                    ui.div(
                        ui.span("Trend", class_="fw-semibold text-muted"),
                        ui.span(trend_str, class_=f"fw-bold {text_color}"),
                        class_="d-flex justify-content-between mb-1"
                    ),
                    # Row 3: R-squared
                    ui.div(
                        ui.span("R²", class_="fw-semibold text-muted"),
                        ui.span(f"{r_squared:.3f}", class_="fw-medium"),
                        class_="d-flex justify-content-between"
                    ),
                    style="font-size: 0.85em;",
                    class_="lh-sm"
                ),
                class_="card px-3 py-2 shadow-sm border-0 bg-light"
            )
            ui_elements.append(card)

        if not ui_elements:
            return ui.p("Not enough overlapping data points to compare the oldest and newest years for these series.", class_="text-muted m-0")

        # Return the finalized Layout
        return ui.div(
            ui.p(translate("quick_stats_content_label_part1"), ui.strong(str(min_year)), translate("quick_stats_content_label_part2"), ui.strong(str(max_year)), ":", class_="mb-2 text-secondary", style="font-size: 0.9em;"),
            ui.div(*ui_elements, class_="d-flex flex-column gap-2")
        )

    @render.ui
    def quick_stats_footer():
        return ui.p(
            f"{translate('quick_stats_footer_label')} ",
            ui.a(
                "Chrimle",
                href="https://github.com/Chrimle",
                target="_blank"
            ),
            class_="m-0 small text-muted"
        )


app = App(app_ui, server)
