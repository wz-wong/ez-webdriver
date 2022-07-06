import json
import os
import platform
import re
import subprocess
import sys
import zipfile
from pathlib import Path

from lxml import etree

import requests
from fake_useragent import UserAgent
requests.packages.urllib3.disable_warnings()

# 判断文件
if getattr(sys, 'frozen', False):  # 判断是exe还是.py程序
    dir_pre = Path(os.path.realpath(sys.executable)).parent  # exe程序路径
elif __file__:
    dir_pre = Path(__file__).parent  # .py程序路径



def __get_cmd_result(cmd)-> str:
    r = subprocess.run(cmd, capture_output=True, stdin=subprocess.PIPE, text=True, shell=True, )
    if r.returncode:
        # print(f'命令执行错误,{r.stderr.strip()} \n-->{r.args}') # 不用输出
        return ''
    return r.stdout.strip()
def __session()-> requests.session():
    '''
    session 关ssl验证, 加headers
    :return:
    '''
    headers = {'User-Agent': UserAgent().random}
    s = requests.session()
    s.verify = False
    s.headers = headers
    s.trust_env = False  # 禁用代理
    return s

# ----------------------获取浏览器版本部分
def __pre(browser_type, name, version, os_type) ->tuple:
    """获取[平台,位数,文件名], 获取版本号"""
    # 判断 平台, name 拆成 list, 用于判断 最终文件名是否包含 name 所有元素
    lst_name = []
    # 平台
    if os_type and os_type.lower() in ['linux', 'win', 'mac']:
        lst_name.append(os_type.lower())
    else:
        pl = sys.platform
        if pl == "linux" or pl == "linux2":
            lst_name.append('linux')
        elif pl == "darwin":
            lst_name.append('mac')
        elif pl == "win32":
            lst_name.append('win')
        else:
            print(f'警告,未知平台{pl},将使用win平台(Warning, unknown platform {pl}, will use Win)')
    pl = lst_name[0]
    # 位数
    if platform.machine().endswith("64"):
        lst_name.append('64')
    else:
        lst_name.append('32')
    lst_name.append(name)
    # 判断当前浏览器的版本(默认 auto), latest最新的, x.x.x 指定具体版本
    if version == 'auto':
        version = __get_browser_version_from_os(browser_type, pl)

    if version:
        print(f'-->当前浏览器版本 {browser_type} : {version}')

    return lst_name, version
