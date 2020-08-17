import os
from tag import create_datasets
from screenshots import take_screenshots

video_src = input('Enter video name: ')

from cnn import predict

if not os.path.exists('./Datasets'):
		os.makedirs('./Datasets')
if not os.path.exists('./Datasets/left_box'):
		os.makedirs('./Datasets/left_box')
if not os.path.exists('./Datasets/right_box'):
		os.makedirs('./Datasets/right_box')
        

print('Creating datasets. This process may take hours.')
create_datasets(video_src)
print('Datasets created.')
print('Starting prediction')
set_classes_right, set_classes_left = predict()
print('Taking screenshots')
take_screenshots(video_src , set_classes_right, set_classes_left)
print('Process finished')
