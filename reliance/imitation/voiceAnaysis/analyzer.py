"""
TODO: 区分辅音、静音（间隔），并把辅音输出 完成，待修改
问题：整体未对齐（timing滞后于pit），辅音控制此暴露问题，已解决
静音pit平滑问题
部分辅音不适合控制，导致
注意，标注需要以元音为准！
"""
import time

import reliance.global_vars
from reliance.imitation.voiceAnaysis import utils
import pyworld as pw
import soundfile as sf
from pydub import AudioSegment
from pydub.silence import detect_silence  # these pydub functions are not relevant with ffmpeg
from reliance.imitation.praatDealer import PraatScript
from numpy import array


def dyn_correct(raw_wav_fn, aim_array, initial=1):  # 大约有两秒的提前,一节 4 beats
    weight = 0.9
    upWeight = 0.6
    topWeight = 0.1

    def get_rough_dyn(diff):
        raw = 10**(diff/20) * 64
        raw = (raw - 64) * weight + 64
        if raw > 64:
            raw = (raw - 64) * upWeight + 64
        if raw > 96:
            raw = (raw - 96) * topWeight + 96
        if raw > 127:
            raw = 127
        elif raw < 0:
            raw = 0
        return raw
    it_list = PraatScript().intensity(raw_wav_fn, utils.ms_per_dot)
    aim_array = list(aim_array)
    # print(it_list)

    beginning = reliance.global_vars.beginning_dots
    del it_list[:beginning]

    for i, it in enumerate(it_list):
        if it[1] < 0:
            it_list[i][1] = 0
    for i, it in enumerate(aim_array):
        if it < 0:
            aim_array[i] = 0

    lowest_sound = 30

    valid_raw = [raw_unit[1] for raw_unit in it_list if raw_unit[1] > lowest_sound]
    mean_raw = float(array(valid_raw).mean())

    valid_aim = [aim_unit for aim_unit in aim_array if aim_unit > lowest_sound]
    mean_aim = float(array(valid_aim).mean())

    if mean_aim < lowest_sound or mean_raw < lowest_sound:
        lowest_sound = 0

    raw_base = abs(mean_raw-lowest_sound)
    aim_base = abs(mean_aim-lowest_sound)
    it_list = [(int(it[0] * 1000 / utils.ms_per_dot - beginning + 1), it[1] / raw_base) for it in it_list]
    aim_array = [it / aim_base for it in aim_array]

    dyn_list = []
    last_t = -1
    for i, it_inf in enumerate(it_list):
        try:
            itn_aim = aim_array[i]
            cur_t = it_inf[0]
            if cur_t == last_t:
                continue
            if it_inf[1]:
                db_ratio_diff = itn_aim - it_inf[1]
                # print(db_ratio_diff)
                # weight = min(abs(db_ratio_diff), 1)
                db_diff = raw_base * db_ratio_diff
                dyn = int(get_rough_dyn(db_diff))
            else:
                dyn = 64
            dyn_list.append((it_inf[0], dyn))
            last_t = cur_t
        except IndexError:
            pass
    # print(dyn_list)
    dyn_list = utils.smooth_with_time(dyn_list, 20)
    return dyn_list


def smooth(dot_pit_array):
    return utils.smooth_pits_by_dots(dot_pit_array)[0]


