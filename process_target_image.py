import numpy as np
import cv2
import os
from os.path import isfile, join

from process_image_palette import PicturePalette


class PhotomosaicPainter:
    """
    Creates photo mosaics given a palette, and a target image.
    """

    def __init__(self, palette_path):
        self.palette = PicturePalette(palette_path)

    def create_photomosaic(self, target_image_path, width_in_images=None, height_in_images=None):
        """
        Creates an image based on the target image using its palette.

        If the width or height are not given, they are automatically set to some values in line with the target image's
        proportions. If only one is given, then the other value is generated based on the target image's proportions.
        If none are given, then the width is to be 10.

        :param target_image_path:
        :param width_in_images: How many images should span the final product width-wise.
        :param height_in_images: How many images should span the final product height-wise.
        :return: path to new image.
        """

        target_image = cv2.imread(target_image_path)

        # First, resize the palette.
        self.resize_palette(target_image.shape, width_in_images, height_in_images)

        # Then, resize the target image to the image/height width.
        target_image.resize((width_in_images, height_in_images))


        # TODO: Find the picture whose avg pixel value is closest for each pixel in the resized image.
        # TODO: Stitch together the palette's pictures to create a final picture.

    def resize_palette(self, target_image_shape, width_in_images=None, height_in_images=None):
        """

        :param target_image_shape: tuple containing (width, height) of target image.
        :param width_in_images:
        :param height_in_images:
        :return:
        """
        DEFAULT_WIDTH = 10

        # First, resize the palette.
        if width_in_images is None or height_in_images is None:
            if width_in_images is not None:
                height_in_images = round(width_in_images * target_image_shape[1] / target_image_shape[0])
            elif height_in_images is not None:
                width_in_images = round(height_in_images * target_image_shape[0] / target_image_shape[1])
            else:
                width_in_images = DEFAULT_WIDTH
                height_in_images = round(width_in_images * target_image_shape[1] / target_image_shape[0])

        palette_image_dimensions = (
            self.get_palette_image_dimensions(target_image_shape, width_in_images, height_in_images))

        self.palette.resize_images(palette_image_dimensions[0], palette_image_dimensions[1])

    @staticmethod
    def get_palette_image_dimensions(target_image_dimensions, width_in_images, height_in_images):
        """

        :param width_in_images:
        :param height_in_images:
        :param target_image_dimensions: a tuple s.t. (width, height)
        :return: width of each palette image, height of each palette image.
        """

        return round(target_image_dimensions[0] / width_in_images), round(target_image_dimensions[1] / height_in_images)


if __name__ == "__main__":
    pass
