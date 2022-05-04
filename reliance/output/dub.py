import pysrt as p
from reliance.global_vars import dot_to_ms, beginning_ms
from reliance.tyTalk.talker import Talker
import re
from collections import Counter



sep = '?？!！,，。;；:：\s'
def split_and_align(text, py):
    """
    main中，timing信息本就不包括sil
    --> texts and their corresponding index in the py list including sil, end idx included
    """
    t = Talker()
    py_ref = [re.sub('[01234?]', '', p) for p in py]
    py_ref_nosil = [p for p in py_ref if p != 'sil']
    sents = re.split(f'[{sep}]', text)
    sents = [sent for sent in sents if sent]

    py_ori = []
    py_ori_nosil = []
    for sent in sents:
        py_sent = t.get_py(sent)[0]
        py_sent = [re.sub('[012345?]', '', p) for p in py_sent]
        py_ori.append(py_sent)
        py_ori_nosil.append([p for p in py_sent if p != 'sil'])
    py_ori_nosil_len = [len(py) for py in py_ori_nosil]
    len_ori = sum(py_ori_nosil_len)

    # py_ref_idx = [tuple(p) for p in enumerate(py_ref)]
    py_ref_idx = [tuple(p) for p in enumerate(py_ref_nosil)]
    py_ref_idx_nosil = [p for p in py_ref_idx if p[1] != 'sil']

    if len_ori == len(py_ref_nosil):
        # 当长度相等时，默认参考py和文字py是一一对应的关系
        items = []
        start_idx = 0
        for i, sent in enumerate(sents):
            py_len_sent = py_ori_nosil_len[i]
            end_idx = start_idx + py_len_sent
            items.append((py_ref_idx_nosil[start_idx][0], py_ref_idx_nosil[end_idx-1][0], sent))
            start_idx = end_idx
        return items


    def mismatch_score(ori_left, ori_right, ref, right_start):
        c_ori_left = Counter(ori_left)
        c_ori_right = Counter(ori_right)
        c_ref_left = Counter(ref[:right_start])
        c_ref_right = Counter(ref[right_start:])
        left_diff = sum((c_ori_left - c_ref_left).values())+sum((c_ref_left - c_ori_left).values())
        right_diff = sum((c_ori_right - c_ref_right).values())+sum((c_ref_right - c_ori_right).values())
        return left_diff + right_diff

    # end_idx included
    items = []
    start_idx = 0
    for i, sent in enumerate(sents):
        if i == len(sents)-1:
            cur_end_idx = len(py_ref_nosil)
        else:
            py_sent = py_ori_nosil[i]
            py_sent_next = py_ori_nosil[i+1]
            cur_end_idx = start_idx + len(py_sent)
            last_possible_end_idx = cur_end_idx + len(py_ori_nosil[i+1])
            scores = {}
            for n in range(start_idx, last_possible_end_idx+1):
                ref = py_ref_nosil[start_idx:last_possible_end_idx+1]
                scores[n] = mismatch_score(py_sent, py_sent_next, ref, n-start_idx)
            cur_end_idx = min(scores, key=lambda x: scores[x])
        if cur_end_idx == start_idx:
            cur_end_idx += 1
        items.append((py_ref_idx_nosil[start_idx][0], py_ref_idx_nosil[cur_end_idx-1][0], sent))
        start_idx = cur_end_idx

    return items


def py_to_time(items, timing):
    data = []
    for item in items:
        start_dot = timing[item[0]][0]
        start_time = dot_to_ms(start_dot)
        end_dot = timing[item[1]][0] + timing[item[1]][1]
        end_time = dot_to_ms(end_dot)
        text = item[2]
        data.append((start_time, end_time, text))

    return data


def to_dub(data, path=None, shift=0):
    """
    var data: [(start_time, end_time, text)]
    """
    dub = p.srtfile.SubRipFile()
    for i, datum in enumerate(data):
        dub.append(p.srtitem.SubRipItem(i, datum[0], datum[1], datum[2]))
    dub.shift(milliseconds=shift)
    if path is not None:
        dub.save(path)
    else:
        return dub


def to_srt_file(text, py, timing, path, starttime=0):
    items = split_and_align(text, py)
    data = py_to_time(items, timing)
    to_dub(data, path, starttime)


def batch_to_srt_file(data, path, interval, tune_format):
    """
    data: [(text, py, timing),]
    interval: in milliseconds
    tune_format: 'vsqx' or 'svp'
    """
    dubs = []
    if tune_format == 'vsqx':
        start_time = beginning_ms
    elif tune_format == 'svp':
        start_time = 0
    else:
        start_time = 0
    for n, datum in enumerate(data):
        text, py, timing = datum
        items = split_and_align(text, py)
        data = py_to_time(items, timing)
        dub = to_dub(data, shift=start_time)
        start_time = dub[-1].end
        start_time = start_time.hours*60*60*1000+\
                     start_time.minutes*60*1000+\
                     start_time.seconds*1000+\
                     start_time.milliseconds+\
                     interval
        dubs.append(dub)
    out_dub = p.srtfile.SubRipFile()
    counter = 0
    for dub in dubs:
        for item in dub:
            out_dub.append(p.srtitem.SubRipItem(counter, item.start, item.end, item.text))
            counter+=1
    out_dub.save(path)




# test
if __name__ == '__main__':
    r = split_and_align('你好啊,天气可以', 'sil ni2 hai xing bu xing a sil tian sil qi hai ke yi sil'.split(' '))
    print(r)