import asyncio
import hashlib
import json
import os
import random
import re
import sqlite3
import time

import httpx
import langid
from nonebot import get_driver
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, PrivateMessageEvent, Event
from nonebot.adapters.onebot.v11.message import MessageSegment
from nonebot.log import logger
from nonebot.permission import SUPERUSER
from nonebot.plugin.on import on_startswith
from nonebot.plugin.plugin import PluginMetadata

draw_g = on_startswith("画画", priority=51, block=False)
draw_p = on_startswith("画画", priority=52)
set_data = on_startswith("draw设置", priority=30, permission=SUPERUSER)
inject = on_startswith("draw注入", priority=30, permission=SUPERUSER)

current_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + ".") + "\\"

__plugin_meta__ = PluginMetadata(
    name="AI画画",
    description="通过输入关键词让ai画画",
    usage="画画 [关键词]（建议输入英文）",
    extra={
        "example": "画画 loli",
        "author": "r earth or <1669241401@qq.com>",
        "version": "1.0.0",
    },
)
if not os.path.exists(current_path + "temp"):
    os.makedirs(current_path + "temp")


async def translate(text):
    async with httpx.AsyncClient() as client:
        success = False
        _appid = get_driver().config.baidu_translate_appid
        _salt = random.randint(10000000, 99999999)
        _key = get_driver().config.baidu_translate_key
        _sign = f"{_appid}{text}{_salt}{_key}"
        _sign = hashlib.md5(bytes(_sign, 'utf-8')).hexdigest()
        for times in range(5):
            try:
                url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
                params = {
                    "q": text,
                    "from": "zh",
                    "to": "en",
                    "appid": _appid,
                    "salt": _salt,
                    "sign": _sign,
                }
                json_data = await client.post(url, params=params)
            except Exception as e:
                logger.warning(f"第{times + 1}次连接失败... {type(e)}: {e}")
                continue
            else:
                success = True
    if not success:
        logger.debug("翻译失败")
        await draw_g.finish("error,请参考日志")
    json_data = json_data.json()
    logger.debug(f"结果: {json_data}")
    if "error_code" not in json_data.keys():
        _result = json_data['trans_result'][0]
        return _result['dst']
    else:
        logger.debug("翻译返回文件出错")
        await draw_g.finish("error,请参考日志")


def give_time_back(userid, times):
    user_data_con = sqlite3.connect(current_path + "user_data.db")
    user_data_cur = user_data_con.cursor()
    user_data_cur.execute(F"UPDATE USER SET USED_TIME = {times} WHERE QQ_ID={userid}")
    user_data_con.commit()
    user_data_con.close()


