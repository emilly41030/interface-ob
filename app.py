# pythonspot.com
# -*- coding: utf-8 -*-
from flask import Flask, render_template, flash, request, redirect, session, abort, url_for, g, jsonify
from wtforms import Form, TextField, TextAreaField, validators, StringField
from flask_wtf import FlaskForm
import os
from shutil import copyfile
from os import listdir
import configure as config
import threading
import subprocess
import time
import signal
import sys
import shutil
import pandas as pd
# import flask_sijax
# import draw


# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(config)
classes = []   #類別資訊
classNamePath = config.CLASSPATH  #類別名稱
# cfg_set -> 設定訓練類別數量、訓練及測試圖片檔名列表路徑、類別名稱路徑、儲存 .wieght 路徑
cfg_set=config.CFG_DATA
# cfg_yolo -> 設定參數 class 有變動 filter classes
cfg_yolo=config.CFG_YOLO
# app.config["SIJAX_STATIC_PATH"] = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')
datasetPath = 'dataset/'
backupPath = 'scripts/backup'
recordPath = "static/record.txt"
def create_dir(path):
    if not os.path.isdir(path):
        os.mkdir(path)

create_dir(backupPath)
create_dir(datasetPath)
create_dir("static")

def read_record():
    if os.path.isfile(recordPath):
        with open(recordPath, "r") as f:
            for lines in f.readlines():
                if "dataset" in lines:
                    config.DATASET_NAME = lines.split(':')[-1].strip()
                    print(config.DATASET_NAME)
                elif "cfg_setdata" in lines:
                    config.CFG_DATA = lines.split(":")[-1].strip()
                elif "cfg_yolo" in lines:
                    config.CFG_YOLO = lines.split(":")[-1].strip()
                elif "classNamePath" in lines:
                    config.CLASSPATH = lines.split(":")[-1].strip()

def close_pid(pid):    
    os.kill(int(pid), signal.SIGKILL)
    print("kill "+str(pid)+"!!!!!")    

def get_pid(name):
    return subprocess.check_output(["pidof",name])

def check_pid(pid): 
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

def file_remove(file_path):
    if os.path.isfile(file_path):
        os.remove(file_path)
        print("remove "+file_path)
    else:
        print("File doesnot exist: "+file_path)

def add_class(classNamePath):
    try:
        del classes[:]
        with open(classNamePath, 'r') as f:
                for line in f: 
                    if not line=="":
                        line = line.strip() #濾除空白、換行之類的特出符號
                        classes.append(line)
        if "" in classes:
            classes.remove("")
        print("add_class = "+str(classes))
    except:
        return "class import error"

@app.route('/process', methods=['POST'])
def pid_process():
    train_task=0
    if len(config.LIST_PID) != 0:
        for num in config.LIST_PID:
            exist_task = check_pid(num)
            if exist_task:
                train_task+=1
            return jsonify({'task': train_task})
    return jsonify({'error':'No training task'})