def __get_browser_version_from_os(browser_type, pl) -> str:
    """
    两种方式获取版本号,优先注册表,然后powershell
    :param browser_type:
    :return: 版本号 str
    """



    # win 注册表用(优先)
    cmd_mapping_win_reg = {
        'chrome': [(r'HKLM\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Google Chrome', 'version'),
                   ],
        'chromium': [(r'HKCU\SOFTWARE\Chromium\BLBeacon', 'version'),
                     (r'HKLM\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Chromium', 'version'),
                     ],
        'edge': [
            # stable edge
            (r'HKCU\SOFTWARE\Microsoft\Edge\BLBeacon', 'version'),
            # beta edge
            (r'HKCU\SOFTWARE\Microsoft\Edge Beta\BLBeacon', 'version'),
            # dev edge
            (r'HKCU\SOFTWARE\Microsoft\Edge Dev\BLBeacon', 'version'),
            # canary edge
            (r'HKCU\SOFTWARE\Microsoft\Edge SxS\BLBeacon', 'version'),
            # highest edge
            (r'HKLM\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Microsoft Edge', 'version'),
        ],
        "firefox": [(r'HKLM\SOFTWARE\Mozilla\Mozilla Firefox', 'CurrentVersion'),
                    ],
        "ie": [(r'HKLM\SOFTWARE\Microsoft\Internet Explorer', 'svcVersion'),
               (r'HKLM\SOFTWARE\Microsoft\Internet Explorer', 'Version'),
                    ],
    }[browser_type]

    PATTERN = {
        'chrome': r"\d+\.\d+\.\d+",
        "firefox": r"(\d+.\d+)",
        'edge': r"\d+\.\d+\.\d+",
        "ie": r"(\d+.\d+.\d+)",
        'chromium': r"\d+\.\d+\.\d+",   # 未启用,理论和chrom一样
        "brave-browser": r"(\d+)",      # 未启用,理论和chrom一样
    }
    if not PATTERN.get(browser_type):
        print(f'请先选择浏览器类型: {"|".join(PATTERN.keys())}')
        return False
    pattern = PATTERN[browser_type]
    # 优先 用cmd 获取浏览器版本号(更快,若浏览器安装后未启动过,就无注册表记录),备用powershell方式
    version = None
    if pl == 'win':
        version = __get_brower_version_from_os_by_reg(cmd_mapping_win_reg, pattern)
    if not version and browser_type!='ie':
        # linux,mac,win 通用
        cmd_mapping = {
            'chrome': {
                'linux': (
                    "google-chrome",
                    "google-chrome-stable",
                    "google-chrome-beta",
                    "google-chrome-dev",
                ),
                'mac': r"/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version",
                'win': (
                    r'(Get-Item -Path "$env:PROGRAMFILES\Google\Chrome\Application\chrome.exe").VersionInfo.FileVersion',
                    r'(Get-Item -Path "$env:PROGRAMFILES (x86)\Google\Chrome\Application\chrome.exe").VersionInfo.FileVersion',
                    r'(Get-Item -Path "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe").VersionInfo.FileVersion',
                    r'(Get-ItemProperty -Path Registry::"HKCU\SOFTWARE\Google\Chrome\BLBeacon").version',
                    r'(Get-ItemProperty -Path Registry::"HKLM\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Google Chrome").version',
                ),
            },
            'chromium': {
                'linux': ("chromium", "chromium-browser"),
                'mac': r"/Applications/Chromium.app/Contents/MacOS/Chromium --version",
                'win': (
                    r'(Get-Item -Path "$env:PROGRAMFILES\Chromium\Application\chrome.exe").VersionInfo.FileVersion',
                    r'(Get-Item -Path "$env:PROGRAMFILES (x86)\Chromium\Application\chrome.exe").VersionInfo.FileVersion',
                    r'(Get-Item -Path "$env:LOCALAPPDATA\Chromium\Application\chrome.exe").VersionInfo.FileVersion',
                    r'(Get-ItemProperty -Path Registry::"HKCU\SOFTWARE\Chromium\BLBeacon").version',
                    r'(Get-ItemProperty -Path Registry::"HKLM\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Chromium").version',
                ),
            },
            'brave-browser': {
                'linux': (
                    "brave-browser", "brave-browser-beta", "brave-browser-nightly"
                ),
                'mac': r"/Applications/Brave\ Browser.app/Contents/MacOS/Brave\ Browser --version",
                'win': (
                    r'(Get-Item -Path "$env:PROGRAMFILES\BraveSoftware\Brave-Browser\Application\brave.exe").VersionInfo.FileVersion',
                    r'(Get-Item -Path "$env:PROGRAMFILES (x86)\BraveSoftware\Brave-Browser\Application\brave.exe").VersionInfo.FileVersion',
                    r'(Get-Item -Path "$env:LOCALAPPDATA\BraveSoftware\Brave-Browser\Application\brave.exe").VersionInfo.FileVersion',
                    r'(Get-ItemProperty -Path Registry::"HKCU\SOFTWARE\BraveSoftware\Brave-Browser\BLBeacon").version',
                    r'(Get-ItemProperty -Path Registry::"HKLM\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\BraveSoftware Brave-Browser").version',
                ),
            },
            'edge': {
                'linux': (
                    "microsoft-edge",
                    "microsoft-edge-stable",
                    "microsoft-edge-beta",
                    "microsoft-edge-dev",
                ),
                'mac': r"/Applications/Microsoft\ Edge.app/Contents/MacOS/Microsoft\ Edge --version",
                'win': (
                    # stable edge
                    r'(Get-Item -Path "$env:PROGRAMFILES\Microsoft\Edge\Application\msedge.exe").VersionInfo.FileVersion',
                    r'(Get-Item -Path "$env:PROGRAMFILES (x86)\Microsoft\Edge\Application\msedge.exe").VersionInfo.FileVersion',
                    r'(Get-ItemProperty -Path Registry::"HKCU\SOFTWARE\Microsoft\Edge\BLBeacon").version',
                    r'(Get-ItemProperty -Path Registry::"HKLM\SOFTWARE\Microsoft\EdgeUpdate\Clients\{56EB18F8-8008-4CBD-B6D2-8C97FE7E9062}").pv',
                    # beta edge
                    r'(Get-Item -Path "$env:LOCALAPPDATA\Microsoft\Edge Beta\Application\msedge.exe").VersionInfo.FileVersion',
                    r'(Get-Item -Path "$env:PROGRAMFILES\Microsoft\Edge Beta\Application\msedge.exe").VersionInfo.FileVersion',
                    r'(Get-Item -Path "$env:PROGRAMFILES (x86)\Microsoft\Edge Beta\Application\msedge.exe").VersionInfo.FileVersion',
                    r'(Get-ItemProperty -Path Registry::"HKCU\SOFTWARE\Microsoft\Edge Beta\BLBeacon").version',
                    # dev edge
                    r'(Get-Item -Path "$env:LOCALAPPDATA\Microsoft\Edge Dev\Application\msedge.exe").VersionInfo.FileVersion',
                    r'(Get-Item -Path "$env:PROGRAMFILES\Microsoft\Edge Dev\Application\msedge.exe").VersionInfo.FileVersion',
                    r'(Get-Item -Path "$env:PROGRAMFILES (x86)\Microsoft\Edge Dev\Application\msedge.exe").VersionInfo.FileVersion',
                    r'(Get-ItemProperty -Path Registry::"HKCU\SOFTWARE\Microsoft\Edge Dev\BLBeacon").version',
                    # canary edge
                    r'(Get-Item -Path "$env:LOCALAPPDATA\Microsoft\Edge SxS\Application\msedge.exe").VersionInfo.FileVersion',
                    r'(Get-ItemProperty -Path Registry::"HKCU\SOFTWARE\Microsoft\Edge SxS\BLBeacon").version',
                    # highest edge
                    r"(Get-Item (Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe').'(Default)').VersionInfo.ProductVersion",
                    r"[System.Diagnostics.FileVersionInfo]::GetVersionInfo((Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe').'(Default)').ProductVersion",
                    r"Get-AppxPackage -Name *MicrosoftEdge.* | Foreach Version",
                    r'(Get-ItemProperty -Path Registry::"HKLM\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Microsoft Edge").version',
                ),
            },
            "firefox": {
                'linux': ("firefox",),
                'mac': r"/Applications/Firefox.app/Contents/MacOS/firefox --version",
                'win': (
                    r'(Get-Item -Path "$env:PROGRAMFILES\Mozilla Firefox\firefox.exe").VersionInfo.FileVersion',
                    r'(Get-Item -Path "$env:PROGRAMFILES (x86)\Mozilla Firefox\firefox.exe").VersionInfo.FileVersion',
                    r"(Get-Item (Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe').'(Default)').VersionInfo.ProductVersion",
                    r'(Get-ItemProperty -Path Registry::"HKLM\SOFTWARE\Mozilla\Mozilla Firefox").CurrentVersion',
                ),
            },
        }[browser_type][pl]

        version = __get_browser_version_from_os_by_powershell(cmd_mapping, pattern, pl)
    if not version:
        print(
            f'!! 未获取到浏览器版本号,请指定 DriverManage.{browser_type}(version="latest") 或者 DriverManage.{browser_type}(version="x.x")')
    return version
