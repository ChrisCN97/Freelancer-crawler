from bs4 import BeautifulSoup
import requests
import time
import pymysql

def getHTML(url):
    try:
        r=requests.get(url,timeout=200)
        r.raise_for_status()
        r.encoding=r.apparent_encoding
        return r.text
    except:
        print("获取Url失败:", url)
        return 0

def getProUrl(html, proUrl):
    if html == 0:
        return 0
    soup = BeautifulSoup(html, "html.parser")
    projectList = soup.find(id='project-list')
    proUrlList = []
    for project in projectList.children:
        if project == '\n':
            continue
        status = project.find(class_='JobSearchCard-primary-heading-days').string
        if status != "已经结束 left":
            continue
        url = project.find(class_='JobSearchCard-primary-heading-link')['href']
        proUrlList.append(url)
    print("******", proUrl, "本页共有", len(proUrlList), "个项目")
    return proUrlList

def getDetail(html, url):
    if html == 0:
        return 0
    soup = BeautifulSoup(html, "html.parser")
    detailDic = dict()
    if not soup.find(class_='PageProjectViewLogout-header-title'):
        return None
    detailDic['proName'] = soup.find(class_='PageProjectViewLogout-header-title').string
    detailDic['url'] = url
    print(detailDic['proName'], detailDic['url'], end=" ")
    proDescription = ""
    for s in soup.find(class_='PageProjectViewLogout-detail').stripped_strings:
        proDescription += s + " "
    detailDic['proDescription'] = proDescription
    proTag = ""
    for s in soup.find(class_='PageProjectViewLogout-detail-tags').stripped_strings:
        if s == "技能：":
            continue
        proTag += s + " "
    detailDic['proTag'] = proTag
    detailDic['devList'] = []
    award = soup.find(class_='PageProjectViewLogout-awardedTo')
    if award:
        devDic = dict()
        devBasic = award.find(class_='FreelancerInfo-username')
        devDic['name'] = devBasic.string
        devDic['url'] = devBasic['href']
        devDic['description'] = award.find(class_='FreelancerInfo-about')['data-descr-full']
        devDic['isAward'] = "1"
        detailDic['devList'].append(devDic)
    for dev in soup.find_all(class_='PageProjectViewLogout-freelancerInfo'):
        devDic = dict()
        devBasic = dev.find(class_='FreelancerInfo-username')
        devDic['name'] = devBasic.string
        devDic['url'] = devBasic['href']
        devDic['description'] = dev.find(class_='FreelancerInfo-about')['data-descr-full']
        devDic['isAward'] = "0"
        detailDic['devList'].append(devDic)
    print(" 共有", len(detailDic['devList']), "个开发者", end=" ")
    return detailDic

def sqlExe(db, cursor, sql, params):
    try:
        # 执行sql语句
        cursor.execute(sql, params)
        # 提交到数据库执行
        db.commit()
        return True
    except:
        # 如果发生错误则回滚
        db.rollback()
        print("写入失败:", sql)
        return False

def colon(s):
    return "\'" + s + "\'"

def mysqlWrite(detailDic, db, cursor):
    cursor.execute("select 1 from `project` where `url` = " + colon(detailDic['url']) + " limit 1")
    if len(cursor.fetchall()) != 0:
        print("已写入")
        return
    cursor.execute("SELECT MAX(`MATCH`.id) FROM `MATCH`")
    initID = cursor.fetchall()[0][0]
    match = ";"
    for devDic in detailDic['devList']:
        sql = "INSERT INTO `MATCH`(projectUrl, developerUrl, isAward, description) VALUES (%s,%s,%s,%s)"
        params = (detailDic['url'], devDic['url'], devDic['isAward'], devDic['description'])
        if sqlExe(db, cursor, sql, params):
            initID += 1
            match += str(initID) + ";"
        cursor.execute("select 1 from `developer` where `url` = "+colon(devDic['url'])+" limit 1")
        if len(cursor.fetchall()) == 0:
            sql = "INSERT INTO `developer`(url, name, project) VALUES (%s,%s,%s)"
            params = (devDic['url'], devDic['name'], ";"+detailDic['url']+";")
            sqlExe(db, cursor, sql, params)
        else:
            sql = "update `developer` set `project`=CONCAT(`project`, %s) where `url`=%s"
            params = (detailDic['url']+";", devDic['url'])
            sqlExe(db, cursor, sql, params)
    sql = "INSERT INTO `PROJECT`(url, name, tag, description, `match`) VALUES (%s,%s,%s,%s,%s)"
    params = (detailDic['url'], detailDic['proName'], detailDic['proTag'], detailDic['proDescription'], match)
    sqlExe(db, cursor, sql, params)
    print("写入完成")

def control():
    db = pymysql.connect("localhost", "root", "19971002", "freelancer")
    cursor = db.cursor()
    for i in range(39, 151):
        proUrl = "https://www.freelancer.cn/jobs/" + str(i+1) + "/?status=all&languages=zh"
        proUrlList = getProUrl(getHTML(proUrl), proUrl)
        n = 1
        total = len(proUrlList)
        for url in proUrlList:
            print("{}/{} ".format(n, total), end=" ")
            n += 1
            detailDic = getDetail(getHTML("https://www.freelancer.cn"+url), url)
            if not detailDic:
                continue
            mysqlWrite(detailDic, db, cursor)
            time.sleep(3)  # 防止系统检测封IP
    db.close()

if __name__ == "__main__":
    control()