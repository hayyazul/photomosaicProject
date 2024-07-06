import cv2
import os
from os.path import isfile, join

import numpy as np

PICTURES_FOLDER_PATH = "C:/Users/Ayyaz/Pictures/photomosaic palette"
PICTURE_FILETYPES = ("png", "jpg", "jpeg", "webp")


def check_if_file_is_image(file_path):
    image = cv2.imread(file_path)

    try:
        dummy = image.shape  # this line will throw the exception
        return True
    except:
        print("[INFO] Image is not available or corrupted.")
        return False


def convert_pictures_into_arrays(*image_paths):
    picture_arrays = []
    for image_path in image_paths:
        picture_arrays.append(cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB))

    return picture_arrays


class PicturePalette:
    """
    Given a filepath, this class collects all the images in it into a single list.
    """

    def __init__(self, dir_path):

        self.picture_average_pixel_values = []
        self.picture_arrays = []  # type: list[np.ndarray]
        self.picture_paths = []

        # Find the items in a directory which are actually pictures.
        directory_items = os.listdir(dir_path)
        for directory_item in directory_items:
            path_to_file = join(dir_path, directory_item)
            if isfile(path_to_file):
                if check_if_file_is_image(path_to_file):
                    self.picture_paths.append(path_to_file)

        if len(self.picture_paths) == 0:
            raise Exception(f"No images found in directory {dir_path}")

        self.picture_arrays = convert_pictures_into_arrays(*self.picture_paths)
        self.get_average_pixel_values()

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
    palette = PicturePalette(PICTURES_FOLDER_PATH)
    myIndex = palette.find_picture_closest_to_rgb_value(np.array([200, 0, 0]))
    pass
