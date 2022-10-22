import os
import re
import wordninja as wj
import jieba
import xml.dom.minidom
from lxml import etree
import lxml
import jieba.posseg as pseg
import json
import csv
import sys
from bs4 import BeautifulSoup
import bs4
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
import shutil
from data import *

# wxif_pattern = re.compile('wx:if=".*?"', re.S)

def replaceInterp(line):
    line = "".join([_ if not _ in interpunctuations else " " for _ in line])
    return line


def stopword(line):
    for sword in stop_words:
        line = line.replace(sword, "")
    return line


def recordComponents(wxml_ctnt):
    has_any_cmp = False
    res = {}
    parse_html = etree.HTML(wxml_ctnt)
    for cmp in components:
        if not cmp in wxml_ctnt:
            res[cmp] = ""
            continue
        has_any_cmp = True
        res[cmp] = xml(parse_html, cmp.replace("<", ""))
    res["ch"] = extractChinese(wxml_ctnt)
    return has_any_cmp, res


def extractPrivacy(ctnt):
    res = set()
    for kw in inputP:
        if kw in ctnt:
            res.add(kw)
    return res

def scanWholeMiniApp(appid, log_dir):
    res = {}
    # all_ch = ""
    # all_cmp = ""
    aid = appid.split("/")[-1]
    for root, dir, files in os.walk(appid):
        for file in files:
            if not file.endswith(".wxml"):
                continue
            file_path = os.path.join(root, file)
            wxml_ctnt = open(file_path, "r", encoding = "utf-8").read()
            # flag, wxml_res = recordComponents(wxml_ctnt)
            res[file_path] = wxml_ctnt
            # if not flag:
                # continue
            # res[file_path] = wxml_res
            # for key, val in wxml_res.items():
                # if key == "ch":
                    # all_ch += val
                # else:
                    # all_cmp += val
    # res["all_cmp"] = all_cmp
    # res["all_ch"] = all_ch
    # res["all_cmp_keywords"] = extractPrivacy(all_cmp)
    # res["all_ch_keywords"] = extractPrivacy(all_ch)
    open("{}/{}.json".format(log_dir, aid), "w", encoding = "utf-8").write(json.dumps(res, ensure_ascii = False))

# def recordChline(ctnt):
#     if not extractChinese()


def cmpByText(wxml_ctnt, text):
    # root = ET.fromstring(wxml_ctnt)
    # result = root.findall("view")
    # parse_html = etree.HTML(wxml_ctnt)
    # result = parse_html.xpath('//view')
    res = []
    lines = wxml_ctnt.split("\n")
    # lines = wxml_ctnt
    l = len(lines)
    for idx, line in enumerate(lines):
        if text in line:
            context = "\n".join(lines[max(0, idx - 5) : min(l-1, idx + 5)])
            res.append(context)

    # print(res)
    return res


def convert_4_bytes(n):
    bits=4*8
    return (n+2**(bits-1))%2**bits-2**(bits-1)

def hashCode(s):
    h=0
    n=len(s)
    for i,c in enumerate(s):
        h=h+ord(c)*31**(n-1-i)
    return convert_4_bytes(h)

def get_mainpkg(appid):
    return str(hashCode(appid+"$__APP__"))

def get_path(appid,pkg):
    paths=[]
    cnt=0
    global ccnt
    for d in dirlist:
        if appid in os.listdir(d):
            paths.append(d)
            cnt+=1
    for pa in paths:
        path=pa+appid+"/"
        flag=0
        for p in os.listdir(path):
            if pkg in p:
                path+=p.strip(".wxapkg")+"/"
                flag=1
                break
        if(flag):
            return path

def extractChinese(line):
    res = ""
    for cha in line:
        if '\u4e00' <= cha <= '\u9fff':
            res += cha
    return res


def xml(parse_html, tag):
    # self placeholders
    res = parse_html.xpath('//{}/@placeholder'.format(tag))
    res.entend(parse_html.xpath('//{}/@title'.format(tag)))
    res.entend(parse_html.xpath('//{}/@value'.format(tag)))
    res.entend(parse_html.xpath('//{}/@label'.format(tag)))


    # inputs = parse_html.xpath("//{}".format(tag))
    # for ele in inputs:
        # self text
        # if ele.text and ele.text.replace("\n", "").replace(" ", ""):
            # res.append(ele.text.replace("\n", "").replace(" ", ""))
        # parents text
        # if ele.getparent().text and ele.getparent().text.replace("\n", "").replace(" ", ""):
            # res.append(ele.getparent().text.replace("\n", "").replace(" ", ""))
        # siblings text
        # siblings = ele.getparent().getchildren()
        # for sib in siblings:
            # if sib.text and sib.text.replace("\n", "").replace(" ", ""):
                # res.append(sib.text.replace("\n", "").replace(" ", ""))
        # children text
        # for child in ele.getchildren():
            # if child.text and child.text.replace("\n", "").replace(" ", ""):
                # res.append(child.text.replace("\n", "").replace(" ", ""))
    # return ";".join(res)