def __get_browser_version_from_os_by_powershell(cmd_mapping, pattern, pl)-> str:
    """备用方案,修改自 webdriver-manager  3.7.0"""
    pl = pl
    if pl == 'win':
        cmd = "(dir 2>&1 *`|echo CMD);&<# rem #>echo powershell"
        stdout = __get_cmd_result(cmd)
        powershell = "" if stdout == "powershell" else "powershell"

        first_hit_template = """$tmp = {expression}; if ($tmp) {{echo $tmp; Exit;}};"""
        script = "$ErrorActionPreference='silentlycontinue'; " + " ".join(
            first_hit_template.format(expression=e) for e in cmd_mapping
        )
        dt = f'{powershell} -NoProfile "{script}"'
    elif pl == 'linux':
        ignore_errors_cmd_part = " 2>/dev/null" if os.getenv(
            "WDM_LOG_LEVEL") == "0" else ""
        dt = " || ".join(f"{i} --version{ignore_errors_cmd_part}" for i in cmd_mapping)
    elif pl == 'mac':
        dt = cmd_mapping
    else:
        print(f'xx 未知系统类型 - {pl}')
        return False

    # 执行命令
    stdout = __get_cmd_result(dt)
    if stdout:  # 获取版本值
        version = re.search(pattern, stdout)
        version = version.group(0) if version else None
        return version
    return False
