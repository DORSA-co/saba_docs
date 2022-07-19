from pathlib import Path
import os
import random


def load_recent_images(path, image_count=3):
    try:
        # path
        path_main = sorted(Path(path).iterdir(), key=os.path.getmtime)[-1]
        path_list = []
        # 
        for i in range(image_count):
            #
            filename_1 = random.choice(os.listdir(path_main))
            path_random_1 = os.path.join(path_main, filename_1)
            #
            filename_2 = random.choice(os.listdir(path_random_1))
            path_random_2 = os.path.join(path_random_1, filename_2)            
            #
            filename_f = random.choice(os.listdir(path_random_2))
            path_random_f = os.path.join(path_random_2, filename_f) 
            #
            try:
                if (path_random_f[-3:] == 'jpg') or (path_random_f[-3:] == 'png'):
                    path_list.append(path_random_f)
            except:
                continue

        return path_list
    except:
        return False