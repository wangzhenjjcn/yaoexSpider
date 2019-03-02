#coding=utf-8
import sys,time,datetime,os,requests
import json
import base64
# import rsa
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64
from PIL import Image
from random import random
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     

data_file=open("./tmp/data.csv","a",encoding='utf-8')
data_code=open("./tmp/code.csv","a",encoding='utf-8')
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
    # print(f"statusCode = {responseRes.status_code}")
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
    # print(f"statusCode = {responseRes.status_code}")
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
    print(f"statusCode = {responseRes.status_code}"+":"+loginUrl)
    # print(f"text = {responseRes.text}")
    return responseRes.text

def getMainPage():
    mainPageUrl="http://mall.yaoex.com/?source=1"
    # print("mainPageUrl:"+mainPageUrl)
    responseRes = webSession.get(mainPageUrl,  headers = defaultHeader)
    # print(f"statusCode = {responseRes.status_code}" +":"+mainPageUrl)
    # print(f"text = {responseRes.text}")
    webSession.cookies.save()
    return responseRes.text

def getLoginIfo():
    LoginInfoUrl="http://mall.yaoex.com/index/login"
    # print("LoginInfoUrl:"+LoginInfoUrl)
    responseRes = webSession.get(LoginInfoUrl,  headers = defaultHeader)
    # print(f"statusCode = {responseRes.status_code}"+":"+LoginInfoUrl)
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


def getHtmlByCode(fromCode,toCode,data):
    if(fromCode in data and toCode in data[data.index(fromCode):]):
        # print(fromCode+","+toCode+", in data")
        value=data[data.index(fromCode)+len(fromCode):]
        value=value[:value.index(toCode)]
        return value
    else:
        return ""


def getCategoryList():
    categoryListUrl="http://mall.yaoex.com/catg/categoryList"
    # print()
    responseRes = webSession.get(categoryListUrl,  headers = defaultHeader)
    # print(f"statusCode = {responseRes.status_code}"+":"+categoryListUrl)
    # print(f"text = {responseRes.text}")
    webSession.cookies.save()
    return responseRes.text

def getCategoryListByCode(code):
    categoryListUrl="http://mall.yaoex.com/catg/secondCategoryList?code="+code
    # print("categoryListUrl:"+categoryListUrl)
    responseRes = webSession.get(categoryListUrl,  headers = defaultHeader)
    # print(f"statusCode = {responseRes.status_code}"+":"+categoryListUrl)
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
    print(f"statusCode = {responseRes.status_code}"+":"+searchProductListUrl+"     code:"+str(product2ndLMCode)+"   page:"+str(nowPage))
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
    print("开始读取分类列表代码")
    if ("success" in categoryList['status']):
        # print(len(categoryList['data']))
        for category in categoryList['data']:
            category2ListData=getCategoryListByCode(category['code'])
            category2List=json.loads(category2ListData)
            if ("success" in category2List['status']):
                if(len(category2List['data']['snd_catagory'])<1):
                        # print("终极分类："+category['fixCategoryName0'])
                        categoryMin[category['code']]=category['name']
                        cData=category['name']
                        cList[category['code']]=category['code']+","+cData+","+c2Data+","+c3Data
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
                            cList[category2['code']]=category2['code']+","+cData+","+c2Data+","+c3Data
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
                                    cList[category3['code']]=category3['code']+","+cData+","+c2Data+","+c3Data
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
    responseRes = webSession.get(productDetialUrl,  headers = defaultHeader)
    # print(f"statusCode = {responseRes.status_code}" +":"+productDetialUrl)
    # print(f"text = {responseRes.text}")
    webSession.cookies.save()
    return responseRes.text



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

def writeFirstLine(file):
    searchProductList=json.loads(postSearchProductList("ABA",1))
    if (searchProductList['data']==None):
        return None
    try:
        file.write( "分类代码,一级分类,二级分类,三级分类,spuCode,vendorId,")
        file.flush()
        pass
    except:
        return
    for x in searchProductList['data']['shopProducts']:
        for y in x :
            try:
                if(y!=None and y!="None"):
                    file.write( y+",")
                else:
                    file.write(",")
                file.flush()
                pass
            except:
                try:
                    file.write( "\n")
                    file.flush()
                    continue
                except:
                    return
    try:
            file.write( "\n")
            file.flush()
            pass
    except:
            return
    return