@draw_g.handle()
async def draw_group(bot: Bot, event: GroupMessageEvent):
    get_message = event.get_plaintext()
    get_message = get_message.split(" ", 1)
    if len(get_message) == 1:
        await draw_p.finish()
    config_con = sqlite3.connect(current_path + "config.db")
    config_cur = config_con.cursor()
    ban_words = config_cur.execute('''SELECT WORDS FROM BAN_WORDS''').fetchall()
    api_address = config_cur.execute('''SELECT CONFIG FROM CONFIG WHERE NAME = "API_ADDRESS"''').fetchone()[0]
    user_init_times = int(config_cur.execute('''SELECT CONFIG FROM CONFIG WHERE NAME = "USER_INIT_TIMES"''').fetchone()[0])
    user_data_con = sqlite3.connect(current_path + "user_data.db")
    user_data_cur = user_data_con.cursor()
    groupid = int(event.group_id)
    group_data = user_data_cur.execute(f'''SELECT * FROM GROUP_CD WHERE GROUP_ID = {groupid}''').fetchall()
    if len(group_data) == 0:
        # 注册群冷却
        logger.debug(2)
        user_data_cur.execute('''insert into GROUP_CD values(?,?,?)''', (groupid, 10, 0))
        user_data_con.commit()
        group_data = [(groupid, 10, 0)]
    userid = int(event.user_id)

    user_data = user_data_cur.execute(f'''SELECT * FROM USER WHERE QQ_ID = {userid}''').fetchall()
    if len(user_data) == 0:
        # 注册个人使用次数限制
        logger.debug(4)
        user_data_cur.execute('''insert into USER values(?,?,?,?)''', (userid, user_init_times, user_init_times, int(time.time())))
        user_data_con.commit()
        user_data = [(userid, user_init_times, user_init_times, int(time.time()))]
    logger.debug(f"{group_data}{user_data}")
    if int(group_data[0][2]) + int(group_data[0][1]) > int(time.time()):
        await draw_g.finish("冷却中")
        config_con.close()
        user_data_con.close()
    if user_data[0][3] + 86400 < int(time.time()):
        # 与上次使用时间间隔24小时后更新使用次数并更新数据
        logger.debug(5)
        user_data_cur.execute(F'''UPDATE USER SET USED_TIME = {user_data[0][2]} WHERE QQ_ID = {userid}''')
        user_data_cur.execute(F'''UPDATE USER SET FIRST_USE = {int(time.time())} WHERE QQ_ID = {userid}''')
        user_data_con.commit()
        user_data = user_data_cur.execute(f'''SELECT * FROM USER WHERE QQ_ID = {userid}''').fetchall()
    if user_data[0][1] == 0:
        await draw_g.finish("你的使用次数用完了哦")
        config_con.close()
        user_data_con.close()
    else:
        # 使用次数并更新群cd
        await draw_g.send(f"你今天还有{user_data[0][1] - 1}次画画次数")
        user_data_cur.execute(f'''UPDATE USER SET USED_TIME = {user_data[0][1] - 1} WHERE QQ_ID = {userid}''')
        user_data_cur.execute(f'''UPDATE GROUP_CD SET FIRST_TIME = {int(time.time())} WHERE GROUP_ID = {groupid}''')
        user_data_con.commit()
        config_con.close()
        user_data_con.close()
    if langid.classify(get_message[1])[0] == "zh" or get_message[1] == "我老婆":
        # 检测是否需要翻译
        msg_id3 = (await draw_g.send("不建议输入中文的说"))["message_id"]
        _translate = True
        text = await translate(get_message[1])
    else:
        _translate = False
        text = get_message[1]
    for i in ban_words:
        key_word = i[0]
        if text.find(key_word) != -1:
            text = text.replace(key_word, " ")
    if text.find(".") != -1:
        text = text.replace(".", ",")
    logger.info(text)
    # 输出过滤后的结果
    token = get_driver().config.draw_api
    url = api_address + "got_image?tags=" + text + f"&r18=0&token={token}"
    async with httpx.AsyncClient() as client:
        get_image = await client.get(url, timeout=None)
        get_image = get_image.content
        try:
            load_data = json.loads(re.findall('{"steps".+?}', str(get_image))[0])
            seed = load_data["seed"]
        except IndexError:
            give_time_back(userid, user_data[0][1])
            await draw_g.finish("请求失败，请过段时间重试，次数已返还")
    file_name = current_path + "temp\\" + text + str(seed)
    if len(file_name) > 255:
        file_name = file_name[:255] + ".jpg"
    else:
        file_name = file_name + ".jpg"
    try:
        file = open(file_name, mode="wb")
        file.write(get_image)
        file.close()
    except:
        logger.debug("文件保存出错")
        give_time_back(userid, user_data[0][1])
        await draw_g.finish("文件保存失败，请检查输入内容中是否存在奇怪的特殊字符")
    msg_id1 = (await draw_g.send(MessageSegment.image(f"file:///{file_name}")))["message_id"]
    await asyncio.sleep(60)
    msg_id2 = (await draw_g.send('再等你30秒我就撤回了哦~'))['message_id']
    await asyncio.sleep(30)
    await bot.call_api('delete_msg', **{
        'message_id': msg_id1
    })
    await bot.call_api('delete_msg', **{
        'message_id': msg_id2
    })
    if _translate:
        await bot.call_api('delete_msg', **{
            'message_id': msg_id3
        })
    await draw_g.finish()


@draw_p.handle()
async def draw_private(bot: Bot, event: PrivateMessageEvent):
    config_con = sqlite3.connect(current_path + "config.db")
    config_cur = config_con.cursor()
    ban_words = config_cur.execute('''SELECT WORDS FROM BAN_WORDS''').fetchall()
    api_address = config_cur.execute('''SELECT CONFIG FROM CONFIG WHERE NAME = "API_ADDRESS"''').fetchone()[0]
    get_message = event.get_plaintext()
    get_message = get_message.split(" ", 1)
    if len(get_message) == 1:
        await draw_p.finish()
    if langid.classify(get_message[1])[0] == "zh" or get_message[1] == "我老婆":
        # 检测是否需要翻译
        msg_id3 = (await draw_p.send("不建议输入中文的说"))["message_id"]
        _translate = True
        text = await translate(get_message[1])
    else:
        _translate = False
        text = get_message[1]
    for i in ban_words:
        key_word = i[0]
        if text.find(key_word) != -1:
            text = text.replace(key_word, "")
    if text.find(".") != -1:
        text = text.replace(".", ",")
    logger.info(text)
    # 输出过滤后的结果
    token = get_driver().config.draw_api
    url = api_address + "got_image?tags=" + text + f"&r18=0&token={token}"
    async with httpx.AsyncClient() as client:
        get_image = await client.get(url, timeout=None)
        get_image = get_image.content
        try:
            load_data = json.loads(re.findall('{"steps".+?}', str(get_image))[0])
            seed = load_data["seed"]
        except IndexError:
            await draw_g.finish("请求失败，请过段时间重试")
    file_name = current_path + "temp\\" + text + str(seed)
    if len(file_name) > 255:
        file_name = file_name[:255] + ".jpg"
    else:
        file_name = file_name + ".jpg"
    try:
        file = open(file_name, mode="wb")
        file.write(get_image)
        file.close()
    except:
        logger.debug("文件保存出错")
        await draw_g.finish("文件保存失败，请检查输入内容中是否存在奇怪的特殊字符")
    msg_id1 = (await draw_p.send(MessageSegment.image(f"file:///{file_name}")))["message_id"]
    await asyncio.sleep(60)
    msg_id2 = (await draw_p.send('再等你30秒我就撤回了哦~'))['message_id']
    await asyncio.sleep(30)
    await bot.call_api('delete_msg', **{
        'message_id': msg_id1
    })
    await bot.call_api('delete_msg', **{
        'message_id': msg_id2
    })
    if _translate:
        await bot.call_api('delete_msg', **{
            'message_id': msg_id3
        })
    await draw_g.finish()


@set_data.handle()
async def set_data_handle(bot: Bot, event: GroupMessageEvent):
    # 几个常用的设置
    # 只能在群里用
    text = event.get_plaintext()[6:].split()
    if text[0] == "添加关键词":
        # 例：draw设置添加关键词 关键词
        config_con = sqlite3.connect(current_path + "config.db")
        config_cur = config_con.cursor()
        config_cur.execute(f'''INSERT INTO BAN_WORDS VALUES ("{text[1]}")''')
        config_con.commit()
        config_con.close()
        await set_data.finish("添加成功")
    elif text[0] == "删除关键词":
        # 例：draw设置删除关键词 关键词
        user_data_con = sqlite3.connect(current_path + "user_data.db")
        user_data_cur = user_data_con.cursor()
        user_data_cur.execute(f'''DELETE FROM BAN_WORDS WHERE WORDS = "{text[1]}"''')
        user_data_con.commit()
        user_data_con.close()
        await set_data.finish("删除成功")
    elif text[0] == "群":
        # 例：draw设置群 群号 群CD（秒）
        user_data_con = sqlite3.connect(current_path + "user_data.db")
        user_data_cur = user_data_con.cursor()
        if len(text) == 2:
            groupid = int(event.group_id)
        else:
            groupid = int(text[1])
        user_data_cur.execute(f'''UPDATE GROUP_CD SET CD = {int(text[-1])} WHERE GROUP_ID = {groupid}''')
        user_data_con.commit()
        user_data_con.close()
        await set_data.finish("群cd已改为" + text[-1])
    elif text[0] == "用户":
        # 例：draw设置用户 用户QQ 用户使用次数（次）
        # 会同时更新可用次数和已经使用的次数
        user_data_con = sqlite3.connect(current_path + "user_data.db")
        user_data_cur = user_data_con.cursor()
        userid = int(text[1])
        user_data_cur.execute(f'''UPDATE USER SET TOTAL_TIME = {int(text[2])} WHERE QQ_ID = {userid}''')
        user_data_cur.execute(f'''UPDATE USER SET USED_TIME = {int(text[2])} WHERE QQ_ID = {userid}''')
        user_data_con.commit()
        user_data_con.close()
        await set_data.finish("用户可用次数已改为" + text[2])
    elif text[0] == "初始次数":
        # 例：draw设置初始次数 次数
        # 不会对已经加入数据库的用户进行更改
        config_con = sqlite3.connect(current_path + "config.db")
        config_cur = config_con.cursor()
        config_cur.execute(f'''UPDATE CONFIG SET CONFIG = {str(text[1])} WHERE NAME = "USER_INIT_TIME"''')
        config_con.commit()
        config_con.close()
        await set_data.finish("初始次数已改为" + text[1])


@inject.handle()
async def inject_handle(bot: Bot, event: Event):
    # 开放注入的接口给超级管理员，用于一些特殊的需求
    text = event.get_plaintext()[6:].split(" ", 1)
    if text[0] == "user":
        user_data_con = sqlite3.connect(current_path + "user_data.db")
        user_data_cur = user_data_con.cursor()
        user_data_cur.execute(text[1])
        user_data_con.commit()
        user_data_con.close()
        await inject.finish("执行成功")
    elif text[0] == "config":
        config_con = sqlite3.connect(current_path + "config.db")
        config_cur = config_con.cursor()
        config_cur.execute(text[1])
        config_con.commit()
        config_con.close()
        await inject.finish("执行成功")
