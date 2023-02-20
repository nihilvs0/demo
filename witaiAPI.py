import requests
import json
import re

requests.packages.urllib3.disable_warnings()


def read_audio(file):
	with open(file, 'rb') as f:
		audio = f.read()
	return audio


def witAudioToText(audioContent, wit_access_token=""):
	print("--------witAudioToText--------")
	# 官方文档地址：https://wit.ai/docs/http/20230215/#post__speech_link
	# Wit speech API endpoint
	API_ENDPOINT = 'https://api.wit.ai/speech'
	# API_ENDPOINT = "https://api.wit.ai/speech?v=20221114"
	# Wit.ai api access token
	# buster插件的TOKEN，偷来试用
	# wit_access_token = wit_access_token or  'xxxxxx'

	headers = {
		'authorization': 'Bearer ' + wit_access_token,
		# 'Content-Type': 'audio/wav',
		'Content-Type': 'audio/mpeg3', # mp3格式
	}
	resp = requests.post(API_ENDPOINT, headers = headers,
						 data = audioContent)

	print(resp.text)
	data = re.findall('"text": "(.*?)"', resp.text)
	print("data=", data)
	if len(data) < 1:
		print("语音识别失败！")
		return
	text = data[-1]
	print(f"语音识别成功！识别结果：\n{text}")
	return text


def downloadFile(url, savepath=''):
	try:
		down_res = requests.get(url=url, params={}, verify=False)
		if savepath:
			with open(savepath, "wb") as file:
				file.write(down_res.content)
				print('download success, file save at:', savepath)
		else:
			return down_res.content
	except Exception as e:
		print('downloadFile error:\n', e)


def myWitAudioToText(url, wit_access_token):
	print('------myWitAudioToText------')
	try:
		if not url:
			print('Error!语音识别缺少url!')
			return
		Data = downloadFile(url=url)
		if Data and len(Data) > 1000: # DataLen长度一般是3万多，下载链接失效后是下载空白网页了，大小为131
			print('mp3语音下载成功！开始识别')
			Result = witAudioToText(audioContent=Data, wit_access_token=wit_access_token)
			if Result:
				print('wit.ai语音识别成功！')
				return Result
			else:
				print('wit.ai无法获取语音识别结果！')
		else:
			print('mp3语音下载失败！')
	except Exception as e:
		print('myWitAudioToText error:\n', e)





if __name__ == "__main__":
	# file = "myspeech.wav"
	# file = "myspeech.mp3"
	# audioContent = read_audio(file)
	# text =  witAudioToText(audioContent=audioContent)
	# print("语音识别结果: {}".format(text))

	url = 'https://www.google.com/recaptcha/api2/payload/audio.mp3?p=06AFY_a8WXMMgggXsZy8kHt_TC3zNlh5zyyPenREvaNa4NeoYJu2Cf6HryL23mOJPFG-92oCRXZQLhOIApd6Hmv9aLViY_MovvPAqbYsOpleDs_RWtheIRXS4LXgbFzrjIc4eNux8MNKUFg2iKxPMP_fSnOj96fypSiuYL1CIM2WYsd946w2kZ-bVwk8DfZG3e_hqE4uTyiK9j&k=6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-'
	wit_access_token = 'xxxxxx'
	text = myWitAudioToText(url=url, wit_access_token=wit_access_token)
	print("语音识别结果: {}".format(text))



 









