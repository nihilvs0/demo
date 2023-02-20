#coding=utf-8

import socks
from hax_woiden_renew import haxRenewClass





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



















