import cv2
from tools.auxiliar import (
get_img_label_pairs,
get_labels,
get_images,
mkdir_if_success)


class Cropper:
    
    class Condition:
        
        class AfterCrop:
            pass

        class BeforeCrop:
            pass
        
        class Custom:
            pass

    @classmethod
    @mkdir_if_success
    def crop_detections(
                cls,
                path : str,
                target_class_id : int | list[int],
                output_dir = 'crop_output',
                condition : None | Condition = None,
                txt_file = True
                ):
            # Read the image

        for pair in get_img_label_pairs(path):
            image_path = pair[0]
            image_name = image_path.split("/")[-1].split(".")[0]
            label_path = pair[1]
            image = cv2.imread(image_path)

            # Get image dimensions
            height, width, _ = image.shape

            # Read YOLO annotations from the text file
            with open(label_path, 'r') as file:
                annotations = file.readlines()

            # Find the target class bounding box
            target_boxes = cls.__get_target_boxes(target_class_id, annotations, width, height)

            #TODO: implementa a way to check if the boxes ovelap too much
                    
            if len(target_boxes) == 0:
                print(f"No bounding box found for class {target_class_id} in {label_path}")
                continue

            for i, detection in enumerate(target_boxes):
                id, bbox = detection
                # Crop the region of interest
                cropped_image = image[bbox[1]:bbox[3], bbox[0]:bbox[2]]

                # Save the cropped image
                output_image_path = f'{output_dir}/{image_name}-crop-{id}-{i}.jpg'
                cv2.imwrite(output_image_path, cropped_image)

                if not txt_file:
                    continue
                # Adjust the annotations for the cropped image
                adjusted_annotations = []
                for annotation in annotations:
                    class_id, x_center, y_center, box_width, box_height = map(float, annotation.split())
                    x_center *= width
                    y_center *= height
                    box_width *= width
                    box_height *= height

                    # Check if the current class is within the target class bounding box
                    if int(class_id) != target_class_id and bbox[0] < x_center < bbox[2] and bbox[1] < y_center < bbox[3]:
                        # Convert coordinates to be relative to the cropped image
                        new_x_center = (x_center - bbox[0]) / (bbox[2] - bbox[0])
                        new_y_center = (y_center - bbox[1]) / (bbox[3] - bbox[1])

                        new_width = box_width / (bbox[2] - bbox[0])
                        new_height = box_height / (bbox[3] - bbox[1])

                        if condition is not None:
                            pass
                            #TODO: implement the condition

                        adjusted_annotations.append(f"{int(class_id)} {new_x_center} {new_y_center} {new_width} {new_height}\n")

                # Save the adjusted annotations to a text file
                output_annotations_path = output_image_path.replace('.jpg', '.txt')
                with open(output_annotations_path, 'w') as output_file:
                    output_file.writelines(adjusted_annotations)



    def __get_target_boxes(target_class_id, annotations, width, height):
        target_boxes = []
        for id in target_class_id:
            for annotation in annotations:
                class_id, x_center, y_center, box_width, box_height = map(float, annotation.split())
                if int(class_id) == id:
                    x_center *= width
                    y_center *= height
                    box_width *= width
                    box_height *= height

                    x_min = int(x_center - box_width / 2)
                    y_min = int(y_center - box_height / 2)
                    x_max = int(x_center + box_width / 2)
                    y_max = int(y_center + box_height / 2)

                    bbox = (x_min, y_min, x_max, y_max)
                    target_boxes.append((int(id), bbox))
        return target_boxes
