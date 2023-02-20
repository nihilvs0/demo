#coding=utf-8

#1.下载对应版本webdriver，解压exe放到python.exe文件夹或者项目脚本所在文件夹
# 地址：https://registry.npmmirror.com/binary.html?path=chromedriver/
#2.安装库
'''
pip install selenium
pip install selenium-wire
pip install undetected_chromedriver
pip install pyautogui
pip install Pillow
pip install pyperclip
pip install pyopenssl==21.0.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install cryptography==35.0.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
'''

# undetected_chromedriver是专门针对浏览器识别做出来的拓展
# undetected_chromedriver 可以防止浏览器特征被识别，并且可以根据浏览器版本自动下载驱动。
# 下载位置：C:\Users\ye198\AppData\Roaming\undetected_chromedriver\b2c83bca23698da7_chromedriver.exe
# from seleniumwire import undetected_chromedriver as webdriver


# 使用seleniumwire可以获取所有请求的url、method、headers、response等信息
# from seleniumwire import webdriver
import re

from selenium import webdriver
# import pyautogui
import time
# import pyperclip
# import PIL
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait


import socks
from telethon.sync import TelegramClient
# from telethon.tl.functions.messages import GetHistoryRequest
import logging

# 第三方图片验证
from yescaptchaAPI import myYesCaptcha
# 腾讯云语音识别
from tencentAsrAPI import myTencentAsr
# wit.ai语音识别
from witaiAPI import myWitAudioToText



# logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.DEBUG)





#driver下载地址：https://registry.npmmirror.com/binary.html?path=chromedriver/

# 停顿功能
# pyautogui.PAUSE = 1 # 调用在执行动作后暂停的秒数，只能在执行一些pyautogui动作后才能使用，建议用time.sleep
# 自动 防故障功能
# pyautogui.FAILSAFE = True # 启用自动防故障功能，左上角的坐标为（0，0），将鼠标移到屏幕的左上角，来抛出failSafeException异常
# 参考：https://www.jianshu.com/p/b4345e676c34

# seleniumwire和undetected_chromedriver，证书不安全警告问题！
# 解决办法，新开一个CMD窗口，输入命令：
# python -m seleniumwire extractcert
# 就会在同级文件夹生成一个ca.crt证书文件，然后在Chrome浏览器 > 设置里面搜索证书，管理证书，在【受信任的根证书颁发机构】那一栏，导入ca.crt这个证书！这样就没有证书不安全的警告了！！

# seleniumwire和undetected_chromedriver
# 项目停止之后，就不能打开网页了，会提示设置了代理，其实是断开了selenium的代理，导致了没有网络！！
# 解决办法：在项目最后一行，加入：
# value = input("SCRIPT ENDED\n")
# 或者
# time.sleep(1000)
# 或者
# os.system('pause')
# 参考：
# https://stackoverflow.com/questions/62949605/selenium-wire-blocking-connection-due-to-proxy-config
# https://github.com/wkeeling/selenium-wire/issues/136#issuecomment-661707595

# 打开开发者工具，然后在控制台输入下面代码：
# document.onmousemove=function(e){
# console.log(e.pageX, e.pageY)
# }
# 开发者页面以新窗口显示，执行，然后移动鼠标即可。获取(x, y)坐标，方便pyautogui点击！！

# 在cmd命令行批量关闭chromedriver.exe浏览器驱动的方法：
# taskkill /F /im chromedriver.exe



def headerStr_to_table(headerStr):
	myHeaders = {}
	s = headerStr.split('\n')
	s = list(filter(lambda x: x and x.strip(), s))
	for v in s:
		d = v.split(': ')
		# print(d)
		if len(d) < 2:
			continue
		myHeaders[d[0]] = d[1]
	# print(myHeaders)
	return myHeaders


def useXpathScript(xpathScript):
	# 使用devtools里面的$x函数
	xx = '''
	function $x(STR_XPATH, DOCUMENT=document) {
		var xresult = DOCUMENT.evaluate(STR_XPATH, DOCUMENT, null, XPathResult.ANY_TYPE, null);
		var xnodes = [];
		var xres;
		while (xres = xresult.iterateNext()) {
			xnodes.push(xres);
		}
		return xnodes;
	}
	'''
	return '%s\n%s' % (xx, xpathScript)


def tupleAdd(tuple_a, tuple_b):
	return tuple(map(sum, zip(tuple_a, tuple_b)))



