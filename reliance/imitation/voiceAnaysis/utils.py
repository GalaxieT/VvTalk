import time
import numpy
from numpy import array, hanning, convolve, log2
# import numpy.random.common  # only for py36
# import numpy.random.bounded_integers  # only for py36
# import numpy.random.entropy  # 用于提示pyinstaller  # only for py36
from praatio.textgrid import openTextgrid
from os.path import abspath
from reliance.global_vars import *


base_note = 70  # default
base_freq = 440*2**((base_note-81)/12)

N_hanning = 60
bias = 0

least_jump_range = 2800 / (8192 / pbs)
fastest_pit_change = 500 / (8192 / pbs) / ms_per_dot
# pits (semitone) per ms. Practical data based on investigated rare facts (male, talk show, pbs=17):
# 5900 between 2dots, 5751 between 2dots, 7792 between 16dots (487), *3181 among 20dots (167), 5825-2dots (2913)
# not: *3934 among 3dots, 3316 between 2dots, 164
longest_incorrect_region = 500 / ms_per_dot  # unit: dots = ms / ms per dots

def get_pit(f: numpy.array, t, praat_move_back=False, smooth=True, cons_inf=None, timing=None, sil_ranges=None):  # return real pit range
    # TODO: 利用标注信息决定如何修正pit
    # f = 0 则pit返回None
    ttt = time.time()
    f0 = f.copy()
    # cons_ranges = []
    # if sil_ranges is None:
    #     sil_ranges = []
    # if cons_inf and timing is not None:
    #     for i, cons_len in enumerate(cons_inf[0]):
    #         if cons_len > 0:
    #             cons_ranges.append((timing[i][0], cons_len))


    # for i in range(len(f)):
    #     print(t[i], f[i])
    pits = log2((f0+0.001) / 440.0) * 12 + 81  # 单位：半音
    # for i in range(len(f)):
    #     print(t[i], pits[i])

    _ = []
    for i in pits:
        if i > 0:
            _.append(i)
    base_pit = array(_).mean()

    t = t * 1000
    t = t / ms_per_dot
    # print('tt1:', time.time()-ttt)
    ttt = time.time()

    t_accept = []
    pit_accept = []
    t_recent = [-1, -1]
    for i in range(len(t)): # 过滤掉时间重复的
        t_ = int(t[i] + 0.5)
        if t_ not in t_recent:
            t_recent.append(t_)
            t_recent.pop(0)
            t_accept.append(t_)
            if pits[i] < 0:  # f0==0 则 对应pit==None
                pit_ = None
            else:
                pit_ = pits[i] - base_pit
            pit_accept.append(pit_)
    t = array(t_accept)
    pits = array(pit_accept)
    # print('ttt2', time.time()-ttt)
    ttt = time.time()

    # 辅音和静音区域内f0调为0
    # for start, length in cons_ranges+sil_ranges:
    #     for i in range(length):
    #         pits[start+i] = 0
    if praat_move_back:
        tmb = time.time()
        pits = region_move_back(pits, t)
        print('move_back:', time.time()-tmb)


    # _, pits, t = smooth_pits_by_dots([(t[n], pit) for n, pit in enumerate(pits)])


        # print(len(t), len(pits))

    # 将None替换为0，作为列表元素输出
    pits_with_0 = []
    for p in pits:
        if p is None:
            pits_with_0.append(0)
        else:
            pits_with_0.append(p)
    return_list = [(int(t[i]), float(pits_with_0[i])) for i in range(len(t))]
    # print('ttt3', time.time()-ttt)
    return return_list, pits, t


