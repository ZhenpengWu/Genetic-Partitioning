from util.colors import locked_color


class Cell:
    def __init__(self, cell_id: int) -> None:
        self.cell_id: int = cell_id
        self.nets = []
        self.text_id = None
        self.rect_id = None
        self.x = None
        self.y = None

    def __str__(self):
        return str(self.cell_id)

    def get_net_size(self) -> int:
        return len(self.nets)

    def add_net(self, net) -> None:
        self.nets.append(net)

    def update(self, canvas, x, y, node_count, data, app):
        block_id = data.get_node_block_id(self)
        x1, y1 = x[block_id], y[block_id]
        x2, y2 = x1 + app.size, y1 + app.size
        color = locked_color[block_id] if data.is_node_locked(self) else "white"
        if self.rect_id is None:
            self.rect_id = canvas.create_rectangle(x1, y1, x2, y2, fill=color)
        else:
            canvas.coords(self.rect_id, x1, y1, x2, y2)
            canvas.itemconfigure(self.rect_id, fill=color)
        self.__set_text(canvas)

        node_count[block_id] += 1
        next_col = (node_count[block_id] % app.rows) == 0

        x[block_id] = x2 + app.node_pad if next_col else x1
        y[block_id] = app.size // 2 if next_col else y2 + app.node_pad

    def center_coords(self, canvas):
        """
        :param canvas: canvas board
        :return: center coords of the current site in the canvas
        """
        x1, y1, x2, y2 = canvas.coords(self.rect_id)  # get rect coords
        return (x1 + x2) // 2, (y1 + y2) // 2

    def __set_text(self, canvas) -> None:
        """
        set the text, and place at the center of the rectangle
        :param canvas: canvas board
        """
        x, y = self.center_coords(canvas)
        if self.text_id is None:
            self.text_id = canvas.create_text(
                x, y, font=self.__get_font(canvas), text=str(self.cell_id)
            )
        else:
            canvas.coords(self.text_id, x, y)
            canvas.itemconfigure(self.text_id, text=str(self.cell_id))

    def __get_font(self, canvas):
        """
        get the font, and its size is depends on the size of the rectangle
        :param canvas: canvas
        :return: font with an appropriate size
        """
        x1, _, x2, _ = canvas.coords(self.rect_id)
        return "Helvetica", int((x2 - x1) / 3)
