import random
from typing import List

# https://gist.github.com/adewes/5884820

locked_color = ["spring green", "firebrick1"]


def get_random_color(pastel_factor=0.5):
    return [
        (x + pastel_factor) / (1.0 + pastel_factor)
        for x in [random.uniform(0, 1.0) for _ in [1, 2, 3]]
    ]


def color_distance(c1, c2):
    return sum([abs(x[0] - x[1]) for x in zip(c1, c2)])


def generate_new_color(existing_colors, pastel_factor=0.5):
    max_distance = None
    best_color = None
    for _ in range(0, 10):
        color = get_random_color(pastel_factor=pastel_factor)
        if not existing_colors:
            return color
        best_distance = min([color_distance(color, c) for c in existing_colors])
        if not max_distance or best_distance > max_distance:
            max_distance = best_distance
            best_color = color
    return best_color


def from_rgb(rgb) -> str:
    """
    :param rgb: an rgb tuple of int
    :return: a tkinter friendly color code
    """
    rgb = [int(x * 255) for x in rgb]
    r, g, b = rgb
    return "#{:02X}{:02X}{:02X}".format(r, g, b)


def random_colors(n) -> List[str]:
    """
    :param n: the number of colors required
    :return: a list of n unique random colors
    """
    colors, ret = [], []

    for _ in range(n):
        color = generate_new_color(colors, pastel_factor=0.3)
        colors.append(color)
        ret.append(from_rgb(color))

    return ret
