import re
import requests
import bs4
from bs4 import BeautifulSoup


header = {'Host': 'xiazai002.com',
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0',
              'Accept': 'text/html,application/xhtml+xm…plication/xml;q=0.9,*/*;q=0.8',
              'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
              'Accept-Encoding': 'gzip, deflate',
              'Referer': '',
              'Connection': 'keep-alive',
              'Upgrade-Insecure-Requests': '1'}


class Resource:
    def __init__(self, name, type, source_num):
        self.name = name
        self.type = type
        self.source_num = source_num


class Tab:
    def __init__(self, name, source_li, tab_num_list):
        self.name = name
        self.source_li = source_li
        self.tab_num_list = tab_num_list

    def get_size(self):
        return len(self.source_li)

    def print_source_li(self):
        i = 1
        for li in self.source_li:
            print(str(i)+'. '+li)
            i += 1


def get_actual_links(soup, tab_num):
    frame = soup.find('div', attrs={'role': 'tabpanel', 'class': 'tab-pane', 'id': tab_num})
    whole_season = frame.find('ul', attrs={'class': 'down-list'})
    episodes = whole_season.children
    episode_list = []
    for e in episodes:
        if e.name == 'li':
            episode_list.append(e)
    # down_links = []
    for e in episode_list:
        source_name = e.find('div', class_='title').find('span', class_='filename').string
        source_size = e.find('div', class_='title').find('span', class_='filesize').string
        try:
            p = e.find('p', attrs={'class': 'desc'}, text='磁力')
            link = p.parent.get('href')
        except AttributeError:
            try:
                p = e.find('p', attrs={'class': 'desc'}, text='电驴')
                link = p.parent.get('href')
            except AttributeError:
                link = ""
        finally:
            if link != "":
                print("[*] <"+source_name+"> "+source_size+":")
                print(link)
                print()
                # down_links.append(link)


def get_download_links(url, t):
    r = requests.get(url, header)
    soup = BeautifulSoup(r.text, 'lxml')
    side_bar = soup.find('div', attrs={'class': 'sidebar-warpper', 'id': 'scrollspy'}).ul
    tabs = side_bar.children
    tab_list = []
    for tab in tabs:
        if tab.name == 'li':
            tmp_list = []
            tmp_list2 = []
            name = tab.find('a').string
            ul = tab.ul
            if ul:
                tabs2 = tab.ul.children
                for child in tabs2:
                    if child.name == 'li':
                        a = child.find('a')
                        items = a.children
                        for i in items:
                            if type(i) == bs4.element.NavigableString and i != "在线看":
                                tmp_list.append(i)
                                tmp_list2.append(a.get('aria-controls'))
            else:
                a = tab.find('a')
                items = a.children
                for i in items:
                    if type(i) == bs4.element.NavigableString and i != "在线看":
                        tmp_list.append(i)
                        tmp_list2.append(a.get('aria-controls'))
            tab_list.append(Tab(name, tmp_list, tmp_list2))
        else:
            continue

    if len(tab_list) != 0:
        if len(tab_list) == 1 and t == '电影':
            season_choose = tab_list[0]
        else:
            i = 1
            for tab in tab_list:
                print(str(i) + ". " + tab.name)
                i += 1
            season_choose = tab_list[int(input("选择: ")) - 1]
        season_choose.print_source_li()
        type_choose = int(input("选择: ")) - 1
        get_actual_links(soup, season_choose.tab_num_list[type_choose])
    else:
        print("没有资源")


def get_resource_link(t, source_number):
    RegEx = "<h3><a href=(.*?) class"
    if t == '电视剧':
        ty = 'tv'
    elif t == '电影':
        ty = 'movie'
    url = 'http://www.zimuzu.tv/resource/index_json/rid/'+str(source_number)+'/channel/'+ty
    header['Referer'] = 'http://www.zimuzu.tv/gresource/' + str(source_number)
    url_content = requests.get(url, header).text
    url_list = re.findall(RegEx, url_content)
    return url_list[0].replace("\"", "").replace("\\", "")


def search_resources(name):
    search_url = 'http://www.zimuzu.tv/search?'
    params = {'keyword': name, 'type': 'resource'}
    r = requests.get(search_url, params=params)
    soup = BeautifulSoup(r.text, 'lxml')
    source_list = soup.find('div', attrs={'class': 'box search-result-box'}).find_all('li')
    resource_list = []
    for source in source_list:
        name = source.find('strong', attrs={'class': 'list_title'}).string
        t = source.find('em').string
        source_number = source.find('a').get('href').split('/')[-1]
        resource = Resource(name, t, source_number)
        resource_list.append(resource)
    return resource_list


def search(name, auto=False):
    if not auto:
        resource_list = search_resources(name)
        if len(resource_list) != 0:
            i = 1
            for resource in resource_list:
                print(str(i)+". "
                      + resource.name+" "
                      + resource.type)
                i += 1
            num = input("输入资源号: ")
            resource_choose = resource_list[int(num)-1]
            resource_url = get_resource_link(resource_choose.type, resource_choose.source_num)
            get_download_links(resource_url, resource_choose.type)
        else:
            print("搜索不到该资源")
    else:
        print("不支持")


if __name__ == '__main__':
    search(input("输入要找的资源: "))