def smooth_pits_by_dots(pits_by_dots):
    pits = numpy.array([item[1] for item in pits_by_dots])
    dots = numpy.array([item[0] for item in pits_by_dots])
    t = dots
    # 将x(即pit)序列中连续的0，转化为连接两侧一定宽度区域内音高的平均值（补充0对应的无效信息）.两侧三分之一和中间三分之一斜率不同以过渡。忽略起始与结尾的0
    def connect_parts(x: numpy.ndarray, r):
        initial = True
        zero_counting = False
        zero_idx = []
        start_idx = 0
        length_ratio = 1 / 3
        lessen_ratio = 0.5  # 前后三分之一，斜率为原有的0.5倍
        for i, value in enumerate(x):
            if zero_counting:
                if value == 0:
                    zero_idx.append(i)
                else:
                    if start_idx > r:
                        start_left = start_idx - r
                    else:
                        start_left = 0
                    start_mean = x[start_left:start_idx + 1].mean()
                    end_mean = x[i:i + r].mean()
                    total = end_mean - start_mean
                    medium_value_left = start_mean + total * length_ratio * lessen_ratio
                    medium_value_right = end_mean - total * length_ratio * lessen_ratio
                    total_len = len(zero_idx)
                    if total_len > 500:
                        length_ratio = 0.1
                    step = (end_mean - start_mean) / (total_len + 1)
                    lessened_step = step * lessen_ratio
                    center_step = (step * total_len - 2 * length_ratio * total_len * lessen_ratio * step) / (
                                total_len - 2 * length_ratio * total_len)
                    turning_point_l, turning_point_r = total_len // 3, 2 * total_len // 3

                    for i_, idx in enumerate(zero_idx[:turning_point_l]):
                        x[idx] = start_mean + lessened_step * (i_ + 1)

                    for i_, idx in enumerate(zero_idx[turning_point_l:turning_point_r]):
                        x[idx] = medium_value_left + center_step * (i_ + 1)

                    for i_, idx in enumerate(zero_idx[turning_point_r:]):
                        x[idx] = medium_value_right + lessened_step * (i_ + 1)

                    zero_counting = False
                    zero_idx.clear()
                    start_idx = i
            else:
                if value == 0:
                    if not initial:
                        zero_counting = True
                        zero_idx.append(i)
                else:
                    initial = False
                    start_idx = i

    connect_parts(pits, 5)
    # 避免结尾和开头0pit被平滑
    ending_zeroes = True
    ezeroes_count = 0
    sound_end_pit = 0
    while ending_zeroes:
        try:
            pit = pits[-(ezeroes_count + 1)]
        except IndexError:
            print('错误：结尾0pit回溯超出原有长度，一般是pit全为0')
            break
        if pit == 0:
            ezeroes_count += 1
        else:
            sound_end_pit = pit
            ending_zeroes = False
    for i in range(ezeroes_count):
        pits[-(i + 1)] = sound_end_pit

    starting_zeroes = True
    szeroes_count = 0
    sound_start_pit = 0
    while starting_zeroes:
        try:
            pit = pits[szeroes_count]
        except IndexError:
            print('错误：开头0pit回溯超出原有长度，一般是pit全为0')
            break
        if pit == 0:
            szeroes_count += 1
        else:
            sound_start_pit = pit
            starting_zeroes = False
    for i in range(szeroes_count):
        pits[i] = sound_start_pit

    hn_weights = hanning(N_hanning)
    pits_s = convolve(hn_weights / hn_weights.sum(), pits)[N_hanning - 1:-N_hanning + 1]
    pits = pits_s
    t = t[N_hanning - 1:]
    return [(t[n], pit) for n, pit in enumerate(pits)], pits, t


def smooth_with_time(arr, N):
    arr_main = [a[1] for a in arr]
    arr_t = [a[0] for a in arr]
    hn_weights = hanning(N)
    arr_ = convolve(hn_weights / hn_weights.sum(), arr_main)[N - 1:-N + 1]
    arr_t = arr_t[N - 1:]
    return [(int(arr_t[i]), float(arr_[i])) for i in range(len(arr_t))]



def get_timing(boundaries_inf):
    bias = boundaries_inf[0]
    boundaries = boundaries_inf[1:]
    timing = []
    for i, boundary in enumerate(boundaries):
        if boundary[1] == 'start':
            # print(boundaries)
            length = boundaries[i+1][0] - boundary[0]
            timing.append((round((boundary[0]*1000 + bias) / ms_per_dot) + N_hanning - 1, round(length*1000 / ms_per_dot)))
    return timing


# hanning_correct = round(12/45*N_hanning)  # 经验值
hanning_correct = N_hanning


