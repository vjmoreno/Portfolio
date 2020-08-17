# -*- coding: utf-8 -*-
import cv2
import time

def create_datasets(video_src):
    
    cap = cv2.VideoCapture(video_src)

    f = 0
    mean_value = 95
    counter_left = 0
    counter_right = 0
    cars_counter_left = 0
    cars_counter_right = 0
    previous_tag_left = [0] * 50
    previous_tag_right = [0] * 50
    last_ten_tags_left = [0] * 10
    last_ten_tags_right = [0] * 10
    
    while True:
        ret, img = cap.read()
        f += 1
        counter_right += 1
        counter_left += 1
        tagged_right = 0
        tagged_left = 0
        
        if (type(img) == type(None)):
            break
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        mean_diff = int(max(0, mean_value - gray.mean()))
        tag_right = gray[420:470,962]
        mean_change_list_right = [abs(int(a) - int(b)) for a, b in zip(tag_right, previous_tag_right)]
        mean_change_right = sum(mean_change_list_right)/50
        
        if mean_change_right > 1:
            tagged_right = 1
            
        last_ten_tags_right = last_ten_tags_right[1:]
        last_ten_tags_right.append(tagged_right)
    
        if sum(last_ten_tags_right) >= 4 and counter_right > 30:
            #cv2.line(gray, (965,420), (965,470), 255, 2)
            #cv2.rectangle(gray, (857,342), (1025,510), 255,2)
            counter_right = 0
            cars_counter_right += 1
            crop_img_right = img[342:510, 857-mean_diff*4:1025-mean_diff*4]
            resized_right = cv2.resize(crop_img_right, (224, 224), interpolation = cv2.INTER_AREA)
            time_f_right = time.strftime('%H:%M:%S', time.gmtime(int(f/30)))
            time_f_right = time_f_right.replace(':','_')
            cv2.imwrite('./Datasets/right_box/right_{}_{}.jpg'.format(time_f_right, f), resized_right)
        #else:
            #cv2.line(gray, (965,420), (965,470), 0, 2)
            #cv2.rectangle(gray, (857,342), (1025,510), 0,2)
        
        tag_left = gray[580:630,280]
        mean_change_list_left = [abs(int(a) - int(b)) for a, b in zip(tag_left, previous_tag_left)]
        mean_change_left = sum(mean_change_list_left)/50
        
        if mean_change_left > 1:
            tagged_left = 1
            
        last_ten_tags_left = last_ten_tags_left[1:]
        last_ten_tags_left.append(tagged_left)
    
        if sum(last_ten_tags_left) >= 4 and counter_left > 30:
            #cv2.line(gray, (283,580), (283,630), 255, 2)
            #cv2.rectangle(gray, (200,550), (368,718), 255,2)
            counter_left = 0
            cars_counter_left += 1
            crop_img_left = img[550:718, 200+mean_diff*4:368+mean_diff*4]
            resized_left = cv2.resize(crop_img_left, (224, 224), interpolation = cv2.INTER_AREA)
            time_f_left = time.strftime('%H:%M:%S', time.gmtime(int(f/30)))
            time_f_left = time_f_left.replace(':','_')
            cv2.imwrite('./Datasets/left_box/left_{0}_{1}.jpg'.format(time_f_left, f), resized_left)
        #else:
            #cv2.line(gray, (283,580), (283,630), 0, 2)
            #cv2.rectangle(gray, (200,550), (368,718), 0,2)
        previous_tag_left = gray[580:630,280]
        previous_tag_right = gray[420:470,962]
       #cv2.imshow('video', gray)
        
        
        if cv2.waitKey(33) == 27:
            break
    
    cv2.destroyAllWindows()