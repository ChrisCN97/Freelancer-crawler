from bs4 import BeautifulSoup
import requests

def getHTML(url):
    try:
        print("获取url中...")
        r=requests.get(url,timeout=200)
        r.raise_for_status()
        r.encoding=r.apparent_encoding
        print("获取url完成")
        return r.text
    except:
        print("获取Url失败")
        return 0

def getProUrl(html):
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
        url = "https://www.freelancer.cn" + project.find(class_='JobSearchCard-primary-heading-link')['href']
        proUrlList.append(url)
    return proUrlList

def getDetail(html):
    if html == 0:
        return 0
    soup = BeautifulSoup(html, "html.parser")
    detailDic = dict()
    detailDic['proName'] = soup.find(class_='PageProjectViewLogout-header-title').string
    proDescription = ""
    for s in soup.find(class_='PageProjectViewLogout-detail').stripped_strings:
        proDescription += s + " "
    detailDic['proDescription'] = proDescription
    detailDic['devList'] = []
    award = soup.find(class_='PageProjectViewLogout-awardedTo')
    if award:
        devDic = dict()
        devBasic = award.find(class_='FreelancerInfo-username')
        devDic['name'] = devBasic.string
        devDic['url'] = devBasic['href']
        devDic['description'] = award.find(class_='FreelancerInfo-about')['data-descr-full']
        devDic['isAward'] = True
        detailDic['devList'].append(devDic)
    for dev in soup.find_all(class_='PageProjectViewLogout-freelancerInfo'):
        devDic = dict()
        devBasic = dev.find(class_='FreelancerInfo-username')
        devDic['name'] = devBasic.string
        devDic['url'] = devBasic['href']
        devDic['description'] = dev.find(class_='FreelancerInfo-about')['data-descr-full']
        devDic['isAward'] = False
        detailDic['devList'].append(devDic)
    return detailDic

def control():
    for i in range(10):
        proUrl = "https://www.freelancer.cn/jobs/" + str(i+1) + "/?status=all&languages=zh"
        proUrlList = getProUrl(getHTML(proUrl))
        for url in proUrlList:
            getDetail(getHTML(url))


if __name__ == "__main__":
    detailDic = getDetail(getHTML("https://www.freelancer.cn/projects/html/Build-strategy-through-pine-script/"))
    print(detailDic)