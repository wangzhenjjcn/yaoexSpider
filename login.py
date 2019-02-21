#coding=utf-8
import sys,time,datetime,os,requests

import pytesseract
import base64
# import rsa
from Cryptodome.Cipher import PKCS1_v1_5
from Cryptodome.PublicKey import RSA
from PIL import Image
from random import random
 
try:
 
    import cookielib
    print(f"python2.")
except:
 
    import http.cookiejar as cookielib
    print(f"python3.")

 
webSession = requests.session()
webSession.cookies = cookielib.LWPCookieJar(filename = "mafengwoCookies.txt")



url = "http://passport.yaoex.com/"

defaultHeader = {
        'upgrade-insecure-requests': "1",
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        'dnt': "1",
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        'accept-encoding': "gzip, deflate",
        'accept-language': "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6",
        'cache-control': "no-cache"
        }

def openPage(URL):
    print("open:"+URL)
    responseRes = webSession.get(URL,  headers = defaultHeader)
    print(f"statusCode = {responseRes.status_code}")
    # print(f"text = {responseRes.text}")
    webSession.cookies.save()
    return responseRes.text


def postPassportSSOShowTag(passportPage):
    postPassportSSOShowTagURL = "http://passport.yaoex.com/passport/sso/show_tag"
    postPassportSSOShowTagHeader = {
        'upgrade-insecure-requests': "1",
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        'dnt': "1",
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        'accept-encoding': "gzip, deflate",
        'accept-language': "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6",
        'cache-control': "no-cache",
        'referer': url,
        'origin': url,

        }
    postData = { 
        }
    responseRes = webSession.post(postPassportSSOShowTagURL, data = postData, headers = postPassportSSOShowTagHeader,verify=False )
    webSession.cookies.save()
    print(f"statusCode = {responseRes.status_code}")
    # print(f"text = {responseRes.text}")
    return responseRes.text


def getValueById(id,data):
    if("id=\""+id+"\"" in data):
        valueData=data[data.index("id=\""+id+"\""):]
        valueData=valueData[valueData.index("value=\""):]
        valueData=valueData[7:]
        valueData=valueData[:valueData.index("\"")]
        return(valueData)
    else:
        return ""

def getPublicKey(data):
    if("pubkey" in data):
        value=data[data.index("pubkey"):]
        value=value[value.index("\'")+1:]
        value=value[:value.index("\'")]
        print(value)
        return value
    else:
        return ""

 
 
def doLogin(username,password):
    passportPage=openPage(url)
    postPassportSSOShowTag(passportPage)
    boxStatus = "false"
    print(boxStatus)
    isInput="true"
    token = ""
    glCaptchaToken=getValueById("glCaptchaToken",passportPage)
    baclUrl=getValueById("backUrl",passportPage)
    sysname = getValueById("sysname",passportPage)
    print(sysname)
    print(glCaptchaToken)
    print(baclUrl)  
    print(isInput)  
    print(token)  
    publicKey=getPublicKey(passportPage)
    print(publicKey)
    key = RSA.import_key(publicKey)
    passwd = PKCS1_v1_5.new(key)
    # text = base64.b64encode(passwd.encrypt(bytes(password, encoding='utf-8')))
    # password_rsa=rsa.encrypt(password, key)
    print(str(passwd))


if __name__ == "__main__":
    webSession.cookies.load()
    print(webSession.cookies)
    doLogin("test", "123456")





