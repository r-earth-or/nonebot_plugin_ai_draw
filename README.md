# nonebot_plugin_ai_draw  
# 目前无法使用  
这个插件是基于第三方api的novel ai 插件，使用了sqlite3进行违禁词管理，用户次数管理和群冷却管理  
所获取的图片均保存在本插件目录下temp文件夹内 ~~(可以光明正大地收集色图了好耶)~~  
~~(屎山)~~

## 安装
使用git clone或直接下载本插件  
把__init__.py和data_init放入nonebot的插件目录的同一文件夹下  
在.env.dev中加入如下内容  
```
baidu_translate_appid= "你的百度翻译appid"" 
baidu_translate_key= "你的百度翻译key" 
draw_api = "你的token"
```

百度翻译api相关内容可以在[百度翻译api](https://api.fanyi.baidu.com/ )申请  
~~路路的api的token可以点击[这里](http://lulu.uedbq.xyz/token "路佬牛逼")申请~~接口寄了  

## 使用方法  

### 在群中使用  

在装有这个插件的机器人的群中发送  
`画画 你想要输入的tag`  
其中tag建议为英文（中文会经过判断后通过百度翻译api翻译为英文）  
（但是有的时候判断会有些问题，比如`我老婆`会被识别为英文）  
在群中使用会受到用户使用次数和群cd限制  
用户使用次数刷新时间为第一次使用后的24小时  

### 在私聊中使用
和群聊一样，但是不受群cd限制，也没有次数限制


### 管理命令
**这些命令只能对superuser有反应，且只能在群里使用**  
1.添加违禁词  
`draw设置添加关键词 需要屏蔽的关键词`  
2.删除违禁词  
`draw设置删除关键词 需要删除的关键词`  
3.设置群cd  
`draw设置群 群号 群cd时间`  
或  
`draw设置群 群cd时间`（自动获取本群群号）  
（群cd时间单位为秒）  
4.设置用户次数  
`draw设置用户 用户id 次数`  
会同时更新可用次数和已经使用的次数，但不会更新次数刷新的时间  
5.修改用户初始次数
`draw设置初始次数 次数`
不会对已经进入user_data.db的用户进行操作  
6.注入  
允许输入sql语句对数据库进行直接操作  
对user_data.db 操作  
`draw注入user sql语句`  
对config.db 操作  
`draw注入config sql语句`  
user_data.db中的表：GROUP_CD,USER  
GROUP_CD中有三个列：GROUP_ID,CD,FIRST_TIME,类型都是int  
USER中有四个列：QQ_ID,USED_TIME,TOTAL_TIME,FIRST_USE类型都是int  
config.db中的表：BAN_WORDS，CONFIG  
BAN_WORDS中有一个列：WORDS，类型是text  
CONFIG中有梁列：NAME和CONFIG，类型都是text  

### 更新日志 
2023.1.20  
简化代码  
添加检测数据库是否存在的机制并可以自动创建数据库  
（包含预设违禁词和预设使用次数）  
2022.10.18  
更改了业务逻辑，减少了误触发的可能性  
修改了超过文件名长后的处理方式，这样就不会出现超长tag情况下只会保存最后一份了  
bug fix  
2022.10.16  
允许直接更改用户的初始次数（在config.db的CONFIG表中）  
api地址也写入了这一个表  
更新了路路的备用api地址  
bug修复  
注：本次更新需同时更新config.db和__init__.py  
