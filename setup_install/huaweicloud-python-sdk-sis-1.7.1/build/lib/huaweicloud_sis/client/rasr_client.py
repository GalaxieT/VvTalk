# -*- coding: utf-8 -*-

import websocket
from huaweicloud_sis.utils.logger_utils import logger
from huaweicloud_sis.auth import token_service
from huaweicloud_sis.exception.exceptions import ClientException
from huaweicloud_sis.bean.callback import RasrCallBack
from huaweicloud_sis.bean.sis_config import SisConfig
import ssl
from huaweicloud_sis.bean.rasr_request import RasrRequest
from huaweicloud_sis.bean.asr_request import SasrWebsocketRequest
from huaweicloud_sis.auth import aksk_service
import json
import time
import threading

user_dict = dict()
time_dict = dict()

connect_sleep_time = 0.01


class RasrClient:
    """ 实时语音识别client """

    def __init__(self, user_name=None, password=None, domain_name=None, region=None, project_id=None, callback=None,
                 config=SisConfig(), service_endpoint=None, token_url=None, retry_sleep_time=1,
                 ak=None, sk=None, use_aksk=False):
        """
            实时语音识别client初始化。 推荐使用ak、sk认证方式。
        :param user_name:           用户名，当use_aksk为false生效.
        :param password:            密码，当use_aksk为false生效
        :param domain_name:         账户名，一般等同用户名，当use_aksk为false生效
        :param region:              区域，如cn-north-4
        :param project_id:          项目ID，可参考https://support.huaweicloud.com/api-sis/sis_03_0008.html
        :param callback:            回调类RasrCallBack，用于监听websocket连接、响应、断开、错误等
        :param service_endpoint:    终端节点，一般使用默认即可
        :param token_url:           请求token的url，一般使用默认即可
        :param retry_sleep_time:    当websocket连接失败重试的间隔时间，默认为1s
        :param ak                   ak, 当 use_aksk为true生效。
        :param sk                   sk, 当 use_aksk为true生效。
        :param use_aksk             是否使用ak sk认证，为true表示选择ak sk认证。为false表示使用token认证。
        """
        if service_endpoint is None:
            self._service_endpoint = 'wss://sis-ext.' + region + '.myhuaweicloud.com'
        else:
            self._service_endpoint = service_endpoint
        if not isinstance(callback, RasrCallBack):
            logger.error('The parameter callback must be RasrCallBack class')
            raise ClientException('The parameter callback must be RasrCallBack class')
        if not isinstance(config, SisConfig):
            logger.error('The parameter config must by SisConfig class')
            raise ClientException('The parameter config must by SisConfig class')

        self._region = region
        self._project_id = project_id
        self._config = config
        self._callback = callback
        self._status = 'pre_start'
        self._request = None
        self._retry_sleep_time = retry_sleep_time

        self._use_aksk = use_aksk
        if use_aksk:
            if ak is None or sk is None:
                logger.error('you choose aksk authentication, ak or sk is empty, please fill in it')
                raise ClientException('ak or sk is empty, please fill in it')
            self._ak = ak
            self._sk = sk
        else:
            if user_name is None or password is None or domain_name is None:
                logger.error('you choose token authentication, username or password or domain name is empty, '
                             'please fill in it')
                raise ClientException('username or password or domain name is empty, please fill in it')
            self._token = self._get_token(user_name, password, domain_name, token_url)


        # 此变量正常情况下永远为False。除非依赖库websocket-cliet变更，不再自动添加header
        # 1. websocket的库会在请求头部自动添加host信息。而且websocket库的header格式为tuple，即 ['key1:val1', 'key2:val2']
        # 2. apig加密的header也包含host信息。
        # 3. 当将apig加密后的header放在websocket请求中，会形成两个host信息，且无法覆盖。导致无法通过apig鉴权，报错401。
        # 4. 将其设置为false，可以屏蔽apig加密header里的host信息，最终形成header只有一个host，可通过鉴权。
        self._show_host_header = False

    def _connect(self, url):
        def _check_result(result):
            result_str = json.dumps(result)
            if 'error_code' in result and 'error_msg' in result:
                logger.error(result_str)
                # 睡眠2s保证关闭前，发送端有充足时间收到关闭请求。
                self._status = 'close'
                self._callback.on_error(result_str)
                time.sleep(2)
                self._ws.close()
                raise ClientException(result_str)
            if 'resp_type' not in result:
                self._status == 'error'
                error_msg = 'result doesn\'t contain key resp, result is %s' % result_str
                logger.error(error_msg)
                self._callback.on_error(error_msg)
                raise ClientException(error_msg)

        def _on_open(ws):
            logger.info('websocket open')
            self._status = 'connect'
            self._callback.on_open()

        def _on_message(ws, message):
            result = json.loads(message)
            _check_result(result)
            result_type = result['resp_type']
            trace_id = result['trace_id']
            if result_type == 'START':
                self._callback.on_start('trace id is %s' % trace_id)
            elif result_type == 'EVENT':
                event = result['event']
                if event is None or event == '':
                    logger.error("empty event is invalid")
                    return
                self._callback.on_event(event)
                if event == 'EXCEEDED_AUDIO':
                    logger.warn('the duration of the audio is too long, the rest won\'t be recognized')
                    self._status = 'end'
                    self._callback.on_end('the duration of the audio is too long, the rest won\'t be recognized')
                elif event == 'EXCEEDED_SILENCE':
                    logger.error('silent time is too long, the audio won\'t be recognized')
                    self._callback.on_error('silent time is too long, the audio won\'t be recognized')
                    self._status = 'error'
                elif event == 'VOICE_END':
                    logger.warn('detect voice end, the rest won\'t be recognized')
                    self._status = 'end'
                    self._callback.on_end('detect voice end, the rest won\'t be recognized')
            elif result_type == 'RESULT':
                self._callback.on_response(result)
            elif result_type == 'END':
                self._status = 'end'
                self._callback.on_end('trace id is %s' % trace_id)
            else:
                logger.error('%s don\'t belong to any type' % result_type)

        def _on_close(ws, close_status_code='1000', close_msg='close'):
            logger.info('websocket close')
            self._status = 'close'
            self._callback.on_close()

        def _on_error(ws, error):
            logger.error(error)
            self._status = 'error'
            self._callback.on_error(error)
        if self._config.get_certificate_check():
            sslopt = None
        else:
            sslopt = {"cert_reqs": ssl.CERT_NONE}
        headers = self._get_headers(url)
        retry_count = 5
        for i in range(retry_count):
            self._status = 'pre_start'
            self._ws = websocket.WebSocketApp(url, headers, on_open=_on_open, on_close=_on_close,
                                              on_message=_on_message, on_error=_on_error)

            self._thread = threading.Thread(target=self._ws.run_forever,
                                            args=(None, sslopt, self._config.get_connect_lost_timeout() + 10,
                                                  self._config.get_connect_lost_timeout()))
            self._thread.daemon = True
            self._thread.start()

            connect_count = int(self._config.get_connect_timeout() / connect_sleep_time)
            for j in range(connect_count):
                if self._status != 'pre_start':
                    break
                else:
                    time.sleep(connect_sleep_time)
            if self._status == 'start' or self._status == 'connect':
                break
            else:
                logger.error('connect meets error, it will retry %d times, now it is %d' % (retry_count, i + 1))
            time.sleep(self._retry_sleep_time)
        if self._status == 'pre_start' or self._status == 'close' or self._status == 'error' or self._status == 'end':
            logger.error('websocket connect failed， url is %s' % url)
            raise ClientException('websocket connect failed， url is %s' % url)

    def sentence_stream_connect(self, request):
        """
            实时语音识别单句模式
        :param request: 实时语音识别请求
        :return: -
        """
        self._check_request(request)
        self._request = request
        url = self._service_endpoint + '/v1/' + self._project_id + '/rasr/sentence-stream'
        self._connect(url)

    def sasr_stream_connect(self, request):
        self._check_sasr_request(request)
        self._request = request
        url = self._service_endpoint + '/v1/' + self._project_id + '/asr/short-audio'
        self._connect(url)

    def continue_stream_connect(self, request):
        """
            实时语音识别连续模式
        :param request:  实时语音识别请求
        :return: -
        """
        self._check_request(request)
        self._request = request
        url = self._service_endpoint + '/v1/' + self._project_id + '/rasr/continue-stream'
        self._connect(url)

    def short_stream_connect(self, request):
        """
            流式一句话模式
        :param request: 实时语音识别请求
        :return:  -
        """
        self._check_request(request)
        self._request = request
        url = self._service_endpoint + '/v1/' + self._project_id + '/rasr/short-stream'
        self._connect(url)

    def send_start(self):
        """ 发送开始请求，在发送音频前一定要进行这一步，将参数配置发送给服务端 """
        message = json.dumps(self._request.construct_params())
        self._ws.send(message, opcode=websocket.ABNF.OPCODE_TEXT)

    def send_audio(self, data, byte_len=4000, sleep_time=0.06):
        """
            发送音频，按照分片发送，byte_len表示分片大小，sleep_time表示每次发送分片的睡眠时间。
        :param data:        需要发送的数据
        :param byte_len:    分片大小，建议[2000, 20000],不宜太小或太大
        :param sleep_time:  每次发送分片后的睡眠时间。
        :return: -
        """
        now_index = 0
        while now_index < len(data):
            if self._status == 'error' or self._status == 'close':
                break
            next_index = now_index + byte_len
            if next_index > len(data):
                next_index = len(data)
            send_array = data[now_index: next_index]
            self._ws.send(send_array, opcode=websocket.ABNF.OPCODE_BINARY)
            now_index += byte_len
            time.sleep(sleep_time)

    def send_end(self):
        """ 发送结束请求，告诉服务端已不需要发送任何音频 """
        message = '{"command": "END", "cancel": "false"}'
        if self._status != 'error' and self._status != 'close':
            self._ws.send(message, opcode=websocket.ABNF.OPCODE_TEXT)

    def close(self):
        """ 发送结束请求后，一定要进行这一步。否则服务端超过20s没有收到数据会自动断开，并报异常 """
        count = 0  # 20s
        while self._status != 'end' and count < 180:
            time.sleep(0.1)
            count += 1
            if self._status == 'error' or self._status == 'close':
                break
        if self._thread and self._thread.is_alive():
            self._ws.keep_running = False
            self._thread.join()
        self._ws.close()

    def _set_host_header(self, show_host_header):
        """
            正常可访问情况下，永远不要调用这个接口。默认屏蔽，除非依赖库websocket-client变更，不再自动添加header中的host信息。
        :return:
        """
        self._show_host_header = show_host_header


    @staticmethod
    def _check_request(request):
        if not isinstance(request, RasrRequest):
            error_msg = 'The parameter of request in RasrClient should be RasrRequest class'
            logger.error(error_msg)
            raise ClientException(error_msg)

    @staticmethod
    def _check_sasr_request(request):
        if not isinstance(request, SasrWebsocketRequest):
            error_msg = 'The parameter of request  should be SasrWebsocketRequest class'
            logger.error(error_msg)
            raise ClientException(error_msg)

    def _get_headers(self, url):
        if self._use_aksk:
            if not url.startswith('ws'):
                logger.error('%s is invalid' % url)
                raise ClientException('%s is invalid' % url)
            new_url = 'http' + url[2:]
            headers = aksk_service.get_signed_headers(self._ak, self._sk, new_url, None, None, 'GET')
            if 'host' in headers and not self._show_host_header:
                del headers['host']
        else:
            headers = {'X-Auth-Token': self._token}
        return headers

    def _get_token(self, user_name, password, domain_name, token_url):
        if self._use_aksk:
            return None
        if token_url is None:
            token_url = 'https://iam.' + self._region + '.myhuaweicloud.com/v3/auth/tokens'
        # token 缓存必须在client进行，才可以在多线程中生效。
        now_time = time.time()
        token = None
        if user_name in user_dict and user_name in time_dict:
            temp_token = user_dict[user_name]
            save_time = time_dict[user_name]
            if now_time - save_time < 5 * 3600:
                logger.info('use token cache')
                token = temp_token
        if token is None:
            token = token_service.get_token(user_name, password, domain_name, self._region,
                                            url=token_url, config=self._config)
            user_dict[user_name] = token
            time_dict[user_name] = now_time
        return token
