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


data_file=open("data.csv","a")
data_code=open("code.csv","a")
cList={}

try:
 
    import cookielib
    print(f"python2.")
except:
 
    import http.cookiejar as cookielib
    print(f"python3.")

 
webSession = requests.session()
webSession.cookies = cookielib.LWPCookieJar(filename = "cookie.txt")



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
    # print("searchProductListUrl:"+searchProductListUrl+"     code:"+str(product2ndLMCode)+"   page:"+str(nowPage))
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
    # print(f"statusCode = {responseRes.status_code}")
    # print(f"text = {responseRes.text}")
    return responseRes.text

def readCategoryList():
    categoryListData=getCategoryList()
    categoryList=json.loads(categoryListData)
    categoryAll={}
    categoryMin={}
    cData=""
    c2Data=""
    c3Data=""
    if ("success" in categoryList['status']):
        print(len(categoryList['data']))
        for category in categoryList['data']:
            category2ListData=getCategoryListByCode(category['code'])
            category2List=json.loads(category2ListData)
            if ("success" in category2List['status']):
                if(len(category2List['data']['snd_catagory'])<1):
                        # print("终极分类："+category['fixCategoryName0'])
                        categoryMin[category['code']]=category['name']
                        cData=category['name']
                        cList[category['code']]=cData+","+c2Data+","+c3Data
                categoryAll[category['code']]=category['name']
                # print(category2List['data']['snd_catagory'])
                for category2 in category2List['data']['snd_catagory']:
                    category3ListData=getCategoryListByCode(category2['code'])
                    category3List=json.loads(category3ListData)
                    if ("success" in category3List['status']):
                        if(len(category3List['data']['snd_catagory'])<1):
                            # print("终极分类："+category2['name'])
                            categoryMin[category2['code']]=category2['name']
                            cData=category['name']
                            c2Data=category2['name']
                            cList[category2['code']]=cData+","+c2Data+","+c3Data
                        categoryAll[category2['code']]=category2['name']
                        # print(len(category3List['data']['snd_catagory']))
                        for category3 in category3List['data']['snd_catagory']:
                            category4ListData=getCategoryListByCode(category3['code'])
                            category4List=json.loads(category4ListData)
                            if ("success" in category4List['status']):
                                if(len(category4List['data']['snd_catagory'])<1):
                                    # print("终极分类："+category3['name'])
                                    categoryMin[category3['code']]=category3['name']
                                    cData=category['name']
                                    c2Data=category2['name']
                                    c3Data=category3['name']
                                    cList[category3['code']]=cData+","+c2Data+","+c3Data
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


def raedProductDetial(spuCode,vendorId):
    productDetialUrl="http://mall.yaoex.com/product/productDetail/"+str(spuCode)+"/"+str(vendorId)
    print("productDetialUrl:"+productDetialUrl)
    responseRes = webSession.get(productDetialUrl,  headers = defaultHeader)
    print(f"statusCode = {responseRes.status_code}")
    # print(f"text = {responseRes.text}")
    webSession.cookies.save()
    return responseRes.text


def getHtmlByCode(fromCode,toCode,data):
    if(fromCode in data and toCode in data[data.index(fromCode):]):
        print(fromCode+","+toCode+", in data")
        value=data[data.index(fromCode)+len(fromCode):]
        value=value[:value.index(toCode)]
        return value
    else:
        return ""


def getHtmlById(id,htmlCode):
    divData=getHtmlByCode("id=\""+id+"\"","</div>",htmlCode)
    divData=divData[divData.index(">")+1:]
    return divData

def getMainInfo(data):
    return getHtmlByCode("<div class=\"product-inner fl\">","<div class=\"agreement_deal\">",data)   
 
def removeTags(htmlCode):
    data=htmlCode
    while ("<" in data and ">"in data[data.index("<")+1:]):
        databefor=data[:data.index("<")]
        dataafter=data[data.index("<")+1:]
        if((len(dataafter)-1)==(dataafter.index(">")+1)):
            dataafter=""
        else:
            dataafter=dataafter[dataafter.index(">")+1:]
        data=databefor+dataafter
    # print(data)
    return data

def writeFirstLine():
    searchProductList=json.loads(postSearchProductList("ABA",1))
    if (searchProductList['data']==None):
        return None
    try:
        data_file.write( "一级分类,二级分类,三级分类,spuCode,vendorId,")
        data_file.flush()
        pass
    except:
        return
    for x in searchProductList['data']['shopProducts']:
        for y in x :
            try:
                data_file.write( y+",")
                data_file.flush()
                pass
            except:
                try:
                    data_file.write( "\n")
                    data_file.flush()
                    continue
                except:
                    return
    try:
            data_file.write( "\n")
            data_file.flush()
            pass
    except:
            return
    return

