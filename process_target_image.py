import math

import numpy as np
import cv2
import os
from os.path import isfile, join
from PIL import Image

from process_image_palette import PicturePalette


class PhotomosaicPainter:
    """
    Creates photo mosaics given a palette, and a target image.
    """

    MAX_PHOTO_SIZE = 10000 * 5000
    DEFAULT_WIDTH = 10

    def __init__(self, palette_path, scale_factor=1, max_photo_size=10000*5000, diagnostics=False):

        self.MAX_PHOTO_SIZE = max_photo_size
        self.palette = PicturePalette(palette_path)
        self.scale_factor = scale_factor

        self.diagnostics = False

    def create_photomosaic(self, target_image_path, width_in_images=None, height_in_images=None, scale_factor=1.0):
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

        self.scale_factor = scale_factor

        if self.diagnostics:
            print("Reading target image...")

        target_image = cv2.imread(target_image_path)
        target_image = cv2.cvtColor(target_image, cv2.COLOR_BGR2RGB)  # Make sure it is in RGB
        # Note: target_image is in (height, width); but (width, height) is the standard ordering scheme, so you must
        # account for this.

        if self.diagnostics:
            try:
                dummy = target_image.shape
            except:
                print(f"Failed to read target image {target_image_path}")

        if (self.scale_factor ** 2) * target_image.shape[0] * target_image.shape[1] > self.MAX_PHOTO_SIZE:
            raise Exception(f"Picture is too big: px count "
                            f"{(self.scale_factor ** 2) * target_image.shape[0] * target_image.shape[1]} > "
                            f"{self.MAX_PHOTO_SIZE}")

        # First, make sure width and height are properly defined.
        width_in_images, height_in_images = (
            self.define_width_height(target_image.shape[1::-1], width_in_images, height_in_images))

        if self.diagnostics:
            print(f"Using image width {width_in_images} and height {height_in_images}")

        # TODO: check if palette is already loaded; then don't resize it.
        # Then, resize the palette.
        self.resize_palette(target_image.shape, width_in_images, height_in_images)

        # Then, resize the target image to the height width in images.
        scaled_img = cv2.resize(target_image, (width_in_images, height_in_images))

        if self.diagnostics:
            print("Creating canvas...")

        # Create the "canvas," an array to contain the indices of the images whose average pixel value
        # is closest to the pixel value of the scaled down image.
        image_canvas = np.zeros((height_in_images, width_in_images), dtype=np.uint16)
        self.fill_image_canvas(scaled_img, image_canvas)

        if self.diagnostics:
            print("Stitching together images...")
        # TODO: Stitch together the palette's pictures to create a final picture.
        output_image = self.stitch_images_together(image_canvas)

        if self.diagnostics:
            print("Finished.\n   ---   ")

        return output_image

    def define_width_height(self, target_image_shape, width_in_images=None, height_in_images=None):
        """
        If

        :param target_image_shape:
        :param width_in_images:
        :param height_in_images:
        :return:
        """
        if width_in_images is None or height_in_images is None:
            if width_in_images is not None:
                height_in_images = round(width_in_images * target_image_shape[1] / target_image_shape[0])
            elif height_in_images is not None:
                width_in_images = round(height_in_images * target_image_shape[0] / target_image_shape[1])
            else:
                width_in_images = self.DEFAULT_WIDTH
                height_in_images = round(width_in_images * target_image_shape[1] / target_image_shape[0])

        return width_in_images, height_in_images

    def resize_palette(self, target_image_shape, width_in_images=None, height_in_images=None):
        """

        :param target_image_shape: tuple containing (width, height) of target image.
        :param width_in_images:
        :param height_in_images:
        :return:
        """

        palette_image_dimensions = (
            self.get_palette_image_dimensions(target_image_shape, width_in_images, height_in_images))

        self.palette.resize_images(round(self.scale_factor * palette_image_dimensions[0]),
                                   round(self.scale_factor * palette_image_dimensions[1]))

    def fill_image_canvas(self, scaled_down_target_image: np.ndarray, image_canvas: np.ndarray):
        """
        Given an image canvas and a scaled down target image, it fills it with the indices of the pictures whose average
        pixel value is closest to each pixel in the scaled down target image.
        :param scaled_down_target_image:
        :param image_canvas:
        :return:
        """
        if scaled_down_target_image.shape[:2] != image_canvas.shape[:2]:
            raise Exception("Dimension mismatch between scaled down image and image canvas!")

        for i in range(image_canvas.shape[0]):
            for j in range(image_canvas.shape[1]):
                image_canvas[i, j] = self.palette.find_picture_closest_to_rgb_value(scaled_down_target_image[i, j])

    # TODO: Make everything in height, width format.
    # TODO: Fix bug where the stitched images have a gap and are rotated 90 degrees.
    def stitch_images_together(self, image_canvas):
        """
        Given an image_canvas with indices corresponding to each picture in the palette, an image is generated
        by stitching these pictures together.

        :param image_canvas: Array w/ each element corresponding to an index in the palette's selection of pictures.
        :return:
        """

        # The picture arrays are in (height, width) format too.
        picture_palette_width = self.palette.picture_arrays[0].shape[1]
        picture_palette_height = self.palette.picture_arrays[0].shape[0]

        # First, find the total size of the output image.
        output_image_width = image_canvas.shape[1] * picture_palette_width
        output_image_height = image_canvas.shape[0] * picture_palette_height

        # Then, create a new image with this given width/height.
        output_image = Image.new('RGB', (output_image_width, output_image_height), (100, 100, 100))

        # Finally, draw on the canvas in the corresponding areas.
        for i in range(image_canvas.shape[0]):
            for j in range(image_canvas.shape[1]):
                output_image.paste(self.palette.picture_as_pillow_images[image_canvas[i, j]],
                                   (j * picture_palette_width, i * picture_palette_height))

        output_image.save(join("./out_dir/output.png"), "png")
        output_image.show()

        return output_image

    def get_palette_image_dimensions(self, target_image_dimensions, width_in_images, height_in_images):
        """

        :param width_in_images:
        :param height_in_images:
        :param target_image_dimensions: a tuple s.t. (width, height)
        :return: width of each palette image, height of each palette image.
        """

        return (math.floor(self.scale_factor * target_image_dimensions[1] / width_in_images),
                math.floor(self.scale_factor * target_image_dimensions[0] / height_in_images))


if __name__ == "__main__":
    photomosaic_maker = PhotomosaicPainter(join("C:/Users/Ayyaz/Pictures/iCloud Photos"), 1, 20000*10000)
    photomosaic_maker.diagnostics = True
    photomosaic_maker.create_photomosaic(join("C:/Users/Ayyaz/Pictures/632360_20220818163327_1.png"),
                                         168, 105, 4)
