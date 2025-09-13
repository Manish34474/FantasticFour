from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import TYPE_CHECKING

from controller.config.config import Config
from model.location import Location

if TYPE_CHECKING:
    from model.environment import Environment


class Gui(tk.Tk):
    """
    Graphical User Interface (GUI) for visualising the simulation environment.

    Attributes:
        __environment (Environment): The environment instance to visualise.
        __agent_colours (dict): A dictionary mapping agent classes to their corresponding colors.
        __legend_panel (tk.Frame): The legend panel displaying agent types and their counts.
        __closed (bool): Flag indicating whether the GUI window is closed.
        __cells (list): 2D list to store cell references for efficient updates
    """

    def __init__(self, environment: Environment, agent_colours: dict):
        """
        Initialize the GUI with the given environment and agent colors.

        Args:
            environment (Environment): The environment instance to visualise.
            agent_colours (dict): A dictionary mapping agent classes to their corresponding colors.
        """
        super().__init__()
        self.__environment = environment
        self.__agent_colours = agent_colours
        self.__legend_panel = None
        self.__closed = False
        self.__cells = []  # Store cell references for efficient updates
        self.__legend_widgets = []  # Store legend widget references

        self.__init_gui()
        self.__init_info()
        self.__init_world()

    def render(self):
        """Render the current state of the environment - optimized version."""
        self.update_legend()

        # Update only the cells that have changed
        for row_index in range(self.__environment.get_height()):
            for col_index in range(self.__environment.get_width()):
                agent = self.__environment.get_agent(Location(col_index, row_index))
                
                if agent:
                    agent_colour = self.__agent_colours[agent.__class__]
                else:
                    agent_colour = self.__agent_colours[None]
                
                # Only update if the color has changed
                current_color = self.__cells[row_index][col_index].cget('bg')
                if current_color != agent_colour:
                    self.__cells[row_index][col_index].config(bg=agent_colour)

        self.update_idletasks()

    def __init_gui(self):
        """Initialize GUI settings."""
        self.title(Config.simulation_name)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def __init_info(self):
        """Initialize the legend panel."""
        self.legend_panel = tk.Frame(self)
        self.legend_panel.grid(row=0, column=0)

    def __init_world(self):
        """Initialize the world grid with cell references stored for later updates."""
        self.grid_frame = tk.Frame(self)
        self.grid_frame.grid(row=1, column=0)

        # Initialize the cells grid
        self.__cells = []
        for row_index in range(self.__environment.get_height()):
            row_cells = []
            for col_index in range(self.__environment.get_width()):
                agent = self.__environment.get_agent(Location(col_index, row_index))

                if agent:
                    agent_colour = self.__agent_colours[agent.__class__]
                else:
                    agent_colour = self.__agent_colours[None]

                cell = tk.Canvas(self.grid_frame,
                                 width=10,
                                 height=10,
                                 bg=agent_colour,
                                 borderwidth=1,
                                 relief="solid")

                cell.grid(row=row_index, column=col_index)
                row_cells.append(cell)
            self.__cells.append(row_cells)

    def update_legend(self):
        """Update the legend panel with agent counts - optimized version."""
        agent_counts = {}

        # Count agents
        for row_index in range(self.__environment.get_height()):
            for col_index in range(self.__environment.get_width()):
                agent = self.__environment.get_agent(Location(col_index, row_index))
                if agent:
                    agent_class = agent.__class__
                    agent_counts[agent_class] = agent_counts.get(agent_class, 0) + 1

        # Get current legend items for comparison
        current_legend_items = []
        for i in range(0, len(self.__legend_widgets), 2):
            if i + 1 < len(self.__legend_widgets):
                color_widget, text_widget = self.__legend_widgets[i], self.__legend_widgets[i + 1]
                agent_name = text_widget.cget('text').split(' (')[0]
                current_legend_items.append(agent_name)

        # Get new legend items
        new_legend_items = sorted([agent_class.__name__ for agent_class in agent_counts.keys()])

        # Only update if legend has changed
        if current_legend_items != new_legend_items:
            # Clear existing legend widgets
            for widget in self.__legend_widgets:
                widget.destroy()
            self.__legend_widgets.clear()

            # Create new legend items
            sorted_counts = sorted(agent_counts.items(), key=lambda x: x[0].__name__)
            for agent_class, count in sorted_counts:
                color_label = tk.Label(self.legend_panel, bg=self.__agent_colours[agent_class], width=2, height=1)
                color_label.pack(side=tk.LEFT)
                self.__legend_widgets.append(color_label)

                label_text = f"{agent_class.__name__} ({count})"
                label = tk.Label(self.legend_panel, text=label_text)
                label.pack(side=tk.LEFT)
                self.__legend_widgets.append(label)

    def on_closing(self):
        """Handle closing of the GUI window."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.__closed = True
            self.destroy()

    def is_closed(self) -> bool:
        """Check if the GUI window is closed."""
        return self.__closed