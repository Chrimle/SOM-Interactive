from shiny import App, render, ui
import matplotlib.pyplot as plt
import numpy as np

app_ui = ui.page_fluid(
    ui.h2("SOM Interactive"),
    ui.p("This is a WIP project to interact with SOM-data!"),
    ui.input_slider("frequency", "Wave Frequency", 1, 20, 5),
    ui.output_plot("wave_plot"),
)

def server(input, output, session):
    @render.plot
    def wave_plot():
        x = np.linspace(0, 10, 200)
        y = np.sin(input.frequency() * x)
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(x, y, color="purple", linewidth=3)
        return fig

app = App(app_ui, server)
