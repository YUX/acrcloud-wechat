# -*- coding: utf-8 -*-
import sys
import os
import requests
import json
from werkzeug.contrib.cache import SimpleCache
cache = SimpleCache()

from acrcloud_mac.recognizer import ACRCloudRecognizer #I use that because my desktop is OSX
"""if your server is linux DONT forget to change that before you deploy it.
check here to update the Python SDK for acrcloud https://github.com/acrcloud/acrcloud_sdk_python"""
#from acrcloud_linux.recognizer import ACRCloudRecognizer

reload(sys)
sys.setdefaultencoding('utf8')

def get_access_token():
    appid = #appid
    secret = #secret
    access_token = cache.get('access_token')
    if access_token is None:
        access_token = requests.get('https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' %(appid,secret)).json()["access_token"]
        cache.set('access_token', access_token, timeout= 7200)
    return access_token

"""
get_song_info() is function from a song name to get the whole song infomation(title,singer,url,etc..)
Please visit this project for more details.
https://github.com/YUX-IO/163music-APlayer-you-get-docker
"""
def get_song_info(s):
    song_info = cache.get(s)
    if song_info is None:
        l = requests.post("http://music.163.com/api/search/get/",{'s':s,'limit':1,'sub':'false','type':1,'offset':0}, headers={"Referer": "http://music.163.com/"}).json()["result"]["songs"][0]["id"]
        song_info = requests.get("https://music.daoapp.io/api/v1/song?id=%s&type=meta" %l).json()
        song_info["song_url"] = song_info["song_url"]
        song_info["pic_url"] = song_info["pic_url"]
        cache.set(s, song_info, timeout= 72000)
    return song_info

"""
this is to simply download the voice file and save it on the server.
make sure you download the voice before you try to recognise it.
"""
def dl_voice(MEDIA_ID):
    access_token = get_access_token()
    url = "https://api.weixin.qq.com/cgi-bin/media/get?access_token=%s&media_id=%s" %(access_token,MEDIA_ID)
    r = requests.get(url)
    with open("records/%s.amr" % MEDIA_ID, "wb") as code:
        code.write(r.content)
    return None

"""
This is our Star today to recognise our voice file.
visit https://www.acrcloud.com/ for API key
"""
def music_recognise(MediaId):
    config = {
        'host':'HOST',
        'access_key':'ACCESS_KEY',
        'access_secret':'ACCESS_SECRET',
        'debug':False,
        'timeout':5 # seconds
        }
    re = ACRCloudRecognizer(config)
    buf = open("records/%s.amr" % MediaId, "rb").read()
    return re.recognize_by_filebuffer(buf, 0)

"""
This is for sending the music to the user. it's not very useful.
you should use reply_music to reply a music.
http://mp.weixin.qq.com/wiki/14/89b871b5466b19b3efa4ada8e577d45e.html#.E5.9B.9E.E5.A4.8D.E9.9F.B3.E4.B9.90.E6.B6.88.E6.81.AF
"""
def sent_music(OpenID,MUSIC_TITLE,MUSIC_DESCRIPTION,MUSIC_URL):
    access_token = get_access_token()
    url = "https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=%s" % access_token
    data = {
    "touser":OpenID,
    "msgtype":"music",
    "music":
    {
      "title":MUSIC_TITLE,
      "description":MUSIC_DESCRIPTION,
      "musicurl":MUSIC_URL,
      "hqmusicurl":MUSIC_URL,
      "thumb_media_id": #thumb_media_id or just type something
    }
}
    r = requests.post(url, data=json.dumps(data, ensure_ascii=False).encode('utf8'))
    return None