def writeFirstCodeLine(file):
    searchProductList=json.loads(postSearchProductList("ABA",1))
    if (searchProductList['data']==None):
        return None
    try:
        file.write( "分类代码,一级分类,二级分类,三级分类,spuCode,vendorId,")
        file.flush()
        pass
    except:
        print("ERRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")
        return
    for y in searchProductList['data']['shopProducts'][0] :
        try:
            if(y!=None and y!="None"):
                file.write( str(y)+",")
            else:
                file.write( ",")
            
            file.flush()
            pass
        except:
            print("ERRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")
            try:
                file.write( "\n")
                file.flush()
                continue
            except:
                return    
    try:
            file.write( "\n")
            file.flush()
            pass
    except:
            print("ERRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")
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
            if(y!=None and y!="None"):
                data=data+str(x[y]).replace(",","，").strip()+","
            else:
                data=data+","
        productDetial=raedProductDetial(x['spuCode'],x['vendorId'])
        print("Read:"+str(removeTags(getHtmlByCode("<h3>","</h3>",productDetial))).strip().replace(" ","").replace("\n","").replace("   ","").replace("  ","").replace(" ","").replace("&nbsp;","").expandtabs(tabsize=4))
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
        detial=detial.replace("  "," ").replace("\n"," ")
        detial=detial.replace("  "," ").replace("\n"," ")
        detial=detial.replace("  "," ").replace("\n"," ")
        detial=detial.replace("  "," ").replace("\n"," ")
        data=data+detial.replace(",","，").strip().replace("\n"," ")+","
        data=data+"\n"
        data=data.replace("\xef\xbf\xbd","").replace("\ufffd","").replace("\uFFFD","")
        data=data
        # print(data)
        # anything=input()
        try:
            data_code.write(data)
            data_code.flush()
            pass
        except Exception as e:       
            try:
                print("ERRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")
                print("ERRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")
                print("ERRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")
                print(data)
                print("ERRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")
                print("ERRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")
                print("按下任意键继续")
                print(e)
                anything=input()
                data_code.flush()
                continue
            except Exception as e2:  
                print(e2)
                print("按下任意键继续")
                anything=input()
                return searchProductList['data']['shopProducts']
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
            return "err shopProducts None page:" + i +"  code:"+code+"  name:"+name
        # print(len(shopProducts))
        # print(shopProducts)

    return "Finished code:"+code+"  Name:"+name
    


if __name__ == "__main__":
    webSession.cookies.load()
    # print(webSession.cookies)
    mainpage=getMainPage()
    loGinInfo=getLoginIfo()
    if("var showName = \'\'" in loGinInfo ):
        reLogin()
    loGinInfo=getLoginIfo() 
    categoryList=readCategoryList()
    # cList=categoryList
    # writeFirstCodeLine()
    numreturn=0
    dataout=""
    check=""


    for x in categoryList.keys():
        data2add=str(x)+":"+categoryList[x]+""
        for i in range(1,30-len(str(x)+":")-2*len(categoryList[x])):
            data2add+=" "
        dataout=dataout+ data2add
        
        numreturn+=1
        if(numreturn==5):
            numreturn=0
            print(dataout)
            dataout=""
    print(dataout)
    print("按照以上代码，输入你要下载的分类，所有分类请直接回车")

    toCheck=input()
    toCheck=toCheck.upper()
    if(toCheck==None or  toCheck==""):
        data_code=open("./tmp/All.csv","a",encoding='utf-8')
        print("开始读取所有分类商品，请稍候")
    else:    
        if(toCheck in categoryList.keys()):
            data_code=open("./tmp/"+categoryList[toCheck]+".csv","a",encoding='utf-8')
        else:
            data_code=open("./tmp/"+toCheck+".csv","a",encoding='utf-8')
        print("开始读取编码为："+toCheck+"的商品，请稍候")
    writeFirstCodeLine(data_code)
    for x in categoryList.keys():
        if(x==toCheck or toCheck==None or toCheck==""):
            check="yes"
        if(check!="yes"):
            continue
        print("正在读取"+str(x)+":"+categoryList[x])      
        resault=readCategoryProducts(x,categoryList[x],1)
        print(resault)
        if(toCheck!="" and  toCheck!=None):
            break
        # searchProductList=json.loads(postSearchProductList(x,1))
        # print(searchProductList['rtn_msg'])
        # print("pageCount:"+str(searchProductList['data']['pageCount']))
        # print("totalCount"+str(searchProductList['data']['totalCount']))
        # print(searchProductList)

    newFile = open("./"+categoryList[toCheck]+".csv","wb")
    oldFile = open("./tmp/"+categoryList[toCheck]+".csv","rb")
    contents = oldFile.readlines()
    newFile.writelines(contents)
    newFile.close()
    oldFile.close()



data_file.close()
data_code.close()

if data_file:
    data_file.close()
if data_code:
    data_code.close()



anything=input()

    # if ("登录状态异常" in categoryList['rtn_msg']):
    #     print("Login err")
    # else:
    #     print(len(categoryList['data']))