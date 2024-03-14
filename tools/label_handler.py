import cv2
from tools.auxiliar import (
get_img_label_pairs,
get_labels,
get_images,
mkdir_if_success)

class LabelHandler:

    class Condition:

        @staticmethod
        def sorce_grater_than_dest(
            locals
        ):
            locals.update({ 'skip_file' : locals['n_sorce'] > locals['n_dest']})

    @staticmethod
    @mkdir_if_success
    def filter_labels(
            path : str,
            wanted_classes : list[int],
            output_dir = 'filtered_labels'
            ):
        paths = get_labels(path)
        for p in paths:
            name = p.split("\\")[-1]
            with open(p, 'r') as file:
                annotations = file.readlines()
            new_annotations = []
            for annotation in annotations:
                class_id, x_center, y_center, box_width, box_height = map(float, annotation.split())
                if int(class_id) in wanted_classes:
                    new_annotations.append(annotation)
            with open(f'{output_dir}\\{name}', 'w') as file:
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
            name = path.split("\\")[-1]
            with open(path, 'r') as file:
                annotations = file.readlines()
                new_annotations = []
                for annotation in annotations:
                    class_id, x_center, y_center, box_width, box_height = map(float, annotation.split())
                    if int(class_id) in remap_dict:
                        class_id = remap_dict[int(class_id)]
                    new_annotations.append(f"{int(class_id)} {x_center} {y_center} {box_width} {box_height}\n")
            with open(f'{output_dir}\\{name}', 'w') as file:
                file.writelines(new_annotations)
    
    @staticmethod
    @mkdir_if_success
    def merge_labels(
        source_path : str,
        dest_path : str,
        merge_ids : list[int],
        condition = None,
        output_dir = 'merged_labels'
    ):
        source_paths = get_labels(source_path)
        dest_paths = get_labels(dest_path)
        source_paths.sort()
        dest_paths.sort()
        for sp, dp in zip(source_paths, dest_paths):
            spname = sp.split("\\")[-1]
            dpname = dp.split("\\")[-1]
            if spname != dpname:
                raise Exception("Source and dest paths must have the same names")

        for path_sorce, path_dest in zip(source_paths, dest_paths):
            new_lines = []
            for id in merge_ids:
                with open(path_sorce, 'r') as file:
                    source_annotations = file.readlines()
                with open(path_dest, 'r') as file:
                    dest_annotations = file.readlines()
                
                source_lines = LabelHandler.__get_id_lines(id, source_annotations)
                dest_lines = LabelHandler.__get_id_lines(id, dest_annotations)
                n_sorce = len(source_lines)
                n_dest = len(dest_lines)

                for line in source_lines:
                    l = locals()
                    condition(l)
                    if l.get('skip_file'):
                        break
                    if l.get('skip_line'):
                        continue
                    new_lines.append(line)

                if l.get('skip_file'):
                    break
                elif l.get('skip_line'):
                    continue
            if new_lines:
                name = path_sorce.split("\\")[-1]
                with open(output_dir + '\\' + name, 'w') as file:
                    file.writelines(dest_lines)
                    file.write('\n')
                    file.writelines(new_lines)
                    
                

    @staticmethod
    def __get_id_lines(id : int, lines : list[str]):
        return [line for line in lines if int(line.split()[0]) == id]


