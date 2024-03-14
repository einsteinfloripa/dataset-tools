import shutil
import random
from pathlib import Path

from tools.auxiliar import get_img_label_pairs

class Formatter:
    
    def setup_yolo(
            source_dir,
            dataset_name,
            test,
            train,
            val,
            dest_dir = '.',
            copy=False
        ):
        source_dir = Path(source_dir)
        dest_dir = Path(dest_dir)
        pairs = get_img_label_pairs(source_dir)
        sorted_pairs = Formatter.__sort_pairs(pairs, test, train, val)

        dataset_name = Path(dataset_name)
        dataset_name.mkdir(exist_ok=False, parents=True)


        imgs = (dataset_name / 'images')
        labels = (dataset_name / 'labels')
        labels.mkdir()
        imgs.mkdir()
        for percent, name in [(test, 'test'), (train, 'train'), (val, 'val')]:
            if percent > 0:
                (imgs / f'{name}'  ).mkdir()
                (labels / f'{name}').mkdir()
        
        for tp, pairs in sorted_pairs.items():
            for pair in pairs:
                img, label = pair
                img_name = img.split('/')[-1]
                label_name = label.split('/')[-1]
                for img, label in pairs:
                    if copy:
                        shutil.copy(img, dest_dir / 'images' / tp / img_name)
                        shutil.copy(label, dest_dir / 'labels' / tp / label_name)
                    else:
                        shutil.move(img, dest_dir / 'images' / tp / img_name)
                        shutil.move(label, dest_dir / 'labels' / tp / label_name)

        

    def __sort_pairs(pairs, test, train, val):
        if sum([test, train, val]) != 1:
            raise ValueError('The sum of the percentages must be 1')
        n = len(pairs)

        test_n = int(n * test)
        train_n = int(n * train)
        val_n = int(n * val)


        test_pairs = []
        train_pairs = []
        val_pairs = []

        random.shuffle(pairs)
        while n > 0:
            p = pairs.pop()
            if test_n > 0:
                test_n -= 1
                test_pairs.append(p)
            elif train_n > 0:
                train_n -= 1
                train_pairs.append(p)
            elif val_n > 0:
                val_n -= 1
                val_pairs.append(p)
            else:
                random.choice([test_pairs, train_pairs, val_pairs]).append(p)
            n -= 1
        
        return {'test':test_pairs, 'train':train_pairs, 'val':val_pairs}
    

    # TODO: dismantle_yolo