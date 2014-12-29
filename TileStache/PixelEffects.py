""" Different effects that can be applied to tiles.

Options are:

- blackwhite:

    "effect":
    {
        "name": "blackwhite"
    }

- greyscale:

    "effect":
    {
        "name": "greyscale"
    }

- desaturate:
  Has an optional parameter "factor" that defines the saturation of the image.
  Defaults to 0.85.

    "effect":
    {
        "name": "desaturate",
        "factor": 0.85
    }

- pixelate:
  Has an optional parameter "reduction" that defines how pixelated the image
  will be (size of pixel). Defaults to 5.

    "effect":
    {
        "name": "pixelate",
        "factor": 5
    }

- halftone:

    "effect":
    {
        "name": "halftone"
    }

- blur:
  Has an optional parameter "radius" that defines the blurriness of an image.
  Larger radius means more blurry. Defaults to 5.

    "effect":
    {
        "name": "blur",
        "radius": 5
    }
"""

from PIL import Image, ImageFilter, ImageOps
from random import shuffle, randint


def put_original_alpha(original_image, new_image):
    """ Put alpha channel of original image (if any) in the new image.
    """

    try:
        alpha_idx = original_image.mode.index('A')
        alpha_channel = original_image.split()[alpha_idx]
        new_image.putalpha(alpha_channel)
    except ValueError:
        pass
    return new_image


class PixelEffect:
    """ Base class for all pixel effects.
        Subclasses must implement method `apply_effect`.
    """

    def __init__(self):
        pass

    # This method is called by render() in core.py.
    # Each actual pixel effect implementation subclasses from this base class.
    def apply(self, image):
        try:
            image = image.image()  # Handle Providers.Verbatim tiles
        except (AttributeError, TypeError):
            pass
        return self.apply_effect(image)

    def apply_effect(self, image):
        raise NotImplementedError(
            'PixelEffect subclasses must implement method `apply_effect`.'
        )


class Blackwhite(PixelEffect):
    """ Returns a black and white version of the original image.
    """

    def apply_effect(self, image):
        new_image = image.convert('1').convert(image.mode)
        return put_original_alpha(image, new_image)


class Greyscale(PixelEffect):
    """ Returns a grescale version of the original image.
    """

    def apply_effect(self, image):
        return image.convert('LA').convert(image.mode)


class Desaturate(PixelEffect):
    """ Returns a desaturated version of the original image.
        `factor` is a number between 0 and 1, where 1 results in a
        greyscale image (no color), and 0 results in the original image.
    """

    def __init__(self, factor=0.85):
        self.factor = min(max(factor, 0.0), 1.0)  # 0.0 <= factor <= 1.0

    def apply_effect(self, image):
        avg = image.convert('LA').convert(image.mode)
        return Image.blend(image, avg, self.factor)


class Pixelate(PixelEffect):
    """ Returns a pixelated version of the original image.
        `reduction` defines how pixelated the image will be (size of pixels).
    """

    def __init__(self, reduction=5):
        self.reduction = max(reduction, 1)  # 1 <= reduction

    def apply_effect(self, image):
        tmp_size = (int(image.size[0] / self.reduction),
                    int(image.size[1] / self.reduction))
        pixelated = image.resize(tmp_size, Image.NEAREST)
        return pixelated.resize(image.size, Image.NEAREST)


class Halftone(PixelEffect):
    """ Returns a halftone version of the original image.
    """

    def apply_effect(self, image):
        cmyk = []
        for band in image.convert('CMYK').split():
            cmyk.append(band.convert('1').convert('L'))
        new_image = Image.merge('CMYK', cmyk).convert(image.mode)
        return put_original_alpha(image, new_image)


class Blur(PixelEffect):
    """ Returns a blurred version of the original image.
        `radius` defines the blurriness of an image. Larger radius means more
        blurry.
    """

    def __init__(self, radius=5):
        self.radius = max(radius, 0)  # 0 <= radius

    def apply_effect(self, image):
        return image.filter(ImageFilter.GaussianBlur(self.radius))

class Solarize(PixelEffect):
    """
    Solarizes an image given a certain threshold:

    https://github.com/python-pillow/Pillow/blob/master/PIL/ImageOps.py#L396-L410
    """
    def __init__(self, threshold=128):
        self.threshold = threshold

    def apply_effect(self, image):
        # Need to convert to RGB or L image modes.
        # See: https://github.com/python-pillow/Pillow/blob/master/PIL/ImageOps.py#L47-L56
        # And: http://effbot.org/imagingbook/decoder.htm
        image = image.convert("RGB")
        return ImageOps.solarize(image, self.threshold)

class Shredder(PixelEffect):
    """
    Return a `shredded` image. Code Ported From:
    http://instagram-engineering.tumblr.com/post/12651721845/instagram-engineering-challenge-the-unshredder
    """

    def apply_effect(self, image):

        # If random number is even, shred the tile.
        if randint(1, 10) % 2 == 0:
            # Randomly generate shreds.
            SHREDS = randint(1, 10)
            shredded = Image.new("RGBA", image.size)
            width, height = image.size
            shred_width = width/SHREDS
            sequence = range(0, SHREDS)
            shuffle(sequence)

            for i, shred_index in enumerate(sequence):
                shred_x1, shred_y1 = shred_width * shred_index, 0
                shred_x2, shred_y2 = shred_x1 + shred_width, height
                region = image.crop((shred_x1, shred_y1, shred_x2, shred_y2))
                shredded.paste(region, (shred_width * i, 0))

            return shredded
        else:
            return image


class Multiball(PixelEffect):
    """
    Run a single tile through multiple effects.

    - User provides a list of affect names
    - Each will affect will have a 50/50 chance of being applied to each tile.
    """

    def __init__(self, effects):
        self.effects = effects

    def apply_effect(self, image):
        in_image = image

        while len(self.effects) > 0:
            effect_name = self.effects.pop()
            effect_instance = all[effect_name]()
            # 50/50 chance to apply effect to tile
            if randint(1, 10) % 2 == 0:
                mod_image = effect_instance.apply_effect(in_image)
            else:
                mod_image = in_image
            in_image = mod_image

        return in_image


        # return mod_image

        # Turn this into a while loop, popping off effects from the list.
        # for effect_name in self.effects:
        #     effect_instance = all[effect_instance]
        #     modified_image = effect_instance.apply_effect()




# Module level attribute mapping effect names as strings to classes.
# Used in config.py
all = {
    'blackwhite': Blackwhite,
    'greyscale': Greyscale,
    'desaturate': Desaturate,
    'pixelate': Pixelate,
    'halftone': Halftone,
    'blur': Blur,
    'solarize': Solarize,
    'shredder': Shredder,
    'multiball': Multiball
}
