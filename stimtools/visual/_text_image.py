import numpy as np

import PIL.Image
import PIL.ImageFont
import PIL.ImageDraw


def image_with_text(img_size, text, text_pos, font_name="arial", font_size=64):
    """Basic text drawing into an image.

    Parameters
    ----------
    img_size: two-item collection of ints, (width, height)
        Size of the output image.
    text: str
        The text to write.
    text_pos: two-item collection of numbers
        Top left edge of the text, with (0, 0) in the top-left corner.
    font_name: str, optional
        Font face.
    font_size: int, optional
        Size of the text, in points.

    Returns
    -------
    img: np.array, shape `img_size[::-1]`
        Image with the text drawn. The background is 255 and the text is 0.

    """

    img = PIL.Image.new(mode="L", size=img_size, color=255)

    font = PIL.ImageFont.truetype(font=font_name, size=font_size)

    drawer = PIL.ImageDraw.Draw(im=img)

    drawer.text(xy=text_pos, text=text, font=font)

    return np.array(img)
