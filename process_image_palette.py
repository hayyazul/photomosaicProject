import cv2
import os
from os.path import isfile, join, basename, exists
import shutil
import numpy as np

PICTURES_FOLDER_PATH = "./photomosaic palette"

def check_if_file_is_image(file_path):
    """
    Checks if file is an image or not.

    :param file_path:
    :return: bool whether the given file path points to an image or not.
    """
    image = cv2.imread(file_path)

    try:
        dummy = image.shape  # this line will throw an exception if it is not an image.
        return True
    except:
        return False


def convert_pictures_into_arrays(width, height, *image_paths):
    """
    Takes in paths to images, converts them into np.ndarray

    :param height:
    :param width:
    :param image_paths:
    :return: list[np.ndarray] where each array is a rgb representation of the picture.
    """
    picture_arrays = []
    for image_path in image_paths:
        raw_picture = cv2.imread(image_path)
        picture_resized = cv2.resize(raw_picture, (width, height), interpolation=cv2.INTER_LINEAR)
        picture_in_rgb = cv2.cvtColor(picture_resized, cv2.COLOR_BGR2RGB)

        picture_arrays.append(picture_in_rgb)

    return picture_arrays


class PicturePalette:
    """
    Given a filepath, this class collects all the images in it into a single list, creates a temporary file to store
    resized versions of these images, and has some methods to help with creating a photomosaic.
    """

    def __init__(self, dir_path, picture_width=None, picture_height=None):

        if picture_width is None or picture_height is None:
            picture_width, picture_height = 1, 1  # Default value

        # First, make the directory that will contain the resized images.
        self.temp_palette_folder_path = os.path.join("temp", "palette")
        if exists(self.temp_palette_folder_path):
            shutil.rmtree(self.temp_palette_folder_path)
        os.mkdir(self.temp_palette_folder_path)

        self.picture_average_pixel_values = []
        self.picture_arrays = []  # type: list[np.ndarray]
        self.picture_paths = []
        self.original_picture_paths = []

        # Find the items in a directory which are actually pictures.
        directory_items = os.listdir(dir_path)
        for directory_item in directory_items:
            path_to_file = join(dir_path, directory_item)
            if isfile(path_to_file):
                if check_if_file_is_image(path_to_file):
                    self.original_picture_paths.append(path_to_file)
                    self.picture_paths.append(join(self.temp_palette_folder_path, directory_item))

                    self.add_picture_to_palette_directory(path_to_file, picture_width, picture_height)

        if len(self.picture_paths) == 0:
            raise Exception(f"No images found in directory {dir_path}")

        self.picture_arrays = convert_pictures_into_arrays(picture_width, picture_height, *self.picture_paths)
        self.get_average_pixel_values()

    def resize_images(self, new_width, new_height):
        """
        Resizes all the images within the palette to the new value. Also updates all other values which use the palette
        image's height/width.

        This is done by getting rid of the old palette, then regenerating them with the new dimensions.

        :param new_width:
        :param new_height:
        :return:
        """
        for palette_image_path, original_image_path in zip(self.picture_paths, self.original_picture_paths):
            os.remove(palette_image_path)
            self.add_picture_to_palette_directory(original_image_path, new_width, new_height)

        self.picture_arrays = convert_pictures_into_arrays(new_width, new_height, *self.picture_paths)
        self.get_average_pixel_values()

    def add_picture_to_palette_directory(self, image_path, new_width, new_height):
        raw_picture = cv2.imread(image_path)
        picture_resized = cv2.resize(raw_picture, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

        cv2.imwrite(os.path.join(self.temp_palette_folder_path, basename(image_path)), picture_resized)

    def get_average_pixel_values(self):
        """

        :return: None, but sets self.picture_arrays to its appropriate values.
        """
        self.picture_average_pixel_values = [picture_array.sum(0).sum(0) / (picture_array.shape[0] * picture_array.shape[1])
                                             for picture_array in self.picture_arrays]

    def find_picture_closest_to_rgb_value(self, rgb_array):
        """

        :param rgb_array: np.ndarray with values from 0 to 255
        :return: index of picture with avg pixel rgb closest to the given rgb value.
        """
        avg_pixel_values_as_array = np.array(self.picture_average_pixel_values)
        difference_array = avg_pixel_values_as_array - rgb_array
        distances = (difference_array ** 2).sum(1) ** (1/2)
        closest_index = int(np.argmin(distances))

        return closest_index


if __name__ == "__main__":
    palette = PicturePalette(PICTURES_FOLDER_PATH, 100, 100)
    palette.resize_images(200, 200)
    myIndex = palette.find_picture_closest_to_rgb_value(np.array([200, 0, 0]))
    pass
