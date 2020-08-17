import os
import numpy as np
from keras.models import load_model
from keras.preprocessing import image
from sklearn.metrics import confusion_matrix


def predict():
    
    model_right = load_model('new_model_right.h5')
    model_left = load_model('new_model_left.h5')
    datagen_right = image.ImageDataGenerator(rescale = 1./255)
    datagen_left = image.ImageDataGenerator(rescale = 1./255)
    
    dataset_right = datagen_right.flow_from_directory('./Datasets_build/test_set/right_box',
                                                target_size = (224, 224),
                                                batch_size = 32,
                                                class_mode = 'categorical',
                                                shuffle = False)
    dataset_left = datagen_left.flow_from_directory('./Datasets_build/test_set/left_box',
                                                target_size = (224, 224),
                                                batch_size = 32,
                                                class_mode = 'categorical',
                                                shuffle = False)

    Y_pred_right = model_right.predict_generator(dataset_right, len(dataset_right))
    print(Y_pred_right)
    y_pred_right = np.argmax(Y_pred_right, axis=1)
    print(confusion_matrix(dataset_right.classes, y_pred_right))
    print(y_pred_right)
    
    Y_pred_left = model_left.predict_generator(dataset_left, len(dataset_left))
    print(Y_pred_left)
    y_pred_left = np.argmax(Y_pred_left, axis=1)
    print(confusion_matrix(dataset_left.classes, y_pred_left))
    print(y_pred_left)
    
predict()