def __get_brower_version_from_os_by_reg(cmd_mapping_win_reg, pattern) -> str:
    for reg in cmd_mapping_win_reg:
        cmd = r'reg query "' + reg[0] + r'" /v ' + reg[1]
        stdout = __get_cmd_result(cmd)
        if stdout:  # 获取版本值
            version = re.search(pattern, stdout)
            version = version.group(0) if version else None
            return version
    return None

# ----------------------选择版本部分
def __func_select(driver_type, lst_name, version) -> str:
    '''
    1.循环镜像源,找能用的
    2.选择对应获取链接的函数, 获取下载链接
    :return: 返回下载链接
    '''
    driver_url = {
        'chrome': [('npmmirror_json', r'https://registry.npmmirror.com/-/binary/chromedriver'),
                   ('googleapis_xml', r'https://chromedriver.storage.googleapis.com'),

                   ],
        'firefox': [('npmmirror_json', r'https://registry.npmmirror.com/-/binary/geckodriver'),
                    ('githubapi_json', r'https://api.github.com/repos/mozilla/geckodriver/releases'),

                    ],
        'operadriver': [('npmmirror_json', r'https://registry.npmmirror.com/-/binary/operadriver'),

                        ],
        'edge': [('microsoft_html', r'https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver'),

                 ],
        'ie': [('npmmirror_json', r'https://registry.npmmirror.com/-/binary/selenium'),
                ('githubapi_json', r'https://api.github.com/repos/SeleniumHQ/selenium/releases'),
               ],
    }
    # 循环多个镜像源,一个源返回空就继续下一个
    sites = driver_url[driver_type]
    file_url = None
    for site in sites:  # 判断 镜像源类型,执行对应函数
        if site[0] == 'npmmirror_json':
            file_url = __by_npmmirror_json(site[1], lst_name, version)
        elif site[0] == 'googleapis_xml':
            file_url = __by_googleapis_xml(site[1], lst_name, version)
        elif site[0] == 'githubapi_json':
            file_url = __by_githubapi_json(site[1], lst_name, version)
        elif site[0] == 'microsoft_html':
            file_url = __by_microsoft_html(site[1], lst_name, version)
        else:
            print(f'xx 错误,未知镜像源类型{site[0]}')
        if file_url:
            print('已获取下载链接: ', file_url)
            break
        print(f'源: {site[0]} 获取失败')
    if not file_url:
        print(f'xx 错误,未获取到下载链接,请检查版本号是否正确{sites}')
    return file_url
def __version_select(d_version, version) -> list:
    '''
    传来版本字典,返回选择的 版本目录url(列表,最多20个,避免最新版本无对应驱动问题)
    :param dict,version: 版本字典,传进来的版本号
    :return: str
    '''
    dict_ver = {}  # 新的 版本号字典, 用0 补齐 10位
    if not d_version:
        print(f'未找到有效版本')
        return None
    else:  # 版本号处理,填满10位
        for k, v in d_version.items():
            k = '.'.join([x.zfill(10) for x in k.split('.')])
            dict_ver[k] = v

    version_new = '.'.join([x.zfill(10) for x in version.split('.')])
    vers = sorted(dict_ver.keys(), reverse=True)  # 字典先由大到小
    for v in vers:  # 返回指定的版本
        if len(v) >= len(version_new) and v[:len(version_new)] == version_new:
            return [dict_ver[v], ]
    # 找最新版
    if version != 'latest':
        print(f'未找到对应版本,请选择以下版本(默认最新):\n{"|".join(d_version.keys())}')
        return None

    # 找最新版
    lst_ver = [dict_ver[x] for x in vers[:20]]
    return lst_ver  # 若最新版本无文件,往前找20个版本
def __file_select(s, dir_url, lst_name) -> str:
    f_url_default = ''
    # 根据文件名(仅需平台标识), 获取要下载的文件链接
    lst_file = json.loads(s.get(dir_url).text)
    for file in lst_file:
        f_name = file['name']
        f_url = file['url']
        if f_name == lst_name[2] or f_name == '.'.join(f_name.split('.')[:-1]):  # 用户自定义文件名的情况
            return f_url
        if lst_name[2] == 'IEDriverServer':  # ie只有win,64位名称不带win
            if lst_name[1] in f_name:
                return f_url

        if lst_name[0] in f_name and lst_name[2] in f_name:
            if lst_name[1] in f_name:
                return f_url
            f_url_default = f_url

    return f_url_default


