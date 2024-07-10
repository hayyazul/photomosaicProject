from process_target_image import PhotomosaicPainter
from process_image_palette import PicturePalette

from os.path import join

INPUT_IMAGES = "Your filepath to a file with photos. It may contain non-image elements as those are ignored by the program. Photos in subdirectories are not used."
TARGET_IMAGE = "Filepath to an image."

if __name__ == "__main__":
    photomosaic_maker = PhotomosaicPainter(join(INPUT_IMAGES), 1, 20000 * 10000)
    photomosaic_maker.diagnostics = True
    photomosaic_maker.create_photomosaic(join(TARGET_IMAGE),
                                         168, 105, 4)

