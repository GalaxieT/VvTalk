"""
生成praat脚本并执行：打开编辑窗口
"""
import os
from time import sleep
from praatio import pitch_and_intensity
import wave
from praatio import textgrid

SCRIPT_PATH = 'temp.praat'  # 需要保持在根目录，使得praat的工作目录与主程序一致

PRAAT_PATH = 'misc\\Praat-win64_vvTalk.exe'
PR_MIN_PITCH = 75
PR_MAX_PITCH = 500


def file_name(path, extension=False):
    name = ''
    if '\\' in path:
        name = path.split('\\')[-1]
    elif '/' in path:
        name = path.split('/')[-1]
    if extension:
        return name
    else:
        return name.split('.')[-2]


def make_script(wav_path: str, tg_path: str, new_tg: bool, reopen):
    wav_name = file_name(wav_path)
    tg_name = file_name(tg_path)
    if new_tg:
        get_tg = """To TextGrid: \"grid\", \"\"
        Save as text file: \"{tgPath}\"
        Rename: \"{tgName}\"""".format(tgPath=tg_path, tgName=tg_name)
    else:
        get_tg = 'Read from file: \"{}\"'.format(tg_path)
    if reopen:  # 之前格式有问题需要重新保存才能转换为praatio能读的格式，现在已经不需要
        reopen_txt = """
        selectObject: "TextGrid {tgName}"
        Save as text file: "{tgPath}"
        selectObject: "TextGrid {tgName}"
        Remove
        Read from file: "{tgPath}"
        """.format(tgName=tg_name, tgPath=tg_path)
    else:
        reopen_txt = ""

    script = """# 若没有自动进入编辑，点击菜单栏：Run → Run
# 编辑完成后请按下Continue保存并退出
Read from file: "{wavPath}"
{getTg}
{reopen}
selectObject: "Sound {wavName}"
plusObject: "TextGrid {tgName}"
View & Edit
pause 按下Continue保存并退出
selectObject: "TextGrid {tgName}"
Save as text file: "{tgPath}"
runSystem: "taskkill /f /t /im Praat-win64_vvTalk.exe"
    """.format(wavPath=wav_path, getTg=get_tg, reopen=reopen_txt, wavName=wav_name, tgName=tg_name, tgPath=tg_path)
    with open(SCRIPT_PATH, 'w', encoding='utf-8') as f:
        f.write(script)



def start_edit(wav_path: str, tg_path: str, new_tg: bool, reopen: bool):
    make_script(wav_path, tg_path, new_tg, reopen)
    # os.startfile(PRAAT_PATH)
    # sleep(.1)
    # os.system('taskkill /FI "WINDOWTITLE eq Praat Picture"')
    os.system('start {} {}'.format(PRAAT_PATH, SCRIPT_PATH))


class PraatScript:
    def __init__(self, id_name=None):
        """
        param id_name: 区分不同子进程下调用的praat, 主进程则为None
        """
        self.id_name = id_name
        if id_name is not None:
            self.TEMP_PATH = f'misc\\temp\\subprocess_{self.id_name}\\praat_temp\\'
        else:
            self.TEMP_PATH = 'misc\\temp\\praat_temp\\'
        self.PRTEMP_PI = self.TEMP_PATH + 'pitch_intensity.txt'
        self.PRTEMP_PI_CC = self.TEMP_PATH + 'pitch_intensity.txt'
        self.PRTEMP_I = self.TEMP_PATH + 'intensity.txt'
        if not os.path.exists(self.TEMP_PATH):
            os.makedirs(self.TEMP_PATH)

    def pitch_intensity(self, wav_path, frame_period, min_pitch=PR_MIN_PITCH, max_pitch=PR_MAX_PITCH):
        """

        :param wav_path: relative path
        :param frame_period:
        :param min_pitch:
        :param max_pitch:
        :return:
        """
        abs_fn = os.getcwd() + '\\' + wav_path
        abs_fn_prtemp = os.getcwd() + '\\' + self.PRTEMP_PI
        abs_fn_prtemp_cc = os.getcwd() + '\\' + self.PRTEMP_PI_CC
        abs_fn_praat = os.getcwd() + '\\' + PRAAT_PATH
        frame_period = frame_period / 1000

        # 参数设定：标准range

        pi_list = pitch_and_intensity.extractPI(abs_fn, abs_fn_prtemp, abs_fn_praat, min_pitch, max_pitch,
                                                sampleStep=frame_period, undefinedValue=0)
        # pitch_cc_list = pitch_and_intensity.extractPitch(abs_fn, abs_fn_prtemp_cc, abs_fn_praat, min_pitch, max_pitch,
        #                                                  sampleStep=frame_period, undefinedValue=0)
        #
        # for idx, pi in enumerate(pi_list):
        #     if pi[1] == 0:
        #         pi_list[idx] = (pi_list[idx][0], pitch_cc_list[idx][1], pi_list[idx][2])

        return pi_list

    def intensity(self, wav_path, frame_period):
        """

        :param wav_path: absolute path
        :param frame_period:
        :return:
        """
        abs_fn = wav_path
        abs_fn_prtemp = os.getcwd() + '\\' + self.PRTEMP_I
        abs_fn_praat = os.getcwd() + '\\' + PRAAT_PATH
        frame_period = frame_period / 1000
        i_list = pitch_and_intensity.extractIntensity(abs_fn, abs_fn_prtemp, abs_fn_praat, PR_MIN_PITCH,
                                                      sampleStep=frame_period,
                                                      undefinedValue=0)
        return [list(x) for x in i_list]  # [[second, dB]]


def create_seg_tg(wav_path, tg_path, texts: list, just_len=None):
    """
    var just_len: 不按text分长度，直接按这个数确定这一段有多少个py。用来在生成默认的seg tg时避免py与text没对齐
    """
    bias = 4
    with wave.open(wav_path, 'rb') as f:
        nframe = f.getnframes()
        rate = f.getframerate()
        wav_length = nframe / float(rate)  # second
    nums = []
    texts_with_num = []
    if just_len is None:
        for tx in texts:
            nums.append(len(tx))
            texts_with_num.append(f'{tx}_{len(tx)}_')
    else:
        text = ''.join(texts)
        nums.append(just_len)
        texts_with_num.append(f'{text}_{just_len}_')
    entry_list = []
    total_num_with_bias = sum(nums) + len(nums) * bias
    lengths = [wav_length * ((n + bias)/total_num_with_bias) for n in nums]
    last_bound = 0
    for i, text in enumerate(texts_with_num):
        entry_list.append((last_bound, last_bound+lengths[i], text))
        last_bound += lengths[i]
    tg = textgrid.Textgrid()
    tier = textgrid.IntervalTier('segment', entry_list)
    tg.addTier(tier)
    tg.save(tg_path, 'short_textgrid', False)


def get_seg_lengths(tg_path):
    full = os.path.abspath(tg_path)
    tg = textgrid.openTextgrid(full, includeEmptyIntervals=True)
    tier = tg.tierDict['segment']
    lengths = []
    for interval in tier.entryList:
        lengths.append(int(interval[2].split('_')[-2]))
    return lengths


if __name__ == '__main__':
    il = i_list = pitch_and_intensity.extractIntensity(r'D:\Files\OneDrive\pycharmfiles\TyTalk_Shuttle\resources'
                                                       r'\temp_Recording_1.wav', r'd:\tempIntens.txt', r'D:\Files\OneDrive'
                                                                                                   r'\pycharmfiles\TyTalk_Shuttle\misc\Praat-win64_TyTalk.exe',
                                                       PR_MIN_PITCH,
                                                       undefinedValue=0)

