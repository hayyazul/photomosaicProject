from process_target_image import PhotomosaicPainter
from process_image_palette import PicturePalette

from os.path import join

INPUT_IMAGES = "C:/Users/Ayyaz/Pictures/iCloud Photos"
TARGET_IMAGE = "C:/Users/Ayyaz/Pictures/632360_20220818163327_1.png"

if __name__ == "__main__":
    photomosaic_maker = PhotomosaicPainter(join(INPUT_IMAGES), 1, 20000 * 10000)
    photomosaic_maker.diagnostics = True
    photomosaic_maker.create_photomosaic(join(TARGET_IMAGE),
                                         168, 105, 4)

