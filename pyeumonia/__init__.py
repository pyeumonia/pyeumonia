import requests  # Import requests module, which is used to send HTTP requests
import json  # Import json module, which is used to parse JSON data
from bs4 import BeautifulSoup  # Import beautifulsoup4 module, which is used to parse HTML data
import platform  # Import platform module, which is used to get OS type
import locale  # Import locale module, which is used to get system language
import time  # Import time module, which is used to get current time.
import os  # Import os module, which is used to check pypi upgradable
from pypinyin import lazy_pinyin  # Import pypinyin module, get your place name in Chinese
from iso3166 import countries  # Import iso3166 module, get your place name in English
import webbrowser  # Import webbrowser module, it will open a browser to show the result.
class CovidException(Exception):
    """While the wrong parameter is given, CovidException will be raised."""

    def __init__(self, *args): 
        """While the wrong parameter is given, CovidException will be raised."""
        self.args = args


class Covid19:
    """
    # Initialize the class
    
    :param language: The language of the data, default is 'auto', check your language automatically.
    :param check_upgradable: While running the program it will check upgradable version, default is True.
    :param auto_update: If you want to update the program automatically, set it to True.
    Chinese data is also supported, if you want to show Chinese, please initialize the class `covid = Covid('zh_CN')`.
    """

    def __init__(self, language='auto', check_upgradable=True, auto_update=False):
        """
        # generate language from system language, only support Chinese and English.
        
        This function will check your system language and it will check for the latest version of the program automatically.
        """
        if language == 'auto':
            language = locale.getdefaultlocale()[0]
        if language != 'zh_CN':
            language = 'en_US'
        self.language = language
        if check_upgradable:
            self.auto_update = auto_update
            self.check_upgrade()
        url = 'https://ncov.dxy.cn/ncovh5/view/pneumonia'  # Get data from this url
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/80.0.3987.149 Safari/537.36 "
        }
        if platform == 'Linux':
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/80.0.3987.149 Safari/537.36 "
            }
        if platform.system() == 'Darwin':
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/80.0.3987.149 Safari/537.36 "
            }
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        status_code = response.status_code
        if status_code != 200:
            raise CovidException(f'The website is not available, error code: {status_code}.')
        soup = BeautifulSoup(response.text, 'html.parser')  # Initialize beautifulsoup4
        # Get the covid-19 data from China.
        c_soup = soup.find('script', id='getAreaStat')
        self.c_data = json.loads(str(c_soup)
                                 .strip('<script id="getAreaStat">try { window.getAreaStat = ')
                                 .strip('}catch(e){}</script>')
                                 )
        # Get the covid-19 data from the world.
        w_soup = soup.find('script', id='getListByCountryTypeService2true')
        self.w_data = json.loads(str(w_soup)
                                 .strip(
            '<script id="getListByCountryTypeService2true">try { window.getListByCountryTypeService2true = ')
                                 .strip('}catch(e){}</script>')
                                 )
        # Get the news about covid-19 from China.
        n_soup = soup.find('script', id='getTimelineService1')
        self.n_data = json.loads(str(n_soup)
                                 .strip('<script id="getTimelineService1">try { window.getTimelineService1 = ')
                                 .strip('}catch(e){}</script>')
                                 )

    def get_language(self, language='auto'):
        if language == 'auto':
            language = locale.getdefaultlocale()[0]
        if language != 'zh_CN':
            language = 'en_US'
        return language

    def get_region(self, language='prog'):
        """
        # Get the region of the covid-19 data, in order to get the covid-19 data of the region.

        This function is both supported in Chinese and English.
        :param language: The language of the data, default is 'prog', use the program language,
        if you want to check language from system, please set it to 'auto',
        if you want to use English, please set it to 'en_US', if you want to use Chinese, please set it to 'zh_CN'.
        :return: Your region.
        """
        if language == 'auto':
            language = locale.getdefaultlocale()[0]
        elif language == 'prog':
            language = self.language
        elif language == 'zh_CN':
            pass
        else:
            language = 'en_US'
        url = 'https://ipinfo.io/json'
        place = {
            'countryName': '',
            'provinceName': '',
            'cityName': '',
        }
        try:
            response = requests.get(url=url, timeout=2).json()
            # print(response)
        except Exception:
            if language == 'zh_CN':
                print('获取地区失败，请检查网络连接。')
            else:
                print('Get region failed, please check your network connection.')
            return {
                'countryName': 'Failed',
                'provinceName': 'Failed',
                'cityName': 'Failed'
            }
        w_data = self.w_data
        c_data = self.c_data
        for country in w_data: # Get the country name from covid-19 data.
            if countries.get(response['country']).alpha3 == country['countryShortCode']:
                if language == 'zh_CN':
                    place['countryName'] = country['provinceName']
                    if place['countryName'] == '中国':  # If you are in China, you will get the province name and city name.
                        for province in c_data:
                            # Convert province name to Pinyin.
                            province_name = province['provinceShortName']
                            province_name_pinyin = ''.join(lazy_pinyin(province_name))
                            if province_name_pinyin == response['region'].lower():
                                # print(province)
                                place['provinceName'] = province_name
                                for city in province['cities']:
                                    city_name = city['cityName']
                                    city_name_pinyin = ''.join(lazy_pinyin(city_name))
                                    if city_name_pinyin == response['city'].lower():
                                        place['cityName'] = city_name
                                        break
                                break
                else:
                    place['countryName'] = country['countryFullName']
                    place['provinceName'] = response['region']
                    place['cityName'] = response['city']
                    break
        return place

    def check_upgrade(self):
        """Check if there is a new version of the program.
        :return: If there is a new version, return True, otherwise return False, if check failed, return 'Failed'.
        """
        # Get the version of the program.
        version = os.popen('pip show pyeumonia').read()
        try:
            version = version.split('\n')[1].split(' ')[1]
        except IndexError:
            if self.language == 'zh_CN':
                print('pyeumonia好像没有安装，请先安装后再次测试。')
            else:
                print('pyeumonia is not installed, please install it first.')
        # Get the latest version of the program.
        url = 'https://pypi.org/pypi/pyeumonia/json'
        try:
            response = requests.get(url=url, timeout=2).json()
        except Exception:
            if self.language == 'zh_CN':
                print('检查更新失败，请前往 https://pypi.org/project/pyeumonia 查看更新。')
            else:
                print('Check update failed, please visit https://pypi.org/project/pyeumonia to check update.')
            return
        latest_version = response['info']['version']
        if latest_version != version:
            if self.language == 'zh_CN':
                print('检测到新版本，请及时更新！')
                print(f'您当前的版本是{version}，最新版本是{latest_version}')
            else:
                print('New version is available, please update!')
                print(f'Your version is {version}, the latest version is {latest_version}')
        else:
            if self.language == 'zh_CN':
                print(f'您当前安装的版本{version}为最新版！')
            else:
                print(f'You are using the latest version {version}!')
            return
        if self.auto_update:
            is_update = os.system('pip install --upgrade pyeumonia')
            if self.language == 'zh_CN':
                if is_update == 0:
                    raise CovidException('pypi包已更新完成，请重新运行此程序。')
                else:
                    raise CovidException('pypi包更新失败，请检查网络连接。')
            else:
                if is_update == 0:
                    raise CovidException('pypi package has been updated, please restart this program.')
                else:
                    raise CovidException('pypi package update failed, please check your network connection.')

    def cn_covid_data(self):
        """
        # Get the covid-19 data from China.

        This function is only supported in Chinese.
        :return: The data in json format.
        """
        c_data = self.c_data
        data = []
        for province in c_data:
            province_data = {
                'provinceShortName': province['provinceShortName'],
                'currentConfirmedCount': province['currentConfirmedCount'],
                'confirmedCount': province['confirmedCount'],
                'curedCount': province['curedCount'],
                'deadCount': province['deadCount'],
            }
            data.append(province_data)
        return data

    def province_covid_data(self, province_name='北京', show_timeline: int = 0):
        """
        # Get the covid-19 data from China, for every province.

        This function is only supported in Chinese.
        :param province_name: The province you want to get the data, default is '北京', if you want to get the data of province automatically, please set the parameter to 'auto'.
        :param show_timeline: If you want to get covid-19 data before ** days, please set the parameter to ** days.
        :return: The data in json format.
        """
        if province_name == 'auto':
            place = self.get_region(language='zh_CN')
            if place['provinceName'] != 'Failed':
                province_name = place['provinceName']
        cities = []
        data = {}
        c_data = self.c_data
        timeline_url = ''
        for province in c_data:
            if province['provinceName'] == province_name or province['provinceShortName'] == province_name:
                province_data = {
                    'provinceShortName': province['provinceShortName'],
                    'currentConfirmedCount': province['currentConfirmedCount'],
                    'confirmedCount': province['confirmedCount'],
                    'curedCount': province['curedCount'],
                    'deadCount': province['deadCount']
                }
                # print(province)
                data = province_data
                timeline_url = province['statisticsData']
                break
        if show_timeline:
            # print(data)
            t_data = []
            raw_timeline_data = requests.get(timeline_url).json()
            if raw_timeline_data['code'] != 'success':
                raise CovidException(f'获取疫情信息失败，错误代码：{raw_timeline_data["code"]}.')
            now = int(time.strftime('%Y%m%d', time.localtime()))
            # get the date of 30 days ago
            date = int(time.strftime('%Y%m%d', time.localtime(time.time() - show_timeline * 24 * 60 * 60)))
            for timeline in raw_timeline_data['data']:
                if timeline['dateId'] < date:  # get the data of 30 days ago
                    continue
                del timeline['confirmedIncr']
                del timeline['curedIncr']
                del timeline['currentConfirmedIncr']
                del timeline['deadIncr']
                del timeline['highDangerCount']
                del timeline['midDangerCount']
                del timeline['suspectedCount']
                del timeline['suspectedCountIncr']
                t_data.append(timeline)
            timeline_data = {'provinceShortName': data['provinceShortName']}
            del data['provinceShortName']
            data['dateId'] = now
            t_data.append(data)
            timeline_data['data'] = t_data
            return timeline_data
        else:
            return data

    def city_covid_data(self, city_name='杨浦区', show_danger_areas=False):
        """
        # Get covid-19 data from a city

        This function is only supported for Chinese language.
        :param show_danger_areas: If you want to get the danger areas count of the city,
        please set the parameter to True.
        :param city_name: The city you want to get the data, default is '杨浦区', if you want to get the data of the city automatically, please set the parameter to 'auto'.
        :return: The data in json format.
        """
        if city_name == 'auto':
            place = self.get_region(language='zh_CN')
            if place['countryName'] != 'Failed':
                city_name = place['cityName']
        c_data = self.c_data
        for province in c_data:
            for city in province['cities']:
                if city['cityName'] == city_name:
                    city_data = {
                        'cityName': city['cityName'],
                        'currentConfirmedCount': city['currentConfirmedCount'],
                        'confirmedCount': city['confirmedCount'],
                        'curedCount': city['curedCount'],
                        'deadCount': city['deadCount'],
                    }
                    if show_danger_areas:
                        city_data['highDangerCount'] = city['highDangerCount']
                        city_data['midDangerCount'] = city['midDangerCount']
                    return city

    def danger_areas_data(self, city_name=None):
        """
        # Get danger areas data from China.
        
        This function is only supported in Chinese.
        :param city_name: The city you want to get danger areas, default is None, if you want to get danger areas in your city, please set it to 'auto'.
        :return: Return all danger areas if both province_name and city_name are None, else return danger areas from your province and your city.
        """
        if city_name == 'auto':
            city_name = self.get_region(language='zh_CN')['cityName']
        raw_data = self.c_data
        data = []
        for province in raw_data:
            if province['highDangerCount'] == 0 and province['midDangerCount'] == 0:
                continue
            province_data = {
                'provinceName': province['provinceName'],
                'highDangerCount': province['highDangerCount'],
                'midDangerCount': province['midDangerCount'],
                'cities': []
            }
            for city in province['cities']:
                if city['highDangerCount'] == 0 and city['midDangerCount'] == 0:
                    continue
                cityname = city['cityName']
                if cityname == '大兴安岭':
                    cityname = '大兴安岭地区'
                if cityname not in [
                    "锡林郭勒盟",
                    "阿拉善盟",
                    "兴安盟",
                    "甘孜州",
                    "凉山州",
                    "阿坝州",
                    "德宏州",
                    "红河州",
                    "大理州",
                    "文山州",
                    "楚雄州",
                    "赣江新区",
                    "恩施州",
                    "神农架林区",
                    "雄安新区",
                    "喀什地区",
                    "伊犁州",
                    "兵团第四师",
                    "昌吉州",
                    "兵团第九师",
                    "巴州（巴音郭楞蒙古自治州）",
                    "兵团第十二师",
                    "兵团第七师",
                    "阿克苏地区",
                    "黔南州",
                    "黔东南州",
                    "黔西南州",
                    "海北州",
                    "浦东新区",
                    "徐汇区",
                    "黄浦区",
                    "虹口区",
                    "闵行区",
                    "静安区",
                    "杨浦区",
                    "宝山区",
                    "长宁区",
                    "普陀区",
                    "松江区",
                    "嘉定区",
                    "奉贤区",
                    "青浦区",
                    "崇明区",
                    "金山区",
                    "河北区",
                    "北辰区",
                    "和平区",
                    "南开区",
                    "河西区",
                    "西青区",
                    "滨海新区",
                    "东丽区",
                    "津南区",
                    "红桥区",
                    "河东区",
                    "武清区",
                    "宝坻区",
                    "静海区",
                    "宁河区",
                    "朝阳区",
                    "丰台区",
                    "房山区",
                    "海淀区",
                    "通州区",
                    "东城区",
                    "昌平区",
                    "顺义区",
                    "西城区",
                    "大兴区",
                    "石景山区",
                    "经济开发区",
                    "门头沟区",
                    "延庆区",
                    "密云区",
                    "怀柔区",
                    "万州区",
                    "高新区",
                    "江北区",
                    "云阳县",
                    "九龙坡区",
                    "长寿区",
                    "合川区",
                    "綦江区",
                    "奉节县",
                    "开州区",
                    "忠县",
                    "渝北区",
                    "渝中区",
                    "垫江县",
                    "潼南区",
                    "两江新区",
                    "南岸区",
                    "石柱县",
                    "大足区",
                    "巫溪县",
                    "巴南区",
                    "巫山县",
                    "铜梁区",
                    "丰都县",
                    "沙坪坝区",
                    "璧山区",
                    "荣昌区",
                    "永川区",
                    "彭水县",
                    "大渡口区",
                    "江津区",
                    "涪陵区",
                    "梁平区",
                    "黔江区",
                    "城口县",
                    "武隆区",
                    "秀山县",
                    "酉阳县",
                    "万盛经开区"
                ]:
                    cityname = cityname + '市'
                city_data = {
                    'cityName': cityname,
                    'highDangerCount': city['highDangerCount'],
                    'midDangerCount': city['midDangerCount'],
                    'highDangerAreas': [],
                    'midDangerAreas': []
                }
                city_data['cityName'] = cityname
                for area in province['dangerAreas']:
                    if area['cityName'] != city['cityName']:
                        continue
                    if area['dangerLevel'] == 1:    # High danger area
                        city_data['highDangerAreas'].append(area['areaName'])
                    elif area['dangerLevel'] == 2:  # Mid danger area
                        city_data['midDangerAreas'].append(area['areaName'])
                if len(city_data['highDangerAreas']) == 0:
                    del city_data['highDangerAreas']
                    del city_data['highDangerCount']
                if len(city_data['midDangerAreas']) == 0:
                    del city_data['midDangerAreas']
                    del city_data['midDangerCount']
                if city_name == city['cityName']:
                    return city_data
                province_data['cities'].append(city_data)
            data.append(province_data)
        return data

    def world_covid_data(self):
        """
        # Get the covid-19 data from the world.

        Both Chinese and English are supported in this function.
        :return: The data in json format.
        """
        data = []
        w_data = self.w_data
        for country in w_data:
            country_data = {
                'currentConfirmedCount': country['currentConfirmedCount'],
                'confirmedCount': country['confirmedCount'],
                'curedCount': country['curedCount'],
                'deadCount': country['deadCount']
            }
            if self.language == 'zh_CN':
                country_data['countryName'] = country['provinceName']
                country_data['continents'] = country['continents']
            else:
                continents_trans = {  # If user language is not Chinese, the continents will be translated to English.
                    '亚洲': 'Asia',
                    '欧洲': 'Europe',
                    '非洲': 'Africa',
                    '北美洲': 'North America',
                    '南美洲': 'South America',
                    '大洋洲': 'Oceania',
                    '南极洲': 'Antarctica',
                    '其他': 'Other'
                }
                country_data['continents'] = continents_trans[country['continents']]
                country_data['countryName'] = country['countryFullName']
            data.append(country_data)
        return data

    def country_covid_data(self, country_name='United States of America', show_timeline: int = 0):
        """
        # Get the covid-19 data from the world, for every country.

        This function is both supported in Chinese and English.
        :param country_name: The covid-19 data of this country will be returned, default is 'United States of America', if you want to get covid-19 data from your country, set this parameter to "auto".
        :param show_timeline: If you want to get the data for ** days, set this parameter to **.
        :return: The data in json format.
        """
        if country_name == 'auto':
            place = self.get_region()
            if place['countryName'] != 'Failed':
                country_name = place['countryName']
        url = ''
        country_raw_data = {}
        w_data = self.w_data
        for country in w_data:
            if show_timeline:
                url = str(country['statisticsData'])
            if self.language == 'zh_CN':
                if country['provinceName'] == country_name:
                    country_raw_data = {
                        'currentConfirmedCount': country['currentConfirmedCount'],
                        'confirmedCount': country['confirmedCount'],
                        'curedCount': country['curedCount'],
                        'deadCount': country['deadCount'],
                        'countryName': country['provinceName'],
                    }
                    break
            else:
                if country['countryFullName'] == country_name:
                    country_raw_data = {
                        'currentConfirmedCount': country['currentConfirmedCount'],
                        'confirmedCount': country['confirmedCount'],
                        'curedCount': country['curedCount'],
                        'deadCount': country['deadCount'],
                        'countryName': country['countryFullName'],
                    }
                    break
        if show_timeline:
            t_data = []
            raw_timeline_data = requests.get(url).json()
            country_name = country_raw_data['countryName']
            if raw_timeline_data['code'] != 'success':
                raise CovidException(f'There is some error in the data, error code: {raw_timeline_data["code"]}.')
            country_data = {'countryName': country_name}
            now = int(time.strftime('%Y%m%d', time.localtime()))
            # get the date of several days ago
            date = int(time.strftime('%Y%m%d', time.localtime(time.time() - show_timeline * 24 * 60 * 60)))
            for timeline in raw_timeline_data['data']:
                if timeline['dateId'] < date:
                    continue
                t_temp_data = {
                    'dateId': timeline['dateId'],
                    'confirmedCount': timeline['confirmedCount'],
                    'curedCount': timeline['curedCount'],
                    'deadCount': timeline['deadCount'],
                    'currentConfirmedCount': timeline['currentConfirmedCount'],
                }
                t_data.append(t_temp_data)
            del country_raw_data['countryName']
            country_raw_data['dateId'] = now
            t_data.append(country_raw_data)
            country_data['data'] = t_data
            return country_data
        else:
            return country_raw_data

    def cn_news_data(self, province=None, show_summary=True, open_url=False):
        """
        Get the news from CCTV
        :param province: The province you want to get the news, if you want to get the news from your province, set this parameter to True.
        :param show_summary: If you do not want to get the summary of the news, set this parameter to False.
        :param open_url: If you want to open the news url(only work for province or local news), set this parameter to True.
        :return: The latest news
        """
        local_news = {}
        if province == 'auto':
            province = self.get_region()['provinceName']
        n_data = self.n_data
        for news in n_data:
            del news['id']
            pub_timestamp = news['pubDate'] / 1000
            pub_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(pub_timestamp))
            news['pubTime'] = pub_time
            del news['pubDateStr']
            del news['pubDate']
            del news['provinceId']
            del news['articleId']
            del news['category']
            del news['jumpUrl']
            if not show_summary:
                del news['summary']
            if province is None:
                continue
            if province in news['title']:
                local_news = news
                if open_url:
                    webbrowser.open(news['sourceUrl'])
                return local_news
        
        return n_data

    def open_website(self, website='Official'):
        """# It will open a website in your computer.
        
        :param website: Which website you want to open, default is official website.
        Usage:
        ```python
        from pyeumonia import Covid19
        covid = Covid19(language='auto')
        # Official website:
        covid.open_website(website='Official')
        # Send email:
        covid.open_website(website='email')
        # DXY Official website
        covid.open_website(website='DXY')
        # GitHub
        covid.open_website(website='GitHub')
        # PyPi
        covid.open_website(website='PyPi')
        ```
        """
        language = self.language
        if website.lower() == 'official':
            if self.language == 'zh_CN':
                website = 'https://pyeumonia.icu/zh_CN/'
            else:
                website = 'https://pyeumonia.icu'
        elif website.lower() == 'email':
            website = 'mailto:pyeumonia@protonmail.com'
        elif website.lower() == 'dxy':
            if self.language == 'zh_CN':
                website = 'https://ncov.dxy.cn/ncovh5/view/pneumonia'
            else:
                website = 'https://ncov.dxy.cn/ncovh5/view/en_pneumonia?from=dxy&source=&link=&share='
        elif website.lower() == 'github':
            website = 'https://github.com/pyeumonia/pyeumonia'
        elif website.lower() == 'pypi':
            website = 'https://pypi.org/project/pyeumonia/'
        else:
            raise CovidException(f'The website {website} is not supported.')
        webbrowser.open(website)


if __name__ == '__main__':
    """While importing this module, your internet connection is required."""
    try:
        requests.get('https://ncov.dxy.cn/ncovh5/view/pneumonia')
    except Exception:
        raise CovidException('Please check your internet connection.')
