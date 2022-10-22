from packages import downloadMiniApp
from policyAnalyser import scanPolicy
import re
from scanInput import getUserInput
from data import *
import os


def scanDeviceAPI(file):
    res = {}
    ctnt = open(file, "r", encoding = "utf-8").read()
    for api in device_api_privacy.keys():
        if not ".*?" in api:
            if not api in ctnt:
                continue
            item = device_api_privacy[api]
            if item in res:
                tmp = res[item]
                tmp.append({
                    api:file
                })
            else:
                res[item] = [{api:file}]
        else:
            pattern = re.compile(api, re.S)
            if not re.findall(pattern, ctnt):
                continue
            item = device_api_privacy[api]
            if item in res:
                tmp = res[item]
                tmp.append({
                    api:file
                })
            else:
                res[item] = [{api:file}]
    return res

        
def scanPltAPI(file):
    res = {}
    ctnt = open(file, "r", encoding = "utf-8").read()
    for api in plt_api_privacy.keys():
        if not api in ctnt:
            continue
        item = plt_api_privacy[api]
        if item in res:
            tmp = res[item]
            tmp.append({
                api:file
            })
        else:
            res[item] = [{api:file}]
    return res


def overCollectionDetect(target_dir, policy, output_dir):
    policy = scanPolicy(policy)
    
    device = {}
    plt = {}
    for root, dir, files in os.walk(target_dir):
        for file in files:
            if not file.endswith(".js") and not file.endswith(".wxml"):
                continue
            file_path = os.path.join(root, file)
            print("SCAN {}......".format(file_path))
            device_res = scanDeviceAPI(file_path)
            plt_res = scanPltAPI(file_path)

            for item, l in device_res.items():
                if item in device:
                    tmp = device[item]
                    tmp.extend(l)
                    device[item] = tmp
                else:
                    device[item] = l

            for item, l in plt_res.items():
                if item in plt:
                    tmp = plt[item]
                    tmp.extend(l)
                    plt[item] = tmp
                else:
                    plt[item] = l
    uinput = getUserInput(target_dir)

    collect_items = set(uinput.keys()).union(set(device.keys())).union(set(plt.keys()))
    # print(collect_items)
    # print(policy)
    over = collect_items.difference(set(policy))

    over_report = open(output_dir + "/over_collection_report.txt", "w", encoding = "utf-8")
    for item in over:
        if item in device:
            info = device[item]
        elif item in plt:
            info = plt[item]
        elif item in uinput:
            info = uinput[item]
        over_report.write("· 过度收集了隐私项 ---{}---\n:".format(item))
        # over_report.write("\t在文件{}调用了")
        api_mapping = {}
        for single in info:
            for api, file in single.items():
                if api in api_mapping:
                    file_list = api_mapping[api]
                    file_list.append(file)
                    api_mapping[api] = file_list
                else:
                    api_mapping[api] = [file]
        for api, file_list in api_mapping.items():
            over_report.write("\t-在以下文件调用相关API：wx{}\n".format(api))
            for f in file_list:
                over_report.write("\t\t{}\n".format(f))
        over_report.write("\n\n")

    pp = open(output_dir + "/privacy_policy_template.txt", "w", encoding = "utf-8")
    pp.write("我们向您请求以下权限：\n")
    count = 0
    for item in collect_items:
        count += 1
        pp.write("{}. {}\n".format(count, item))
        pp.write("为了____，我们收集您的{}信息。\n\n".format(item))
    pp.write("\n\n\n" + "-"*50 + "\n")
    pp.write("您具体隐私信息收集行为如下：\n")
    for item in collect_items:
        if item in device:
            info = device[item]
        elif item in plt:
            info = plt[item]
        elif item in uinput:
            info = uinput[item]
        pp.write("· 收集了隐私项 ---{}---\n:".format(item))
        api_mapping = {}
        for single in info:
            for api, file in single.items():
                if api in api_mapping:
                    file_list = api_mapping[api]
                    file_list.append(file)
                    api_mapping[api] = file_list
                else:
                    api_mapping[api] = [file]
        for api, file_list in api_mapping.items():
            pp.write("\t-在以下文件调用相关API：wx{}\n".format(api))
            for f in file_list:
                pp.write("\t\t{}\n".format(f))
        pp.write("\n\n")
