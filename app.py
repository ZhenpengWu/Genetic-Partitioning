import logging
import tkinter.font as tk_font
from math import sqrt, ceil
from tkinter import ALL, Canvas, StringVar, Tk, E, N, S, W, filedialog, DISABLED, NORMAL
from tkinter.ttk import Button, Frame, Label

from model.circuit import Circuit
from algorithms.genetic import partition
from util.logging import init_logging


class App:
    def __init__(self, args=None) -> None:
        init_logging(args.verbose)

        self.circuit = Circuit()

        # if no_gui and infile are set, test benchmark directly without gui
        if args.no_gui and args.infile:
            self.__test_benchmark(args.infile)
        else:  # otherwise, display GUI
            self.root = Tk()
            self.__init_gui()
            if args.infile:
                self.__load_benchmark(args.infile)
            self.root.mainloop()

    def __test_benchmark(self, file):
        logging.info("opened benchmark: {}".format(file))
        self.circuit.parse_file(file)
        partition(self.circuit)

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

        self.__load_benchmark(filename)

        self.__init_canvas()
        self.root.nametowidget("btm.partition")["state"] = NORMAL

    def __load_benchmark(self, filename):
        """
        load the input file, initialize the canvas, update related info in the info frame
        :param filename: the input file
        """
        logging.info("opened benchmark: {}".format(filename))
        self.circuit.parse_file(filename)

        self.circuit.iteration = 1

        self.__update_info("info.iteration", self.circuit.iteration)
        self.__update_info("info.benchmark", self.circuit.benchmark)
        self.__update_info("info.cells", self.circuit.get_cells_size())
        self.__update_info("info.nets", self.circuit.get_nets_size())

    def __partitioning(self):
        """
        called when "partition" is pressed, execture the branch and bound partitioning
        """
        partition(self.circuit, self)
        self.root.nametowidget("btm.partition")["state"] = DISABLED

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
            btm_frame, text="open", command=self.__open_benchmark, name="open"
        )
        open_button.grid(column=0, row=0, padx=5, pady=5)

        # add partition button to the bottom frame
        partition_button = Button(
            btm_frame,
            text="partition",
            command=self.__partitioning,
            name="partition",
        )
        partition_button.grid(column=2, row=0, padx=5, pady=5)
        partition_button["state"] = DISABLED

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
        self.__update_cutsize(data.cutsize)

    def __update_cells(self, canvas, data):
        x = [self.size // 2, self.cw // 2 + self.size // 2]
        y = [self.size // 2, self.size // 2]
        node_count = [0, 0]
        for cell in self.circuit.cells:
            cell.update(canvas, x, y, node_count, data, self)

    def __update_nets(self, canvas):
        """Draw nets in canvas."""
        # Draw rats nest of nets
        canvas.delete("netlist")

        for net in self.circuit.nets:
            source = net.get_source()
            x1, y1 = source.center_coords(canvas)
            for sink in net.get_sinks():
                x2, y2 = sink.center_coords(canvas)
                canvas.create_line(x1, y1, x2, y2, tags="netlist", fill=net.color)

    def __update_cutsize(self, cutsize):
        self.__update_info("info.cutsize", cutsize)

    def update_iteration(self, iteration):
        self.__update_info("info.iteration", iteration)

    def __update_info(self, name: str, val):
        num_cells = self.root.nametowidget(name)
        varname = num_cells.cget("textvariable")
        num_cells.setvar(varname, val)
