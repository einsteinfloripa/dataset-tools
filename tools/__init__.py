import cv2
from auxiliar import get_pair_img_labels

class Cropper:
    
    class Condition:
        
        class AfterCrop:
            pass

        class BeforeCrop:
            pass
        
        class Custom():
            pass


    def crop_detections(
                path : str,
                target_class_id : int,
                output_dir = 'output',
                condition = None | Condition):
            # Read the image

        for pair in get_pair_img_labels(path):
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
            target_boxes = []
            for annotation in annotations:
                class_id, x_center, y_center, box_width, box_height = map(float, annotation.split())
                if int(class_id) == target_class_id:
                    x_center *= width
                    y_center *= height
                    box_width *= width
                    box_height *= height

                    x_min = int(x_center - box_width / 2)
                    y_min = int(y_center - box_height / 2)
                    x_max = int(x_center + box_width / 2)
                    y_max = int(y_center + box_height / 2)

                    target_bbox = (x_min, y_min, x_max, y_max)
                    target_boxes.append(target_bbox)

            #TODO: implementa a way to check if the boxes ovelap too much
                    
            if len(target_boxes) == 0:
                raise ValueError(f"No bounding box found for class {target_class_id} in {label_path}")

            for i, target_bbox in enumerate(target_boxes):
                # Crop the region of interest
                cropped_image = image[target_bbox[1]:target_bbox[3], target_bbox[0]:target_bbox[2]]

                # Save the cropped image
                output_image_path = f'{output_dir}/{image_name}-crop-{target_class_id}-{i}.jpg'
                cv2.imwrite(output_image_path, cropped_image)

                # Adjust the annotations for the cropped image
                adjusted_annotations = []
                for annotation in annotations:
                    class_id, x_center, y_center, box_width, box_height = map(float, annotation.split())
                    x_center *= width
                    y_center *= height
                    box_width *= width
                    box_height *= height

                    # Check if the current class is within the target class bounding box
                    if int(class_id) != target_class_id and target_bbox[0] < x_center < target_bbox[2] and target_bbox[1] < y_center < target_bbox[3]:
                        # Convert coordinates to be relative to the cropped image
                        new_x_center = (x_center - target_bbox[0]) / (target_bbox[2] - target_bbox[0])
                        new_y_center = (y_center - target_bbox[1]) / (target_bbox[3] - target_bbox[1])

                        new_width = box_width / (target_bbox[2] - target_bbox[0])
                        new_height = box_height / (target_bbox[3] - target_bbox[1])

                        if condition is not None:
                            pass
                            #TODO: implement the condition

                        adjusted_annotations.append(f"{int(class_id)} {new_x_center} {new_y_center} {new_width} {new_height}\n")

                # Save the adjusted annotations to a text file
                output_annotations_path = output_image_path.replace('.jpg', '.txt')
                with open(output_annotations_path, 'w') as output_file:
                    output_file.writelines(adjusted_annotations)