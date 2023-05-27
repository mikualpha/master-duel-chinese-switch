# Master Duel 中文翻译补丁(2023.05修改版)

[原项目地址](https://gitee.com/fetiss/master-duel-chinese-switch) | [原发布页](https://www.bilibili.com/read/cv21869124) | [API来源](https://ygocdb.com/)

本项目是在作者 [@叶lf](https://space.bilibili.com/23834819) / [@Timelic](https://space.bilibili.com/8664322) 工作的基础上进行的，在此表示感谢！

----

因为MD自2023年5月初版本起，将`data.unity3d`的文件释放到`LocalData`文件夹下了，原有的翻译补丁失效。所以对原项目进行了一定的修改。

因为开发环境没有接`Gitee`(外加发`Releases`没有`GitHub`友好)，所以把库拉到了`GitHub`来修改了……

严格意义来说并不符合开源礼仪，原作者大大看到了还请见谅Orz

如果出现报错或闪退可提issue，**欢迎有兴趣的童鞋提PR~~~**

----
### 注意事项
1. 因为文件结构发生了变化，使用本地替换的话请把`output`下的所有文件夹替换至游戏目录`LocalData/c7afc9a7/0000`文件夹下(应该粘贴时有覆盖提示)；

2. 原版文件备份存储于`EXE`文件同目录下的`_TranslationBackup`文件夹内，只有进行过汉化翻译安装才有备份，所以没进行过汉化的无法进行一键翻译恢复，这点需要注意；

3. **游戏客户端版本更新**，需要重新安装翻译时**请删除**`_TranslationBackup`**文件夹**(不然可能有未知问题)。

### 未解决的问题

1. 目前字体替换方面还有BUG(隶书的部分字没有覆盖到)，推测为字库文件需要更新(但并不会改这玩意QAQ)。请先使用楷体。


### 开发相关
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
