# SPO

Our code and dataset to study the Privacy Over-collection in Sub-apps (SPO)



[EN]

## Input

### parameters

1. certain user's user_hash which can be found in path /data/data/com.tencent.mm/MicroMsg/
2. target output directory {TARGET_DIR}
3. name of sub-app to be analysed
4. privacy policy of sub-app to be analysed

## Detection Process

1. Download Main Package
   output:
   a. {TARGET_DIR}/appinfo.txt: username, appID, nickname(name of sub-app)
   b. main package in path {TARGET_DIR}/{APPID}/{MAIN_PACKAGE_NAME}.wxapkg
2. Unpack Main Package And Extract Sub-Packages Info
   output:
   a. {TARGET_DIR}/{APPID}/pkg/*.wxapkg and relative depacked directories
3. Detect Over-Collection Behavior
   output:
   a. over-collection report in {TARGET_DIR}/{APPID}/over_collection_report.txt
   b. privacy policy template in {TARGET_DIR}/{APPID}/privacy_policy_template.txt

## Output

1. apkinfo.txt
2. {APPID}
   a. main package and relative directory
   b. pkg/*: sub packages and relative directories
   c. over_collection_report.txt
   d. privacy_policy_template.txt

## Note

Due to difference among phone models, you may modify value of coordinates of several components which we have annotated specific information in the *setBackground* function of file 'packages.py'.

This tool requires Xposed, so you need to get Xposed prepared by yourself and install the two modules in the *modules* beforehand.



[CN]

## 输入

### 参数

1. 微信专属 user_hash，可以在 /data/data/com.tencent.mm/MicroMsg/ 路径下找到
2. 目标输出路径 {TARGET_DIR}
3. 待检测小程序名
4. 待检测小程序隐私政策文本

## 运行流程

1. 根据给定小程序名爬取主包，输出：
   a. {TARGET_DIR}/appinfo.txt，文档中给出目标小程序的 开发者id、APPID、小程序名
   b. 小程序主包，{TARGET_DIR}/{APPID}/{主包名}.wxapkg
2. 解包主包代码，扫描主包配置文件，获取子包信息列表，逐个爬取子包，输出
   a. {TARGET_DIR}/{APPID}/pkg/*.wxapkg 及对应解包文件夹
3. 扫描代码行为，与隐私政策文本进行差异性分析，输出
   a. 小程序超范围隐私收集报告，{TARGET_DIR}/{APPID}/over_collection_report.txt
   b. 小程序隐私政策文本模板，{TARGET_DIR}/{APPID}/privacy_policy_template.txt

## 输出

1. apkinfo.txt
2. {APPID}
   a. 主包文件及文件夹
   b. pkg/*，子包文件及文件夹
   c. over_collection_report.txt
   d. privacy_policy_template.txt

## 说明

由于测试机型不同，使用时需要修改 packages.py 中 setBackground 方法中的组件坐标。具体组件已在注释中标注，修改相应坐标值即可。

本工具需要使用Xposed，使用时请自行安装Xposed，并事先安装好modules文件夹中的两个模块。
