import pyaudio
import wave
import threading as trd
import time
import struct
import numpy as np
# from praatio.audioio import extractSubwav



CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
# RECORD_SECONDS = 2
DEFAULT_OUTPUT_FILENAME = "speech.wav"


# 此处代码有参考
class Recorder:
    def __init__(self, of=DEFAULT_OUTPUT_FILENAME):
        self.rec_flag = False
        self.frames = []
        self.output_filename = of

    def _record(self):
        p = pyaudio.PyAudio()
        t1 = time.time()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)  # 耗很多时间
        self.rec_flag = True

        t2 = time.time()
        print('录音启动准备时长', t2-t1)

        print("开始录音")

        frames = self.frames

        # for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        #     data = stream.read(CHUNK)
        #     frames.append(data)
        while self.rec_flag:
            data = stream.read(CHUNK)
            frames.append(data)

        print("录音结束")

        stream.stop_stream()
        stream.close()
        p.terminate()


    def start(self):
        trd.Thread(target=self._record).start()

    def complete(self, ):  # 直接丢弃未完成的chunk
        wf = wave.open(self.output_filename, 'wb')
        wf.setnchannels(CHANNELS)
        p = pyaudio.PyAudio()
        wf.setsampwidth(p.get_sample_size(FORMAT))
        p.terminate()
        wf.setframerate(RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        self.abort()

    def abort(self):
        self.rec_flag = False
        self.frames.clear()
        if self.frames:
            self.abort()


# 部分代码参考自https://www.jianshu.com/p/d5f9077668fd
def to_one_channel_file(file_name, dest_name):
    with wave.open(file_name, 'rb') as wf:
        channel = wf.getnchannels()
        nframes = wf.getnframes()
        framerate = wf.getframerate()
        str_data = wf.readframes(nframes)
        sample_width = wf.getsampwidth()
    if channel != 2:
        if framerate == 16000:
            with open(file_name, 'rb') as f:
                data = f.read()
            with open(dest_name, 'wb') as f:
                f.write(data)
        else:
            # wf_out = wave.open(dest_name, 'wb')
            # wf_out.setnchannels(1)
            # wf_out.setframerate(16000)
            with open(file_name, 'rb') as f:
                data = f.read()
            with open(dest_name, 'wb') as f:
                f.write(data)
    else:
        # 将波形数据转换成数组
        wave_data = np.fromstring(str_data, dtype=np.short)
        wave_data.shape = (-1, 2)
        wave_data = wave_data.T
        mono_wave = (wave_data[0] + wave_data[1]) / 2
        wf_mono = wave.open(dest_name, 'wb')
        wf_mono.setnchannels(1)
        wf_mono.setframerate(framerate)
        wf_mono.setsampwidth(sample_width)
        timetotal = [0, 0]

        # 耗时长，约花费音频时长的10.5%的时间
        for i in mono_wave:
            data = struct.pack('<h', int(i))  # 3份时间
            wf_mono.writeframesraw(data)  # 8份时间
        wf_mono.close()
        # print(timetotal)

# The following methods conflict with pyinstaller
# from soundfile import write as sf_write
# from librosa import load as lr_load
# conflicts with pyinstaller, so it is out of use
# 参考：https://www.zhihu.com/question/434408504/answer/1623778090
def __cut(wav_path, dest_paths: list, ranges: list):
    """

    :param wav_path: str
    :param dest_paths: list
    :param ranges: (start second, end second)
    :return: None
    """
    assert len(dest_paths) == len(ranges)
    outs = []
    source_audio, sample_rate = lr_load(wav_path, sr=None)
    for range_ in ranges:
        start = int(range_[0] * sample_rate)
        end = int(range_[1] * sample_rate)
        out = source_audio[start:end]
        outs.append(out)

    for i, out in enumerate(outs):
        sf_write(dest_paths[i], out, sample_rate)

# out of use right now (only compatible for praatio version <= 4.5
'''
# Though the method extractSub... is in praatio, it is actually has nothing to do with praat, only to save coding time.
def cut(wav_path, dest_paths: list, ranges: list):
    """

    :param wav_path: str
    :param dest_paths: list
    :param ranges: (start second, end second)
    :return: None
    """
    assert len(dest_paths) == len(ranges)
    for i, range_ in enumerate(ranges):
        extractSubwav(wav_path, dest_paths[i], range_[0], range_[1])
'''


if __name__ == '__main__':
    r = Recorder()
    r.start()
    r.complete()
