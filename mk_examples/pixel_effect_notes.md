# Implementation Notes

These notes reference this [commit][1].

1. A config file is parsed in `config.py`. Each layer is searched for a `pixel effect` parameter.
2. An additional parameter `pixel_effect` is added to the `layer` object in `config.py`.
3. When a layer is rendered in `Core.py` that contains a `pixel_effect` parameter, the
   Pixel Effect's `apply()` method is called.
4. Pixel Effect classes must subclass the `PixelEffect` class, and must override the `apply_effect()`
   method.

# References of Interest

PIL ImageOps: https://github.com/python-pillow/Pillow/blob/master/PIL/ImageOps.py

# PIL Image Modes

| mode    | description |
| ------- | ---------- |
| “1”     | 1-bit bilevel, stored with the leftmost pixel in the most significant bit. 0 means black, 1 means white. |
| “1;I”   | 1-bit inverted bilevel, stored with the leftmost pixel in the most significant bit. 0 means white, 1 means black. |
| “1;R”   | 1-bit reversed bilevel, stored with the leftmost pixel in the least significant bit. 0 means black, 1 means white. |
| “L”     | 8-bit greyscale. 0 means black, 255 means white. |
| “L;I”   | 8-bit inverted greyscale. 0 means white, 255 means black. |
| “P”     | 8-bit palette-mapped image. |
| “RGB”   | 24-bit true colour, stored as (red, green, blue). |
| “BGR”   | 24-bit true colour, stored as (blue, green, red). |
| “RGBX”  | 24-bit true colour, stored as (blue, green, red, pad). |
| “RGB;L” | 24-bit true colour, line interleaved (first all red pixels, the all green pixels, finally all blue pixels). |

[1]: https://github.com/TileStache/TileStache/pull/204/files?diff=split