# ----------------------保存驱动文件部分(返回Path路径)
def __check_file(path,lst_name,browser_type, version) ->Path:
    """"检查目录下是否有对应浏览器版本的驱动文件"""

    dir = Path(path) if path else Path(dir_pre/'_webdriver')
    dir.mkdir(parents=True, exist_ok=True)

    _ = version+'-'+'-'.join(lst_name[:2])
    dir_file = dir/browser_type/_
    if dir_file.is_dir():
        for f in dir_file.glob('*.*'):
            if f.stem==lst_name[2]:
                return f
    dir_file.mkdir(parents=True)  # 创建对应目录
    return dir_file
def __save_file(path_driver,file_url)->Path:
    """下载保存文件"""
    try:
        s = __session()
        f_name = file_url.split('/')[-1]
        file_path = path_driver/f_name

        # 断点续传
        print('下载中(约10秒)/Downloading (about 10 seconds)...')
        temp_size = file_path.stat().st_size if file_path.exists() else 0
        s.headers.update({'Range': 'bytes=%d-' % temp_size,})
        res_left = s.get(file_url, stream=True)
        # 写入
        with open(file_path, "ab") as f:
            for chunk in res_left.iter_content(chunk_size=1024):
                temp_size += len(chunk)
                f.write(chunk)
                f.flush()
        # 解压
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(path_driver)
        # 删除zip文件
        os.remove(file_path)
    except Exception as err:
        print('xx 下载驱动文件失败(download failed)',err)
        return False
    print('下载完成(finished)')
    return file_path


# ----------------------处理镜像的url,获取下载地址
def __by_npmmirror_json(url, lst_name, version) -> str:
    '''
    处理 npmmirror url
    默认获取 用户电脑上匹配版本
    获取不到就获取最新的 (chrome 获取第二新的)
    :return: 文件下载链接
    '''
    # 获取所有版本  (网页返回的是json)
    s = __session()
    lst_data = json.loads(s.get(url).text)
    d_version = {}
    for dt in lst_data:
        if '/' not in dt['name']:  # 剔除非目录的
            continue
        # 处理掉名称开头和结尾的 非数字部分
        ver_name = re.search('^\D*(.*?)\D*$', dt['name'])
        ver_name = ver_name[1] if ver_name[1] else dt['name']
        ver_url = dt['url']
        d_version[ver_name] = ver_url

    lst_ver = __version_select(d_version, version)
    if not lst_ver:
        return None
    for dir_url in lst_ver:  # 循环 20个版本,新->旧 ,找能用的
        # 根据文件名(仅需平台标识),判断要下载的文件
        file_url = __file_select(s, dir_url, lst_name)
        if file_url:
            return file_url
    return None
def __by_googleapis_xml(url, lst_name, version) -> str:
    '''
    处理 googleapis url(返回的是 xml 数据)
    获取版本号后,直接拼接下载链接
    [linux64,mac64,mac64_m1,win32]
    默认获取 用户电脑上匹配版本
    获取不到就获取最新的 (LATEST_RELEASE 文件下的内容)
    :return: 文件下载链接
    '''
    # 获取所有版本  (网页返回的是xml)
    s = __session()
    d_version = {}
    # xml = etree.fromstring(s.get(url).content)
    # for c in xml.xpath('//Key'):
    keys = re.findall('<Key>(.*?)</Key>', s.get(url).text)
    for k in keys:
        l = k.split('/')
        if len(l) != 2 or 'notes.txt' in k:
            continue
        f_ver, f_name = l[0], l[1]
        if lst_name[0] in f_name and lst_name[2] in f_name:
            if not d_version.get(f_ver):
                d_version[f_ver] = []
            d_version[f_ver].append('/'.join([url, f_ver, f_name]))
    # 选择版本
    lst_ver = __version_select(d_version, version)
    if not lst_ver:
        return None
    for dir_url in lst_ver:  # 循环 20个版本,新->旧 ,找能用的
        file_url = dir_url[0]
        if file_url:
            return file_url
    return False
