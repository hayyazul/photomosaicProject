import numpy as np
import cv2
import os
from os.path import isfile, join

from process_image_palette import PicturePalette


class PhotomosaicPainter:
    """
    Creates photo mosaics given a palette, and a target image.
    """

    DEFAULT_WIDTH = 10

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
        target_image = cv2.cvtColor(target_image, cv2.COLOR_BGR2RGB)  # Make sure it is in RGB

        # First, make sure width and height are properly defined.
        width_in_images, height_in_images = (
            self.define_width_height(target_image.shape, width_in_images, height_in_images))

        # Then, resize the palette.
        self.resize_palette(target_image.shape, width_in_images, height_in_images)

        # Then, resize the target image to the height width in images.
        scaled_img = cv2.resize(target_image, (width_in_images, height_in_images))

        # Create the "canvas," an array to contain the indices of the images whose average pixel value
        # is closest to the pixel value of the scaled down image.
        image_canvas = np.zeros((height_in_images, width_in_images), dtype=np.uint8)
        self.fill_image_canvas(scaled_img, image_canvas)

        import matplotlib.pyplot as plt

        plt.imshow(image_canvas)
        plt.show()

        # TODO: Stitch together the palette's pictures to create a final picture.

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

        self.palette.resize_images(palette_image_dimensions[0], palette_image_dimensions[1])

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

    def stitch_images_together(self, image_canvas):
        """
        Given an image_canvas with indices corresponding to each picture in the palette, an image is generated
        by stitching these pictures together.

        :param image_canvas: Array w/ each element corresponding to an index in the palette's selection of pictures.
        :return:
        """
        pass

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
    photomosaic_maker = PhotomosaicPainter(join("./photomosaic palette"))
    photomosaic_maker.create_photomosaic(join("./Bliss.jpg"))
