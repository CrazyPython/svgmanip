from __future__ import division
import re
import os
from tempfile import NamedTemporaryFile

import svgutils
from lxml import etree
import mpmath as math
from ensure import ensure
from svgutils.compose import SVG, Figure, Unit
from svgutils import transform as _transform

math.dps = 17  # SVG's precision is double, which may be up to 17 digits

__all__ = ['Element']


def rotate_point(x, y, degrees):
    radians = math.radians(degrees)

    cos_theta = math.cos(radians)
    sin_theta = math.sin(radians)
    return x * cos_theta - y * sin_theta, \
           x * sin_theta + y * cos_theta


def get_shift_and_dims(points, degrees):
    rotated = [
        rotate_point(*point, degrees=degrees)
        for point in points
    ]

    unrotated = points

    # find highest x in rotated
    max_x_unrotated = max(unrotated, key=lambda point: point[0])[0]
    max_y_unrotated = max(unrotated, key=lambda point: point[1])[1]

    max_x_rotated = max(rotated, key=lambda point: point[0])[0]
    max_y_rotated = max(rotated, key=lambda point: point[1])[1]
    min_x_rotated = min(rotated, key=lambda point: point[0])[0]
    min_y_rotated = min(rotated, key=lambda point: point[1])[1]

    # Python's float is double precision so we can convert losslessly
    # However, mpmath has higher precision for  sin, cos, and tan.
    shift = float(max_x_rotated - max_x_unrotated), float(max_y_rotated - max_y_unrotated)
    dims = max_x_rotated - min_x_rotated, max_y_rotated - min_y_rotated
    return shift, dims


def get_quad_shift_and_dims(width, height, degrees):
    return get_shift_and_dims(
        [(+width / 2, -height / 2),
         (-width / 2, -height / 2),
         (+width / 2, +height / 2),
         (-width / 2, +height / 2), ],
        degrees,
    )


class Element(Figure):
    @staticmethod
    def _parse_string_dimension(dimension):
        if dimension is None:
            raise ValueError('Expected `dimension` to be str, Unit, float, or int, got None.')

        if isinstance(dimension, str):
            dimension = dimension.strip()
            groups = re.match(r'(\d+)\w*', dimension).groups()
            assert len(groups) == 1  # if this errors, your SVG probably has an invalid size!
            return float(groups[0])
        elif isinstance(dimension, Unit):
            return dimension.to('px').value
        elif isinstance(dimension, float) or isinstance(dimension, int):
            return dimension  # it *should* be a float

    def __init__(self, width_or_filename, height=None, *svgelements):
        if height is None:
            # some pretty hacky code to autodetect height
            assert len(svgelements) == 0
            svgfigure = svgutils.transform.fromfile(width_or_filename)
            svg = SVG(width_or_filename).scale(1)  # scale of 1 converts to an Element
            super(Element, self).__init__(self._parse_string_dimension(svgfigure.width),
                                          self._parse_string_dimension(svgfigure.height), svg)
        else:
            super(Element, self).__init__(width_or_filename, height, *svgelements)

    def placeat(self, element, x, y):
        ensure(element).is_an(Element)
        ensure(x).is_numeric()
        ensure(y).is_numeric()
        super(Element, self).__init__(self.width, self.height, self, element.move(x, y))

    @property
    def width(self):
        return self._parse_string_dimension(self._width)

    @width.setter
    def width(self, new):
        self._width = new

    @property
    def height(self):
        return self._parse_string_dimension(self._height)

    @height.setter
    def height(self, new):
        self._height = new

    def rotate(self, angle, x=None, y=None):
        if x is None and y is None:
            self.rotate(angle, self._parse_string_dimension(self.width) / 2,
                        self._parse_string_dimension(self.height) / 2)
            # height then width
            quad_shift, quad_dims = get_quad_shift_and_dims(self.width, self.height, angle)
            figure = type(self)(quad_dims[0], quad_dims[1], self)
            figure.move(*quad_shift)

            return figure
        else:
            ensure(x).is_numeric()
            ensure(y).is_numeric()
            return super(Element, self).rotate(angle, x, y)

    @staticmethod
    def loads(string):
        return svgutils.transform.fromstring(string)

    @staticmethod
    def load(filename):
        return svgutils.transform.fromfile(filename)

    def dumps(self):
        # the default .tostr() function fails to return the same text .dump() would return
        element = _transform.SVGFigure(self.width, self.height)
        element.append(self)
        out = etree.tostring(element.root, xml_declaration=True,
                             standalone=True,
                             pretty_print=True)
        # but even this doesn't make it. The encoding must be changed to UTF-8 (otherwise svgexport fails)
        out = out.replace("version='1.0'", 'version="1.0"')
        out = out.replace("encoding='ASCII'", 'encoding="UTF-8"')
        return out

    def dump(self, filename):
        return self.save(filename)

    def to_png(self, width, height=None):
        # rather unfortunately, the two available python libraries either
        #  a) don't support Python 2.7 or b) generate awful images
        if height is None:
            wh_string = width
        else:
            wh_string = "{}:{}".format(width, height)
        # svgexport fails on files missing the svg extension
        in_tempfile = NamedTemporaryFile(suffix=".svg", delete=False)
        in_tempfile.write(self.dumps())

        # svgexport also fails if the file isn't closed
        in_tempfile.close()

        out_tempfile = NamedTemporaryFile()
        command = 'svgexport {} {} {} > /dev/null'.format(in_tempfile.name, out_tempfile.name, wh_string)
        exit_code = os.system(command)
        if exit_code != 0:
            raise RuntimeError("External command svgexport failed")
        out_tempfile.seek(0)
        return out_tempfile.read()

    def save_as_png(self, filename, width, height=None):
        with open(filename, mode="wb") as f:
            f.write(self.to_png(width, height))

    def find_id(self, element_id):
        """Find a single element with the given ID.

        Parameters
        ----------
        element_id : str
            ID of the element to find

        Returns
        -------
        found element
        """
        element = _transform.FigureElement.find_id(self, element_id)
        return type(self)(element.root)
