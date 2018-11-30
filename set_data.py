#coding=utf-8
import os
import shutil

##############  將 label 分成兩個資料夾 有東西分一類 ##############
labelpath = "/home/kelly/data/Dataset/Mura/LCD4/Annotations"
files = os.listdir(labelpath)
newPath_0 = '/home/kelly/data/Dataset/Mura/LCD4/no_label-A'
newPath_1 = '/home/kelly/data/Dataset/Mura/LCD4/has_label-A'

if not os.path.isdir(newPath_0):
    os.mkdir(newPath_0)
if not os.path.isdir(newPath_1):
    os.mkdir(newPath_1)
for f in files:
    size = os.path.getsize(labelpath+'/'+f)
    print(str(labelpath)+'/'+str(f)+": "+str(size)+" bytes")
    if size==0:
        shutil.move(labelpath+'/'+f, newPath_0+'/'+f)
    else:
        shutil.move(labelpath+'/'+f, newPath_1+'/'+f)
#############################################################

############## 將 images 分成兩個資料夾 有東西分一類 ##############
# imgpath = '/home/kelly/data/Dataset/Mura/LCD4/JPEGImages22'
# labelpath = '/home/kelly/data/Dataset/Mura/LCD4/no_label'
# # labelpath = '/home/kelly/data/Dataset/Mura/LCD4/has_label'
# newPath_0 = '/home/kelly/data/Dataset/Mura/LCD4/label_img'
# newPath_1 = '/home/kelly/data/Dataset/Mura/LCD4/no_label_img'
# if not os.path.isdir(newPath_0):
#     os.mkdir(newPath_0)
# if not os.path.isdir(newPath_1):
#     os.mkdir(newPath_1)

# files = os.listdir(labelpath)
# for f in files:
#     shutil.copyfile(imgpath+'/'+f.split('.')[0]+'.png', newPath_1+'/'+f.split('.')[0]+'.png')