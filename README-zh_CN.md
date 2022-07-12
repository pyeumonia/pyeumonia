# Pyeumonia

本程序仍处于内测阶段，但是它是开源的，如果你在你的代码中有任何错误，请在我的[GitHub](https://github.com/senge-studio/pyeumonia/issues)提交一个issue。

新冠肺炎疫情API，可以从[丁香园官网](https://ncov.dxy.cn/ncovh5/view/pneumonia)获取最新数据。

## 安装pypi

安装pypi包:

```bash
pip install pyeumonia
```

## 自动配置

如果你已经安装了pyeumonia，并且它的版本比`0.1.0a0`新，它将自动检查更新，你也可以按照以下步骤配置参数来实现自动更新。

```python
from pyeumonia.covid19 import Covid19
covid = Covid19(check_upgradable=True, auto_update=True)
```

如果你不想自动检查更新，可以这样配置:

```python
from pyeumonia.covid19 import Covid19
covid = Covid19(check_upgradable=False)
```

如果你想手动升级它，可以使用`pip install --upgrade pyeumonia`。

## 如何使用

### 从全球获得最新数据

```python
from pyeumonia.covid19 import Covid19
covid = Covid19(language='zh_CN')
data = covid.world_covid_data()
```

### 获取某个国家的疫情信息。

```python
from pyeumonia.covid19 import Covid19
covid = Covid19(language='zh_CN')
# 获取日本近30天的疫情信息
data = covid.country_covid_data(country_name='Japan', show_timeline=30)
```

### 如果你的所在地不在中国，你可以用这个方法获取你所在国家的疫情信息。
```python
from pyeumonia.covid19 import Covid19
covid = Covid19(language='zh_CN')
# 获取你所在国家近30天的疫情信息
data = covid.country_covid_data(auto=True, show_timeline=30)
```

### 获取国内的疫情信息

```python
from pyeumonia.covid19 import Covid19
covid = Covid19(language='zh_CN')
# 获取国内的疫情信息
data = covid.cn_covid_data()
```

### 获取国内某个省/自治区/直辖市/特别行政区的疫情信息

```python
from pyeumonia.covid19 import Covid19
covid = Covid19(language='zh_CN')
# 获取浙江省近30天的疫情信息，并获取当前各个城市的疫情信息
data = covid.province_covid_data(province_name='浙江', show_timeline=30, include_cities=True)
```

### 根据你的位置获取疫情信息
```python
from pyeumonia.covid19 import Covid19
covid = Covid19(language='zh_CN')
# 获取当前位置的疫情信息(精确到省份)
data = covid.province_covid_data(auto=True)
# 获取当前位置的疫情信息并显示风险地区的数量（如果没有风险地区，则不显示）
city_data = covid.city_covid_data(auto=True, show_danger_areas=True)
```

> **注意**:
>- 如果你使用了代理服务器，那么你获取的位置信息会有错误，请在关闭代理服务器的情况下调用该方法。

### 获取国内的中高风险地区

```python
from pyeumonia.covid19 import Covid19
covid = Covid19(language='zh_CN')
# 获取国内的中高风险地区(不显示国内的风险地区数量)
data = covid.danger_areas_data(include_cities=False, include_counts=False, include_danger_areas=True)
```

### 获取国内近期和疫情有关的新闻信息
```python
from pyeumonia.covid19 import Covid19
covid = Covid19(language='zh_CN')
news = covid.cn_news_data()
```

## 开放源代码许可

本程序使用[GNU GPL v3](https://jxself.org/translations/gpl-3.zh.shtml)开源，请遵守以下条款：

- 你可以免费给自己的python程序使用本程序的源代码。
- 你可以对本程序进行修改和分发，但必须保留上述的许可说明和原作者信息
- 无论出于任何目的，本程序禁止用于商业用途，包括但不限于企业网站、商业应用、商业推广等。
