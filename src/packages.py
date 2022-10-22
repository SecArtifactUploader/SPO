import subprocess
import os
import time
import uiautomator2 as u2
import sys
import re
import json
import operator
# from packages_sub import *
import shutil
from OCDetect import *


def convert_4_bytes(n):
    bits=4*8
    return (n+2**(bits-1))%2**bits-2**(bits-1)

def hashCode(s):
    h=0
    n=len(s)
    for i,c in enumerate(s):
        h=h+ord(c)*31**(n-1-i)
    return convert_4_bytes(h)


def printLog(tag, content):
    print(">>>>>>>>>\t{}".format(tag))
    print("...{}".format(content))

def sleep(length = 0.5):
    time.sleep(0.5)

def setBackground(keyword):
    ### mini program searching activity
    ### [HIGILIGHT] Modify component coordinates according to phone model ###
    d.app_start("com.tencent.mm", stop = True)
    time.sleep(5)
    d(text="发现").click()
    sleep()
    scroll_e = d(scrollable=True)
    if scroll_e.exists():
        scroll_e.scroll.toEnd()
    d(text="小程序").click()
    time.sleep(5)
    
    d.click(886, 126)       # coordinates of "search" icon
    time.sleep(6)
    d.click(207, 142)       # coordinates of "search" text
    time.sleep(1)
    d.set_clipboard(keyword)
    time.sleep(2)
    d.click(207, 142)       # coordinates of "search" text
    d.long_click(207, 142)  # coordinates of "search" text
    time.sleep(3)
    d.click(187, 210)       # coordinates of "paste" icon
    time.sleep(3)
    d.click(207, 142)       # coordinates of "search" text
    time.sleep(1)
    d.click(975, 2117)      # coordinates of "enter" button in keyboard
    time.sleep(3)
    d.click(301, 486)       # coordinates of the first mini-app in result list
    time.sleep(8)
    return


def refreshWechat():
    d.app_start("com.tencent.mm" , stop = True)
    print("******RESTART WECHAT******")
    time.sleep(5)


def copyPkgDown(user_hash, output_dir):
    cmd = 'adb shell "su -c cp /data/data/com.tencent.mm/MicroMsg/{}/appbrand/pkg/* /sdcard/pkg/"'.format(user_hash)
    with os.popen(cmd) as f:
        printLog("DOWNLOAD", "copying pkgs")
    downcmd = 'adb pull /sdcard/pkg {}'.format(output_dir)
    with os.popen(downcmd) as f:
        printLog("DOWNLOAD", "pulling pkgs")


def extract_metadata_by_line(line):
    line_list = line.split(", ")
    username = line_list[0].split("'")[1]
    appId = line_list[1].split("'")[1]
    brandName = line_list[2].split("'")[1]
    return [username, appId, brandName]


def extractAppid(output_dir):
    meta_pattern = re.compile("username='.*?', appId='.*?', brandName='.*?'", re.S)
    cmd = 'adb shell tail -n 1 /sdcard/appid.txt'
    read_line = os.popen(cmd)
    line = read_line.buffer.read().decode("utf-8")

    meta_info = re.findall(meta_pattern, line)[0]
    info_list = extract_metadata_by_line(meta_info)

    open(output_dir + "appinfo.txt", "w", encoding = "utf-8").write(str(info_list) + "\n")

    return info_list[1]


def clearPkgs(user_hash):
    cmd = 'adb shell "su -c rm /data/data/com.tencent.mm/MicroMsg/{}/appbrand/pkg/*"'.format(user_hash)
    handle = os.popen(cmd)
    with handle as f:
        printLog("DOWNLOAD", "clear pkgs in mini-apps")
    cmd = 'adb shell "su -c rm /sdcard/pkg/*"'
    handle = os.popen(cmd)
    with handle as f:
        printLog("DOWNLOAD", "clear pkgs in /sdcard/pkg/")

def downloadMiniApp(user_hash, mini_name, output_dir):
    # print(mini_name)
    try:
        # clearPkgs(user_hash)
        printLog("DOWNLOAD", "downloading pkgs in mini-apps")
        setBackground(mini_name)
    except Exception as e:
        print(e)
        print("err!!!{}".format(mini_name))
    copyPkgDown(user_hash, output_dir)
    appid = extractAppid(output_dir)
    hashcode = str(hashCode(appid + "$__APP__"))
    print(appid, hashcode)
    return appid, hashcode


