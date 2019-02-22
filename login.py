#coding=utf-8
import sys,time,datetime,os,requests
import json
import pytesseract
import base64
# import rsa
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64
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
        return value
    else:
        return ""


def handle_pub_key(key):
    start = '-----BEGIN PUBLIC KEY-----\n'
    end = '-----END PUBLIC KEY-----'
    result = ''
    # 分割key，每64位长度换一行
    divide = int(len(key) / 64)
    divide = divide if (divide > 0) else divide+1
    line = divide if (len(key) % 64 == 0) else divide+1
    for i in range(line):
        result += key[i*64:(i+1)*64] + '\n'
    result = start + result + end
    return result


def encrypt(content,key):
    pub_key = handle_pub_key(key)
    pub = RSA.import_key(pub_key)
    cipher = PKCS1_v1_5.new(pub)
    encrypt_bytes = cipher.encrypt(content.encode(encoding='utf-8'))
    result = base64.b64encode(encrypt_bytes)
    result = str(result, encoding='utf-8')
    return result 
 
def doLogin(username,password):
    passportPage=openPage(url)
    postPassportSSOShowTag(passportPage)
    boxStatus = "false"
    isInput="true"
    token = ""
    glCaptchaToken=getValueById("glCaptchaToken",passportPage)
    baclUrl=getValueById("backUrl",passportPage)
    sysname = getValueById("sysname",passportPage)
    publicKey=getPublicKey(passportPage)
    password_rsa=encrypt(password,publicKey)
    timenow=(int(round(time.time() * 1000)))
    loginUrl="http://passport.yaoex.com/passport/sso/pc_login"
    postData = { 
        "boxStatus": boxStatus,
        "isInput": isInput,
        "pc_userToken": token,
        "username": username,
        "password": password_rsa,
        "glCaptchaToken": glCaptchaToken,
        "sysname": sysname,
        "time": timenow,
        "backUrl":baclUrl
        }
    responseRes = webSession.post(loginUrl, data = postData, headers = defaultHeader,verify=False )
    webSession.cookies.save()
    print(f"statusCode = {responseRes.status_code}")
    # print(f"text = {responseRes.text}")
    return responseRes.text

def getMainPage():
    mainPageUrl="http://mall.yaoex.com/?source=1"
    print("mainPageUrl:"+mainPageUrl)
    responseRes = webSession.get(mainPageUrl,  headers = defaultHeader)
    print(f"statusCode = {responseRes.status_code}")
    # print(f"text = {responseRes.text}")
    webSession.cookies.save()
    return responseRes.text

def getLoginIfo():
    LoginInfoUrl="http://mall.yaoex.com/index/login"
    print("LoginInfoUrl:"+LoginInfoUrl)
    responseRes = webSession.get(LoginInfoUrl,  headers = defaultHeader)
    print(f"statusCode = {responseRes.status_code}")
    # print(f"text = {responseRes.text}")
    webSession.cookies.save()
    return responseRes.text

def reLogin():
    print("输入用户名：")
    username=input()
    print("输入密码：")
    password=input()
    login_msg=doLogin(username, password)
    if("\"successful\":true"in login_msg):
        print("登陆成功！")
    else:
        print("登录失败！！")
        print(login_msg)


def getCategoryList():
    categoryListUrl="http://mall.yaoex.com/catg/categoryList"
    print("categoryListUrl:"+categoryListUrl)
    responseRes = webSession.get(categoryListUrl,  headers = defaultHeader)
    print(f"statusCode = {responseRes.status_code}")
    # print(f"text = {responseRes.text}")
    webSession.cookies.save()
    return responseRes.text

def getCategoryListByCode(code):
    categoryListUrl="http://mall.yaoex.com/catg/secondCategoryList?code="+code
    print("categoryListUrl:"+categoryListUrl)
    responseRes = webSession.get(categoryListUrl,  headers = defaultHeader)
    print(f"statusCode = {responseRes.status_code}")
    # print(f"text = {responseRes.text}")
    webSession.cookies.save()
    return responseRes.text

