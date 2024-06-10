import cv2
from dsTools.auxiliar import (
PathParsers,
mkdir_if_success)

class Drawer:
    
    colors = [
        (0, 255, 0),
        (0, 0, 255),
        (255, 0, 0),
        (255, 255, 0),
        (0, 255, 255),
        (255, 0, 255),
        (255, 255, 255),
        (0, 0, 0),
        (128, 128, 128),
        (128, 0, 0),
        (128, 128, 0),
        (0, 128, 0),
        (128, 0, 128),
        (0, 128, 128),
        (0, 0, 128)
    ]

    @classmethod
    @mkdir_if_success
    def draw_boxes(
        cls,
        path : str,
        output_dir = 'drawn_output'
    ):
        '''
        Copia as imagens de um diretório para um diretorio de saida,
        desenhando os bounding boxes de acordo com os labels.
        '''
        for pair in PathParsers.get_img_label_pairs(path):
            image_path, label_path = pair
            image = cv2.imread(image_path)
            height, width, _ = image.shape
            with open(label_path, 'r') as file:
                annotations = file.readlines()
            for annotation in annotations:
                class_id, x_center, y_center, box_width, box_height = map(float, annotation.split())
                x_center *= width
                y_center *= height
                box_width *= width
                box_height *= height
                x_min = int(x_center - box_width / 2)
                y_min = int(y_center - box_height / 2)
                x_max = int(x_center + box_width / 2)
                y_max = int(y_center + box_height / 2)
                cv2.rectangle(image, (x_min, y_min), (x_max, y_max), cls.colors[int(class_id)], 4)
            output_image_path = f'{output_dir}/{image_path.split("/")[-1]}'
            cv2.imwrite(output_image_path, image)
