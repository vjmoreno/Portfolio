from keras.layers import Dense, Flatten
from keras.models import Model
from keras.applications.vgg16 import VGG16
from sklearn.metrics import confusion_matrix
from keras.preprocessing.image import ImageDataGenerator
import numpy as np



IMAGE_SIZE = [224, 224]

vgg_right = VGG16(input_shape=IMAGE_SIZE + [3], weights='imagenet', include_top=False)
vgg_left = VGG16(input_shape=IMAGE_SIZE + [3], weights='imagenet', include_top=False)

for layer in vgg_right.layers:
    layer.trainable = False
for layer in vgg_left.layers:
    layer.trainable = False

x_right = Flatten()(vgg_right.output)
x_left = Flatten()(vgg_left.output)
prediction_right = Dense(2, activation='softmax')(x_right)
prediction_left = Dense(2, activation='softmax')(x_left)

# create a model object
model_right = Model(inputs=vgg_right.input, outputs=prediction_right)
model_left = Model(inputs=vgg_left.input, outputs=prediction_left)

# view the structure of the model
model_right.summary()
model_left.summary()

# tell the model what cost and optimization method to use
model_right.compile(
  loss='categorical_crossentropy',
  optimizer='adam',
  metrics=['accuracy']
)
model_left.compile(
  loss='categorical_crossentropy',
  optimizer='adam',
  metrics=['accuracy']
)


train_datagen_right = ImageDataGenerator(rescale = 1./255)
train_datagen_left = ImageDataGenerator(rescale = 1./255)

validation_datagen_right = ImageDataGenerator(rescale = 1./255)
validation_datagen_left = ImageDataGenerator(rescale = 1./255)

test_datagen_right = ImageDataGenerator(rescale = 1./255)
test_datagen_left = ImageDataGenerator(rescale = 1./255)

training_set_right = train_datagen_right.flow_from_directory('./Datasets/train_set/right_box',
                                                 target_size = (224, 224),
                                                 batch_size = 32,
                                                 class_mode = 'categorical',
                                                 shuffle = False)
training_set_left = train_datagen_left.flow_from_directory('./Datasets/train_set/left_box',
                                                 target_size = (224, 224),
                                                 batch_size = 32,
                                                 class_mode = 'categorical',
                                                 shuffle = False)

validation_set_right = validation_datagen_right.flow_from_directory('./Datasets/validation_set/right_box',
                                            target_size = (224, 224),
                                            batch_size = 32,
                                            class_mode = 'categorical',
                                            shuffle = False)
validation_set_left = validation_datagen_left.flow_from_directory('./Datasets/validation_set/left_box',
                                            target_size = (224, 224),
                                            batch_size = 32,
                                            class_mode = 'categorical',
                                            shuffle = False)
test_set_right = test_datagen_right.flow_from_directory('./Datasets/test_set/right_box',
                                            target_size = (224, 224),
                                            batch_size = 32,
                                            class_mode = 'categorical',
                                            shuffle = False)
test_set_left = test_datagen_left.flow_from_directory('./Datasets/test_set/left_box',
                                            target_size = (224, 224),
                                            batch_size = 32,
                                            class_mode = 'categorical',
                                            shuffle = False)

# fit the model
r_right = model_right.fit(
  training_set_right,
  validation_data=validation_set_right,
  epochs=3,
  steps_per_epoch=len(training_set_right),
  validation_steps=len(validation_set_right)
)
r_right = model_left.fit(
  training_set_left,
  validation_data=validation_set_left,
  epochs=3,
  steps_per_epoch=len(training_set_left),
  validation_steps=len(validation_set_left)
)

model_right.save('new_model_right.h5')
model_left.save('new_model_left.h5')



#Confution Matrix and Classification Report
Y_pred_right = model_right.predict_generator(test_set_right, len(test_set_right))
y_pred_right = np.argmax(Y_pred_right, axis=1)
print('Confusion Matrix right')
print(confusion_matrix(test_set_right.classes, y_pred_right))
score_right = model_right.evaluate(test_set_right, verbose=2)
print(score_right)

Y_pred_left = model_left.predict_generator(test_set_left, len(test_set_left))
y_pred_left = np.argmax(Y_pred_left, axis=1)
print('Confusion Matrix left')
print(confusion_matrix(test_set_left.classes, y_pred_left))
score_left = model_left.evaluate(test_set_left, verbose=2)
print(score_left)


