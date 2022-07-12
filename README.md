# Pyeumonia

This program is in private beta, but it's open source, if there is some error(s) in your code, please submit an issue to [Github](https://github.com/senge-studio/pyeumonia/issues).

A covid-19 api to get the latest data from [DXY](https://ncov.dxy.cn/ncovh5/view/pneumonia).

Chinese user can see [README-zh_CN.md](https://github.com/senge-studio/pyeumonia/blob/master/README-zh_CN.md).

国内用户请访问[README-zh_CN.md](https://github.com/senge-studio/pyeumonia/blob/master/README-zh_CN.md).

## How to install

install pypi package:

```bash
pip install pyeumonia
```

## Configurations

If you have already installed pyeumonia, and it's newer than `0.1.0a0`, it will automatically check for updates, you can also configure it by following the steps below to let it automatically update.

```python
from pyeumonia.covid19 import Covid19

covid = Covid19(check_upgradable=True, auto_update=True)
```

If you don't want to check updates automatically, you can configure like this.

```python
from pyeumonia.covid19 import Covid19

covid = Covid19(check_upgradable=False)
```

If you want to upgrade it manually, you can use `pip install --upgrade pyeumonia`.

## Usage

### Get the latest data from the world:

```python
from pyeumonia.covid19 import Covid19

covid = Covid19(language='en_US')
data = covid.world_covid_data()
```

### Get timeline data from a country:

```python
from pyeumonia.covid19 import Covid19

covid = Covid19(language='en_US')
# Get covid-19 data from Japan in the last 30 days
data = covid.country_covid_data(country_name='Japan', show_timeline=30)
```

### Get timeline data from your country:
```python
from pyeumonia.covid19 import Covid19

covid = Covid19(language='en_US')
# Get covid-19 data from your country in the last 30 days
data = covid.country_covid_data(auto=True, show_timeline=30)
```

> **Warning**:
>- If you are using a proxy, you need to turn off the proxy in your device, or the result will be wrong.

## Open Source license

The project is open source and licensed under the [GNU GPL v3 license](https://www.gnu.org/licenses/gpl-3.0.txt). If you want to use it, please obey these license:

- You can use the project for your python projects.
- You can modify and redistribute the project, but you must use GPLv3 license and keep the author's name in your source code.
- For any purpose, this program is forbidden to use for commercial use, including but not limited to enterprise website, business application, business promotion.