def cutLine(line):
    line = "".join(line.split("/"))
    words = pseg.cut(line)
    res = ""
    for w in words:
        res += "{} {}/".format(w.word, w.flag)
    return res[:-1]


def extractNoun(line):
    line = line.strip()
    words = line.split("/")
    len_ = len(words)
    res = []
    for idx, word in enumerate(words):
        if not word.split(" ")[0] in keyverb:
            continue
        n_count = 0
        noun = ""
        if idx == len_ - 1:
            continue
        for j in range(idx+1, len_):
            w_tmp = words[j].split(" ")
            noun += w_tmp[0]
            if w_tmp[1] == "v" and not w_tmp[1] in keyverb:
                break
            if w_tmp[1] == "n":
                n_count += 1
            if n_count == 2:
                break
        res.append(noun)
    return ";".join(res)


# def containsKV(stc):
#     res = []
#     for kv in keyverb:
#         if kv in stc:
#             res.append(kv)
#     return res

def extractNoun2(line):
    sentences = line.strip().split("。")
    res = set()
    for stc in sentences:
        kvs = containsKV(stc)
        if not kvs:
            continue
        for kv in kvs:
            res.add(stc.split(kv)[1])
    return ";".join(res)


def func(ctnt, kwd):
    res = set()
    for segment in ctnt:
        children = ET.fromstring(segment)
        children_text = [] # 
        grand_ch = []
        for child in children:
            child_text = ET.tostring(child, encoding='UTF-8').decode("utf-8")
            if kwd in child_text:
                children_text.append(child_text)
            grand_ch.extend([ET.tostring(_, encoding='UTF-8').decode("utf-8") for _ in child if kwd in ET.tostring(_, encoding='UTF-8').decode("utf-8")])
        if children_text and not grand_ch:
            res.add(segment)
        else:
            res = res.union(func(children_text, kwd))
    # print(res)
    return res


def bsfunc(ctnt, kwd):
    res = set()
    for segment in ctnt:
        xml_soup = BeautifulSoup(segment, "xml")
        raw = None
        for x in xml_soup.children:
            raw = x
            break
        children_text = [] # 
        grand_ch = []
        if not raw:
            continue
        for child in raw.children:
            if type(child) is bs4.element.NavigableString:
                continue
            c_children = child.children
            child_text = str(child)
            if kwd in child_text:
                children_text.append(child_text)
            # grand_ch.extend([str(_) for _ in c_children if kwd in str(_)])
            for _ in c_children:
                if type(_) is bs4.element.NavigableString:
                    continue
                if kwd in str(_):
                    grand_ch.append(str(_))
        # print(children_text, grand_ch)
        if children_text and not grand_ch:
            res.add(segment)
        else:
            res = res.union(bsfunc(children_text, kwd))
    # print(res)
    return res

def preprocessXML(ctnt):
    # head = "<body>"
    # tail = "</body>"
    # lines = ctnt.split("\n")
    # lines = ["    " + line for line in lines]
    # new_ctnt = [head]
    # new_ctnt.extend(lines)
    # new_ctnt.append(tail)
    # new_ctnt = "\n".join(new_ctnt)
    new_ctnt = ctnt
    new_ctnt = new_ctnt.replace("wx:else", "")
    wxifs = re.findall(wxif_pattern, new_ctnt)
    for wxif in wxifs:
        new_ctnt = new_ctnt.replace(wxif, "")
    # print(new_ctnt)
    return new_ctnt


def compare(cmp_, ch_):
    # c_l = cmp_.split(", ")
    c_l = cmp_
    ch_l = ch_
    # ch_l = ch_.split(", ")
    res = []
    for ch in ch_l:
        if not ch in c_l:
            res.append(ch)
    return res


def containCmpKwd(ctnts):
    for ctnt in ctnts:
        for cmp in components_kwd:
            if cmp in ctnt:
                return True
    return False


def getTags(ctnt):
    # parse_html = etree.HTML(ctnt)
    soup = BeautifulSoup(ctnt, "xml")
    ds = soup.descendants
    ds = set([_.name for _ in ds if not type(_) is bs4.element.NavigableString])
    return ds


def getJson(file_path):
    res = {}
    try:
        lines = open(file_path, "r", encoding = "utf-8").readlines()
        new_lines = []
        for line in lines:
            if line.startswith("}"):
                new_lines.append("}")
                break
            new_lines.append(line)
        new_ctnt = "".join(new_lines)
        # return json.loads(new_ctnt)
        res = json.loads(new_ctnt)
        return res
    except Exception:
        return res


def getAbsPath(path, tmp_path):
    out_num = tmp_path.count("../")
    # print(out_num)
    for x in range(out_num + 1):
        path = str(path[:path.rfind("/")])
        # print(path)
    return path + tmp_path[tmp_path.rfind("..") + 2:] + ".wxml"



