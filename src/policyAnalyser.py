import re
import jieba
import os
import json
from data import *


def process_neg(score,words):
    for i in range(len(words)):
        if(words[i] in deny_kw):
            for j in range(i,len(words)):
                score[j]*=-1
    return score

def process_exp(score,words):    
    for i in range(len(words)):
        if(words[i] in except_kw1):
            for j in range(i,len(words)):
                score[j]*=-1
                if(words[j] in except_kw2):
                    break
    return score


def scanPolicy(file):
    # dir=r"/mnt/iscsi/app_22_0901/app/pp/"
    tkw = text_kw
    for i in policy_kw:
        tkw+=policy_kw[i]
    for i in tkw:
        jieba.add_word(i)
    policy_dic={}
    text=open(file,'r',encoding='utf-8').read()
    privacy=[]
    rev_privacy=[]
    for line in re.split("[（）。；\n]",text):
        # print(line)
        c=0
        for w in disable_kw:
            if w in line:
                c=1
                break
        if(c):
            continue
        words=list(jieba.cut(line))
        score=[1]*len(words)
        score=process_neg(score,words)
        score=process_exp(score,words)
        kw=list(zip(words,score))
        for w,s in kw:
            for type in policy_kw:
                if(s==1 and w in policy_kw[type]):
                    if(type not in privacy):
                        privacy.append(type)
                        #print(line)
                        if(type not in rev_privacy):
                            pass#print("发现权限：",(w,type))
                        else:
                            pass#print("发现矛盾:",(w,type))
                elif(s==-1 and w in policy_kw[type]):
                    # print(line)
                    # print(w)
                    # input()
                    if(type not in rev_privacy):
                        rev_privacy.append(type)
                        if(type not in privacy):
                            #print(line)
                            pass#print("发现矛盾:",(w,type))
    #print(privacy)
    # policy_dic[f.strip(".txt")]=privacy
    # print(privacy)
    return privacy
