class Cell:
    def __init__(self, cell_id: int) -> None:
        self.cell_id: int = cell_id
        self.nets = []
        self.__text_id = None
        self.__rect_id = None

    def get_nets_size(self) -> int:
        return len(self.nets)

    def add_net(self, net) -> None:
        self.nets.append(net)

    def update(self, canvas, x1, y1, x2, y2, color=None):
        """
        update location and color of the cell in the canvas
        """
        if self.__rect_id is None:
            self.__rect_id = canvas.create_rectangle(x1, y1, x2, y2, fill=color)
        else:
            canvas.coords(self.__rect_id, x1, y1, x2, y2)
            canvas.itemconfigure(self.__rect_id, fill=color)
        self.__set_text(canvas)

    def center_coords(self, canvas):
        """
        :param canvas: canvas board
        :return: center coords of the current cell in the canvas
        """
        x1, y1, x2, y2 = canvas.coords(self.__rect_id)  # get rect coords
        return [(x1 + x2) // 2, (y1 + y2) // 2]

    def __set_text(self, canvas) -> None:
        """
        set the text, and place at the center of the rectangle
        :param canvas: canvas board
        """
        x, y = self.center_coords(canvas)
        if self.__text_id is None:
            self.__text_id = canvas.create_text(
                x, y, font=self.__get_font(canvas), text=str(self.cell_id)
            )
        else:
            canvas.coords(self.__text_id, x, y)
            canvas.itemconfigure(self.__text_id, text=str(self.cell_id))

    def __get_font(self, canvas):
        """
        get the font, and its size is depends on the size of the rectangle
        :param canvas: canvas
        :return: font with an appropriate size
        """
        x1, _, x2, _ = canvas.coords(self.__rect_id)
        return "Helvetica", int((x2 - x1) / 3)