def __by_githubapi_json(url, lst_name, version) -> str:
    '''
    处理 githubapi url (返回的是json字符串)
    默认获取 最新版本
    可指定 version
    :return: 文件下载链接
    '''
    # 获取所有版本  (网页返回的是json)
    f_url_default = None
    s = __session()
    lst_data = json.loads(s.get(url, timeout=5, allow_redirects=False, verify=False).text)
    if not isinstance(lst_data, list):
        return None
    d_version = {}
    for dt in lst_data:
        if not dt['tag_name']:
            continue
        ver_name = dt['tag_name'][1:] if dt['tag_name'][0] == 'v' else dt['tag_name']

        d_version[ver_name] = {}
        for i in dt['assets']:
            d_version[ver_name][i['name']] = i['browser_download_url']

    lst_ver = __version_select(d_version, version)
    if not lst_ver:
        return None
    for dict_file in lst_ver:  # 循环 20个版本,新->旧 ,找能用的
        # 根据文件名,判断要下载的文件
        for f_name, f_url in dict_file.items():
            if f_name == lst_name[2]:  # 用户自定义文件名的情况
                return f_url
            if lst_name[2] == 'IEDriverServer':  # ie只有win,64位名称不带win
                if lst_name[1] in f_name:
                    return f_url
            if lst_name[0] in f_name and lst_name[2] in f_name:
                if lst_name[1] in f_name:
                    return f_url
                f_url_default = f_url
    return f_url_default
def __by_microsoft_html(url, lst_name, version) -> str:
    '''
    处理 microsoft url (返回的是html)
    默认获取 稳定版
    可指定 version
    :return: 文件下载链接
    '''
    # 获取所有版本  (返回的是html)
    f_url_default = None
    s = __session()
    html = etree.HTML(s.get(url).text)
    modules = html.xpath('//div[@class="module"]')
    set_ver = set()
    if modules:
        if version == 'latest':  # 默认返回稳定版
            for link in modules[0].xpath('.//p[@class="driver-download__meta"]//a/@href'):
                f_name = link.split('/')[-1]
                if f_name == lst_name[2]:  # 用户自定义文件名的情况
                    return link
                if lst_name[0] in f_name and lst_name[2] in f_name:
                    if lst_name[1] in f_name:
                        return link
                    f_url_default = link
        else:
            for module in modules:
                for link in module.xpath('.//p[@class="driver-download__meta"]//a/@href'):
                    f_version = link.split('/')[-2]
                    set_ver.add(f_version)
                    f_name = link.split('/')[-1]

                    if version == f_version:
                        if f_name == lst_name[2]:  # 用户自定义文件名的情况
                            return link
                        if lst_name[0] in f_name and lst_name[2] in f_name:
                            if lst_name[1] in f_name:
                                return link
            print(f'未找到对应版本,请选择以下版本(默认稳定版):\n{"|".join(sorted(list(set_ver)))}')
    return f_url_default




# ----------------------外部可调用部分
def chrome(version="auto", path=None, name="chromedriver", os_type=None) -> Path:
    """
    version: 三种参数 auto(匹配当前版本)  latest(最新版本)  x.x(指定版本,2级就够,太细的版本可能匹配不到)
    path: 可以是目录(指定放置驱动文件的目录),可以是文件(指定驱动文件的路径)
    name: 下载的驱动文件名称(下载的文件名,除非镜像源的文件改名了,否则不要改动)
    os_type: 默认自动检测,指定只能三选一['linux', 'win', 'mac']
    """
    # 判断版本
    browser_type = 'chrome'
    lst_name, version = __pre(browser_type, name, version, os_type)
    if not version:
        return False
    # 检查缓存的是否有对应版本driver
    path_driver = __check_file(path,lst_name,browser_type, version)
    if path_driver.is_file():   # 如果检测文件已存在,返回路径
        return path_driver

    # 获取下载链接
    file_url = __func_select(browser_type, lst_name, version)
    if not file_url:
        return None
    # 根据下载连接,下载解压文件
    result = __save_file(path_driver,file_url)
    return result
