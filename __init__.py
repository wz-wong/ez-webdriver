# coding:utf-8
from . import ez_webdriver


def chrome(version="auto", path=None, name="chromedriver", os_type=None, is_arm=False) -> str:
    """
    version: 三种参数 auto(匹配当前版本)  latest(最新版本)  x.x(指定版本,2级就够,太细的版本可能匹配不到)
    path: 可以是目录(指定放置驱动文件的目录),可以是文件(指定驱动文件的路径)
    name: 下载的驱动文件名称(下载的文件名,除非镜像源的文件改名了,否则不要改动)
    os_type: 默认自动检测,手动-> win32, win64, win-arm64, linux32, linux64, linux-arm64, mac, mac-arm
    """
    return ez_webdriver.chrome(version=version, path=path, name=name, os_type=os_type, is_arm=is_arm)


def firefox(version="auto", path=None, name="geckodriver", os_type=None, is_arm=False) -> str:
    """
    version: 三种参数 auto(匹配当前版本)  latest(最新版本)  x.x(指定版本,2级就够,太细的版本可能匹配不到)
    path: 可以是目录(指定放置驱动文件的目录),可以是文件(指定驱动文件的路径)
    name: 下载的驱动文件名称(下载的文件名,除非镜像源的文件改名了,否则不要改动)
    os_type: 默认自动检测,指定只能三选一['linux', 'win', 'mac']
    """
    return ez_webdriver.firefox(version=version, path=path, name=name, os_type=os_type, is_arm=is_arm)


def edge(version="auto", path=None, name="edgedriver", os_type=None, is_arm=False) -> str:
    """
    version: 三种参数 auto(匹配当前版本)  latest(最新版本)  x.x(指定版本,2级就够,太细的版本可能匹配不到)
    path: 可以是目录(指定放置驱动文件的目录),可以是文件(指定驱动文件的路径)
    name: 下载的驱动文件名称(下载的文件名,除非镜像源的文件改名了,否则不要改动)
    os_type: 默认自动检测,指定只能三选一['linux', 'win', 'mac']
    """
    return ez_webdriver.edge(version=version, path=path, name=name, os_type=os_type, is_arm=is_arm)


def ie(version="auto", path=None, name="IEDriverServer", os_type=None, is_arm=False) -> str:
    """
    version: 三种参数 auto(匹配当前版本)  latest(最新版本)  x.x(指定版本,2级就够,太细的版本可能匹配不到)
    path: 可以是目录(指定放置驱动文件的目录),可以是文件(指定驱动文件的路径)
    name: 下载的驱动文件名称(下载的文件名,除非镜像源的文件改名了,否则不要改动)
    os_type: 默认自动检测,指定只能三选一['linux', 'win', 'mac']
    """
    return ez_webdriver.ie(version=version, path=path, name=name, os_type=os_type, is_arm=is_arm)


def clear_cache(path=None) -> None:
    """
    path: 指定清除的目录(会删除目录下所有文件)
    清除驱动缓存,清空默认目录 _webdriver 下所有内容
    (适用驱动文件损坏情况,本模块仅保留一个冗余旧版本)
    """
    return ez_webdriver.clear_cache(path)