def find_dataset():
    datasetList=[]
    files = os.listdir(datasetPath)  
    for f in files:
        fullpath = os.path.join(datasetPath, f)   
        if os.path.isdir(fullpath):
            datasetList.append(f)
    return datasetList


    
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dataset', methods=['GET', 'POST'])
def ImportDataset():
    if request.method == 'POST':       
        OriginImgPath = request.form.get('train_imagePath') #/home/kelly/data/Dataset/Mura/LCD4/JPEGImages
        if str(OriginImgPath)=="":
            return "Image path error"
        OriginLabelPath = request.form.get('train_labelPath') #/home/kelly/data/Dataset/Mura/LCD4/JPEGImages
        if str(OriginLabelPath)=="":
            return "Label path error"
        datasetName = request.form.get('dataset_name')
        if str(datasetName)=="":
            return "Dataset name error"
        config.DATASET_NAME=datasetName
        firName = OriginImgPath.split('/')[-3]    # firName = Mura
        secName = OriginImgPath.split('/')[-2]    # secName = LCD4
        #os.path.dirname(os.path.dirname(datasetPath))  擷取 JPEGImages 上上層 /home/kelly/data/Dataset/Mura
        create_dir(datasetPath+datasetName)
        print()
        if os.path.isdir(datasetPath+datasetName+'/'+firName):
            shutil.rmtree(datasetPath+datasetName+'/'+firName, ignore_errors=True)
        class_temp = request.form['classes'] # 讀進來是 unicode
        classNamePath = 'data/voc_'+datasetName+'.names'
        config.CLASSPATH = classNamePath
        
        try:
            file_remove(classNamePath)
            del classes[:]
            with open(classNamePath,'w+') as f:
                f.write(str(class_temp))
            add_class(classNamePath)
        except:          
            return ".names 寫檔錯誤!!!"        
        print("classes = "+str(classes))
        # print(datasetPath+'Creat_listName.py')
        if not os.path.isfile(datasetPath+'Creat_listName.py'):
            if os.path.isfile('Creat_listName.py'):
                copyfile('Creat_listName.py', datasetPath+'Creat_listName.py')
            elif os.path.isfile('python/Creat_listName.py'):
                copyfile('python/Creat_listName.py', datasetPath+'Creat_listName.py')
            else:
                return "No such file: Creat_listName.py"
           
        # 將資料集路徑的捷徑建立到 dataset/
        newPath = datasetPath+datasetName+'/'+firName
        print("newPath = "+str(newPath))
        print("OriginImgPath" + str(OriginImgPath))
        ImagesPath = os.getcwd()+'/'+newPath + "/"+ secName +'/JPEGImages'
        LabelPath = os.getcwd()+'/'+newPath + "/"+ secName +'/Annotations'
        create_dir(os.getcwd()+'/'+newPath)
        create_dir(os.getcwd()+'/'+newPath + "/"+ secName)
        subprocess.call(["ln","-sf",OriginImgPath, ImagesPath])
        subprocess.call(["ln","-sf",OriginLabelPath, LabelPath])
        file_remove(newPath+"/"+secName+"/ImageSets/Main/train.txt")
        file_remove(newPath+"/"+secName+"/ImageSets/Main/val.txt")

        # 將 JPEGImages 的圖片寫入 /ImageSets/Main/train.txt、val.txt
        p1=subprocess.Popen(["python",datasetPath+"Creat_listName.py",ImagesPath])     
        print(datasetPath+"voc_"+datasetName+".data")
        print("Creat_listName finish")
        
        # voc_label_Mura.py  創建 訓練、驗證完整的路徑檔案 scripts/xxx_train.txt、xxx_val.txt，
        #                    產生 label 資料夾
        if not os.path.isfile(datasetPath+'voc_label.py'):
            if os.path.isfile('voc_label.py'):
                shutil.move('voc_label.py', datasetPath+'voc_label.py')
            elif os.path.isfile('python/voc_label.py'):
                shutil.move('python/voc_label.py', datasetPath+'voc_label.py')
            else:
                return "No such file: voc_label.py"
        # print("python "+datasetPath+"voc_label.py "+ImagesPath+" "+datasetName)
        subprocess.Popen(["python",datasetPath+"voc_label.py",ImagesPath, datasetName]+classes)        
        #  寫 .data 檔
        cfg_set = datasetPath+datasetName+"/voc_"+datasetName+".data"
        with open(cfg_set, 'w+') as f:
            f.write("classes= "+str(len(classes))+'\n')
            f.write("train  = "+os.getcwd()+"/"+datasetPath+ datasetName + '/' + secName+'_train.txt\n')
            f.write("valid  = "+os.getcwd()+"/"+datasetPath+ datasetName + '/' + secName+'_val.txt\n')
            f.write("names = data/voc_"+datasetName+".names\n")

        datasetList=[]
        datasetList = find_dataset()
        return render_template('train.html', dirList=datasetList)
       
    return render_template("dataset.html")

