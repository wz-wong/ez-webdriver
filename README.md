



# ez-webdriver
一个下载管理浏览器驱动的python库, 优先使用国内镜像源, 单文件少依赖,调用简单,复制即用,可作为 webdriver_manager 库的国内替代
- 获取驱动时,优先用国内镜像源,下载更快
- 下载的驱动永久保存,每次执行时判断旧版本数量,只保留一个旧版本驱动的冗余
- 代码精简,单文件,只需复制 ez_webdriver.py 文件到自己项目即可使用
- 修改方便,如果有新增镜像源,仅需写一个处理镜像源链接的函数即可
- 手动指定arm平台(没找到判断arm的办法)


## 支持的浏览器/For now support:

[谷歌浏览器/ChromeDriver](#chrome) [火狐浏览器/GeckoDriver](#use-with-firefox) [Edge浏览器/EdgeChromiumDriver](#use-with-edge) [IE浏览器/IEDriver](#use-with-ie)

## 演示



## 用法/Usage:
<div>
    <table border="0">
	  <tr>
	    <th>谷歌浏览器</th>
	    <th>火狐浏览器</th>
      <th>Edge浏览器</th>
      <th>IE浏览器</th>
	  </tr>
	  <tr>
	    <td>ez_webdriver.chrome()</td>
	    <td>ez_webdriver.firefox()</td>
      <td>ez_webdriver.edge()</td>
      <td>ez_webdriver.ie()</td>
	  </tr>
    </table>
</div>


以上4个方法, 均会返回一个驱动的 `Path` 对象,或者 `False` (自动下载对应驱动版本)

总之,仅需将上面4个之一赋值给 `webdriver` 的位置参数即可正常使用

```python
# selenium 4 (省略部分import,见示例)
import ez_webdriver
driver = webdriver.Chrome(service=Service(ez_webdriver.chrome()))

# selenium 3 (省略部分import,见示例)
import ez_webdriver
driver = webdriver.Chrome(ez_webdriver.chrome())

# 其它浏览器同理,仅需更改 ez_webdriver 后的 chrome() 改成对应浏览器即可
```

## 示例
### Chrome
```python
# selenium 4
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import ez_webdriver # 导入驱动管理模块

# 将 ez_webdriver.chrome() 传递给 server 参数即可
driver = webdriver.Chrome(service=Service(ez_webdriver.chrome()))
```

```python 
# selenium 3
from selenium import webdriver
import ez_webdriver # 导入驱动管理模块

# selenium 3 -->直接填入即可
driver = webdriver.Chrome(ez_webdriver.chrome())
```

### Firfox
```python
# selenium 4
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import ez_webdriver # 导入驱动管理模块

# 将 ez_webdriver.firefox() 传递给 server 参数即可
driver = webdriver.Chrome(service=Service(ez_webdriver.firefox()))
```

```python 
# selenium 3
from selenium import webdriver
import ez_webdriver # 导入驱动管理模块

# selenium 3 -->直接填入即可
driver = webdriver.Chrome(ez_webdriver.firefox())
```

### Edge
```python
# selenium 4
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import ez_webdriver # 导入驱动管理模块

# 将 ez_webdriver.edge() 传递给 server 参数即可
driver = webdriver.Chrome(service=Service(ez_webdriver.edge()))
```

```python 
# selenium 3
from selenium import webdriver
import ez_webdriver # 导入驱动管理模块

# selenium 3 -->直接填入即可
driver = webdriver.Chrome(ez_webdriver.edge())
```

### IE
```python
# selenium 4
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import ez_webdriver # 导入驱动管理模块

# 将 ez_webdriver.ie() 传递给 server 参数即可
driver = webdriver.Chrome(service=Service(ez_webdriver.ie()))
```

```python 
# selenium 3
from selenium import webdriver
import ez_webdriver # 导入驱动管理模块

# selenium 3 -->直接填入即可
driver = webdriver.Chrome(ez_webdriver.ie())
```

## 全部函数及实现
- chrome()    `返回Path对象或Fase,自动获取浏览器驱动`
- firfox()    `返回Path对象或Fase,自动获取浏览器驱动`
- edge()    `返回Path对象或Fase,自动获取浏览器驱动`
- ie()    `返回Path对象或Fase,自动获取浏览器驱动`
- clear_cache()    `适用于浏览器驱动文件损坏的情况,将清除下载的驱动文件,估计不会被用上`

### 函数参数
`chrome()` `firfox()` `edge()` `ie()`  均有如下参数
	
	version: 三种参数 auto(匹配当前版本,默认)  latest(最新版本)  x.x.x(指定版本)
	path: 可目录(指定放置驱动文件的目录),可文件(指定驱动文件的路径,用文件就是多此一举)
	name: 下载的驱动文件名称(下载的文件名,除非镜像源的文件改名了,否则不要改动)
	os_type: 默认自动检测,指定只能三选一 'linux'|'win'|'mac'

> 默认值: `chrome(version="auto", path=None, name="chromedriver", os_type=None) `


## 致谢
此模块参考了 [webdriver_manager](https://github.com/SergeyPirogov/webdriver_manager) 的设计思路,

添加了国内镜像,每个浏览器均有至少两个下载镜像可用
弃用了缓存过期时间(cache_valid_range)的设定,改为了每次执行时判断是否有旧版本驱动,只保留一个冗余旧版本
弃用类,改用函数的形式,导入模块时不用那么复杂
获取浏览器版本时,优先用注册表,powershell备用(用的它的代码),占用少,响应更快