def extractCustomCmp(target_dir):
    mapping = {}
    for pkg_root in os.listdir(target_dir):
        pkg_root = os.path.join(target_dir, pkg_root)
        for root, dir, files in os.walk(pkg_root):
            for file in files:
                if not file.endswith(".json"):
                    continue
                file_path = os.path.join(root, file)
                # file_json = json.loads(open(file_path, "r", encoding = "utf-8").read())
                file_json = getJson(file_path)
                if not "usingComponents" in file_json:
                    continue
                components = file_json["usingComponents"]
                for cmp, tmp_path in components.items():
                    if cmp in mapping:
                        continue
                    abs_path = ""
                    # print(tmp_path)
                    if tmp_path.startswith("/"):
                        abs_path = pkg_root + tmp_path + ".wxml"
                    else:
                        # abs_path = os.path.abspath(file_path, tmp_path) + ".wxml"
                        abs_path = getAbsPath(file_path, tmp_path)
                    #     print(abs_path)
                    # print(abs_path)
                    # print(pkg_root)
                    # print(file_path)
                    try:
                        cmp_ctnt = open(abs_path, "r", encoding = "utf-8").read()
                        mapping[cmp] = list(getTags(cmp_ctnt))
                    except Exception as e:
                        continue
                        # print(e)
    # open(output_dir + appid + ".json", "w", encoding = "utf-8").write(json.dumps(mapping))
    return mapping


def getBasis(mapping):
    # if not kwd in mapping:
    #     return set({kwd})
    # res = set(mapping[kwd])
    # diff = res.difference(default_cmps)
    # if not diff:
    #     return res
    # for item in diff:
    #     alternative = getBasis(item, mapping)
    #     res.remove(item)
    #     res = res.union(alternative)
    # return res
    res = {}
    for dcmp in default_cmps:
        res[dcmp] = [dcmp]
    keys = set(mapping.keys())
    while len(res.keys()) - 54 < len(keys):
        flag = False
        for cmp, lcmps in mapping.items():
            # print(cmp)
            # print(lcmps)
            if cmp in res:
                continue
            lcmps = set(lcmps)
            diff = lcmps.difference(res.keys())
            # print(diff)
            if not diff:
                flag = True
                tmp_val = set()
                for diff_item in lcmps:
                    tmp_val = tmp_val.union(set(res[diff_item]))
                res[cmp] = list(tmp_val)
                # print(cmp)
        if not flag:
            break
    for kwd, lcmps in mapping.items():
        if kwd in res:
            continue
        res[kwd] = lcmps + ["added"]
    return res


def constructCustomJson(target_dir):
    # extractCustomCmp(appid, output_dir)
    # raw_json = json.loads(open(output_dir + appid + ".json", "r", encoding = "utf-8").read())
    raw_json = extractCustomCmp(target_dir)
    transformed_json = getBasis(raw_json)
    return transformed_json


def transformTags(tags, target_json):
    # reliance = ""
    if not os.path.exists(target_json):
        reliance_json = constructCustomJson(target_json.replace(".json", "/"))
        res = set()
        for tag in tags:
            if tag in reliance_json:
                res = res.union(set(reliance_json[tag]))
            else:
                res.add(tag)
        return res
    try:
        reliance_json = json.loads(open(reliance, "r", encoding = "utf-8").read())
    except:
        return tags
    res = set([reliance_json[_] for _ in tags])
    return res


def judgeTags(tags):
    if tags.intersection(components_kwd):
        return True
    else:
        return False


def confirmWXML(wxml_path, target_json):
    res = set()
    try:
        file_ctnt = open(wxml_path, "r", encoding = "utf-8").read()
    except Exception as e:
        # print(e)
        file_ctnt = ""
    # print(file_ctnt)
    if not file_ctnt:
        return res
    keywords = set()
    for kwd in inputP:
        if kwd in file_ctnt:
            keywords.add(kwd)
    # print(keywords)
    for kwd in keywords:
        try:
            segments = bsfunc([file_ctnt], kwd)
        except Exception as e:
            print(e)
        contain_flag = False
        for seg in segments:
            tags = getTags(seg)
            # print(tags)
            # if not tags.difference(default_cmps):
            #     contain_flag = judgeTags(tags)
            # else:
            #     new_tags = transformTags(tags, target_json)
            #     contain_flag = judgeTags(new_tags)
            default_tags = [target_json[_] for tag in tags]
            contain_flag = judgeTags(default_tags)
            if contain_flag:
                break
        if contain_flag:
            res.add(kwd)
    return res


def confirmInput(path, target_json):
    # kwds = set()
    res = {}
    try:
        for root, dir, files in os.walk(path):
            for file in files:
                if not file.endswith(".wxml"):
                    continue
                file_path = os.path.join(root, file)
                single_wxml_kwds = confirmWXML(file_path, target_json)
                for kwd in single_wxml_kwds:
                    item = input_kwd_privacy[kwd]
                    if item in res:
                        tmp = res[item]
                        tmp.append({kwd:file_path})
                        res[item] = tmp
                    else:
                        res[item] = [{kwd:file_path}]
        return res
    except:
        return res


def getUserInput(path):
    # path = r"D:\lab\AImodelMobile\MicroProgram\Privacy\privacypolicy\code\test\wx32540bd863b27570"
    tags_mapping = constructCustomJson(path)
    kwds = confirmInput(path, tags_mapping)
    return kwds
