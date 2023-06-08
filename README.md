<h1 align="center">Master Duel 中文翻译补丁(2023.05修改版)</h1>
<div align="center">

![GitHub releases](https://img.shields.io/github/v/release/mikualpha/master-duel-chinese-switch?style=flat-square)
![GitHub license](https://img.shields.io/github/license/mikualpha/master-duel-chinese-switch?style=flat-square)
![GitHub last commit](https://img.shields.io/github/last-commit/mikualpha/master-duel-chinese-switch?style=flat-square)
![GitHub download count](https://img.shields.io/github/downloads/mikualpha/master-duel-chinese-switch/total?style=flat-square)

[原项目地址](https://gitee.com/fetiss/master-duel-chinese-switch) | [原发布页](https://www.bilibili.com/read/cv21869124) | [API来源](https://ygocdb.com/)
  
</div>

本项目是在作者 [@叶lf](https://space.bilibili.com/23834819) / [@Timelic](https://space.bilibili.com/8664322) 工作的基础上进行的，在此表示感谢！

----

因为自2023年5月初版本起，MD将`data.unity3d`的文件释放到`LocalData`文件夹下了，原有的翻译补丁失效。所以对原项目进行了一定的修改。

## 使用方式
前往[Releases页面](https://github.com/mikualpha/master-duel-chinese-switch/releases)下载`MDTR_vx.x.x.exe`，同时参考本项目README和原项目发布页使用。

（因`MDTR_vx.x.x.exe`已能正常使用，短期内不再提供离线补丁`OfficialPatch.zip`）

### 注意事项
1. 因为文件结构发生了变化，使用本地替换的话请把`output`下的所有文件夹替换至游戏目录`LocalData/[随机8位16进制数]/0000`文件夹下（粘贴时应该有覆盖提示）；

2. 原版文件备份存储于`EXE`文件同目录下的`_TranslationBackup`文件夹内，只有进行过汉化翻译安装才有备份，所以没进行过汉化的无法进行一键翻译恢复，这点需要注意；

3. 当**游戏版本更新**，需要重新安装翻译时**请删除`_TranslationBackup`文件夹**（不然可能有未知问题）。

### 未解决的问题
1. 暂时只支持在源语言是`简体中文`的情况下进行转换，因为现在MD切换语言会把之前的语言文件删掉，暂时没想到有什么可以跨语言对照文本的方法；

2. 因社区翻译中的个别生僻字没有被官方字体文件收录，UI上的`黑体`字可能会出现缺字现象（如`魊影`系列卡片），从字体文件修改难度（以及卡片使用率）的角度考虑，先暂时搁置此问题（**有想法的欢迎提PR**）。

## 开发相关
本项目使用 `UnityPy` 解包，使用 `flet` 制作界面。

![](./images/display.jpg)
#### 准备

```
pip install -r requirements.txt
```

#### 开发

无界面

```
python index.py
```

flet 界面

```
flet run interface.py
```

#### 打包

PowerShell:

```
./release.ps1
```

## 题外话
因为开发环境没有接`Gitee`(外加发`Releases`没有`GitHub`友好)，所以把库拉到`GitHub`来修改了……严格意义来说并不符合开源礼仪，还请原作者大大见谅Orz

如果出现报错或闪退可提issue，**欢迎有兴趣的童鞋提PR~~~**

**若认为此项目对您有帮助可考虑给项目点个`Star`，谢谢~**
