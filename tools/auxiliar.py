import inspect
import re
from pathlib import Path


def mkdir_if_success(func):
    par = inspect.signature(func).parameters.get("output_dir")
    default = par.default
    def wrapper(*args, **kwargs):
        append = kwargs.get('append_to_dir', False)
        try: 
            path = Path(kwargs["output_dir"])
        except KeyError:
            path = Path(default)
        
        if path.exists() and not append:
            raise FileExistsError(f"{path} already exists.")
        path.mkdir(parents=True, exist_ok=True)
        
        try:
            func(*args, **kwargs)
        except Exception as e:
            if not append:
                path.rmdir()
            raise e
    return wrapper

# PATHS
def get_img_label_pairs(path: str, ignore_single=False) -> list[tuple[str, str]]:
    path = Path(path)
    if not path.is_dir():
        return [get_img_label_pair(path)]
    img_files = list(path.glob("*.jpg")) + list(path.glob("*.png"))
    label_files = list(path.glob("*.txt"))
    
    if len(img_files) != len(label_files):
        raise ValueError(f"Number of images and labels do not match in {path}")

    labels = []
    for l in label_files:
        labels.append(l.stem)
    found = []
    for img in img_files:
        if img.stem in labels:
            found.append((str(img), f"{str(img.parent)}/{str(img.stem)}.txt"))
            continue
        if not ignore_single:    
            raise ValueError(f"Image {img} does not have a label file in {path}")
        
    return found

def get_img_label_pair(namepath: str) -> tuple[str, str]:
    namepath = Path(namepath)
    path = namepath.parent
    name = namepath.name
    image = None
    for ext in ['.jpg', '.png']:
        img = path / (name + ext)
        if img.exists():
            image = img
            break
    if image is None:
        raise FileNotFoundError(f"Image not found for {namepath}")
    label = path / (name + '.txt')
    if not label.exists():
        raise FileNotFoundError(f"Label not found for {namepath}")
    return (str(image), str(label))

def get_labels(path: str) -> list[str]:
    path = Path(path)
    if path.is_file():
        return [str(path)]
    label_files = list(path.glob("*.txt"))
    return [str(path) for path in label_files]

def get_images(path: str) -> list[str]:
    path = Path(path)
    if path.is_file():
        return [str(path)]
    img_files = list(path.glob("*.jpg")) + list(path.glob("*.png"))
    return [str(path) for path in img_files]