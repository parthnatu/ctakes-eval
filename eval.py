import requests
import json
import sys
import logging
import pandas as pd
import os
URL = 'https://10.245.2.102:9999/ctakes'
text = ''
classifications = ['MedicationMention','ProcedureMention']#,'SignSymptomMention','DiseaseDisorderMention','AnatomicalSiteMention']
ul = list()
wl = list()
EXCLUSION_STR = "org.apache.ctakes.typesystem.type.textsem."

if(len(sys.argv)<2):
    print('usage: eval.py <data-folder> <classification-type>\neval.py <data-folder>')
    exit()
if(os.path.isdir(sys.argv[1]+'\output')==False):
    os.mkdir(sys.argv[1]+'\output')
with open(sys.argv[1]+'/sample.txt', 'r') as f: #ADD THE DATA FOLDER PATH INSTEAD OF INPUT.TXT
    text = f.read()
data = str(requests.post(url=URL, data=text,verify=False).json())
data = data.replace("'", "\"")
data = data.replace("None", "\"\"")
df = pd.read_json(json.dumps(json.loads(data), indent=4))
s = list()


def calculateMetrics(ul,wl):
    tp=0
    tn=0
    fp=0
    fn=0
    list = ul.copy()
    ul_ = ul.copy()
    wl_ = wl.copy()
    for i in wl_:
        if(i not in list):
            list.append(i)
    for word in list:
        if(word in ul_ and word in wl_):
            print("TP:"+word)
            tp+=1
        elif(word not in ul_ and word in wl_):
            print("FP:"+word)
            fp+=1
        elif(word in ul_ and word not in wl_):
            print("FN:"+word)
            fn+=1
        else:
            print("TN:"+word)
            tn+=1
    precision = tp/(tp+fp)
    recall = tp/(tp+fn)
    f1 = (precision*recall*2)/(precision+recall)
    return(tp,tn,fp,fn,precision,recall,f1)

def writeToExcel(path,data):
    writer = pd.ExcelWriter(path, engine='xlsxwriter')
    pd.DataFrame(data).to_excel(writer, sheet_name='Sheet1')
    workbook  = writer.book
    worksheet = writer.sheets['Sheet1']
    writer.save()

if(len(sys.argv)==2):
    for i in range(len(classifications)):
        ul=[]
        wl=[]
        with open(str(sys.argv[1])+'/ul_'+classifications[i]+'.txt','r') as f:
            ul = f.read().split('\n')

        for j in range(len(df["annotation"])):
            op_text = text[df["annotation"][j]["begin"]:df["annotation"][j]["end"]].strip()
            annotation = df["typ"][j].strip()
            if(annotation==EXCLUSION_STR+classifications[i]):
                wl.append(op_text)
        metrics = calculateMetrics(ul,wl)
        writeToExcel(sys.argv[1]+'\output\output_'+classifications[i]+'.xlsx',[text,ul,wl,str(metrics[0])+'_TP',str(metrics[1])+'_TN',str(metrics[2])+'_FP',str(metrics[3])+'_FN',str(metrics[4]*100)+'%_PREC',str(metrics[5]*100)+'%_REC',str(metrics[6]*100)+'%_F1'])