def postSearchProductList(product2ndLMCode,nowPage):
    searchProductListUrl="http://gateway-b2b.fangkuaiyi.com/api/search/searchProductList"
    print("searchProductListUrl:"+searchProductListUrl)
    postData = { 
        "tradername": "yaoex_pc",
        "trader": "pc",
        "closesignature": "yes",
        "signature_method": "md5",
        "signature": "****",
        "timestamp": (int(round(time.time() * 1000))),
        "inputCharset": "utf-8",
        "charsetColumns": "keyword",
        "keyword": "",
        "decodeKeyword":  "" ,
        "userId":  "",
        "roleId":  "",
        "userType":  "",
        "buyerCode": "" ,
        "sellerCode": "" ,
        "spuCode":  "",
        "product2ndLMCode": product2ndLMCode,
        "haveGoodsTag": "false",
        "promotionTag": "false",
        "buyerHistoryTag": "false",
        "templateId":  "",
        "factoryIds":  "",
        "sellerCodes":  "",
        "sortColumn": "default",
        "sortMode": "desc",
        "nowPage": nowPage,
        "per": 10,
        "invokeType":  "",
        "drugName":  "",
        "factoryName": "" ,
        "spec": "" ,
        "sellerName":  "",
        }
    responseRes = webSession.post(searchProductListUrl, data = postData, headers = defaultHeader,verify=False )
    webSession.cookies.save()
    print(f"statusCode = {responseRes.status_code}")
    # print(f"text = {responseRes.text}")
    return responseRes.text

def readCategoryList():
    categoryListData=getCategoryList()
    categoryList=json.loads(categoryListData)
    categoryAll={}
    categoryMin={}
    if ("success" in categoryList['status']):
        print(len(categoryList['data']))
        for category in categoryList['data']:
            category2ListData=getCategoryListByCode(category['code'])
            category2List=json.loads(category2ListData)
            if ("success" in category2List['status']):
                if(len(category2List['data']['snd_catagory'])<1):
                        # print("终极分类："+category['fixCategoryName0'])
                        categoryMin[category['code']]=category['name']
                categoryAll[category['code']]=category['name']
                # print(category2List['data']['snd_catagory'])
                for category2 in category2List['data']['snd_catagory']:
                    category3ListData=getCategoryListByCode(category2['code'])
                    category3List=json.loads(category3ListData)
                    if ("success" in category3List['status']):
                        if(len(category3List['data']['snd_catagory'])<1):
                            # print("终极分类："+category2['name'])
                            categoryMin[category2['code']]=category2['name']
                        categoryAll[category2['code']]=category2['name']
                        # print(len(category3List['data']['snd_catagory']))
                        for category3 in category3List['data']['snd_catagory']:
                            category4ListData=getCategoryListByCode(category3['code'])
                            category4List=json.loads(category4ListData)
                            if ("success" in category4List['status']):
                                if(len(category4List['data']['snd_catagory'])<1):
                                    # print("终极分类："+category3['name'])
                                    categoryMin[category3['code']]=category3['name']
                                else:
                                    print("居然还有分类："+category4List['data']['snd_catagory'])
                                categoryAll[category3['code']]=category3['name']
                            # print("==读取："+category['fixCategoryName0']+" 次级目录中")
                            # print("====读取："+category2['name']+"   次级目录中")
                            # print("======读取："+category3['name']+"     次级目录中")
        return categoryMin
    else:
        print("Login err")
        return {}


def raedProductList(code,page):
    searchProductList=json.loads(postSearchProductList(code,1))
    print(searchProductList['rtn_msg'])
    pageCount=searchProductList['data']['pageCount']
    totalCount=searchProductList['data']['totalCount']
    print("pageCount:"+str(pageCount))
    print("totalCount"+str(totalCount))
            
def readCategoryProducts(code,name,page):
    print(code+ ":" + name)
    searchProductList=json.loads(postSearchProductList(code,1))
    print(searchProductList['rtn_msg'])
    pageCount=searchProductList['data']['pageCount']
    totalCount=searchProductList['data']['totalCount']
    print("pageCount:"+str(pageCount))
    print("totalCount"+str(totalCount))
    for i in range(1,pageCount+1):
        raedProductList(code,i)
    anything=input()


if __name__ == "__main__":
    webSession.cookies.load()
    print(webSession.cookies)
    mainpage=getMainPage()
    loGinInfo=getLoginIfo()
    # if("var showName = \'\'" in loGinInfo ):
    #     reLogin()
    # loGinInfo=getLoginIfo() 
    categoryList=readCategoryList()
    for x in categoryList.keys():
        print(x+ "  :  " + categoryList[x])
        searchProductList=json.loads(postSearchProductList(x,1))
        print(searchProductList['rtn_msg'])
        print("pageCount:"+str(searchProductList['data']['pageCount']))
        print("totalCount"+str(searchProductList['data']['totalCount']))
        print(searchProductList)
        anything=input()
        

    
     
    
    # if ("登录状态异常" in categoryList['rtn_msg']):
    #     print("Login err")
    # else:
    #     print(len(categoryList['data']))

 





