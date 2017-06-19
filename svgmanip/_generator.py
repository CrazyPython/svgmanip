from __future__ import division
import re
import svgutils
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


def rotate_from_svgobj(svgobj, width, height, degrees):
    svgobj.rotate(degrees, width / 2, height / 2)
    # height then width
    quad_shift, quad_dims = get_quad_shift_and_dims(width, height, degrees)
    figure = Figure(quad_dims[0], quad_dims[1], svgobj)

    figure.move(*quad_shift)
    return figure


def rotate_from_file(filename, width, height, degrees, output_filename):
    original = SVG(filename)
    figure = rotate_from_svgobj(original)
    figure.save(output_filename)


def arrange_images(images, positions, dimensions, final_width, final_height, degrees=None, scalings=None):
    if scalings is None:
        scalings = [1] * len(images)
    if degrees is None:
        degrees = [0] * len(images)

    parameters = [
        rotate_from_svgobj(svgutils.transform.fromstring(image).scale(scaling), *dimension, degrees=degree,
                           position=position) for
        image, position, dimension, scaling, degree in
        zip(images, positions, dimensions, scalings, degrees)
    ]
    figure = Figure(final_width, final_height, *parameters)
    return figure.tostr()


class Element(Figure):
    @staticmethod
    def _parse_string_dimension(dimension):
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
    def load(self, filename):
        return svgutils.transform.fromfile(filename)

    def dumps(self):
        return self.tostr()

    def dump(self, filename):
        return self.save(filename)

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