def get_timing_py_praat(tg_name):
    """
    return:
        timing_cons_back: 后一个音的辅音含在前一个音的时长中
        timing_cons_front: 一个音的时长包含它自己的辅音和元音
    """
    timing_v_only = []
    texts = []
    sil_parts = []
    sil_lengths_dot = []
    timing_cons_front = []  # [(xmin, xmax),] in milliseconds
    consonant_lengths = []  # [(len, bool: attached_to_previous_vowel)]
    cons_length = 0
    intervals = openTextgrid(abspath(tg_name), False).tierDict['grid'].entryList

    cons_attached_to_pre = False
    for i, interval in enumerate(intervals):
        xmin = interval[0] * 1000
        xmin_dot = int(xmin / ms_per_dot + 0.5) + hanning_correct - 1
        xmax = interval[1] * 1000
        xmax_dot = int(xmax / ms_per_dot + 0.5) + hanning_correct - 1
        text = interval[2]
        # xmin_dot -= cons_length  # 使元音时长包含同音节的辅音时长
        dur = xmax_dot - xmin_dot
        is_vowel = True
        text = text.strip()
        if text and text[-1] == '5':
            text = text[:-1]+'0'
        if text == '-' or text == '1' or text == 'sil':
            sil_parts.append((xmin, xmax))
            sil_lengths_dot.append((xmin_dot, dur))
            is_vowel = False
        elif text == '=' or text == '2' or text == 'con':
            cons_length = dur
            is_vowel = False
        if is_vowel:
            consonant_lengths.append((cons_length, cons_attached_to_pre))
            cons_length = 0

            cons_next = False
            try:
                text_next = intervals[i+1][2]
                cons_next = text_next == '=' or text_next == '2' or text_next == 'con'
            except IndexError:
                pass
            timing_v_only.append((xmin_dot, dur, cons_next))

            cons_attached_to_pre = cons_next

            texts.append(text)
            timing_cons_front.append((xmin, xmax))

    timing_cons_back = []
    for i, item in enumerate(timing_v_only):
        if item[2]:
            dur = item[1] + consonant_lengths[i+1][0]
        else:
            dur = item[1]
        timing_cons_back.append((item[0], dur))

    py = texts
    return timing_cons_back, py, sil_parts, timing_cons_front, consonant_lengths, sil_lengths_dot


def _ms_to_dot(ms):
    # for internal use only because different projects may have different value of hanning_correct
    return int(ms / ms_per_dot + 0.5) + hanning_correct - 1


