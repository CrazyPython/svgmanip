# `svgmanip`

Using`svgmanip`, you can easily rotate and scale SVGs on the fly. In Warfrogs, this code:

```python
from svgmanip import Element
output = Element(384, 356)  # size of the output file.

fate = Element('assets/fate.svg').rotate(-15)
skip = Element('assets/skip.svg').rotate(-5)
attack = Element('assets/attack.svg').rotate(5)
output.placeat(fate, 0.73, 23.55)
output.placeat(skip, 107.81, 8.76)
output.placeat(attack, 170.9, 0.08)

output.dump('output.svg')
```

Generates this image:

<img src="https://uploads.avertly.co/1b8.svg"/>

<center>*(the cropped edges are because of the output dimensions, which are customizable)*</center>

Unlike [`svgutils `](https://github.com/btel/svg_utils) (which this module is based on), `.rotate()` rotates about the center of the graphic, instead of the top left corner. This produces results the user would expect.

Did you notice that you didn't need to specify the dimensions of an imported image? That's because `svgmanip` detects it automatically behind the scenes!

## Documentation

`.rotate()` additionally supports passing optional `x` and `y` coordinates.

Since the `Element` class inherits from the `Figure` class in `svgutils`, it also supports these `svgutils` methods:

- `.scale(factor)` - scale the SVG by a particular factor
- `.find_id(element_id)` - find the inner SVG element with the given id. This method is guranteed to return an `Element` object from`svgmanip`.
- `.find_ids(element_ids)` - find the inner SVG elements with the given ids. This returns a [Panel object](https://svgutils.readthedocs.io/en/latest/compose.html#svgutils.compose.Panel) from `svgutils`.


`svgmanip` also supports these methods in addition to the ones listed in the example:

- `.dumps` - dump to a string
- `.loads` - load from a string
- `.load` - load from a file (*note:* using the default constructor is reccomended in this context)


## License

Apache 2.0. Example image of the Warfrogs cards is licensed under the [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode).