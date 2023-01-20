import sqlite3
import os

current_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + ".") + "\\"


def config_init():
    config_con = sqlite3.connect(current_path + "config.db")
    config_cur = config_con.cursor()
    config_cur.execute('''CREATE TABLE BAN_WORDS
    (WORDS TEXT NOT NULL);
    ''')
    init_words = ["&r18=1", "nsfw", "sex", "cum", "/", "completely rude", "penis", "nude", "bdsm", 'no clothes',
                  "without clothes", ":"]
    for words in init_words:
        config_cur.execute('''INSERT INTO BAN_WORDS VALUES(?)''', (words,))
    config_cur.execute('''CREATE TABLE CONFIG
    (NAME TEXT NOT NULL,
    CONFIG TEXT NOT NULL)''')
    config_cur.execute('''INSERT INTO CONFIG VALUES(?, ?)''', ("USER_INIT_TIMES", "5"))
    config_cur.execute('''INSERT INTO CONFIG VALUES(?, ?)''', ("API_ADDRESS", "http://91.217.139.190:5010/"))
    config_con.commit()
    config_con.close()


def userdata_init():
    userdata_con = sqlite3.connect(current_path + "user_data.db")
    userdata_cur = userdata_con.cursor()
    userdata_cur.execute('''CREATE TABLE GROUP_CD
    (GROUP_ID INT NOT NULL, 
    CD INT NOT NULL,
    FIRST_TIME INT NOT_NULL);
    ''')
    userdata_cur.execute('''CREATE TABLE USER
    (QQ_ID INT NOT NULL,
    USED_TIME INT NOT NULL,
    TOTAL_TIME INT NOT NULL,
    FIRST_USE INT NOT NULL
    );''')
    userdata_con.commit()
    userdata_con.close()