class vtalker:
    def __init__(self, id_name=None):
        self.boundaries_inf = []
        self.textgrid_name = None
        self.auto_tg_name = None

        self.id_name = id_name

    def get_result(self, WAVpath, source=1, method=0, consonant_control=False):
        """

        :param WAVpath:
        :param source: auto_praat, manual_praat, or simple_annotation(has been aborted)
        :param method: 'praat' or 'pyworld'
        :param consonant_control: 是否从pit分析中直接预测辅音
        :return:
        """
        ps = PraatScript(self.id_name)
        its = None
        if method == 'pyworld' or method == 1:
            # raise ValueError
            x, fs = sf.read(WAVpath)
            f0, t = pw.dio(x, fs, frame_period=utils.ms_per_dot, allowed_range=0.17)  # t: seconds (numpy)
            if consonant_control:
                f0_cons, t_ = pw.dio(x, fs, frame_period=utils.ms_per_dot, allowed_range=0.04)

            pits = utils.get_pit(f0, t, praat_move_back=False)[0]

        elif method == 'praat' or method == 2:
            t, f0, its = [], [], []
            pr_result = ps.pitch_intensity(WAVpath, utils.ms_per_dot)
            for point in pr_result:
                t.append(point[0])
                f0.append(point[1])
                its.append(point[2])
            t = array(t)
            f0 = f0_cons = array(f0)
            its = array(its)

            pits = utils.get_pit(f0, t, praat_move_back=True)[0]

        elif method == 'mix' or method == 0:
            st = time.time()
            x, fs = sf.read(WAVpath)
            f0_pw, t_pw = pw.dio(x, fs, frame_period=utils.ms_per_dot, allowed_range=0.17)  # t: seconds (numpy)
            if consonant_control:
                f0_cons, t_ = pw.dio(x, fs, frame_period=utils.ms_per_dot, allowed_range=0.04)

            t_pr, f0_pr, its = [], [], []
            pr_result = ps.pitch_intensity(WAVpath, utils.ms_per_dot)
            for point in pr_result:
                t_pr.append(point[0])
                f0_pr.append(point[1])
                its.append(point[2])

            t_pr = array(t_pr)
            f0_pr = array(f0_pr)

            _, pits_pw, t_pw = tuple(utils.get_pit(f0_pw, t_pw, praat_move_back=False))  # [(t, pits)]
            _, pits_pr, t_pr = tuple(utils.get_pit(f0_pr, t_pr, praat_move_back=True))  # [(t, pits)]
            print('get_pit:', time.time()-st)
            st = time.time()
            f0_pw = pits_pw
            f0_pr = pits_pr

            means_dup = []
            f0_pr_valid = [x for x in f0_pr if x is not None]
            f0_pw_valid = [x for x in f0_pw if x is not None]

            f0_pr_mean = array(f0_pr_valid).mean()
            f0_pw_mean = array(f0_pw_valid).mean()
            for i, f0w in enumerate(f0_pw):
                if f0w is not None:
                    f0_pw[i] = f0w - f0_pw_mean + f0_pr_mean
            print('pre-mix:', time.time()-st)
            pw_weight = 0.7
            pr_weight = 1-pw_weight
            ttt = time.time()
            if len(f0_pw) < len(f0_pr):  # 目的是按个数少的那个算
                for i in range(len(f0_pw)):
                    if f0_pr[i] and f0_pw[i]:  # 如果此时praat和pw都有识别结果
                        means_dup.append(((f0_pw[i]*pw_weight+f0_pr[i]*pr_weight), (t_pw[i]*pw_weight+t_pr[i]*pr_weight)))
                    elif f0_pw[i]:  # 如果此时pw有结果
                        means_dup.append(((f0_pw[i]*pw_weight+f0_pr_mean*pr_weight), (t_pw[i]*pw_weight + t_pr[i]*pr_weight)))
                    elif f0_pr[i]:  # 如果此时pr有结果
                        means_dup.append(((f0_pr[i]*pr_weight+f0_pw_mean*pw_weight), (t_pw[i]*pw_weight + t_pr[i]*pr_weight)))
                    else:
                        means_dup.append((0, (t_pw[i]*pw_weight + t_pr[i]*pr_weight)))
            else:
                for i in range(len(f0_pr)):
                    if f0_pr[i] and f0_pw[i]:  # 如果此时praat有识别结果
                        means_dup.append(((f0_pw[i]*pw_weight+f0_pr[i]*pr_weight), (t_pw[i]*pw_weight+t_pr[i]*pr_weight)))
                    elif f0_pw[i]:  # 如果此时pw有结果
                        means_dup.append(((f0_pw[i]*pw_weight+f0_pr_mean*pr_weight), (t_pw[i]*pw_weight + t_pr[i]*pr_weight)))
                    elif f0_pr[i]:  # 如果此时pr有结果
                        means_dup.append(((f0_pr[i]*pr_weight+f0_pw_mean*pw_weight), (t_pw[i]*pw_weight + t_pr[i]*pr_weight)))
                    else:
                        means_dup.append((0, (t_pw[i]*pw_weight + t_pr[i]*pr_weight)))
            dur = time.time()-ttt
            print('mix:', dur)
            means_dup.sort(key=lambda x: x[1])

            # 去重
            cur_t = None
            means = []
            if means_dup:
                cur_t = means_dup[0][1]
                means.append(means_dup[0])
            for mean in means_dup[1:]:
                if mean[1] != cur_t:
                    means.append(mean)
                    cur_t = mean[1]
            f0 = array([x[0] for x in means])
            t = array([x[1] for x in means])

            # f0 = array([x[0] for x in means_dup])
            # t = array([x[1] for x in means_dup])

            pits = [(t[i], f0[i]) for i in range(len(f0))]

            its = array(its)

        # timing
        # [print(round(f[1], 2),round(t[f[0]], 3), end=' || ') for f in enumerate(f0_cons)]
        # c = pw.d4c()
        # f0 = pw.stonemask(x, f0, t, fs)
        py = None
        consonant_inf = None  # None or ([cons_lengths], 'manual'/'auto')
        if source == 1 or source == 0:  # praat标注自动或手动, 现在都是1
            # if source == 0:
            #     result = utils.get_timing_py_praat(self.auto_tg_name)
            # else:
            result = utils.get_timing_py_praat(self.textgrid_name)
            timing = result[0]
            py = result[1]
            cons_list_manual = result[4]
            cons_manual = False
            for n in cons_list_manual:
                if n:
                    cons_manual = True
                    break

            def auto_get_consonant_len():
                sil_marks = result[2]
                a_seg = AudioSegment.from_wav(WAVpath)
                back_noise = -60  # default
                if sil_marks:
                    silences = a_seg[sil_marks[0][0]: sil_marks[0][1]]
                    for sil_mark in sil_marks[1:]:
                        silences = silences + a_seg[sil_mark[0]: sil_mark[1]]
                    db = silences.dBFS
                    if db != -float("infinity"):
                        back_noise = db
                        # print(back_noise)
                s_list = detect_silence(a_seg, min_silence_len=30, silence_thresh=back_noise * 0.85, seek_step=1)

                def zeroes(s, least=0.05, error=0.5):
                    """
                    找到一段数列中，第一组成串的0
                    :param s: 数列
                    :param least: 0串占总长度最少的比例
                    :param error: 容许开头存在非零数据占总长度的比例
                    :return: 符合条件的第一段零数据(含error)的个数
                    """
                    max_error = round(len(s) * error)
                    error_count = 0
                    least_zero = round(len(s) * least)
                    zero_count = 0
                    for i, n in enumerate(s):
                        if n == 0:
                            zero_count += 1
                        else:
                            if zero_count >= least_zero:
                                return zero_count + error_count
                            elif i+1 > max_error:
                                return 0
                            else:
                                error_count = i+1
                                zero_count = 0
                    return zero_count + error_count

                def nearest_index(lis: list, des: float):  # slightly higher index
                    if des in lis:
                        return lis.index(des)
                    else:
                        mix = sorted(lis + [des])
                        return mix.index(des)

                note_boundaries = result[3]
                note_f0_boundaries = []
                t_list = list(t)
                for note_b in note_boundaries:
                    start_timing = note_b[0] / 1000
                    end_timing = note_b[1] / 1000
                    mid = sorted(t_list+[start_timing, end_timing])
                    start_idx = mid.index(start_timing)
                    end_idx = mid.index(end_timing) - 2
                    if start_idx >= end_idx:
                        continue
                    note_f0_boundaries.append((start_idx, end_idx))

                cons_inf = []
                for nfb in note_f0_boundaries:
                    z_num = zeroes(f0_cons[nfb[0]:nfb[1]])
                    # print(z_num, nfb)
                    cons_end = nfb[0] + z_num - 1
                    cons_inf.append((nfb[0], cons_end))
                # print(cons_inf, 'ci')
                cons_result = []
                for i, cons in enumerate(cons_inf):
                    start_t_ms = t[cons[0]] * 1000
                    end_t_ms = t[cons[1]] * 1000
                    latest_sil_end = 0
                    condition = 'unchanged'
                    for s_region in s_list:
                        if s_region[0] <= end_t_ms <= s_region[1]:  # 0基频后端点位于静音区间内
                            condition = 'invalid'
                            break
                        if start_t_ms <= s_region[1] <= end_t_ms:  # 0基频区间内存在静音后端点
                            latest_sil_end = max(s_region[1], latest_sil_end)
                            condition = 'shortened'
                    # print(condition)
                    if condition == 'invalid':
                        cons_result.append(0)
                    elif condition == 'shortened':
                        # 修正音符起始，统一到辅音起始处
                        new_start = utils._ms_to_dot(latest_sil_end)
                        shortened = new_start - timing[i][0]
                        timing[i] = (new_start, timing[i][1] - shortened)
                        cons_result.append(cons[1] - nearest_index(t_list, latest_sil_end / 1000))
                    elif condition == 'unchanged':
                        cons_result.append(utils._ms_to_dot(end_t_ms) - utils._ms_to_dot(start_t_ms))
                    else:
                        cons_result.append(0)
                        print("错误: 辅音识别中，f0与响度分析出现问题")

                note_dots = [nfb[1]-nfb[0] for nfb in note_f0_boundaries]

                for i, cr in enumerate(cons_result):  # 规则限制
                    if cr > 0:
                        ratio = cr / note_dots[i]
                        if ratio < 0.2:
                            cons_result[i] = round(note_dots[i] * 0.2)
                        if ratio > 0.4:
                            cons_result[i] = round(note_dots[i] * 0.4)

                return cons_result
            if cons_manual:
                consonant_inf = (cons_list_manual, 'manual')
            elif consonant_control and not cons_manual:
                consonant_lengths = auto_get_consonant_len()
                # print(consonant_lengths)
                consonant_inf = (consonant_lengths, 'auto')
            # pits = tuple(utils.get_pit(f0, t, cons_inf=consonant_inf, timing=timing, sil_ranges=result[5]))  # [(t, pits)]

        # aborted function from simple annotation
        elif source == 2:
            timing = tuple(utils.get_timing(self.boundaries_inf))
            pits = tuple(utils.get_pit(f0, t)[0])
        else:
            timing = ()
            pits = tuple(utils.get_pit(f0, t)[0])

        tsm = time.time()
        pits = smooth(pits)
        print('smooth:', time.time()-tsm)

        timing = tuple(timing)
        if its is not None:
            its = tuple(its.tolist())

        return timing, pits, py, consonant_inf, its
