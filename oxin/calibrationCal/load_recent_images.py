from pathlib import Path
import os
import random


def load_recent_images(path, image_count=3):
    try:
    
        path_main = sorted(Path(path).iterdir(), key=os.path.getmtime)
        path_list = []

        # 
        for i in range(image_count):
            #
            file_path = str(random.choice(path_main))

            try:
                if (file_path[-3:] == 'jpg') or (file_path[-3:] == 'png'):
                    path_list.append(file_path)
            except:
                continue
    
        return path_list

    except:
        return []