@app.route('/train')
def train():
    datasetList=[]
    datasetList = find_dataset()
    if 'backup' in datasetList:
        datasetList.remove('backup')
    if len(datasetList)==0:
        return render_template('train.html',error="No found any dataset")
    return render_template('train.html', dirList=datasetList)

@app.route('/index')
def index():
    return render_template('index.html')

# @flask_sijax.route('/train2')
# def train2():
#     def file_handler(obj_response):
#         obj_response.attr('')
#     datasetList=[]
#     datasetList = find_dataset()
#     if 'backup' in datasetList:
#         datasetList.remove('backup')
#     return render_template('train.html', dirList=datasetList)

def parse_loss_log(self,log_path, line_num=2000):
        result = pd.read_csv(log_path, skiprows=[x for x in range(line_num) if ((x % 10 != 9) | (x < 10))],error_bad_lines=False, names=['loss', 'avg', 'rate', 'seconds', 'images'])
        result['loss'] = result['loss'].str.split(' ').str.get(1)
        result['avg'] = result['avg'].str.split(' ').str.get(1)
        result['rate'] = result['rate'].str.split(' ').str.get(1)
        result['seconds'] = result['seconds'].str.split(' ').str.get(1)
        result['images'] = result['images'].str.split(' ').str.get(1)


