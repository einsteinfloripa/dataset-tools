import cv2
from tools.auxiliar import (
get_img_label_pairs,
get_labels,
get_images,
mkdir_if_success)

class LabelHandler:

    @staticmethod
    @mkdir_if_success
    def filter_labels(
            path : str,
            wanted_classes : list[int],
            output_dir = 'filtered_labels'
            ):
        paths = get_labels(path)
        for p in paths:
            name = p.split("/")[-1]
            with open(p, 'r') as file:
                annotations = file.readlines()
            new_annotations = []
            for annotation in annotations:
                class_id, x_center, y_center, box_width, box_height = map(float, annotation.split())
                if int(class_id) in wanted_classes:
                    new_annotations.append(annotation)
            with open(f'{output_dir}/{name}', 'w') as file:
                file.writelines(new_annotations)
    
    @staticmethod
    @mkdir_if_success
    def change_labels(
            path : str,
            remap_dict : dict[int, int],
            output_dir = 'remaped_labels'
            ):
        paths = get_labels(path)
        for path in paths:
            name = path.split("/")[-1]
            with open(path, 'r') as file:
                annotations = file.readlines()
                new_annotations = []
                for annotation in annotations:
                    class_id, x_center, y_center, box_width, box_height = map(float, annotation.split())
                    if int(class_id) in remap_dict:
                        class_id = remap_dict[int(class_id)]
                    new_annotations.append(f"{int(class_id)} {x_center} {y_center} {box_width} {box_height}\n")
            with open(f'{output_dir}/{name}', 'w') as file:
                file.writelines(new_annotations)