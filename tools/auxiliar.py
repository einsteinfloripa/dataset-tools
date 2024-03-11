from pathlib import Path
import re

def __assert_dir(func):
    def wrapper(dir_path, *args, **kwargs):
        path = Path(dir_path)
        assert path.exists(), f"{dir_path} does not exist."
        assert path.is_dir(), f"{dir_path} is not a directory."
        return func(dir_path, *args, **kwargs)
    return wrapper

@__assert_dir
def get_img_label_pair(dir_path: Path) -> list[tuple[str, str]]:
    img_files = list(dir_path.glob("*.jpg")) + list(dir_path.glob("*.png"))
    label_files = list(dir_path.glob("*.txt"))
    
    if len(img_files) != len(label_files):
        raise ValueError(f"Number of images and labels do not match in {dir_path}")

    for img in img_files:
        pattern = re.compile(img.stem)
        if not any(pattern.match(label.stem) for label in label_files):
            raise ValueError(f"Image {img} does not have a label file in {dir_path}")
    return [(str(img), str(label)) for img, label in zip(img_files, label_files)]

@__assert_dir
def get_labels(dirpath: str) -> list[str]:
    label_files = list(dirpath.glob("*.txt"))
    return [str(path) for path in label_files]

@__assert_dir
def get_images(dirpath: str) -> list[str]:
    img_files = list(dirpath.glob("*.jpg")) + list(dirpath.glob("*.png"))
    return [str(path) for path in img_files]