def writeFirstCodeLine():
    searchProductList=json.loads(postSearchProductList("ABA",1))
    if (searchProductList['data']==None):
        return None
    try:
        data_code.write( "一级分类,二级分类,三级分类,spuCode,vendorId,")
        data_code.flush()
        pass
    except:
        return
    for x in searchProductList['data']['shopProducts']:
        for y in x :
            try:
                data_code.write( y+",")
                data_code.flush()
                pass
            except:
                try:
                    data_code.write( "\n")
                    data_code.flush()
                    continue
                except:
                    return    
    try:
            data_code.write( "\n")
            data_code.flush()
            pass
    except:
            return
    return

def raedProductList(code,page):
    searchProductList=json.loads(postSearchProductList(code,page))
    if (searchProductList['data']==None):
        return None
    # print(searchProductList['rtn_msg'])
    # pageCount=int(searchProductList['data']['pageCount'])
    # totalCount=int(searchProductList['data']['totalCount'])
    # print("pageCount:"+str(pageCount))
    # print("totalCount"+str(totalCount))
    for x in searchProductList['data']['shopProducts']:
        data=""
        data=data+cList[code]+","+ x['spuCode']+","+x['vendorId']+","
        for y in x:
            data=data+str(x[y]).replace(",","，").strip()+","
        productDetial=raedProductDetial(x['spuCode'],x['vendorId'])
        detial=getMainInfo(productDetial)
        detial=removeTags(detial)
        detial=detial.expandtabs(tabsize=4)
        detial=detial.strip()
        detial=detial.replace("\n/g"," ")
        detial=detial.replace("\n\n"," ")
        detial=detial.replace("\n"," ")
        detial=detial.replace("&nbsp;","")
        detial=detial.expandtabs(tabsize=4)
        detial=detial.expandtabs(tabsize=4)
        detial=detial.replace("  "," ")
        detial=detial.replace("  "," ")
        detial=detial.replace("  "," ")
        detial=detial.replace("  "," ")
        # print(detial)
        # anything=input()
        # # print(removeTags(productName))
        # # anything=input()
        # # print(productDetial)
        # anything=input()
        data=data+detial.replace(",","，").strip().replace("\n"," ")+","
        data=data+"\n"
        # print(data)
        # anything=input()
        try:
            data_code.write(data)
            data_code.flush()
            pass
        except:       
            try:
                data_code.write("\n")
                data_code.flush()
                continue
            except  :
                return searchProductList['data']['shopProducts']
    return searchProductList['data']['shopProducts']
            
def readCategoryProducts(code,name,page):
    print(code+ ":" + name)
    searchProductList=json.loads(postSearchProductList(code,1))
    print(searchProductList['rtn_msg'])
    pageCount=searchProductList['data']['pageCount']
    totalCount=searchProductList['data']['totalCount']
    print("pageCount:"+str(pageCount))
    print("totalCount"+str(totalCount))
    for i in range(page,pageCount+1):
        print(cList[code]+"   : page :"+str(i)+"  ALL:"+ str(totalCount))
        shopProducts=raedProductList(code,i)
        if(shopProducts==None):
            return
        # print(len(shopProducts))
        # print(shopProducts)

        
    


if __name__ == "__main__":
    webSession.cookies.load()
    print(webSession.cookies)
    mainpage=getMainPage()
    loGinInfo=getLoginIfo()
    # if("var showName = \'\'" in loGinInfo ):
    #     reLogin()
    loGinInfo=getLoginIfo() 
    categoryList=readCategoryList()
    # cList=categoryList
    writeFirstLine()
    for x in categoryList.keys():
        readCategoryProducts(x,categoryList[x],1)
        # searchProductList=json.loads(postSearchProductList(x,1))
        # print(searchProductList['rtn_msg'])
        # print("pageCount:"+str(searchProductList['data']['pageCount']))
        # print("totalCount"+str(searchProductList['data']['totalCount']))
        # print(searchProductList)
    anything=input()
data_file.close()
data_code.close()
    # if ("登录状态异常" in categoryList['rtn_msg']):
    #     print("Login err")
    # else:
    #     print(len(categoryList['data']))