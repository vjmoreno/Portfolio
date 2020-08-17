import os
import numpy as np
from keras.models import load_model
from keras.preprocessing import image

def predict():
    model_right = load_model('new_model_right.h5')
    model_left = load_model('new_model_left.h5')
    images_right = []
    images_names_right = []
    
    for img in os.listdir('./Datasets/right_box'):
        images_names_right.append(img)
        img = os.path.join('./Datasets/right_box', img)
        img = image.load_img(img, target_size=(224, 224))
        img = image.img_to_array(img)
        img = np.expand_dims(img, axis=0)
        images_right.append(img)

    images_right = np.vstack(images_right)
    classes_right = model_right.predict(images_right, batch_size=32)
    classes_right = classes_right.argmax(axis=-1)
    set_classes_right = set(zip(images_names_right, classes_right))
    images_left = []
    images_names_left = []
    
    for img in os.listdir('./Datasets/left_box'):
        images_names_left.append(img)
        img = os.path.join('./Datasets/left_box', img)
        img = image.load_img(img, target_size=(224, 224))
        img = image.img_to_array(img)
        img = np.expand_dims(img, axis=0)
        images_left.append(img)

    images_left = np.vstack(images_left)
    classes_left = model_left.predict(images_left, batch_size=32)
    classes_left = classes_left.argmax(axis=-1)
    set_classes_left = set(zip(images_names_left, classes_left))
        
    return set_classes_right, set_classes_left
