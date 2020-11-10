# 3dtiles_downloader
python3 3dtiles下载工具

### 依赖环境
python3

### 使用方法
直接运行downloader.py

### 目前存在的问题
access_token 目前需要自己指定，通过查看请求titleset.json request headers 中accept信息可以拿到access_token

### 关于代理设置
自动套用系统代理设置

### 适用版本
cesium 1.75 (2020-11)。
后继若版本升级，在验证机制不大改的情况下，从Cesium/Source/Core/ION.js提取新token。

### 参考内容
[elfc2000/3dtilesdownloader](https://github.com/elfc2000/3dtilesdownloader)
[junyuz/3dtiles_downloader](https://github.com/junyuz/3dtiles_downloader)
