# Truck detector

### 1. Introduction
This project has been developed using OpenCV to analyze the data from
the images to detect objects passing through a road. The program once is
running will start saving images of every car detected. After that, a trained
CNN will classify the images in two classes: trucks and no trucks (everything
that is not a truck). Once it is all classified, the screenshots are going to be
saved.
### 2. Python 3.7 requirements
* cv2
* keras
* numpy
* os
* time
### 3. Performance
The program has two different CNNs, one for the cars coming from the
left and one from the right. The amount of images used for train, validate
and test the CNNs is represented in the following table:

Class / Direction | Train | Validation | test
----------------- | ----- | ---------- | -----
Trucks / Right | 320 | 70 | 80
Trucks / Left | 300 | 64 | 80
No trucks / Right | 650 | 100 | 100
No trucks / Left | 650 | 100 | 100


The confusion matrices obtained with the testing set are the following:

#### Right:
Class | No Trucks | Trucks
----- | --------- | ------
No trucks | 90 | 10
No trucks | 2 | 78

#### Left:
Class | No Trucks | Trucks
----- | --------- | ------
No trucks right | 94 | 6
No trucks right | 2 | 78

Only 2.5% (2/80) of trucks are being classified as no trucks, and for every
truck with tray, the program takes between 2-3 pictures, so the probability of
a truck with tray to not get detected is at most 0.025*0.025*100 = 0.0625%.
Of course, these are the results for just one video, and the performance may
change.


### 4. Usage

1. Make sure you downloaded the following files: main.py, tag.py, cnn.py,
screenshots.py, new model left.h5 and new model right.h5. Store everything in the same folder.
2. Put the video that you want to analyze in the same folder and run
main.py
3. Enter the video name and wait!. A 12hrs video might take 8-12 hours
to be completely processed. The program will start creating the folders ./Datasets, ./Datasets/right box and ./Datasets/left box. The last
two folders will contain the images to classify. Once the program finishes the whole process, you will be able to find the screenshot in the
folder ./Datasets/screenshots. Probably you will find false positives
(no trucks classified as trucks).
