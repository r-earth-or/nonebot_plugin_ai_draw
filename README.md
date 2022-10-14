# nonebot_plugin_ai_draw  

这个插件是基于第三方api的novel ai 插件，使用了sqlite3进行违禁词管理，用户次数管理和群冷却管理  
~~(屎山)~~

## 安装
使用git clone或直接下载本插件  
把__init__.py和config.db,user_data.db放入nonebot的插件目录的同一文件夹下  
在.env.dev中加入如下内容  
```
baidu_translate_appid= "你的百度翻译appid"" 
baidu_translate_key= "你的百度翻译key" 
draw_api = "你的token"
```

百度翻译api相关内容可以在[百度翻译api](https://api.fanyi.baidu.com/ )申请  
路路的api的token可以点击[这里](http://91.217.139.190:5010/token "路佬牛逼")申请  

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
5.注入  
允许输入sql语句对数据库进行直接操作  
对user_data.db 操作  
`draw注入user sql语句`  
对config.db 操作  
`draw注入config sql语句`  
user_data.db中的表：GROUP_CD,USER  
GROUP_CD中有三个列：GROUP_ID,CD,FIRST_TIME,类型都是int  
USER中有四个列：QQ_ID,USED_TIME,TOTAL_TIME,FIRST_USE类型都是int  
config.db中的表：BAN_WORDS  
BAN_WORDS中有一个列：WORDS，类型是text  
