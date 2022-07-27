import os
import shutil

import pyttsx3 as pt

# huawei cloud tts

from huaweicloud_sis.client.tts_client import TtsCustomizationClient
from huaweicloud_sis.bean.tts_request import TtsCustomRequest
from huaweicloud_sis.bean.sis_config import SisConfig
from huaweicloud_sis.utils.logger_utils import logger, file_handler
import logging.handlers

# 修改huawei tts所维护的log的位置
logger.removeHandler(file_handler)
file_handler.close()
try:
    os.remove('huaweicloud_sis.log')
except:
    pass

"""
http://tts.baidu.com/text2audio?lan=zh&ie=UTF-8&text= 
"""


def base_tts(text, location):
    engine = pt.init()
    engine.save_to_file(text, location)
    engine.runAndWait()


def huawei_tts(text, location):
    # 修改huawei tts所维护的log的位置
    adapted_handler = logging.handlers.RotatingFileHandler('misc/tts/huaweicloud_sis.log', maxBytes=1024 * 1024,
                                                           backupCount=5, encoding='utf-8')
    adapted_handler.setLevel(logging.INFO)
    adapted_handler.setFormatter(logging.Formatter('[%(asctime)s] - [%(levelname)s] - [%(message)s]'))
    logger.addHandler(adapted_handler)
    assert len(text.encode('utf8')) <= 500
    paras = get_config()
    ak, sk, region, project_id = paras
    text = text  # 待合成文本，不超过500字
    path = location  # 保存路径，需要具体到音频文件，如D:/test.wav，可在设置中选择不保存本地

    # step1 初始化客户端
    config = SisConfig()
    config.set_connect_timeout(10)  # 设置连接超时，单位s
    config.set_read_timeout(10)  # 设置读取超时，单位s
    # 设置代理，使用代理前一定要确保代理可用。 代理格式可为[host, port] 或 [host, port, username, password]
    # config.set_proxy(proxy)
    ttsc_client = TtsCustomizationClient(ak, sk, region, project_id, sis_config=config)

    # step2 构造请求
    ttsc_request = TtsCustomRequest(text)
    # 设置请求，所有参数均可不设置，使用默认参数
    # 设置属性字符串， language_speaker_domain, 默认chinese_xiaoyan_common
    ttsc_request.set_property('chinese_huaxiaowen_common')
    # 设置音频格式，默认wav，可选mp3和pcm
    ttsc_request.set_audio_format('wav')
    # 设置采样率，8000 or 16000, 默认8000
    ttsc_request.set_sample_rate('16000')
    # 设置音量，[0, 100]，默认50
    ttsc_request.set_volume(50)
    # 设置音高, [-500, 500], 默认0
    ttsc_request.set_pitch(0)
    # 设置音速, [-500, 500], 默认0
    ttsc_request.set_speed(0)
    # 设置是否保存，默认False
    ttsc_request.set_saved(True)
    # 设置保存路径，只有设置保存，此参数才生效
    ttsc_request.set_saved_path(path)

    # step3 发送请求，返回结果。如果设置保存，可在指定路径里查看保存的音频。
    try:
        result = ttsc_client.get_ttsc_response(ttsc_request)
    # print(json.dumps(result, indent=2, ensure_ascii=False))
    finally:
        logger.removeHandler(adapted_handler)
        adapted_handler.close()


def get_config():
    par = []
    with open(r'misc/tts/huawei.txt') as f:
        for line in f:
            line = line.strip()
            if not line or line[0] == '#':
                continue
            assert line
            par.append(line)
    return par


def render(text, location):
    try:
        huawei_tts(text, location)
    except:
        base_tts(text, location)

if __name__ == '__main__':
    base_tts('今天的天气还是挺不错的', r'E:\Files\Projects\TyTalk\test.wav')