def write_log(datasetName, current, paras):
    add_class('data/voc_'+datasetName+'.names')       
    classes_size=str(len(classes))
    os.mkdir("scripts/"+datasetName+"_"+current)

    # 寫 yolov3_voc.cfg 檔案
    subprocess.Popen(["python", "read_reversed.py",classes_size]+paras)
    #  寫 .data 檔
    cfg_set = "scripts/"+datasetName+"_"+current+"/voc_"+datasetName+".data"
    copyfile(datasetPath+datasetName+"/voc_"+datasetName+".data", cfg_set)
    config.CFG_DATA=cfg_set
    backupDir = backupPath+"/"+datasetName+"_"+current
    with open(cfg_set, 'a+') as f:
        f.write("backup = "+backupDir)
    create_dir(backupPath+"/"+datasetName+"_"+current)
    logPath='scripts/'+datasetName+"_"+current+'/log'
    create_dir(logPath)
    logfile = open(logPath+'/logfile.log', 'w+')
    cfg_set = os.getcwd()+'/scripts/'+datasetName+"_"+current+'/voc_'+datasetName+".data"
    cfg_yolo = os.getcwd()+"/scripts/"+datasetName+"_"+current+"/yolov3_"+datasetName+".cfg"
    # print("cfg_yolo = "+str(cfg_yolo))
    # print("cfg_set = "+str(cfg_set))
    time.sleep(1)
    print("./darknet detector train "+cfg_set+" "+cfg_yolo+ " darknet53.conv.74")
    p = subprocess.Popen(['./darknet', 'detector', 'train', cfg_set,cfg_yolo , "darknet53.conv.74"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    config.PID = p.pid
    config.LIST_PID.append(p.pid)
    for line in p.stdout:
        sys.stdout.write(line)
        logfile.write(line)    
    print ('write_log finish')
    with open("static/test.txt", "w+") as f:
        f.write("")

def draw_loss(datasetName, current):
    time.sleep(30)
    while (check_pid(config.PID)):
        print("config.pid=" + str(config.PID))
        print("draw~~~~~~~ start ~~~~~~~~~~")
        log_path = 'scripts/'+datasetName+"_"+current+'/log/logfile.log'
        result_dir = 'scripts/'+datasetName+"_"+current
        # logVis = draw.Yolov3LogVisualization(log_path,result_dir)
        # print(logVis)
        p = subprocess.Popen(['python','draw_log.py',log_path, result_dir])       
        print("draw~~~~~~~ end ~~~~~~~~~~")
        time.sleep(60)
    print("draw finish !!!!!")



pid = 12
@app.route('/training', methods=['GET', 'POST'])
def training():
    paras = []
    file_remove("static/test.txt")
    if request.method == 'POST':
        current = time.strftime("%Y%m%d-%H%M%S", time.localtime())
        config.EPOCH = request.form.get('max_batches')
        datasetName = request.form.get('comp1_select')
        config.DATASET_NAME=datasetName
        print("datasetName="+str(datasetName))
        config.LIST_PID.append(pid)
        paras.append(datasetName)
        paras.append(request.form.get('max_batches'))
        paras.append(request.form.get('learning_rate'))
        paras.append(request.form.get('batch'))
        paras.append(request.form.get('subdivisions'))
        paras.append(current)
               
        Thread1=threading.Thread(target=write_log, args=(datasetName, current, paras))
        Thread1.start()       
        Thread2=threading.Thread(target=draw_loss, args=(datasetName, current))
        Thread2.start()
     
    return render_template("training.html", pid=config.PID, paras=paras)
    
@app.route("/option", methods=['GET', 'POST'])
def option():
    datasetList=[]
    datasetList = find_dataset()
    if 'backup' in datasetList:
                    datasetList.remove('backup')
    if request.method == 'POST':
        file_remove("static/test.txt")
        if request.form["btn"] == "Test":
            return render_template('test.html')
        if request.form["btn"] == "Train again":
            return render_template("train.html", pid=config.PID, dirList=datasetList)
        if request.form["btn"] == "Close":
            if (check_pid(config.PID)):
                close_pid(config.PID)
            
    return render_template("train.html", pid=config.PID, dirList=datasetList)

@app.route("/testing", methods=['GET', 'POST'])
def testing():
    dataset = config.DATASET_NAME
    wei_file = request.form.get('comp1_select')
    img = request.form.get('comp2_select')
    print("./darknet detector test scripts/"+dataset+"/voc_"+dataset+".data scripts/backup/"+dataset+"/"+str(wei_file)+ ' data/'+str(img))
    p = subprocess.Popen(["./darknet", "detector", "test","scripts/"+dataset+"/voc_"+dataset+".data","scripts/backup/"+dataset+"/"+str(wei_file), 'data/'+str(img)])
    time.sleep(2)
    # shutil.move('predictions.jpg', 'static/Figure/result/'+str(wei_file)+'-'+dataset+'.jpg')
    return render_template("testing.html", img=config.TEST_IMG)



@app.route("/test", methods=['GET', 'POST'])
def test():  
    imgPath = "data"
    backupDir = []
    img=[]
    backupfiles = listdir(backupPath)
    for f in backupfiles:
        backupDir.append(f)
    imgfiles = listdir(imgPath)
    for f in imgfiles:
        img.append(f)  
    if len(backupDir) > 3:
        size_d = 3
    elif len(backupDir)==0:
        error = "Cannot find any backup"        
        return render_template('test.html',error=error)
    else:
        size_d=len(backupDir)
    config.DATASET_NAME=backupDir[0]
    dataset=config.DATASET_NAME
    childtree = []
    dirfiles = listdir(backupPath+"/"+str(config.DATASET_NAME))
    size_d = 0
    
    for f in dirfiles:
        childtree.append(f)
    if request.method == "POST":
        if request.form['comp0_select']:
            dataset = request.form.get('comp0_select')
            del childtree
            childtree=[]
            dirfiles = listdir(backupPath+"/"+str(dataset))
            for f in dirfiles:
                childtree.append(f)
            config.TEST_DATASET=dataset
    return render_template('test.html',size_d=size_d, dataset=config.TEST_DATASET,tree=backupDir, childtree=childtree, img=img, error=error)


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    if not os.path.isfile("darknet"):
        subprocess.Popen(["make","-j16"])
    file_remove("test.txt")
    read_record()
    app.run(debug=True,host='0.0.0.0', port=6060, threaded=True)


# def make_tree(path):
#     tree = dict(name=os.path.basename(path), children=[])
#     try: lst = os.listdir(path)
#     except OSError:
#         pass #ignore errors
#     else:
#         for name in lst:
#             fn = os.path.join(path, name)
#             if os.path.isdir(fn):
#                 tree['children'].append(make_tree(fn))
#             else:
#                 tree['children'].append(dict(name=name))
#     return tree