def firefox(version="auto", os_type=None, path=None, name="geckodriver")-> Path:
    """
    version: 三种参数 auto(匹配当前版本)  latest(最新版本)  x.x(指定版本,2级就够,太细的版本可能匹配不到)
    path: 可以是目录(指定放置驱动文件的目录),可以是文件(指定驱动文件的路径)
    name: 下载的驱动文件名称(下载的文件名,除非镜像源的文件改名了,否则不要改动)
    os_type: 默认自动检测,指定只能三选一['linux', 'win', 'mac']
    """
    # 判断版本
    browser_type = 'firefox'
    lst_name, brower_version = __pre(browser_type, name, version, os_type)
    if not brower_version:
        return False
    elif brower_version=='latest':
        pass
    else:       # 版本映射对应的驱动版本
        lst_version_map = [
            (53,'0.18.0'),
            (55,'0.20.1'),
            (57,'0.22.0'),
            (65,'0.25.0'),
            (79,'0.29.0'),
            (89,'0.30.0'),
        ]
        # 循环,最大版本开始
        for v in sorted(lst_version_map,key=lambda x:x[0],reverse=True):
            _ver = 'latest'
            if brower_version.split('.') and int(brower_version.split('.')[0])>v[0]:
                version = _ver
                break
            else:
                version = v[1]
    # 检查缓存的是否有对应版本driver
    path_driver = __check_file(path,lst_name,browser_type, brower_version)
    if path_driver.is_file():   # 如果检测文件已存在,返回路径
        return path_driver

    # 获取下载链接
    file_url = __func_select(browser_type, lst_name, version)
    if not file_url:
        return None
    # 根据下载连接,下载解压文件
    result = __save_file(path_driver,file_url)
    return result
def edge(version="auto", os_type=None, path=None, name="edgedriver")-> Path:
    """
    version: 三种参数 auto(匹配当前版本)  latest(最新版本)  x.x(指定版本,2级就够,太细的版本可能匹配不到)
    path: 可以是目录(指定放置驱动文件的目录),可以是文件(指定驱动文件的路径)
    name: 下载的驱动文件名称(下载的文件名,除非镜像源的文件改名了,否则不要改动)
    os_type: 默认自动检测,指定只能三选一['linux', 'win', 'mac']
    """
    # 判断版本
    browser_type = 'edge'
    lst_name, browser_version = __pre(browser_type, name, version, os_type)
    version = browser_version
    if not version:
        return False
    # 检查缓存的是否有对应版本driver
    path_driver = __check_file(path,lst_name,browser_type, browser_version)
    if path_driver.is_file():   # 如果检测文件已存在,返回路径
        return path_driver

    # 获取下载链接
    file_url = __func_select(browser_type, lst_name, version)
    if not file_url:
        return None
    # 根据下载连接,下载解压文件
    result = __save_file(path_driver,file_url)
    return result
def ie(version="auto", os_type=None, path=None, name="IEDriverServer")-> Path:
    """
    version: 三种参数 auto(匹配当前版本)  latest(最新版本)  x.x(指定版本,2级就够,太细的版本可能匹配不到)
    path: 可以是目录(指定放置驱动文件的目录),可以是文件(指定驱动文件的路径)
    name: 下载的驱动文件名称(下载的文件名,除非镜像源的文件改名了,否则不要改动)
    os_type: 默认自动检测,指定只能三选一['linux', 'win', 'mac']
    """
    # 判断版本
    browser_type = 'ie'
    lst_name, brower_version = __pre(browser_type, name, version, os_type)

    if not brower_version:
        return False
    else:       # IE8-IE10  用3.8.0, 其他用最新
        try:
            v = int(brower_version.split('.')[0])
            version = 'latest' if v>10 else '3.8'
        except:
            version = 'latest'
    # 检查缓存的是否有对应版本driver
    path_driver = __check_file(path,lst_name,browser_type, brower_version)
    if path_driver.is_file():   # 如果检测文件已存在,返回路径
        return path_driver

    # 获取下载链接
    file_url = __func_select(browser_type, lst_name, version)
    if not file_url:
        return None
    # 根据下载连接,下载解压文件
    result = __save_file(path_driver,file_url)
    return result
def clear_cache(path=None) ->None:
    """
    path: 指定清除的目录(会删除目录下所有文件)
    清除驱动缓存,清空默认目录 _webdriver 下所有内容
    (适用驱动文件损坏或时间太久累积了较多无用驱动)
    """
    if path:
        if not Path(path).is_dir():
            print('路径错误,path 应该是一个目录(The argument should be a directory)')
            return
        else:
            dir_default = Path(path)
    else:
        dir_default = dir_pre/'_webdriver'
    err_file = []
    # 先删文件, 部分因为嵌套删不了的,放到err_file
    for file in sorted(dir_default.rglob('*'),reverse=True):
        try:        # 跳过被占用而不能删除的
            if file.is_file():
                file.unlink()
            else:
                file.rmdir()
        except:
            err_file.append(file.__str__())

    print('缓存清理完毕(cache clearing completed)')
    if err_file:
        print('以下文件/目录被占用,需手动删除(directory is occuped,please removed manually)\n','\n'.join(err_file))



