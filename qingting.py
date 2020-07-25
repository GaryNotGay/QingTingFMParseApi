import json
import time
import hmac
import base64
import requests

def getDetail(userID, channel):
    url = 'https://i.qingting.fm/capi/v3/channel/' + str(channel) + '?user_id=' + str(userID)
    response = requests.get(url)
    result = response.content.decode('utf-8')
    resultJson = json.loads(result)
    v = resultJson['data']['v']
    name = resultJson['data']['title']
    total = resultJson['data']['program_count']
    return v, name, total

def getList(userID, v, channel, total):
    if total <= 100:
        url = 'https://i.qingting.fm/capi/channel/' + str(channel) + '/programs/' + str(v) + '?curpage=1&pagesize=' + str(total) + '&order=asc'
        response = requests.get(url)
        result = response.content.decode('utf-8')
        resultJson = json.loads(result)
        detail = resultJson['data']['programs']
        return detail
    else:
        detail = []
        for index in range(int(total/100) + 1):
            url = 'https://i.qingting.fm/capi/channel/' + str(channel) + '/programs/' + str(v) + '?curpage=' + str(index+1) + '&pagesize=100&order=asc'
            response = requests.get(url)
            result = response.content.decode('utf-8')
            resultJson = json.loads(result)
            detail += resultJson['data']['programs']
        return detail

def getUserInfo():
    user_id = 'Your LoginID'
    password = 'Your Password'
    data = {'account_type': '5', 'device_id': 'web', 'user_id': user_id, 'password': password}
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4181.9 Safari/537.36'}
    url = 'https://u2.qingting.fm/u2/api/v4/user/login'
    response = requests.post(url = url, json = data, headers = headers)
    result = response.content.decode('utf-8')
    resultJson = json.loads(result)
    qingting_id = resultJson['data']['qingting_id']
    access_token = resultJson['data']['access_token']
    return qingting_id, access_token

def getLen(length):
    i = ''
    h = int(length / 3600)
    if not h == 0:
        i += str(h)
        i += 'h'
    length %= 3600
    m = int(length / 60)
    if not m == 0:
        i += str(m)
        i += 'm'
    length %= 60
    if not length == 0:
        i += str(length)
        i += 's'
    return i

def CreatSign(url):
    message = bytes(url, 'utf-8')
    key = bytes('fpMn12&38f_2e', 'utf-8')
    sign = hmac.new(key, message, digestmod='MD5').hexdigest()
    return sign

def getDownUrl(channel, audioID, userID, AccessToken):
    cookies = {'qingting_id': ''}
    cookies['qingting_id'] = userID
    timestamp = int(time.time() * 1000)
    domain = 'https://audio.qingting.fm'
    url =  '/audiostream/redirect/' + str(channel) + '/' + str(audioID) + '?access_token=' + str(AccessToken) + '&device_id=MOBILESITE&qingting_id=' + str(userID) + '&t=' + str(timestamp)
    sign = CreatSign(url)
    url += '&sign=' + str(sign)
    return domain + url

info = '232855+0'
#info = '232855+10104604'
infoarr = info.split('+')
channel = infoarr[0]
audioID = infoarr[1]
isFull = False
if audioID == '0':
    isFull = True

UserInfo = getUserInfo()
userID = UserInfo[0]
AccessToken = UserInfo[1]
AudioDetail = getDetail(userID, channel)
v = AudioDetail[0]
name = AudioDetail[1]
total = AudioDetail[2]
AudioList = getList(userID, v, channel, total)

if not isFull:
    res = {}
    for index in range(len(AudioList)):
        if str(AudioList[index]['id']) == audioID:
            audioName = AudioList[index]['title']
            duration = AudioList[index]['duration']
            break
    length = getLen(duration)
    downUrl = getDownUrl(channel, audioID, userID, AccessToken)
    res[name + '-' + audioName + '-' + length] = downUrl
    print(res)
else:
    res = {}
    for index in range(len(AudioList)):
        audioName = AudioList[index]['title']
        duration = AudioList[index]['duration']
        length = getLen(duration)
        downUrl = getDownUrl(channel, audioID, userID, AccessToken)
        res[audioName + '-' + length] = downUrl
    print(name)
    print(res)