def region_move_back(pits, times):
    """
    Aiming to return a consecutive array (except for zeroes, which was ignored in the array), draw the region of
    values back to the normal level.
    :param pits: array like
    :param times: array like
    :return: a copy of manipulated x
    """
    pits = list(pits)
    times = tuple(times)
    max_rate = fastest_pit_change  # pit per ms

    def is_jump(x1, y1, x2, y2):
        dy = abs(y1-y2)
        if dy > least_jump_range:
            slope = (y2-y1) / (x2-x1)
        else:
            return False
        if abs(slope) > max_rate:
            return True
        else:
            return False

    # examine jumps between each point and the next one. Return the index of left and right sides of the jumps.
    def get_jumps():
        _jumps = []
        for i, p in enumerate(pits):
            try:
                p1, p2 = pits[i], pits[i+1]
                t1, t2 = times[i], times[i+1]
                if None not in (p1, p2) and is_jump(t1, p1, t2, p2):
                    _jumps.append((i, i+1))
            except IndexError:
                pass
        return _jumps

    # find all 0pit ("None", now actually) regions (index), return [(start, end),]，not ignoring initial and ending.
    def get_zero_regions(x):
        if not x:
            return []
        zero_regions = []
        cur_region = [0, 0]
        zero_before = False
        for i, value in enumerate(x):
            if value is None:
                if not zero_before:
                    cur_region[0] = i
                    zero_before = True
            else:
                if zero_before:
                    cur_region[1] = i-1
                    zero_regions.append(tuple(cur_region))
                    cur_region = [0, 0]
                zero_before = False
        if cur_region[0]:
            cur_region[1] = len(x)-1
            zero_regions.append(tuple(cur_region))
        # if zero_regions and zero_regions[0][0] == 0:
        #     del zero_regions[0]
        return zero_regions

    def pit0_is_jump(zr):
        # 两侧是jump
        # print('pij', zr)
        correctness = []
        for z_start, z_end in zr:
            try:
                start = z_start - 1
                end = z_end + 1
                if start < 0:
                    raise IndexError()
                p1, p2 = pits[start], pits[end]
                t1, t2 = times[start], times[end]
                correctness.append(is_jump(t1, p1, t2, p2))
                # print((t1, p1, t2, p2), is_jump(t1, p1, t2, p2))
            except IndexError:
                correctness.append(False)
        return correctness

    def to_region_list(et):
        # 一个region是由jump分隔的区域的端点元组的列表 [(区域左端点idx，区域右端点idx),]
        event_list = et
        region_list = []
        region = []
        section = [0, 0]
        # print('el: ', event_list)
        for event in event_list:
            if event[0] == 'interval':
                section[1] = event[1] - 1
                if region:
                    if section[0] != section[1]:
                        region.append(tuple(section))
                    if len(region) > 1:
                        region_list.append(region[:])
                    region.clear()
                section[0] = event[2] + 1
            if event[0] == 'jump':
                section[1] = event[1]
                if section[0] != section[1]:
                    region.append(tuple(section))
                section[0] = event[2]
        if region:
            section[1] = len(pits)-1
            if section[0] != section[1]:
                region.append(tuple(section))
            if len(region) > 1:
                region_list.append(region[:])
                region.clear()
        return region_list

    def wrong_sections_in_region(r):
        # r: region with sections in it. doubted list not working (referring to section_correct)
        inf = []
        wrong = []
        doubted = []
        for idx, section in enumerate(r):
            wrong.append(False)
            doubted.append(False)
            length = section[1]-section[0]
            pit_mean = numpy.mean(pits[section[0]:section[1]])
            inf.append((idx, length, pit_mean))
        max_len_idx = max(inf, key=lambda x: x[1])[0]
        farthest_pit_idx = max(inf, key=lambda x: abs(x[2]))[0]
        if len(r) == 3:  # 二夹一，大概率中间是错误音高
            if inf[1][1] < longest_incorrect_region:
                wrong[1] = True
                return wrong, doubted
        if len(r) == 2:  # 二选一，音高不正常的有可能是错误音高
            if inf[farthest_pit_idx][1] < longest_incorrect_region:
                wrong[farthest_pit_idx] = True
                doubted[farthest_pit_idx] = True
                return wrong, doubted
        if max_len_idx != farthest_pit_idx:  # 两个判断标准都符合，则大概率是正确音高
            correct_base = max_len_idx
            m = correct_base % 2
            for idx, inf_ in enumerate(inf):
                if idx % 2 != m and inf_[1] < longest_incorrect_region:
                    wrong[idx] = True
        else:  # 不符合，可能性降低
            correct_base = max_len_idx
            m = correct_base % 2
            for idx, inf_ in enumerate(inf):
                if idx % 2 != m and inf_[1] < longest_incorrect_region:
                    wrong[idx] = True
                    doubted[idx] = True

        return wrong, doubted

    def section_correct(r, aim_i, doubted: bool, to_zero=False):
        def get_k(i0, i1, side):  # side: the location relative to the aim section
            # print(r)
            assert i1 > i0
            k = 0
            if side == 'left':
                ref_point = [i1, pits[i1]]
                if i1-i0 > 2:
                    p1 = (pits[i1-2] + pits[i1-3]) / 2
                    p2 = (pits[i1] + pits[i1-1]) / 2
                    k = (p2 - p1) / 2
                    ref_point = [i1-1.5, (p1+p2)/2]
                elif i1-i0 == 2:
                    p1 = (pits[i1 - 2] + pits[i1 - 1]) / 2
                    p2 = (pits[i1] + pits[i1 - 1]) / 2
                    k = p2 - p1
                    ref_point = [i1-1, (p1+p2)/2]
                elif i1-i0 == 1:
                    k = pits[i1] - pits[i1 - 1]
                    ref_point = [i1-0.5, (pits[i1] + pits[i1 - 1])/2]
                elif i1-i0 == 0:
                    k = 0
                    ref_point = [i1, pits[i1]]
            elif side == 'right':
                ref_point = [i0, pits[i0]]
                if i1-i0 > 2:
                    p2 = (pits[i0+2] + pits[i0+3]) / 2
                    p1 = (pits[i0] + pits[i0+1]) / 2
                    k = (p2 - p1) / 2
                    ref_point = [i0+1.5, (p1+p2)/2]
                elif i1-i0 == 2:
                    p2 = (pits[i0 + 2] + pits[i0 + 1]) / 2
                    p1 = (pits[i0] + pits[i0 + 1]) / 2
                    k = p2 - p1
                    ref_point = [i0+1, (p1+p2)/2]
                elif i1-i0 == 1:
                    k = pits[i0 + 1] - pits[i0]
                    ref_point = [i0+0.5, (pits[i0] + pits[i0 + 1])/2]
                elif i1-i0 == 0:
                    k = 0
                    ref_point = [i0, pits[i0]]
            return k, ref_point

        aim_sect = r[aim_i]
        if not to_zero:
            try:
                left_ref = r[aim_i-1]
            except IndexError:
                left_ref = None
            try:
                right_ref = r[aim_i+1]
            except IndexError:
                right_ref = None
            if left_ref and right_ref:  # 两个k预测adjust，取两个adjust的距离加权均值
                left_d = aim_sect[0] - left_ref[1]
                right_d = right_ref[0] - aim_sect[1]

                k_l, rp_l = get_k(left_ref[0], left_ref[1], 'left')
                aim_pit = rp_l[1] + k_l * (aim_sect[0] - rp_l[0])
                # aim_pit = pits[left_ref[1]]
                adjustment_l = aim_pit - pits[aim_sect[0]]

                k_r, rp_r = get_k(right_ref[0], right_ref[1], 'right')
                aim_pit = rp_r[1] + k_r * (aim_sect[1] - rp_r[0])
                # aim_pit = pits[right_ref[0]]
                adjustment_r = aim_pit - pits[aim_sect[1]]

                w_l, w_r = 1/(5+left_d), 1/(5+right_d)  # weights
                s = w_l + w_r
                dif = adjustment_r - adjustment_l
                adjustment = adjustment_l + dif*(w_r/s)
                # adjustment = adjustment_l
            elif left_ref:
                k, rp = get_k(left_ref[0], left_ref[1], 'left')
                aim_pit = rp[1] + k * (aim_sect[0] - rp[0])
                # aim_pit = pits[left_ref[1]]
                adjustment = aim_pit - pits[aim_sect[0]]
            elif right_ref:
                k, rp = get_k(right_ref[0], right_ref[1], 'right')
                aim_pit = rp[1] + k * (aim_sect[0] - rp[0])
                # aim_pit = pits[right_ref[0]]
                adjustment = aim_pit - pits[aim_sect[1]]
            else:
                adjustment = 0
            if doubted:
                # adjustment /= 2
                pass
            # print(aim_sect, adjustment)
            for j in range(aim_sect[0], aim_sect[1]+1):  # +2? 说明之前有索引不严谨的地方
                pits[j] = pits[j] + adjustment
        else:
            for j in range(aim_sect[0], aim_sect[1]+1):  # +2? 说明之前有索引不严谨的地方
                pits[j] = None

    jumps = get_jumps()
    z_regions = get_zero_regions(pits)
    zr_jump = pit0_is_jump(z_regions)

    event_track = [('jump', i1, i2) for i1, i2 in jumps]
    for i, boo in enumerate(zr_jump):
        if boo:
            try:
                event_track.append(('jump', z_regions[i][0]-1, z_regions[i][1]+1))
            except IndexError as e:
                print(e)
        else:
            try:
                event_track.append(('interval', z_regions[i][0], z_regions[i][1]))
            except IndexError as e:
                print(e)
    event_track.sort(key=lambda event: event[1])
    region_list = to_region_list(event_track)
    # print('rl:', region_list)
    for region in region_list:
        correctness_list, doubted_list = wrong_sections_in_region(region)
        # print(region, correctness_list)
        for j, section in enumerate(region):
            if correctness_list[j]:
                if j:  # 不是第一个
                    if not correctness_list[j-1]:
                        left_ref = [region[j - 1]]
                        aim_sec_idx = 1
                    else:
                        left_ref = []
                        aim_sec_idx = 0
                else:
                    left_ref = []
                    aim_sec_idx = 0
                try:
                    if not correctness_list[j+1]:
                        right_ref = [region[j + 1]]
                    else:
                        right_ref = []
                except IndexError:
                    right_ref = []
                section_correct(left_ref+[section]+right_ref, aim_sec_idx, doubted_list[j])

    return array(pits)