class haxRenewClass:
	def __init__(self, website_code=1, username='', password='', cookie='', proxy=None, telegram_session_name='session_name',  api_id=123, api_hash='', yescaptcha_clientKey='', tencent_SecretId='', tencent_SecretKey='', wit_access_token = '', chrome_user_data_dir='', argTable={}):
		for k, v in argTable.items():
			self.__setattr__(k, v)
		self.cookie = cookie
		self.username = username
		self.password = password
		# 是否登录成功
		self.loginSuccess = False
		# 已尝试登录的次数
		self.loginTimes = 0
		# 登录失败重试次数
		self.loginFailedRetryTimes = 0
		# 续期 Verification Code
		self.VerificationCode=''
		# windows使用telethon库，需要开启proxy
		self.proxy = proxy
		# telegram application配置信息
		self.api_id = int(api_id)
		self.api_hash = api_hash
		# telegram_session_name，每次使用telegram client会生成一个{session_name}.session，首次登录要输入手机号和两步验证密码
		# 如果有多个hax账号，需要使用多个telegram账号，那么每个账号对应的session_name要各不相同，以免文件覆盖
		self.telegram_session_name = telegram_session_name or 'session_name'
		# yescaptcha 帐户密钥 ClientKey
		self.yescaptcha_clientKey = yescaptcha_clientKey
		# 腾讯云api配置信息
		self.tencent_SecretId = tencent_SecretId
		self.tencent_SecretKey = tencent_SecretKey
		# wit.ai语音识别
		self.wit_access_token = wit_access_token
		# Renew失败重试次数
		self.renewRetryTimes = 0
		# 已经尝试Renew的次数
		self.renewTimes = 0
		# 是否已经Renew成功
		self.renewSuccess = False
		# hax或者woiden平台地址设置
		self.website_code = int(website_code) # hax为1，woiden为2
		# 更新平台各页面地址
		self.update_urls()
		# Chrome浏览器数据存放位置
		# chrome_user_data_dir = r"D:\yuchenye\Downloads\seleniumtest"
		self.chrome_user_data_dir = chrome_user_data_dir





		# 浏览器设置
		options = webdriver.ChromeOptions()
		# 切换到开发者模式
		options.add_experimental_option('excludeSwitches', ['enable-automation'])
		# 加下面这一句防止出现滑块验证（chrome的版本大于等于88）
		options.add_argument('--disable-blink-features=AutomationControlled')
		# 如果使用undetected_chromedriver，就不需要上面2个的设置

		# chrome的版本号小于88，在你启动浏览器的时候（此时没有加载任何网页内容），向页面嵌入js代码，去掉webdriver
		# driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": """Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"""})
		# 连接操作已有的浏览器
		# chrome.exe --remote-debugging-port=9527 --user-data-dir="F:\Django-project\taobao_login\AutomationProfile
		# options.add_experimental_option("debuggerAddress", "127.0.0.1:9527")
		# options.add_argument('--disable-gpu')
		# options.add_argument("--disable-software-rasterizer")
		# 忽略不信任证书
		# options.add_argument("--ignore-certificate-errors")
		# options.set_capability('acceptInsecureCerts', True)
		# 指定浏览器分辨率
		# options.add_argument("--window-size=1920,1080")

		# options.add_argument('--disable-infobars') # 禁止策略化
		options.add_argument('--no-sandbox') # 解决DevToolsActivePort文件不存在的报错，非沙盒模式运行
		# options.add_argument('window-size=1920x3000') # 指定浏览器分辨率
		options.add_argument('--disable-gpu') # 谷歌文档提到需要加上这个属性来规避bug
		# options.add_argument('--incognito') # 隐身模式（无痕模式）
		# options.add_argument('--disable-javascript') # 禁用javascript
		# options.add_argument('--start-maximized') # 最大化运行（全屏窗口）,不设置，取元素会报错
		options.add_argument('--disable-infobars') # 禁用浏览器正在被自动化程序控制的提示
		# options.add_argument('--hide-scrollbars') # 隐藏滚动条, 应对一些特殊页面
		# options.add_argument('blink-settings=imagesEnabled=false') # 不加载图片, 提升速度
		# options.add_argument('--headless') # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败

		# options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe" # 手动指定使用的浏览器位置

		# options.add_argument('--single-process') # 单进程运行
		# options.add_argument('--start-maximized') # 启动Google Chrome就最大化
		# 指定用户的配置地址，并加载至配置对象中。直接复制不好使，每台电脑都不一样，参照路径自己写
		# options.add_argument("--user-data-dir="+r"C:\Users\yuchenye\AppData\Local\Google\Chrome\User Data\Default")
		# options.add_argument("--user-data-dir="+r"C:\Users\yuchenye\AppData\Local\Google\Chrome\User Data")
		# 不能使用默认的User Data路径，好像是权限问题，没有管理员权限？
		# options.add_argument("--remote-debugging-port=9527")  # 9222，不要这句，不然好像获取不到header
		# 要先开启9527，不然：chrome not reachable
		# CMD执行命令：C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9527 --user-data-dir=“D:\yuchenye\Downloads\seleniumtest”
		# chrome.exe --remote-debugging-port=9527 --user-data-dir=“D:\yuchenye\Downloads\seleniumtest”

		# options.add_argument("--user-data-dir=" + r"D:\yuchenye\Downloads\seleniumtest")  # 浏览器数据位置，固定user-data-dir可以使用同1个浏览器，注释掉就使用临时浏览器，每次打开都是全新的浏览器
		# options.add_argument("--user-data-dir=" + r"D:\myExeApplications\seleniumtest")

		if self.chrome_user_data_dir:
			print('Chrome浏览器数据位置：', self.chrome_user_data_dir)
			options.add_argument("--user-data-dir=" + self.chrome_user_data_dir)  # 浏览器数据位置，固定user-data-dir可以使用同1个浏览器，注释掉就使用临时浏览器，每次打开都是全新的浏览器



		self.browser = webdriver.Chrome(options=options, keep_alive=True, service_args=["--ignore-ssl-errors=true", "--ssl-protocol=any"])
		# self.browser = webdriver.Chrome(options=options, keep_alive=True)
		# # 窗口最大化保证坐标正确
		self.browser.maximize_window() # 这个可能失败报错
		# 获取session_id
		session_id = self.browser.session_id
		# command_executor_url = self.browser.command_executor._url
		print('session_id=', session_id, self.browser.command_executor._url)

		# 连接已有的driver
		# executor = "http://localhost:52915"
		# session_id = "b8a2107d453d393d9d7f27fc4908a387"
		# driver = webdriver.Remote(command_executor=executor , desired_capabilities={}, keep_alive=True)
		# driver.session_id = session_id
		# self.browser = driver
		# print('webdriver.Remote已成功连接：', executor, session_id)
		# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
		# desired_capabilities=DesiredCapabilities.CHROME
		# 原文链接：https://blog.csdn.net/fured/article/details/104483877/

		# 可以设置request和response注入函数，详见：https://pypi.org/project/selenium-wire
		# self.browser.request_interceptor = self.request_interceptor
		# self.browser.response_interceptor = self.response_interceptor

		# 启动登录
		# self.login()

		# self.browser.get(self.url)


	def update_urls(self):
		self.url = 'https://hax.co.id' if self.website_code == 1 else 'https://woiden.id'
		self.website_hostname = self.url.split('//')[1]
		self.url_login = self.url + '/login'
		self.url_logout = self.url + '/logout'
		self.url_vps_info = self.url + '/vps-info'
		self.url_vps_renew = self.url + '/vps-renew'
		self.url_vps_renew_code = self.url + '/vps-renew-code'


	def request_interceptor(self, request):
		pass
		# del request.headers['Referer']  # Remember to delete the header first
		# request.headers['Referer'] = 'some_referer'  # Spoof the referer

	def response_interceptor(self, request, response):  # A response interceptor takes two args
		pass
		print(request.date, request.method, response.status_code, request.url)
		if request.url.find('sycm.taobao.com/mc/v2/mq/mkt/rank/shop/hotsale.json?dateRange') > -1:
			print('捕获到数据：生意参谋 - 市场排行 - 店铺排行 - 高交易')
		# if request.url == 'https://server.com/some/path':
		#     response.headers['New-Header'] = 'Some Value'
		# from seleniumwire.utils import decode
		# # 解析body
		# body = decode(response.body, response.headers.get('Content-Encoding', 'identity'))


	def cookieStr_to_table(self, cookieStr):
		print(cookieStr)
		cookies = {}
		for v in cookieStr.split(';'):
			name, value = v.strip().split('=', 1)
			cookies[name] = value
		# print(cookies)
		return cookies

	def setCookies(self, cookieStr, url=''):
		self.browser.get(url or self.url)
		cookies = self.cookieStr_to_table(cookieStr)
		print(cookies)
		for k, v in cookies.items():
			self.browser.add_cookie(cookie_dict={'name': k, 'value': v})
		self.browser.get(url)

	def login(self, logout=True):
		# 多个账号用同1个浏览器，需要退出之前的账号，logout=True，表示如果在登录状态，会先退出登录，如果只有1个号，可以设置logout=False，减少登录验证
		print('------login------')
		browser = self.browser
		browser.get(self.url_login)
		time.sleep(5)
		if browser.current_url.find('login') < 0:
			# 有可能已在登录状态，会自动跳转到https://hax.co.id/dashboard
			if logout:
				self.loginSuccess = False
				# 先退出账号，再进行登录（别的账号）
				browser.get(self.url_logout)
				time.sleep(5)
				browser.get(self.url_login)
			else:
				self.loginSuccess = True
				return True

		browser.execute_script(f'document.querySelector("#text").value="{self.username}"')
		browser.execute_script(f'document.querySelector("#password").value="{self.password}"')


		# reCaptcha 图片或音频验证
		self.reCaptcha_V2(browser)

		# 随机点击验证图片 测试代码
		# self.reCaptcha_random_click_test(browser)


		# 点击登录按钮
		browser.find_element(By.XPATH, '/html/body/main/div/div/div[2]/div/div/div/div/div/form/button').click()

		# 验证登录结果
		print('等待15秒验证登录结果')
		time.sleep(15)
		try:
			current_url = browser.current_url
			page_source = browser.page_source
			if current_url.find('info') > -1 and page_source.find('ACTIVE') > -1:
				self.loginSuccess = True
				res = browser.execute_script('''return document.querySelector("body > main > div > div > div:nth-child(2) > div > div > div > div > div > div:nth-child(6) > div").textContent''')
				msg = f'{self.website_hostname}\n login Success!\nVPS Valid until:{res}'
				print(msg)
				self.sendMessageToTelegram(sendto='me', msg=msg)
			else:
				self.sendMessageToTelegram(sendto='me', msg=f'{self.website_hostname}\n login Failed!')
		except Exception as e:
			self.loginSuccess = False
			logging.error('验证登录结果失败:\n', e)



	def loginSuccessCheck(self):
		print('------loginSuccessCheck------')
		print(f'loginSuccess={self.loginSuccess}')
		if self.loginSuccess:
			# 有可能登录成功后一段时间登录状态已失效
			print('---检查登录状态---')
			self.browser.get(self.url_vps_info)
			# 如果登录失效，会自动跳转到登录页面
			time.sleep(5)
			if self.browser.current_url.find('login') > -1:
				self.loginSuccess = False
				print('登录已失效')
				self.login()
		else:
			print('---用户未登录---')
			self.login()
		return self.loginSuccess


	def loginSuccessCallback(self):
		print(f'----------登录成功：{self.username}----------')
		return True

	def getPageCookie(self, url=''):
		if url:
			self.browser.get(url)
		cookies = self.browser.get_cookies()
		print(f'cookies = \n{cookies}')
		cookies = ';'.join(list(map(lambda x: x['name'] + '=' + str(x['value']), cookies)))
		return cookies

	def getPageHeader(self, url='', urlFilter=''):
		if url:
			self.browser.get(url)
		reqs = self.browser.requests
		# print('reqs=', reqs)
		reqs = list(filter(lambda x: urlFilter in x.url, reqs))
		header = []
		headers = {}
		for request in reqs:
			print(request)
			print(request.headers)
			# print(request.response.status_code, request.response.body, request.response.headers)
			for k, v in request.headers.items():
				header.append(k + ': ' + v)
				headers[k] = v

		print('getPageHeader header=', header)
		return headers


	def renew(self, cookie=''):
		# time.sleep(10)
		if cookie or self.cookie:
			self.setCookies(cookieStr=cookie or self.cookie, url=self.url)
		if not self.loginSuccessCheck(): # 检查登录状态
			print('---用户登录检查失败---')
			return
		self.browser.get(self.url_vps_renew)
		self.numberCaptcha(self.browser)
		time.sleep(20)
		self.inputRenewCode(self.browser)
		# self.sendMessageToTelegram(sendto='me', msg=f'{self.website_hostname} Renew Success!')
		self.sendMessageToTelegram(sendto='me', msg=f'------{self.website_hostname} Renew end!------')
		# 随机点击测试，注释掉上面
		# self.browser.get(self.url_vps_renew_code)
		# self.inputRenewCode(self.browser)

	def renew_multiple_accounts(self, accounts=[], commonArgs={}, renewRetryTimes=0):
		# commonArgs可以放每个账号都相同的配置，例如proxy和yescaptcha_clientKey
		# renewRetryTimes为续期失败重试次数
		print('------renew_multiple_accounts------')
		self.renewRetryTimes = int(renewRetryTimes)
		for k, v in commonArgs.items():
				self.__setattr__(k, v)
		for idx, account in enumerate(accounts):
			if account.get('skip'):
				# skip为True可以跳过本账号，主要用于首次登录telegram，生成session_name_1（不同的序号文件）
				print(f'跳过第{idx + 1}个账号:\n', account['username'])
				continue
			print(f'开始续费第{idx + 1}个账号:\n', account['username'])
			# 每个账号可以配置session_name，这样可以让hax和woiden的同tg账号使用同1个session_name
			self.telegram_session_name = account.get('session_name') or f'session_name_{idx + 1}'
			print(f'telegram_session_name={self.telegram_session_name}')
			self.loginSuccess = False
			self.renewTimes = 0
			self.renewSuccess = False
			for k, v in account.items():
				self.__setattr__(k, v)
			self.update_urls() # 更新平台地址
			try:
				while self.renewTimes <= self.renewRetryTimes:
					self.renewTimes += 1
					print(f'当前尝试第{self.renewTimes}次续期（失败重试次数={renewRetryTimes}）')
					self.renew()
					if self.renewSuccess:
						print(f"账号：{account['username']}\n平台：{self.website_hostname}\n已成功续期！")
						break
					time.sleep(random.randint(10, 20))
			except Exception as e:
				logging.error(f"{account['username']}续费失败:\n", e)
			if idx == len(accounts) - 1:
				print('所有账号已续费完毕')
			else:
				print('等待15~25秒后续费下1个账号')
				time.sleep(random.randint(15, 25))

	def getNumberCaptchaResult(self, browser):
		print('--------getNumberCaptchaResult--------')
		try:
			number1 = int(browser.execute_script(useXpathScript('return $x("/html/body/main/div/div/div[2]/div/div/div/div/div/form/div[2]/div[1]/img[1]")[0].currentSrc')).split('-')[1][0])
			number2 = int(browser.execute_script(useXpathScript('return $x("/html/body/main/div/div/div[2]/div/div/div/div/div/form/div[2]/div[1]/img[2]")[0].currentSrc')).split('-')[1][0])
			caculateMethod = browser.execute_script(useXpathScript('return $x("/html/body/main/div/div/div[2]/div/div/div/div/div/form/div[2]/div[1]")[0].childNodes[0].parentElement.childNodes[2].data'))
			print(f'{number1} {caculateMethod} {number2} =')
			captcha_result = ''
			if caculateMethod == '+':
				captcha_result = number1 + number2
			elif caculateMethod == '-':
				captcha_result = number1 - number2
			elif caculateMethod == 'X':
				captcha_result = number1 * number2
			elif caculateMethod == '/':
				captcha_result = number1 / number2
			print(f'captcha_result={captcha_result}')
			return captcha_result
		except Exception as e:
			logging.error('getNumberCaptchaResult error:\n', e)
			return ''

	def numberCaptcha(self, browser):
		print('--------numberCaptcha--------')
		try:
			# 填写hax.co.id或者Woiden.id
			website = 'hax.co.id' if self.website_code == 1 else 'Woiden.id'
			browser.execute_script(useXpathScript(f'$x("/html/body/main/div/div/div[2]/div/div/div/div/div/form/div[1]/input")[0].value="{website}"'))
			# 填写算术题计算结果
			captcha_result = self.getNumberCaptchaResult(browser)
			browser.execute_script(useXpathScript(f'$x("/html/body/main/div/div/div[2]/div/div/div/div/div/form/div[2]/div[2]/input")[0].value="{captcha_result}"'))
			# 勾选 Please Renew my server and keep my data
			browser.execute_script(useXpathScript('$x("/html/body/main/div/div/div[2]/div/div/div/div/div/form/fieldset/div/div/div/input")[0].checked=true'))
			# 点击renew
			time.sleep(2)
			if self.website_code == 1:
				browser.find_element(By.XPATH, '/html/body/main/div/div/div[2]/div/div/div/div/div/form/button').click()
			else:
				browser.execute_script('document.querySelector("#form-submit > button").click()')
		except Exception as e:
			logging.error('numberCaptcha error:\n', e)

	def adsClear(self, browser):
		# woiden有可能出现几种不同的全屏广告
		# https://woiden.id/vps-renew#google_vignette
		print('------全屏广告检测中------')
		time.sleep(3)
		if browser.current_url.find('#google_vignette') > -1:
			print('发现全屏广告，尝试关闭')
			time.sleep(3)
			# 重新加载页面会丢失已输入的信息，注意必须关闭广告后再输入
			browser.get(browser.current_url.strip('#google_vignette'))
			return True

	def reCaptcha_V2(self, browser):
		print('--------reCaptcha_V2--------')
		# 这里前文已经有输入，所以不能在此处检测广告，会导致页面输入信息丢失
		# self.adsClear(browser)

		# 点击 进行reCaptcha V2版本人机验证
		print('点击 进行人机验证')
		# 控件包含在frame里面，找不到元素，需要先跳转到相应的frame
		# https://stackoverflow.com/questions/43089070/python-selenium-cant-find-existing-element-how-switch-frame
		frame = wait(browser, 20).until(EC.presence_of_element_located((By.XPATH, "/html/body/main/div/div/div[2]/div/div/div/div/div/form/div[3]/div/div/div/iframe")))
		browser.switch_to.frame(frame)
		browser.execute_script(useXpathScript('''$x('//*[@id="rc-anchor-container"]')[0].click()'''))
		# browser.switch_to.default_content() # 这个移到下面去了

		# 有可能点击直接就通过了，点击直接出现验证打勾✔通过，这时候不需要图片验证
		try:
			time.sleep(5)
			outerHTML = browser.execute_script('return document.documentElement.outerHTML')
			clickPass = outerHTML.find('recaptcha-checkbox-checked') > -1
			print(f'clickPass={clickPass}')
			if clickPass:
				print('点击已经直接验证打勾✔通过！')
				browser.switch_to.default_content() # 记得回到默认frame
				return
		except:
			pass

		browser.switch_to.default_content() # 从上面移到这里来了

		# 使用腾讯云语音验证或者yescaptcha验证
		if self.wit_access_token or (self.tencent_SecretId and self.tencent_SecretKey):
			print('采用腾讯或者wit.ai进行语音识别验证')
			self.tencentAsrCaptcha(browser)
		elif self.yescaptcha_clientKey:
			print('采用yesCaptcha验证')
			self.yesCaptcha(browser)
		else:
			print('缺少腾讯云api配置或yescaptcha客户端密钥！\n尝试采用随机点击图片验证，本功能仅测试使用，可人为辅助点击！')
			self.reCaptcha_random_click_test(browser)


	def tencentAsrCaptcha(self, browser):
		# 使用腾讯云语音一句话识别
		# 跳转到图片验证 帧
		time.sleep(2)
		xpath = '/html/body/div[11]/div[4]/iframe' if self.website_code == 1 else '/html/body/div[12]/div[4]/iframe'
		frame = wait(browser, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
		print('frame=', frame)
		browser.switch_to.frame(frame)

		time.sleep(5)
		audio_style = browser.execute_script('''return document.querySelector("#recaptcha-audio-button").style.cssText''')
		# 显示音频按钮是''，显示图片是'display: none;'
		print(f'audio_style={audio_style}')
		if audio_style.find('none') < 0:
			# 点击使用音频验证
			print('点击切换到语音验证')
			# browser.execute_script('''document.querySelector("#recaptcha-image-button").click()''')
			browser.execute_script('''document.querySelector("#recaptcha-audio-button").click()''')
		time.sleep(5)

		# 是否出现稍后重试，您的计算机或网络可能在发送自动查询内容。为了保护我们的用户，我们目前无法处理您的请求。如需了解更多详情，请访问我们的帮助页面
		laterRetry = browser.execute_script('''return document.querySelector("body > div > div > div:nth-child(1) > div.rc-doscaptcha-header > div")?.textContent != undefined''')
		if laterRetry:
			print('出现了稍后重试，语音验证已被禁用，请稍等几个小时，或者更换IP')
			# 切换到yescaptcha验证
			if self.yescaptcha_clientKey:
				print('检测到yescaptcha_clientKey，切换到yescaptcha验证')
				browser.switch_to.default_content()
				# 可能因为frame问题，这里有点问题，得处理一下
				# 可以刷新页面，重新验证，reCaptcha_V2里面，强制：采用yesCaptcha验证
				self.yesCaptcha(browser)
			return False

		url = browser.execute_script('''return document.querySelector("#rc-audio > div.rc-audiochallenge-tdownload > a").href''')
		if not url:
			print('无法获取音频url地址：', url)
			return
		print('成功获取音频url地址：', url)
		# url = ''
		# 根据url获取语音识别结果
		print('开始进行语音识别')
		if self.wit_access_token:
			print('使用wit.ai进行语音识别')
			Result = myWitAudioToText(url=url, wit_access_token=self.wit_access_token)
		else:
			print('使用腾讯语音识别')
			Result = myTencentAsr(SecretId=self.tencent_SecretId, SecretKey=self.tencent_SecretKey, url=url)
		if not Result:
			print('无法获取语音识别结果')
			return

		# 填写语音结果
		browser.execute_script(f'''document.querySelector("#audio-response").value="{Result}"''')
		# 点击验证
		browser.execute_script('''document.querySelector("#recaptcha-verify-button").click()''')
		time.sleep(5)

		# 检测验证结果
		# 是否出现稍后重试，您的计算机或网络可能在发送自动查询内容。为了保护我们的用户，我们目前无法处理您的请求。如需了解更多详情，请访问我们的帮助页面
		laterRetry = browser.execute_script('''return document.querySelector("body > div > div > div:nth-child(1) > div.rc-doscaptcha-header > div")?.textContent != undefined''')
		if laterRetry:
			print('出现了稍后重试，语音验证已被禁用，请稍等几个小时，或者更换IP')
		else:
			# print('语音验证成功！')
			browser.switch_to.default_content()
			frame = wait(browser, 20).until(EC.presence_of_element_located((By.XPATH, "/html/body/main/div/div/div[2]/div/div/div/div/div/form/div[3]/div/div/div/iframe")))
			browser.switch_to.frame(frame)
			# 不要用 driver.page_source，那样得到的页面源码不标准。outerHTML也是要先跳转到相应的frame，才能正常获取，不然只能获取到当前所在frame的源码
			outerHTML = browser.execute_script('return document.documentElement.outerHTML')
			# open('pageSource.txt', 'w').write(outerHTML)
			if outerHTML.find('recaptcha-checkbox-checked') > -1:
				print('语音验证成功！')
			else:
				print('语音验证失败！')

		# time.sleep(10)
		browser.switch_to.default_content()
		# time.sleep(15)
		# 语音识别结束


	def yesCaptcha(self,  browser):
		# 使用第三方进行图片验证
		time.sleep(2)
		# 登录页面
		# sitekey = browser.execute_script('''return document.querySelector("body > main > div > div > div:nth-child(2) > div > div > div > div > div > form > div:nth-child(3) > div").getAttribute("data-sitekey")''')
		# Renew VPS页面
		# sitekey = browser.execute_script('''return document.querySelector("#form-submit > div:nth-child(3) > div").getAttribute("data-sitekey")''')
		# 通用版本
		# sitekey = '6LdZ3_YZAAAAALyzLQjyjE6RPFdcG9A-TLr6AxF0'
		sitekey = re.findall('data-sitekey="(.*?)"',  browser.page_source )[0]
		# print(sitekey)
		if sitekey.find('"') > -1:
			sitekey = sitekey.split('"')[0]
		print('获取data-sitekey成功:\n', sitekey)
		if sitekey:
			print('开始获取gRecaptchaResponse')
			# websiteURL = browser.current_url
			websiteURL = self.url_vps_renew_code
			gRecaptchaResponse = myYesCaptcha(clientKey=self.yescaptcha_clientKey, websiteKey=sitekey, websiteURL=websiteURL, task_type='NoCaptchaTaskProxyless')
			browser.execute_script(f'''document.getElementById("g-recaptcha-response").text="{gRecaptchaResponse}"''')
			browser.execute_script(f'''document.getElementById("g-recaptcha-response").value="{gRecaptchaResponse}"''')
			# 参考：https://yescaptcha.atlassian.net/wiki/spaces/YESCAPTCHA/pages/2818199/Python+DEMO+selenium+demo+selenium.py
			# 执行回调函数，每个网站回调函数并不相同，需要自己找一下
			# # 一般为data-callback=xxxx，这个xxxx就是回调函数
			# driver.execute_script(f'onSuccess("{response}")')
			# browser.execute_script(f'''onSubmit("{gRecaptchaResponse}")''')
			time.sleep(1)
		# 图片验证结束


		# 点击空白处，让图片验证页面消失
		time.sleep(5)
		# 这以句有可能失败：javascript error: Cannot read properties of null (reading 'click')
		# browser.execute_script('''document.querySelector("body > div:nth-child(34) > div:nth-child(1)").click()''')
		seconds = 20
		while seconds > 0:
			try:
				# 此处参考：https://github.com/Zakkoree/woiden_extend/blob/main/main.py#L477
				browser.execute_script('''$.each($('body>div'),function(index,e){a=$('body>div').eq(index);if(a.css('z-index')=='2000000000'){a.children('div').eq(0).click()}})''')
				# if self.website_code == 1:
				# 	browser.execute_script('''document.querySelector("body > div:nth-child(34) > div:nth-child(1)").click()''')
				# else:
				# 	browser.execute_script('''document.querySelector("body > div:nth-child(27) > div:nth-child(1)").click()''')
				break
			except Exception as e:
				logging.error('点击图片验证页面消失，失败:\n', e)
			seconds = seconds - 1
			time.sleep(1)


	def inputRenewCode(self, browser):
		print('--------inputRenewCode--------')
		try:
			# 先检测是否跳转到全屏广告页面
			adsAppear = self.adsClear(browser)
			if adsAppear:
				print('关闭广告页面重新加载')
				time.sleep(3)
				return self.inputRenewCode(browser)

			# Your verification code has been sent to your telegram account, please input here to renew your VPS:
			# 点击INPUT RENEW CODE
			# if self.website_code == 1:
			# 	browser.find_element(By.XPATH, '/html/body/main/div/div/div[2]/div/div/div/div/div/div[2]/div/a').click()
			# else:
			# 	browser.execute_script('document.querySelector("#response > div > a").click()')
			# 不点击RENEW CODE，直接vps_renew_code访问页面
			browser.get(self.url_vps_renew_code)
			time.sleep(5)
			# 填写 Verification Code:
			# browser.get(self.url_vps_renew_code)
			# VerificationCode = 'xxxxxx'
			self.updateVerificationCode()
			VerificationCode = self.VerificationCode
			if not VerificationCode:
				VerificationCode = input('请输入Verification Code:')
			browser.execute_script(useXpathScript(f'$x("/html/body/main/div/div/div[2]/div/div/div/div/div/form/div[1]/input")[0].value="{VerificationCode}"'))

			# 填写算术题计算结果
			captcha_result = self.getNumberCaptchaResult(browser)
			browser.execute_script(useXpathScript(f'$x("/html/body/main/div/div/div[2]/div/div/div/div/div/form/div[2]/div[2]/input")[0].value="{captcha_result}"'))

			# 这里woiden平台可能会弹出全屏广告，要先点击CLOSE
			if self.website_code == 2:
				time.sleep(3)
				# adsAppear = browser.page_source.find('id="dismiss-button"') > -1
				# if adsAppear:
				# 	print('出现了页面全屏广告，尝试点击关闭')
				# 	browser.execute_script('''document.querySelector("#dismiss-button")?.click()''')
				adsAppear = self.adsClear(browser)
				if adsAppear:
					print('关闭广告页面重新加载')
					time.sleep(3)
					return self.inputRenewCode(browser)


			# reCaptcha 图片或者语音验证
			self.reCaptcha_V2(browser)

			# 随机点击验证图片 测试代码
			# self.reCaptcha_random_click_test(browser)


			# 点击Renew VPS
			if self.website_code == 1:
				browser.find_element(By.XPATH, '/html/body/main/div/div/div[2]/div/div/div/div/div/form/button').click()
			else:
				# 这个有时候找不到元素，好像是没browser.switch_to.default_content()
				browser.execute_script('document.querySelector("#form-submit > button").click()')

			# 验证续费结果
			print('15秒后验证Renew VPS续费结果')
			time.sleep(15)
			# 也可以使用while True每间隔一段时间检测一次，成功就退出，一定次数不成功就判定为失败
			try:
				res = browser.execute_script('''return document.querySelector("#response > div").textContent''')
				print(res)
				if res.find('renewed') > -1:
					self.renewSuccess = True
					self.sendMessageToTelegram(sendto='me', msg=f'{self.website_hostname}\nRenew Success!\n{res}')
				else:
					self.sendMessageToTelegram(sendto='me', msg=f'{self.website_hostname}\nRenew Failed!\n{res}')
			except Exception as e:
				logging.error('Renew VPS验证结果失败', e)



		except Exception as e:
			logging.error('inputRenewCode error:\n', e)


	def reCaptcha_random_click_test(self, browser):
		print('--------reCaptcha_random_click_test--------')
		time.sleep(5)
		frame = wait(browser, 20).until(EC.presence_of_element_located((By.XPATH, "/html/body/main/div/div/div[2]/div/div/div/div/div/form/div[3]/div/div/div/iframe")))
		browser.switch_to.frame(frame)
		browser.execute_script(useXpathScript('''$x('//*[@id="rc-anchor-container"]')[0].click()'''))
		# time.sleep(10)

		try:
			time.sleep(5)
			outerHTML = browser.execute_script('return document.documentElement.outerHTML')
			clickPass = outerHTML.find('recaptcha-checkbox-checked') > -1
			print(f'clickPass={clickPass}')
			if clickPass:
				print('点击已经直接验证打勾✔通过！')
				return
		except:
			pass

		browser.switch_to.default_content()

		# 跳转到图片验证 帧
		time.sleep(10)
		xpath = '/html/body/div[11]/div[4]/iframe' if self.website_code == 1 else '/html/body/div[12]/div[4]/iframe'
		frame = wait(browser, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
		print('frame=', frame)
		browser.switch_to.frame(frame)

		# browser.execute_script(useXpathScript('''document.querySelector("#rc-imageselect-target > table > tbody > tr:nth-child(1) > td:nth-child(1)").click()'''))
		# imageTableName = browser.execute_script('''return document.querySelector("#rc-imageselect-target > table").className''')
		# 'rc-imageselect-table-44'
		# 'rc-imageselect-table-33'

		def getRandomClickList(imageNum=9):
			# 验证图片分割数量：9或16
			clickList = []
			# script = '''document.querySelector("#rc-imageselect-target > table > tbody > tr:nth-child(1) > td:nth-child(1)").click()'''
			def getXY(number):
				x = 1 # 行
				y = 1 # 列
				n = 3 if imageNum == 9 else 4
				a = number // n # 取整
				b = number % n # 取余
				if b == 0:
					x = a
					y = n
				else:
					x = a + 1
					y = b

				script = f'''document.querySelector("#rc-imageselect-target > table > tbody > tr:nth-child({x}) > td:nth-child({y})").click()'''
				return script

			randomNumbers = []
			if imageNum == 9:
				randomNumbers = random.sample(range(1, 10), random.randint(2, 6))
			elif imageNum == 16:
				randomNumbers = random.sample(range(1, 17), random.randint(3, 9))
			else:
				logging.error('验证图片分割数量仅支持9或16')
			print(f'imageNum={imageNum}  randomNumbers={randomNumbers}')
			clickList = list(map(getXY, randomNumbers))
			return clickList


		# code = input("输入调试代码，输入exit退出：")
		# while code and code != 'exit':
		# 	code = input("输入调试代码，输入exit退出：")
		# 	try:
		# 		exec(code)
		# 	except Exception as e:
		# 		logging.error('exec code error:\n', e)

		# 点击验证按钮
		#  document.querySelector("#recaptcha-verify-button").textContent
		# 验证、跳过、下一个
		# document.querySelector("#rc-imageselect > div.rc-imageselect-payload > div:nth-child(4) > div.rc-imageselect-error-select-more").textContent
		# '请选择所有相符的图片。'
		# document.querySelector("#rc-imageselect > div.rc-imageselect-payload > div:nth-child(4) > div.rc-imageselect-error-dynamic-more").textContent
		# '另外，您还需查看新显示的图片。'
		# document.querySelector("#rc-imageselect > div.rc-imageselect-payload > div.rc-imageselect-incorrect-response").textContent
		# '请重试。'
		# document.querySelector("#rc-imageselect > div.rc-imageselect-payload > div.rc-imageselect-incorrect-response").getAttribute('style')
		# 'display:none'
		contentList = [
			"#rc-imageselect > div.rc-imageselect-payload > div:nth-child(4) > div.rc-imageselect-error-select-more",
			"#rc-imageselect > div.rc-imageselect-payload > div:nth-child(4) > div.rc-imageselect-error-dynamic-more",
			"#rc-imageselect > div.rc-imageselect-payload > div.rc-imageselect-incorrect-response"
		]

		btn = browser.find_element(By.ID, 'recaptcha-verify-button')
		# 这一步又可能找不到元素，肯能需要等待一段时间图片加载出来
		print('发现验证按钮：', btn)
		while btn:
			print('获取验证图片分割数量')
			# 如果点击直接出现验证打勾✔通过，这时候会找不到元素
			imageTableName = None
			try:
				imageTableName = browser.execute_script('''return document.querySelector("#rc-imageselect-target > table").className''')
			except Exception as e:
				logging.error('未能获取imageTableName:\n', e)
			imageNum = 9
			if not imageTableName:
				print('未能获取imageTableName')
				break
			if imageTableName == 'rc-imageselect-table-33':
				imageNum = 9
			elif imageTableName == 'rc-imageselect-table-44':
				imageNum = 16
			print(f'图片分割数={imageNum}')

			print('开始随机点击验证')
			randomClickList = getRandomClickList(imageNum=9)
			print('点击个数=', len(randomClickList))
			for s in randomClickList:
				print(s)
				browser.execute_script(s)
				time.sleep(2)

			print('点击验证按钮')
			try:
				btn.click()
			except Exception as e:
				logging.error('点击按钮失败:\n', e)

			print('验证提示')
			time.sleep(3)
			for c in contentList:
				cs = browser.execute_script(f'''return document.querySelector("{c}").getAttribute('style')''')
				# 'display:none'
				if cs.find('none') < 0:
					print(browser.execute_script(f'''return document.querySelector("{c}").textContent'''))
					break

			print('检测验证结果')
			time.sleep(3)
			btn = browser.find_element(By.ID, 'recaptcha-verify-button')
			if btn and btn.get_attribute('class').find('disabled') < 0:
				# document.querySelector("#recaptcha-verify-button").className
				# 'rc-button-default goog-inline-block'
				# document.querySelector("#recaptcha-verify-button").className
				# 'rc-button-default goog-inline-block rc-button-default-disabled'
				print('验证失败，若干秒后重新点击')
				time.sleep(random.randint(3, 12))
			else:
				print('验证通过！')
				break



		# time.sleep(10)
		browser.switch_to.default_content()
		# time.sleep(15)


	def getHaxBotCode(self, name='session_name', api_id=12345, api_hash='xxxxxx', chat='HaxTG_bot', proxy=None):
		name = self.telegram_session_name
		# 开启telegram application网址：https://my.telegram.org/apps
		# 注意+86的手机号要使用香港节点，不然会一直返回ERROR
		# chat = 'me' # 收藏夹
		# proxy = (socks.SOCKS5, '127.0.0.1', 10808, True)
		# 注意电脑版使用proxy需要安装：python-socks[asyncio]
		# pip install python-socks[asyncio] -i https://pypi.tuna.tsinghua.edu.cn/simple
		# 参考：
		# https://github.com/LonamiWebs/Telethon/issues/3962
		# https://docs.telethon.dev/en/stable/basic/signing-in.html?highlight=python-socks#signing-in-behind-a-proxy

		with TelegramClient(name, api_id, api_hash, proxy=proxy) as client:
			# print(client.get_me().stringify())
			messages = client.iter_messages(chat, limit=5, search='Your Code is')
			for idx, message in enumerate(messages): # 取前10条消息，搜索'Your Code is'
			# for message in client.iter_messages(chat, limit=10): # 取前10条消息
				# see more here:
				# https://docs.telethon.dev/en/stable/modules/client.html#telethon.client.messages.MessageMethods.iter_messages
				# https://docs.telethon.dev/en/stable/modules/custom.html#telethon.tl.custom.message.Message
				# id、date、from_id、peer_id
				# print(message.sender_id, ':', message.text)
				print(idx, '> ', message.date, ': ', message.text)
			VerificationCode = list(messages)[0].text.strip('Your Code is').strip(' ').strip('\n').strip('**')
			print(f'getHaxBotCode success:\n{VerificationCode}')
			return VerificationCode

	def updateVerificationCode(self):
		print('--------updateVerificationCode--------')
		try:
			VerificationCode = self.getHaxBotCode(api_id=self.api_id, api_hash=self.api_hash, proxy=self.proxy)
			self.VerificationCode = VerificationCode
		except Exception as e:
			logging.error('updateVerificationCode error:\n', e)

	def sendMessageToTelegram(self, name='session_name', sendto='HaxTG_bot', msg='Hello'):
		name = self.telegram_session_name
		proxy = self.proxy
		print('--------sendMessageToTelegram--------')
		# sendto = 'me'
		# client.send_message('username', 'Hello! Talking to you from Telethon')
		with TelegramClient(name, self.api_id, self.api_hash, proxy=proxy) as client:
			client.send_message(sendto, msg)
			print(f'sendMessageToTelegram success:\nsendto={sendto}\nmsg={msg}')


















# 案例获取鼠标的位置，方便复制我们定位的鼠标坐标点到代码中
# def get_mouse_position():
# 	time.sleep(5) # 准备时间
# 	# print('开始获取鼠标位置')
# 	try:
# 		for i in range(10):
# 			x, y = pyautogui.position()
# 			positionStr = '鼠标坐标点（X,Y）为：{},{}'.format(str(x).rjust(4), str(y).rjust(4))
# 			# pix = pyautogui.screenshot().getpixel((x, y)) # 获取鼠标所在屏幕点的RGB颜色
# 			# positionStr += ' RGB:(' + str(pix[0]).rjust(3) + ',' + str(pix[1]).rjust(3) + ',' + str(pix[2]).rjust(3) + ')'
# 			print(positionStr)
# 			time.sleep(0.5) # 停顿时间
# 	except:
# 		print('获取鼠标位置失败')

# if __name__ == "__main__":
#     pyautogui.alert(text='要开始程序么？', title='请求框', button='OK')
#     get_mouse_position()
#     exit()





if __name__ == '__main__':
	# 注意在Pychram中好像无法输入telegram两步验证密码，第一次现在CMD运行脚本即可！
	# 登录一次后，可以把session_name.session文件复制到同级目录，就可以移植到其它平台，免去重复登录！
	# 有些节点会出现CF5秒盾，第一次可以手动验证一下，或者更换节点！
	# 使用前，在__init__函数相应位置，修改下面2句代码，或者指定chrome_user_data_dir
	# options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
	# options.add_argument("--user-data-dir=" + r"D:\yuchenye\Downloads\seleniumtest")
	# Chrome浏览器数据存放位置，为空则使用随机位置
	# chrome_user_data_dir = ''
	# chrome_user_data_dir = r"D:\yuchenye\Downloads\seleniumtest"

	# username = 'xxx'
	# password = 'xxx'
	# cookie = ''
	# # proxy = None
	# proxy = (socks.SOCKS5, '127.0.0.1', 10808, True)
	# # proxy = (socks.HTTP, '127.0.0.1', 10809, True)
	# # telegram application配置
	# telegram_session_name = 'session_name'
	# api_id = 123
	# api_hash = 'xxx'
	# # yescaptcha 帐户密钥 ClientKey
	# yescaptcha_clientKey = 'xxx'
	# # 腾讯云api配置信息
	# tencent_SecretId = 'xxx'
	# tencent_SecretKey = 'xxx'
	# wit.ai语音识别
	# wit_access_token = 'xxx'
	#
	#
	# website_code = 1 # hax为1，woiden为2,
	# myClass = haxRenewClass(website_code=1,
	# 		  				username=username, password=password,
	# 						cookie=cookie,
	# 						telegram_session_name=telegram_session_name,
	# 						api_id=api_id, api_hash=api_hash,
	# 						yescaptcha_clientKey=yescaptcha_clientKey,
	# 						tencent_SecretId=tencent_SecretId, tencent_SecretKey=tencent_SecretKey,
	# 						wit_access_token = wit_access_token,
	# 						proxy=proxy,
	# 						chrome_user_data_dir=chrome_user_data_dir,
	# 						)

	# myClass.login(logout=True)
	# myClass.renew()
	# myClass.renew_multiple_accounts(accounts=[])
	# myClass.updateVerificationCode()
	# myClass.sendMessageToTelegram(sendto='HaxTG_bot', msg='Hello')



	# 续费多个账号版本

	myClass = haxRenewClass()
	accounts = [
		{
		'skip': True, # skip为True可以跳过本账号
		'website_code': 1, # hax为1，woiden为2
		'username': 'xxx',
		'password': 'xxx',
		# telegram application配置
		# hax和woiden使用同1个tg账号，可以使用同1个session_name。也可以注释掉，默认的session_name为session_name_idx+1
		'session_name': 'session_name_1',
		'api_id': 123,
		'api_hash': 'xxx',
		},
		{
		'skip': True, # skip为True可以跳过本账号
		'website_code': 2, # hax为1，woiden为2
		'username': 'xxx',
		'password': 'xxx',
		# telegram application配置
		'session_name': 'session_name_2',
		'api_id': 456,
		'api_hash': 'xxx',
		},
		{
		'skip': False, # skip为True可以跳过本账号
		'website_code': 1, # hax为1，woiden为2
		'username': 'xxx',
		'password': 'xxx',
		# telegram application配置
		'session_name': 'session_name_2',
		'api_id': 456,
		'api_hash': 'xxx',
		},
	]
	# 多个账号相同的配置
	# commonArgs = {}
	commonArgs = {
		# Chrome浏览器数据存放位置，为空则使用随机位置
		# 'chrome_user_data_dir': '',
		'chrome_user_data_dir': r"D:\yuchenye\Downloads\seleniumtest",
		# 'chrome_user_data_dir': r"D:\myExeApplications\seleniumtest",

		# telegram代理
		# 'proxy': None,
		'proxy': (socks.SOCKS5, '127.0.0.1', 10808, True),
		# proxy = (socks.HTTP, '127.0.0.1', 10809, True)

		# 可以同时输入2个平台的配置信息，优先使用语音，如果语音被禁用，会自动切换到图片验证
		# 也可以只输入其中1个平台，将会采用输入的平台进行验证
		# 如果1个都没有输入，将采用随机点击图片验证，仅测试功能，需人工辅助点击才能正确通过验证
		# yescaptcha 帐户密钥 ClientKey
		'yescaptcha_clientKey': 'xxx',
		# 腾讯云api配置信息
		'tencent_SecretId': 'xxx',
		'tencent_SecretKey': 'xxx',
		# wit.ai语音识别
		'wit_access_token': 'xxx',
	}
	renewRetryTimes = 0 # 续期失败重试次数
	myClass.renew_multiple_accounts(accounts=accounts, commonArgs=commonArgs, renewRetryTimes=renewRetryTimes)


	# 防止网络代理或者窗口关闭
	input("SCRIPT ENDED\n")












