import os
import cv2

def take_screenshots(video_src, set_right, set_left):
    if not os.path.exists('./Datasets/screenshots'):
        os.makedirs('./Datasets/screenshots')
    cap = cv2.VideoCapture(video_src)
    for image_name, class_n in set_right:
        if class_n == 1:
            list_name = image_name.split('_')
            frame = int(list_name[4][:-4])
            cap.set(1, frame)
            ret, frame = cap.read()
            cv2.imwrite('./Datasets/screenshots/{}'.format(image_name), frame)
            os.rename('./Datasets/right_box/{}'.format(image_name), './Datasets/right_box/truck_{}'.format(image_name))
            #take screenshot and change pic name
    for image_name, class_n in set_left:
        if class_n == 1:
            list_name = image_name.split('_')
            frame = int(list_name[4][:-4])
            cap.set(1, frame)
            ret, frame = cap.read()
            cv2.imwrite('./Datasets/screenshots/{}'.format(image_name), frame)
            os.rename('./Datasets/left_box/{}'.format(image_name), './Datasets/left_box/truck_{}'.format(image_name))