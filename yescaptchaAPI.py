"""
author: Zakkoree
"""
import time
import requests
# from commonlog import Logger
import logging


requests.packages.urllib3.disable_warnings()
# 配合verify=False可以允许抓包
# 代理会报错，需要安装旧版本urllib3，参考：https://blog.csdn.net/Ig_thehao/article/details/122145325
# pip install urllib3==1.25.11
# 但是selenium需要1.26版本，踏马的绝了
# selenium 4.4.3 requires urllib3[socks]~=1.26, but you have urllib3 1.25.11 which is incompatible.
#
# logger = Logger(LoggerName="yescaptchaAPI")


def create_task(clientKey: str, websiteKey: str, websiteURL: str, task_type: str) -> str:
    data = {
        "clientKey": clientKey,
        "task": {
            "websiteURL": websiteURL,
            "websiteKey": websiteKey,
            "type": task_type or "NoCaptchaTaskProxyless",
            # "isInvisible": False # isinvisable类型才需要添加 true 值
        }
    }
    return create(data)

def create(data):
    try:
        url = "https://api.yescaptcha.com/createTask"
        requests.packages.urllib3.disable_warnings()
        res = requests.post(url, json=data, verify=False).json()
        print(res)
        return res
    except Exception as e:
        logging.error('yescaptcha createTask error:\n', e)
        return None


def create_task_v3(clientKey: str, websiteKey: str, websiteURL: str, pageAction: str) -> str:
    data = {
        "clientKey": clientKey,
        "task": {
            "websiteURL": websiteURL,
            "websiteKey": websiteKey,
            "pageAction" : pageAction,
            "type": "RecaptchaV3TaskProxyless"
        }
    }
    return create(data)


def get_response(taskID: str, clientKey: str):
    print('------get_response------')
    times = 0
    while times < 120:
        try:
            url = f"https://api.yescaptcha.com/getTaskResult"
            data = {
                "clientKey": clientKey,
                "taskId": taskID
            }
            requests.packages.urllib3.disable_warnings()
            result = requests.post(url, json=data, verify=False).json()
            print(result)
            solution = result.get('solution', {})
            if solution:
                response = solution.get('gRecaptchaResponse')
                if response:
                    return response
            if result.get('errorId') == 1:
                return None
        except Exception as e:
            logging.error(e)

        times += 3
        time.sleep(3)
    logging.error("yescaptcha get_response timeout")
    return None

        

def verify_website(response, websiteURL):
    data = {"g-recaptcha-response": response}
    r = requests.post(websiteURL, data=data)
    if r.status_code == 200:
        return r.text
        
        
def asr(clientKey: str, websiteKey: str, websiteURL: str, task_type: str):
    taskResult = create_task(clientKey, websiteKey, websiteURL, task_type)
    taskId = taskResult.get('taskId')
    if taskId is not None:
        response = get_response(taskId, clientKey)
        print("yescaptcha :", response)
        logging.info("yescaptcha :",  response)
        return response
        # result = verify_website(response)
        # print('验证结果：', result)
    else:
        logging.error("yescaptcha create_task :", taskResult.get('errorDescription'))
        return None

def asrV3(clientKey: str, websiteKey: str, websiteURL: str, pageAction: str):
    taskResult = create_task_v3(clientKey, websiteKey, websiteURL, pageAction)
    taskId = taskResult.get('taskId')
    if taskId is not None:
        response = get_response(taskId, clientKey)
        logging.info("yescaptcha V3 :" + response)
        return response
        # result = verify_website(response, websiteURL)
        # print('验证结果：', result)
    else:
        logging.error("yescaptcha V3 create_task :" + taskResult.get('errorDescription'))
        return None



def myYesCaptcha(clientKey = 'xxxxxx', websiteKey='6LdZ3_YZAAAAALyzLQjyjE6RPFdcG9A-TLr6AxF0', websiteURL="https://hax.co.id/vps-renew-code", task_type='NoCaptchaTaskProxyless'):
    # 目标参数：
    websiteKey = websiteKey or '6LdZ3_YZAAAAALyzLQjyjE6RPFdcG9A-TLr6AxF0'
    # 目标参数：
    # websiteURL = "https://woiden.id"
    websiteURL = websiteURL or "https://hax.co.id/vps-renew-code"
    # websiteURL = "https://hax.co.id/"
    task_type = task_type or 'NoCaptchaTaskProxyless'
    # taskType可参考：https://yescaptcha.atlassian.net/wiki/spaces/YESCAPTCHA/pages/164286
    response = asr(clientKey, websiteKey, websiteURL, task_type)
    return response



if __name__ == '__main__':
    # clientKey：在个人中心获取
    clientKey = "xxxxxxxx"
    # 目标参数：
    websiteKey = '6LdZ3_YZAAAAALyzLQjyjE6RPFdcG9A-TLr6AxF0'
    # 目标参数：
    # websiteURL = "https://woiden.id"
    websiteURL = "https://hax.co.id/vps-renew-code"
    # websiteURL = "https://hax.co.id/"
    task_type = 'NoCaptchaTaskProxyless'
    # taskType可参考：https://yescaptcha.atlassian.net/wiki/spaces/YESCAPTCHA/pages/164286
    asr(clientKey, websiteKey, websiteURL, task_type)







