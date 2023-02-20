#coding=utf-8
"""
pip install --upgrade tencentcloud-sdk-python-common tencentcloud-sdk-python-asr -i https://mirrors.tencent.com/pypi/simple/
"""

import base64
import requests
requests.packages.urllib3.disable_warnings()

import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.asr.v20190614 import asr_client, models


def fileToBase64(file, txt):
    with open(file, 'rb') as fileObj:
        data = fileObj.read()
        base64_data = base64.b64encode(data)
        fout = open(txt, 'w')
        fout.write(base64_data.decode())
        fout.close()

def downloadFile(url, savepath=''):
    DataLen, Data = 0, ''
    try:
        down_res = requests.get(url=url, params={}, verify=False)
        if savepath:
            with open(savepath, "wb") as file:
                file.write(down_res.content)
                print('download success, file save at:', savepath)
        else:
            DataLen = len(down_res.content)
            Data = base64.b64encode(down_res.content).decode()
    except Exception as e:
        print('downloadFile error:\n', e)
    return DataLen, Data


def tencentAsr(SecretId='xxx', SecretKey='xxx', Data='', DataLen=0):
    # 腾讯云语音识别 > 一句话识别
    # Data是base64编码音频文件后的字符内容，DataLen是未编码前的音频文件字节数
    try:
        # 实例化一个认证对象，入参需要传入腾讯云账户 SecretId 和 SecretKey，此处还需注意密钥对的保密
        # 代码泄露可能会导致 SecretId 和 SecretKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考，建议采用更安全的方式来使用密钥，请参见：https://cloud.tencent.com/document/product/1278/85305
        # 密钥可前往官网控制台 https://console.cloud.tencent.com/cam/capi 进行获取
        cred = credential.Credential(SecretId, SecretKey)
        # 实例化一个http选项，可选的，没有特殊需求可以跳过
        httpProfile = HttpProfile()
        httpProfile.endpoint = "asr.tencentcloudapi.com"

        # 实例化一个client选项，可选的，没有特殊需求可以跳过
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        # 实例化要请求产品的client对象,clientProfile是可选的
        client = asr_client.AsrClient(cred, "", clientProfile)

        # 实例化一个请求对象,每个接口都会对应一个request对象
        req = models.SentenceRecognitionRequest()
        # 更多参数详见：https://console.cloud.tencent.com/api/explorer?Product=asr&Version=2019-06-14&Action=SentenceRecognition
        params = {
            "ProjectId": 0,
            "SubServiceType": 2,
            "EngSerViceType": "16k_en",
            "SourceType": 1,
            "VoiceFormat": "mp3",
            "UsrAudioKey": "_",
            "Data": Data,
            "DataLen": int(DataLen)
        }
        req.from_json_string(json.dumps(params))

        # 返回的resp是一个SentenceRecognitionResponse的实例，与请求对象对应
        resp = client.SentenceRecognition(req)
        # 输出json格式的字符串回包
        # print(resp.to_json_string())
        res = resp.to_json_string()
        print('tencentAsr SentenceRecognitionResponse:\n', res)
         # {"Result": "A very gentle character.", "AudioDuration": 4514, "WordSize": 0, "WordList": null, "RequestId": "xxx"}
        res = json.loads(res)
        Result = res.get('Result')
        if not Result or res.get('Error'):
            print('tencentAsr 一句话识别失败:', res.get('Error'))
        else:
            print('一句话识别成功：', Result)
            # return Result
            return Result.strip('.') # 去除英文句子结尾的.号

    except TencentCloudSDKException as err:
        print('tencentAsr error:\n', err)



    """
    reCaptcha测试网页：https://www.google.com/recaptcha/api2/demo
    
    使用base64编码音频文件，正常返回
    {
        "AudioDuration": 4439,
        "RequestId": "xxx",
        "Result": "Different websites today.",
        "WordList": null,
        "WordSize": 0
    }
    
    使用url会调用失败
    例如：https://www.google.com/recaptcha/api2/payload/audio.mp3?p=06AFY_a8U5urKl3uANKxFOl9cdnILNLp7U0RF50rKXk_JT5yMWJasvCwfT0i42mwy_7trqOajDEyXWtbdlM42w2kBi9KS6IRXPSTVVTTpcFKopvwnRHsgYhVkx4EIiqc3x1mWxYXDZh-evHDSHcyA73w0gHo7Oii165zYRk-qbS6aGkrdV0DBEiCrEuvxVXc6ywxW5hiZNkr7C&k=6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-
    {
        "AudioDuration": 0,
        "Error": {
          "Code": "InvalidParameterValue.ErrorInvalidUrl",
          "Message": "Failed to download!"
        },
        "RequestId": "xxx",
        "Result": "",
        "WordList": null,
        "WordSize": 0
    }
    
    """


def myTencentAsr(SecretId='xxx', SecretKey='xxx', url=''):
    print('------myTencentAsr------')
    try:
        if not url:
            print('Error!语音识别缺少url!')
            return
        DataLen, Data = downloadFile(url=url)
        if DataLen and Data and DataLen > 1000: # DataLen长度一般是3万多，下载链接失效后是下载空白网页了，大小为131
            print('mp3语音base64编码成功！')
            Result = tencentAsr(SecretId=SecretId, SecretKey=SecretKey, Data=Data, DataLen=DataLen)
            if Result:
                print('一句话语音识别成功！')
                return Result
            else:
               print('无法获取语音识别结果！')
        else:
            print('mp3语音base64编码失败！')
            print(f'DataLen={DataLen}')
    except Exception as e:
        print('myTencentAsr error:\n', e)






if __name__ == '__main__':
    SecretId = 'xxx'
    SecretKey = 'xxx'
    # Data是base64编码音频文件后的字符内容，DataLen是未编码前的音频文件字节数
    # tencentAsr(SecretId=SecretId, SecretKey=SecretKey, Data='', DataLen=0)
    url = 'https://www.google.com/recaptcha/api2/payload/audio.mp3?p=06AFY_a8WBbHMmjIEl7TlOEf94dOw_JMdeOXBoWl4OyU5Zog73Yx8vfEX5X_fSsBZyPMBRw9AUlDgCVCx7XjxO_4kuKEkNsfw3LwsvgNsVdpfVRCyCfY8Z8AJNRrSkUfJsjSdRMVJTm4x0DoxyK7EnbLVEHUr2X-aMni8AiMSuKBtKYrVkMw7o42uMw_jkQOMP2ytLcG0kepfc&k=6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-'
    myTencentAsr(SecretId=SecretId, SecretKey=SecretKey, url=url)
    # print(downloadFile(url=url))









