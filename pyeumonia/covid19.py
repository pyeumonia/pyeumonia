import requests  # Import requests module, which is used to send HTTP requests
import json  # Import json module, which is used to parse JSON data
from bs4 import BeautifulSoup  # Import beautifulsoup4 module, which is used to parse HTML data
import platform  # Import platform module, which is used to get OS type
import locale  # Import locale module, which is used to get system language
import time  # Import time module, which is used to get current time.
import os  # Import os module, which is used to check pypi upgradable
from pypinyin import lazy_pinyin  # Import pypinyin module, get your place name in Chinese
from iso3166 import countries  # Import iso3166 module, get your place name in English


class CovidException(Exception):
    """While the wrong parameter is given, CovidException will be raised."""

    def __init__(self, *args):
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
        # generate language from system language, only support Chinese and English.
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

    def get_region(self):
        """
        # Get the region of the covid-19 data, in order to get the covid-19 data of the region.

        :return: Your region.
        """
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
            if self.language == 'zh_CN':
                print('获取地区失败，请检查网络连接。')
            else:
                print('Get region failed, please check your network connection.')
            return {
                'countryName': 'Failed',
                'provinceName': 'Failed',
                'cityName': 'Failed'
            }
        for country in self.w_data:
            if countries.get(response['country']).alpha3 == country['countryShortCode']:
                if self.language == 'zh_CN':
                    place['countryName'] = country['provinceName']
                    if place['countryName'] == '中国':
                        for province in self.c_data:
                            # Convert province name to Pinyin.
                            province_name = province['provinceShortName']
                            province_name_pinyin = ''.join(lazy_pinyin(province_name))
                            if province_name_pinyin == response['region'].lower():
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
        version = os.popen('pip show pyeumonia').read().split('\n')[1].split(' ')[1]
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
            os.system('pip install --upgrade pyeumonia')
            if self.language == 'zh_CN':
                raise CovidException('pypi包已更新完成，请重新运行此程序。')
            else:
                raise CovidException('pypi package has been updated, please restart this program.')

    def cn_covid_data(self):
        """
        # Get the covid-19 data from China.

        This function is only supported in Chinese.
        :return: The data in json format.
        """
        c_data = self.c_data
        data = []
        for province in c_data:
            del province['provinceName']
            del province['comment']
            del province['locationId']
            del province['statisticsData']
            del province['highDangerCount']
            del province['midDangerCount']
            del province['suspectedCount']
            del province['cities']
            del province['dangerAreas']
            del province['detectOrgCount']
            del province['vaccinationOrgCount']
            data.append(province)
        return data

    def province_covid_data(self, province_name='北京', show_timeline: int = 0, include_cities=False, auto=False):
        """
        # Get the covid-19 data from China, for every province.

        This function is only supported in Chinese.
        :param province_name: The province you want to get the data, default is '北京'.
        :param show_timeline: If you want to get covid-19 data before ** days, please set the parameter to ** days.
        :param include_cities: If you want to get the data of cities, please set the parameter to True.
        :param auto: If you want to get the data of province automatically, please set the parameter to True.
        :return: The data in json format.
        """
        if auto:
            place = self.get_region()
            if place['provinceName'] != 'Failed':
                province_name = place['provinceName']
        cities = []
        data = {}
        c_data = self.c_data
        for province in c_data:
            if province['provinceName'] == province_name or province['provinceShortName'] == province_name:
                del province['comment']
                del province['locationId']
                del province['provinceName']
                if not show_timeline:
                    del province['statisticsData']
                del province['highDangerCount']
                del province['midDangerCount']
                del province['suspectedCount']
                for city in province['cities']:
                    ignore_cities = ['待明确地区', '境外输入', '外地来沪', '境外来沪', '境外输入人员', '外地来津', '外地来京', '省十里丰监狱', '省级（湖北输入）']
                    if city['cityName'] not in ignore_cities:
                        cities.append({'cityName': city['cityName'], 'confirmedCount': city['confirmedCount'],
                                       'currentConfirmedCount': city['currentConfirmedCount'],
                                       'deadCount': city['deadCount'], 'curedCount': city['curedCount']})
                if not include_cities or show_timeline:
                    del province['cities']
                del province['dangerAreas']
                del province['detectOrgCount']
                del province['vaccinationOrgCount']
                data = province
                break
        if show_timeline:
            # print(data)
            t_data = []
            timeline_url = str(data['statisticsData'])
            raw_timeline_data = requests.get(timeline_url).json()
            if raw_timeline_data['code'] != 'success':
                raise CovidException(f'There is some error in the data, error code: {raw_timeline_data["code"]}.')
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
            del data['statisticsData']
            data['dateId'] = now
            t_data.append(data)
            timeline_data['data'] = t_data
            if include_cities:
                timeline_data['cities'] = cities
            return timeline_data
        else:
            if include_cities:
                data['cities'] = cities
            return data

    def city_covid_data(self, province_name='上海', city_name='杨浦区', auto=False, show_danger_areas=False):
        """
        # Get covid-19 data from a city

        This function is only supported for Chinese language. :param province_name: The province you want to get the
        data, default is '上海'. :param city_name: The city you want to get the data, default is '杨浦区'.
        :param auto: If you want to get the data of the city automatically, please set the parameter to True.
        :param show_danger_areas: If you want to get the danger areas count of the city,
        please set the parameter to True.
        :param province_name: The province you want to get the data, default is '上海'.
        :param city_name: The city you want to get the data, default is '杨浦区'.
        :return: The data in json format.
        """
        if auto:
            place = self.get_region()
            if place['countryName'] != 'Failed':
                province_name = place['provinceName']
                city_name = place['cityName']
        c_data = self.c_data
        for province in c_data:
            if province['provinceShortName'] == province_name:
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
                            if city['highDangerCount'] > 0:
                                city_data['highDangerCount'] = city['highDangerCount']
                            if city['midDangerCount'] > 0:
                                city_data['midDangerCount'] = city['midDangerCount']
                        return city

    def danger_areas_data(self, include_cities=True, include_counts=True, include_danger_areas=True):
        """
        # Get the danger areas data from China.

        This function is only supported in Chinese.
        :param include_cities: Include the danger areas count for every city default.
        :param include_counts: Include the danger areas count default.
        :param include_danger_areas: Include high danger and middle danger areas default.
        """
        if not include_cities and not include_counts and not include_danger_areas:
            raise CovidException('Parameter include_cities, include_counts, include_danger_areas cannot be all False.')
        data = []
        merged_data = {
            'midDangerAreas': [],
            'highDangerAreas': [],
        }
        c_data = self.c_data
        for province in c_data:
            '''If the province have no any danger areas, the province will not be included in the data.'''
            if province['highDangerCount'] > 0 or province['midDangerCount'] > 0:
                p_data = {
                    'provinceName': province['provinceShortName']
                }
                if include_danger_areas:
                    p_data['midDangerAreas'] = []
                    p_data['highDangerAreas'] = []
                if include_cities:
                    p_data['cities'] = []
                    for city in province['cities']:
                        """If the city have no any danger areas, the city will not be included in the data."""
                        if city['highDangerCount'] > 0 or city['midDangerCount'] > 0:
                            cn_data = {
                                'cityName': city['cityName'],
                                'highDanger': city['highDangerCount'],
                                'midDanger': city['midDangerCount']
                            }
                            # print(cn_data)
                            p_data['cities'].append(cn_data)
                if include_counts:
                    p_data['highDanger'] = province['highDangerCount']
                    p_data['midDanger'] = province['midDangerCount']
                if include_danger_areas:
                    for area in province['dangerAreas']:
                        # Remove the province name from the area name.
                        danger_lv = 'dangerAreas'
                        if area['dangerLevel'] == 1:
                            danger_lv = 'highDangerAreas'
                        elif area['dangerLevel'] == 2:
                            danger_lv = 'midDangerAreas'
                        area_name = area['areaName']
                        if province['provinceName'] in area_name:
                            area_name.strip(province['provinceName'])
                        if province['provinceShortName'] in area_name:
                            area_name.strip(province['provinceShortName'])
                        cityname = area['cityName']
                        if area['cityName'] == '大兴安岭':
                            cityname = '大兴安岭地区'
                        city_names = [
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
                        ]
                        if cityname not in city_names:
                            cityname = cityname + '市'
                        if area['cityName'] in area_name:
                            area_name = area_name.strip(area['cityName'])
                        area_name = cityname + area_name
                        p_data[danger_lv].append(area_name)
                        merged_data[danger_lv].append(province['provinceName'] + area_name)
                data.append(p_data)
        if not data:  # If there is no danger areas in China, return None.
            return None
        if not include_cities and not include_counts:
            data = merged_data
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

    def country_covid_data(self, country_name='United States of America', show_timeline: int = 0, auto=False):
        """
        # Get the covid-19 data from the world, for every country.

        This function is both supported in Chinese and English.
        :param country_name: The covid-19 data of this country will be returned, default is 'United States of America'.
        :param show_timeline: If you want to get the data for ** days, set this parameter to **.
        :param auto: If you want to get covid-19 data from your country, set this parameter to True.
        :return: The data in json format.
        """
        if auto:
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
            # get the date of 30 days ago
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

    def cn_news_data(self):
        """
        Get the news from CCTV
        :return: The latest news
        """
        n_data = self.n_data
        raw_news = n_data
        for news in raw_news:
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
        print(raw_news)


if __name__ == '__main__':
    covid = Covid19(language='zh_CN', check_upgradable=False)
    region = covid.city_covid_data(auto=True, show_danger_areas=True)
    print(region)
    # Check the internet connection while pyeumonia has been imported.
    try:
        requests.get('https://ncov.dxy.cn/ncovh5/view/pneumonia')
    except Exception:
        raise CovidException('Please check your internet connection.')
