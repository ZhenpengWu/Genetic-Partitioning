import logging
import tkinter.font as tk_font
from math import sqrt, ceil
from tkinter import ALL, Canvas, StringVar, Tk, E, N, S, W, filedialog, DISABLED, NORMAL
from tkinter.ttk import Button, Frame, Label

from algorithms.genetic import genetic
from algorithms.kl import kl
from model.circuit import Circuit
from util.colors import locked_color
from util.logging import init_logging


class App:
    def __init__(self, args=None) -> None:
        init_logging(args.verbose)

        self.circuit = Circuit()
        self.root = Tk()
        self.__init_gui()
        self.root.mainloop()

    def __open_benchmark(self):
        """
        called when "open" button is pressed, a dialog is opened for the user
        if a file is selected, load the file and initialize the canvas
        """
        filename = filedialog.askopenfilename(
            initialdir="benchmarks",
            title="Select file",
            filetypes=[("Text files", "*.txt"), ("all files", "*.*")],
        )

        if not filename:
            return

        logging.info("opened benchmark: {}".format(filename))
        self.circuit.parse_file(filename)

        self.circuit.iteration = 1

        self.__update_info("info.iteration", self.circuit.iteration)
        self.__update_info("info.benchmark", self.circuit.benchmark)
        self.__update_info("info.cells", self.circuit.get_cells_size())
        self.__update_info("info.nets", self.circuit.get_nets_size())

        self.__init_canvas()
        self.update_partition_button(True)

    def __partitioning(self, algorihtm):
        """
        called when "partition" is pressed, execture the branch and bound partitioning
        """
        if algorihtm == "kl":
            kl(self.circuit, self)
        else:
            genetic(self.circuit, self)
        self.update_partition_button(False)

    def __init_gui(self):
        """
        initialize the GUI
        """
        self.root.title("partitioning")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(4, weight=1)

        # set up the canvas / top frame
        top_frame = Frame(self.root, name="top")
        top_frame.grid(column=1, row=0, sticky=E + W + N + S)

        # add canvas to the top frame
        canvas = Canvas(top_frame, width=500, height=400, bg="gray66", name="canvas")
        canvas.grid(column=0, row=0, sticky=E + W + N + S)

        # set up the bottom / button frame
        btm_frame = Frame(self.root, name="btm")
        btm_frame.grid(column=1, row=1)

        # add open button to the bottom frame
        open_button = Button(
            btm_frame, text="Open", command=self.__open_benchmark, name="open"
        )
        open_button.grid(column=0, row=0, padx=5, pady=5)

        # add partition button to the bottom frame
        kl_button = Button(
            btm_frame,
            text="Kernighan-Lin",
            command=lambda: self.__partitioning("kl"),
            name="kl",
        )
        kl_button.grid(column=1, row=0, padx=5, pady=5)
        kl_button["state"] = DISABLED

        genetic_button = Button(
            btm_frame,
            text="Genetic",
            command=lambda: self.__partitioning("genetic"),
            name="genetic",
        )
        genetic_button.grid(column=2, row=0, padx=5, pady=5)
        genetic_button["state"] = DISABLED

        # set up the info frame
        info_frame = Frame(self.root, name="info")
        info_frame.grid(column=2, row=0, rowspan=2, sticky=E + W)

        # add informations to the info frame
        font = tk_font.Font(family="Helvetica", size=13)
        for i, v in enumerate(["benchmark", "cells", "nets", "cutsize", "iteration"]):
            fg = "red" if v == "cutsize" or v == "iteration" else "black"
            label = Label(info_frame, font=font, foreground=fg, text=v + ":")
            label.grid(column=0, row=i, padx=5, pady=5, sticky=W)
            val = StringVar(info_frame, value="-")
            val_label = Label(
                info_frame, font=font, foreground=fg, textvariable=val, name=v
            )
            val_label.grid(column=1, row=i, padx=5, pady=5)

    def __init_canvas(self):
        canvas = self.root.nametowidget("top.canvas")
        canvas.delete(ALL)

        self.node_pad = 5

        max_cells_per_block = (self.circuit.get_cells_size() // 2) + 2

        self.rows = ceil(sqrt(max_cells_per_block))
        self.cols = ceil(max_cells_per_block / self.rows)

        w_size = self.root.winfo_screenwidth() * 0.8 / (2 * (self.cols + 1)) - self.node_pad
        h_size = self.root.winfo_screenheight() * 0.8 / self.rows - self.node_pad
        # calculate the size of cells in the canvas, depends on the number of rows and cols
        self.size = int(min(w_size, h_size))

        self.cw = 2 * ((self.cols + 1) * self.size + (self.cols - 1) * self.node_pad)
        self.ch = (self.rows + 1) * self.size + (self.rows - 1) * self.node_pad
        canvas.config(width=self.cw, height=self.ch)

    def update_canvas(self, data):
        """Draw the canvas and update statistics being displayed."""
        canvas = self.root.nametowidget("top.canvas")

        self.__update_cells(canvas, data)
        self.__update_nets(canvas)
        self.__update_info("info.cutsize", data.cutsize)
        self.__update_info("info.iteration", data.iteration)

    def __update_cells(self, canvas, data):
        x = [self.size // 2, self.cw // 2 + self.size // 2]
        y = [self.size // 2, self.size // 2]
        node_count = [0, 0]
        for cell in self.circuit.cells:
            block_id = data.get_node_block_id(cell)
            x1, y1 = x[block_id], y[block_id]
            x2, y2 = x1 + self.size, y1 + self.size
            color = locked_color[block_id] if data.is_node_locked(cell) else "white"
            cell.update(canvas, x1, y1, x2, y2, color)
            node_count[block_id] += 1
            next_col = (node_count[block_id] % self.rows) == 0

            x[block_id] = x2 + self.node_pad if next_col else x1
            y[block_id] = self.size // 2 if next_col else y2 + self.node_pad

    def __update_nets(self, canvas):
        """Draw nets in canvas."""
        canvas.delete("netlist")

        for net in self.circuit.nets:
            source = net.get_source()
            x1, y1 = source.center_coords(canvas)
            for sink in net.get_sinks():
                x2, y2 = sink.center_coords(canvas)
                canvas.create_line(x1, y1, x2, y2, tags="netlist", fill=net.color)

    def __update_info(self, name: str, val):
        info = self.root.nametowidget(name)
        varname = info.cget("textvariable")
        info.setvar(varname, val)

    def update_partition_button(self, enable):
        self.root.nametowidget("btm.kl")["state"] = NORMAL if enable else DISABLED
        self.root.nametowidget("btm.genetic")["state"] = NORMAL if enable else DISABLED