def depackageMainPkg(main_pkg):
    printLog("DOWNLOAD", "...depackage main pkg...")
    depack_tool = "./modules/wxappUnpacker/wuWxapkg.js"
    cmd = "node {} {}".format(depack_tool, main_pkg)
    # depack = os.popen(cmd)
    printLog("DEPACKAGE", main_pkg)
    res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    sout, serr = res.communicate()
    if sout:
        print('[*]', str(sout, 'utf-8'))
    if serr:
        print('[*]', str(serr, 'utf-8'))

    


def depackageSubPkg(main_dir, sub_pkg):
    depack_tool = "./modules/wxappUnpacker/wuWxapkg.js"
    cmd = "node {} {} -s={}".format(depack_tool, sub_pkg, main_dir)
    # depack = os.popen(cmd)
    printLog("DEPACKAGE", sub_pkg)
    res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    sout, serr = res.communicate() 

def mycopyfile(srcfile,dstfile):
    if not os.path.isfile(srcfile):
        print ("%s not exist!"%(srcfile))
    else:
        fpath=os.path.dirname(srcfile)    #获取文件路径
        if not os.path.exists(fpath):
            os.makedirs(fpath)                #没有就创建路径
        shutil.copyfile(srcfile,dstfile)      #复制文件到默认路径
        print ("copy %s -> %s"%( srcfile,os.path.join(fpath,dstfile)))  


def setsubBackground():
    top_ac = os.popen('adb shell "dumpsys activity top | grep ACTIVITY"').readlines()[-1].strip()
    if "com.tencent.mm/.plugin.appbrand.ui.AppBrandUI" in top_ac:
        return
    if not "com.tencent.mm/.plugin.appbrand.ui.AppBrandLauncherUI" in top_ac:
        os.popen('adb shell "su -c am start -n com.tencent.mm/.plugin.appbrand.ui.AppBrandLauncherUI"')
    time.sleep(1)
    d.click(645, 1488)
    time.sleep(3)
    return


def invokeMiniApp(appid):
    cmdBase = 'adb shell am broadcast -a android.intent.myper --es appid "{}"'
    cmd = cmdBase.format(appid)
    setsubBackground()
    os.popen(cmd)
    time.sleep(3)
    # d.click(400,2500)
    time.sleep(2)
    d.click(1321,184)


def downloadSubpkgs(appid, paths):
    setsubBackground()
    mainpkg=str(hashCode(appid+"$__APP__"))
    invokeMiniApp(appid)
    for path in paths:
        if not path.startswith("/"):
            path='/'+path
        path=path.replace("(","\\(").replace(")","\\)")
        print(appid, path)
        invokeMiniApp(appid+"$"+path)


if __name__ == "__main__":    
    d = u2.connect()
    # print(d.info)

    ########################################### configure ####################################
    # user_hash = "185437c2627bfcf90395612a7a0cfce0"
    # output_dir = "D:/lab/AImodelMobile/MicroProgram/Privacy/privacypolicy/code/test/"
    # mini_name = "拼多多"
    user_hash = sys.argv[1]
    output_dir = sys.argv[2]
    mini_name = sys.argv[3]
    policy_path = sys.argv[4]

    ####################################### download Main package ############################################
    pkg_dir = output_dir + "pkg/"
    appid, hashcode = downloadMiniApp(user_hash, mini_name, output_dir)
    miniapp_dir = output_dir + "{}/".format(appid)
    if not os.path.exists(miniapp_dir):
        os.makedirs(miniapp_dir)
    main_pkg = ""
    pkg_ver = ""
    for filename in os.listdir(pkg_dir):
        if hashcode in filename:
            main_pkg = filename
            pkg_ver = filename.split(".wxapkg")[0].split("_")[-1]
            mycopyfile(pkg_dir + filename, miniapp_dir + filename)
    printLog("DOWNLOAD", "MAIN PACKAGE DOWNLOADED IN {}".format(pkg_dir))
    main_dir = miniapp_dir + main_pkg.replace(".wxapkg", "/")

    ################################## depackage Main package and extract sub pkg info ###############################
    depackageMainPkg(miniapp_dir + main_pkg)
    appconfig = main_dir + "app-config.json"
    appconfig_json = json.loads(open(appconfig, "r", encoding = "utf-8").read())
    subs = appconfig_json["subPackages"]
    subs = [_["pages"][0] for _ in subs]

    ######################### download sub packages ############################
    downloadSubpkgs(appid, subs)
    copyPkgDown(user_hash, miniapp_dir)
    sub_pkg_dir = miniapp_dir + "pkg/"
    for subpkg in os.listdir(sub_pkg_dir):
        if "_{}.wxapkg".format(pkg_ver) in subpkg:
            depackageSubPkg(main_dir, sub_pkg_dir + subpkg)
        else:
            continue

    ########################## analysis #######################################
    overCollectionDetect(miniapp_dir, policy_path, miniapp_dir)

