# out of use right now

'''
import os
import sys
from sppas.bin import annotation
from praatio import tgio
from reliance.audioTools import cut

SPPAS_DIR_NAME = 'misc\\temp'
SPPAS_OUTPUT_FOLDER_NAME = 'sppas_temp'
text_args = r"""
-I .\samples\samples-eng
-l eng
-e .TextGrid
--fillipus --textnorm --phonetize --alignment
"""
args_proto = ['-I', None, '-l', 'cmn', '-e', '.TextGrid', '--fillipus', '--textnorm', '--phonetize', '--alignment']
arg_len = len(args_proto)

# consonant length, total length
phone_lengths = {'a': (0, 1), 'ai': (0, 2), 'an': (0, 2), 'ang': (0, 2), 'ao': (0, 2), 'ba': (1, 2), 'bai': (1, 3),
                 'ban': (1, 3), 'bang': (1, 3), 'bao': (1, 3), 'bei': (1, 3), 'ben': (1, 3), 'beng': (1, 3),
                 'bi': (1, 2), 'bian': (1, 4), 'biao': (1, 4), 'bie': (1, 3), 'bin': (1, 3), 'bing': (1, 4),
                 'bo': (1, 3), 'bu': (1, 2), 'ca': (1, 2), 'cai': (1, 3), 'can': (1, 3), 'cang': (1, 3), 'cao': (1, 3),
                 'ce': (1, 2), 'ceng': (1, 3), 'cha': (1, 2), 'chai': (1, 3), 'chan': (1, 3), 'chang': (1, 3),
                 'chao': (1, 3), 'che': (1, 2), 'chen': (1, 3), 'cheng': (1, 3), 'chi': (1, 2), 'chong': (1, 3),
                 'chou': (1, 3), 'chu': (1, 2), 'chuai': (1, 4), 'chuan': (1, 4), 'chuang': (1, 4), 'chui': (1, 4),
                 'chun': (1, 4), 'chuo': (1, 3), 'ci': (1, 2), 'cong': (1, 3), 'cou': (1, 3), 'cu': (1, 2),
                 'cuan': (1, 4), 'cui': (1, 4), 'cun': (1, 4), 'cuo': (1, 3), 'da': (1, 2), 'dai': (1, 3),
                 'dan': (1, 3), 'dang': (1, 3), 'dao': (1, 3), 'de': (1, 2), 'dei': (1, 3), 'deng': (1, 3),
                 'di': (1, 2), 'dian': (1, 4), 'diao': (1, 4), 'die': (1, 3), 'ding': (1, 4), 'diu': (1, 4),
                 'dong': (1, 3), 'dou': (1, 3), 'du': (1, 2), 'duan': (1, 4), 'dui': (1, 4), 'dun': (1, 4),
                 'duo': (1, 3), 'e': (0, 1), 'en': (0, 2), 'er': (0, 1), 'fa': (1, 2), 'fan': (1, 3), 'fang': (1, 3),
                 'fei': (1, 3), 'fen': (1, 3), 'feng': (1, 3), 'fo': (1, 3), 'fou': (1, 3), 'fu': (1, 2), 'ga': (1, 2),
                 'gai': (1, 3), 'gan': (1, 3), 'gang': (1, 3), 'gao': (1, 3), 'ge': (1, 2), 'gei': (1, 3),
                 'gen': (1, 3), 'geng': (1, 3), 'gong': (1, 3), 'gou': (1, 3), 'gu': (1, 2), 'gua': (1, 3),
                 'guai': (1, 4), 'guan': (1, 4), 'guang': (1, 4), 'gui': (1, 4), 'gun': (1, 4), 'guo': (1, 3),
                 'ha': (1, 2), 'hai': (1, 3), 'han': (1, 3), 'hang': (1, 3), 'hao': (1, 3), 'he': (1, 2),
                 'hei': (1, 3), 'hen': (1, 3), 'heng': (1, 3), 'hong': (1, 3), 'hou': (1, 3), 'hu': (1, 2),
                 'hua': (1, 3), 'huai': (1, 4), 'huan': (1, 4), 'huang': (1, 4), 'hui': (1, 4), 'hun': (1, 4),
                 'huo': (1, 3), 'ji': (1, 2), 'jia': (1, 3), 'jian': (1, 4), 'jiang': (1, 4), 'jiao': (1, 4),
                 'jie': (1, 3), 'jin': (1, 3), 'jing': (1, 4), 'jiong': (1, 4), 'jiu': (1, 4), 'ju': (1, 2),
                 'juan': (1, 4), 'jue': (1, 3), 'jun': (1, 3), 'ka': (1, 2), 'kai': (1, 3), 'kan': (1, 3),
                 'kang': (1, 3), 'kao': (1, 3), 'ke': (1, 2), 'ken': (1, 3), 'keng': (1, 3), 'kong': (1, 3),
                 'kou': (1, 3), 'ku': (1, 2), 'kua': (1, 3), 'kuai': (1, 4), 'kuan': (1, 4), 'kuang': (1, 4),
                 'kui': (1, 4), 'kun': (1, 4), 'kuo': (1, 3), 'la': (1, 2), 'lai': (1, 3), 'lan': (1, 3),
                 'lang': (1, 3), 'lao': (1, 3), 'le': (1, 2), 'lei': (1, 3), 'leng': (1, 3), 'li': (1, 2),
                 'lia': (1, 3), 'lian': (1, 4), 'liang': (1, 4), 'liao': (1, 4), 'lie': (1, 3), 'lin': (1, 3),
                 'ling': (1, 4), 'liu': (1, 4), 'long': (1, 3), 'lou': (1, 3), 'lu': (1, 2), 'luan': (1, 4),
                 'lue': (1, 3), 'lun': (1, 4), 'luo': (1, 3), 'ma': (1, 2), 'mai': (1, 3), 'man': (1, 3),
                 'mang': (1, 3), 'mao': (1, 3), 'me': (1, 2), 'mei': (1, 3), 'men': (1, 3), 'meng': (1, 3),
                 'mi': (1, 2), 'mian': (1, 4), 'miao': (1, 4), 'mie': (1, 3), 'min': (1, 3), 'ming': (1, 4),
                 'miu': (1, 4), 'mo': (1, 3), 'mou': (1, 3), 'mu': (1, 2), 'na': (1, 2), 'nai': (1, 3),
                 'nan': (1, 3), 'nang': (1, 3), 'nao': (1, 3), 'ne': (1, 2), 'nei': (1, 3), 'nen': (1, 3),
                 'neng': (1, 3), 'ni': (1, 2), 'nian': (1, 4), 'niang': (1, 4), 'niao': (1, 4), 'nie': (1, 3),
                 'nin': (1, 3), 'ning': (1, 4), 'niu': (1, 4), 'nong': (1, 3), 'nu': (1, 2), 'nuan': (1, 4),
                 'nue': (1, 3), 'nuo': (1, 3), 'ou': (0, 2), 'pa': (1, 2), 'pai': (1, 3), 'pan': (1, 3),
                 'pang': (1, 3), 'pao': (1, 3), 'pei': (1, 3), 'pen': (1, 3), 'peng': (1, 3), 'pi': (1, 2),
                 'pian': (1, 4), 'piao': (1, 4), 'pie': (1, 3), 'pin': (1, 3), 'ping': (1, 4), 'po': (1, 3),
                 'pu': (1, 2), 'q': (1, 4), 'qi': (1, 2), 'qia': (1, 3), 'qian': (1, 4), 'qiang': (1, 4),
                 'qiao': (1, 4), 'qie': (1, 3), 'qin': (1, 3), 'qing': (1, 4), 'qiong': (1, 4), 'qiu': (1, 4),
                 'qu': (1, 2), 'quan': (1, 4), 'que': (1, 3), 'qun': (1, 3), 'ran': (1, 3), 'rang': (1, 3),
                 'rao': (1, 3), 're': (1, 2), 'ren': (1, 3), 'reng': (1, 3), 'ri': (1, 2), 'rong': (1, 3),
                 'rou': (1, 3), 'ru': (1, 2), 'ruan': (1, 4), 'rui': (1, 4), 'run': (1, 4), 'ruo': (1, 3),
                 'sa': (1, 2), 'sai': (1, 3), 'san': (1, 3), 'sang': (1, 3), 'sao': (1, 3), 'se': (1, 2),
                 'sen': (1, 3), 'seng': (1, 3), 'sha': (1, 2), 'shai': (1, 3), 'shan': (1, 3), 'shang': (1, 3),
                 'shao': (1, 3), 'she': (1, 2), 'shen': (1, 3), 'sheng': (1, 3), 'shi': (1, 2), 'shou': (1, 3),
                 'shu': (1, 2), 'shua': (1, 3), 'shuai': (1, 4), 'shuan': (1, 4), 'shuang': (1, 4), 'shui': (1, 4),
                 'shun': (1, 4), 'shuo': (1, 3), 'si': (1, 2), 'song': (1, 3), 'sou': (1, 3), 'su': (1, 2),
                 'suan': (1, 4), 'sui': (1, 4), 'sun': (1, 4), 'suo': (1, 3), 'ta': (1, 2), 'tai': (1, 3),
                 'tan': (1, 3), 'tang': (1, 3), 'tao': (1, 3), 'te': (1, 2), 'teng': (1, 3), 'ti': (1, 2),
                 'tian': (1, 4), 'tiao': (1, 4), 'tie': (1, 3), 'ting': (1, 4), 'tong': (1, 3), 'tou': (1, 3),
                 'tu': (1, 2), 'tuan': (1, 4), 'tui': (1, 4), 'tun': (1, 4), 'tuo': (1, 3), 'unk': (0, 1),
                 'wa': (0, 2), 'wai': (0, 3), 'wan': (0, 3), 'wang': (0, 3), 'wei': (0, 3), 'wen': (0, 3),
                 'weng': (0, 3), 'wo': (0, 2), 'wu': (0, 1), 'xi': (1, 2), 'xia': (1, 3), 'xian': (1, 4),
                 'xiang': (1, 4), 'xiao': (1, 4), 'xie': (1, 3), 'xin': (1, 3), 'xing': (1, 4), 'xiong': (1, 4),
                 'xiu': (1, 4), 'xu': (1, 2), 'xuan': (1, 4), 'xue': (1, 3), 'xun': (1, 3), 'ya': (0, 2),
                 'yan': (0, 3), 'yang': (0, 3), 'yao': (0, 3), 'ye': (0, 2), 'yi': (0, 1), 'yin': (0, 2),
                 'ying': (0, 3), 'yong': (0, 3), 'you': (0, 3), 'yu': (0, 1), 'yuan': (0, 3), 'yue': (0, 2),
                 'yun': (0, 2), 'za': (1, 2), 'zai': (1, 3), 'zan': (1, 3), 'zang': (1, 3), 'zao': (1, 3),
                 'ze': (1, 2), 'zei': (1, 3), 'zen': (1, 3), 'zeng': (1, 3), 'zha': (1, 2), 'zhai': (1, 3),
                 'zhan': (1, 3), 'zhang': (1, 3), 'zhao': (1, 3), 'zhe': (1, 2), 'zhen': (1, 3), 'zheng': (1, 3),
                 'zhi': (1, 2), 'zhong': (1, 3), 'zhou': (1, 3), 'zhu': (1, 2), 'zhua': (1, 3), 'zhuan': (1, 4),
                 'zhuang': (1, 4), 'zhui': (1, 4), 'zhun': (1, 4), 'zhuo': (1, 3), 'zi': (1, 2), 'zong': (1, 3),
                 'zou': (1, 3), 'zu': (1, 2), 'zuan': (1, 4), 'zui': (1, 4), 'zun': (1, 4), 'zuo': (1, 3),
                 'sil': (0, 1)}


# considering the failures of the sppas alignment: a batch of phones were left with a whole interval with no text.
# 对空interval的处理：both phon tier and token tier
# 直接用tier中的信息而不是从参数中接受的py进行填充
# 为什么在主序列中先删除sil？因为是拼接的地方，拼音和标注数量不能一一对应
def normalize(tier_phon, tier_tokens, only_vowel):
    # print(tier_tokens)
    def include_pys(start, end):
        vicinity = 0.001
        start, end = start-vicinity, end+vicinity
        tokens_whole = []
        for interval_tokens in tier_tokens:
            if interval_tokens[0] >= start and interval_tokens[1] <= end:
                tokens_whole.append(interval_tokens)
            if interval_tokens[1] > end:
                break
        py_list = []
        for tkw in tokens_whole:
            py_list.extend(tkw[2].split('\n'))

        return py_list

    sil_i = []
    tier_phon = tier_phon[:]
    # print('whole', tier_phon)
    output = []
    itv = tgio.Interval
    to_insert = []  # (start_aim_idx, total_length, [intervals])
    for i, interval_phon in enumerate(tier_phon):
        # print('text:', interval_phon)
        if interval_phon[2] == '#':
            output.append(itv(interval_phon[0], interval_phon[1], 'sil'))
            sil_i.append(i)
        if interval_phon[2] == '':
            # the unrecognized parts will be filled with blank intervals by praatio.
            # However, we should see whether such a interval is a valid voiced part, if not, we should delete it.
            # print('start', interval_phon)
            pys = include_pys(interval_phon[0], interval_phon[1])
            # print(i, interval_phon, pys)
            if not pys:
                sil_i.append(i)
                # print('del',i, len(tier_phon))
                continue
            # print('selected', pys)
            total_time = interval_phon[1] - interval_phon[0]
            total_length = 0
            py_lengths = []
            for py in pys:
                length = phone_lengths.get(py, (0, 1))
                total_length += length[1]
                py_lengths.append(length[1])
            avg_time = total_time/total_length
            py_intervals = []
            end = len(pys) - 1
            last_end = interval_phon[0]
            for i_py, py in enumerate(pys):
                if i_py < end:
                    cur_end = last_end+avg_time*py_lengths[i_py]
                else:
                    cur_end = interval_phon[1]
                py_intervals.append((last_end, cur_end, py))
                last_end = cur_end

            phon_itvs_insert = []
            for itv_py in py_intervals:
                phon_itvs_insert.append((itv_py[0], itv_py[1], 'dummy_align'))
            to_insert.append((i, len(phon_itvs_insert), phon_itvs_insert))

    operations = []
    for ii, si in enumerate(sil_i):
        operations.append((si, 'd', ii))
    for ii, inf in enumerate(to_insert):
        operations.append((inf[0], 'i', ii))
    operations.sort(key=lambda x: x[0])

    move_count = 0
    for operation in operations:
        if operation[1] == 'd':
            del tier_phon[sil_i[operation[2]] + move_count]
            move_count -= 1
        else:  # del the blank interval and insert
            inf = to_insert[operation[2]]
            del tier_phon[inf[0]+move_count]

            reversed_ins = reversed(inf[2])
            for to_be_itv in reversed_ins:
                tier_phon.insert(inf[0]+move_count, to_be_itv)
            move_count += (inf[1] - 1)
            # print('changed', reversed_ins)
    # tier_phone中无sil
    py_given = []  # 也去掉sil,因为拼音的sil数量与标注的sil数量不一定相同，已经失去意义
    for tkw in tier_tokens:
        py_cluster = tkw[2].split('\n')
        if py_cluster[0] or py_cluster != ['']:  # ''.split('\n')  -->  ['']
            py_given.extend(py_cluster)
    for i__, p_ in enumerate(py_given):
        if p_ == '#':
            py_given[i__] = 'sil'
    py_given = [x for x in py_given if x != 'sil']

    # combine the vowel phonemes to vowel phones (including consonant if the phone is made after error)
    # keep the consonants
    if not only_vowel:
        for p in py_given:
            if p != 'sil':
                try:
                    length = phone_lengths[p]
                except KeyError:
                    length = (0, 1)
                # print('go', p)
                # print(tier_phon[0])
                cur_phoneme = tier_phon[0]
                if cur_phoneme[2] == 'dummy_align':
                    length = (0, 1)

                if length[0] == 1:
                    cons = tier_phon[0]
                    output.append(itv(cons[0], cons[1], 'con'))
                    vows = tier_phon[1:length[1]]
                    output.append(itv(vows[0][0], vows[-1][1], p))
                else:
                    vows = tier_phon[0:length[1]]
                    output.append(itv(vows[0][0], vows[-1][1], p))
                # print(p, [x[2] for x in tier_phon[:length[1]]])
                del tier_phon[:length[1]]

    # incorporate the following consonant to the preceding vowel
    else:
        first = True
        for idx, p in enumerate(py_given):
            try:
                next_cons_len = phone_lengths.get(py_given[idx + 1], (0, 1))[0]
            except IndexError:
                next_cons_len = 0

            length = phone_lengths.get(p, (0, 1))
            # cur_phoneme = tier_phon[0]
            # if cur_phoneme[2] == 'spn':
            #     length = (0, 1)
            if next_cons_len:
                wrapping_length = length[1] - length[0] + next_cons_len
                wrapping_phonemes = tier_phon[0:wrapping_length]
                self_last = wrapping_phonemes[-next_cons_len - 1]
                next_first = wrapping_phonemes[-next_cons_len]
                if self_last[1] == next_first[0]:
                    actual_length = wrapping_length
                else:
                    actual_length = length[1] - length[0]
                    output.append(itv(next_first[0], wrapping_phonemes[-1][1], 'sil'))  # 将不连续的下一辅音置为静音
            else:
                actual_length = wrapping_length = length[1] - length[0]
            if first and length[0] == 1:
                first = False
                wrapping_length += 1
                phonemes = tier_phon[1:1 + actual_length]
                cons = tier_phon[0]
                output.append((itv(cons[0], cons[1], 'sil')))
            else:
                first = False
                phonemes = tier_phon[0:actual_length]
            output.append(itv(phonemes[0][0], phonemes[-1][1], p))
            del tier_phon[:wrapping_length]
    output.sort(key=lambda x: x[0])

    return output


class Sppas:
    def __init__(self, wav_filename, seg_tg_name, py, text_in):
        self.wav_filename = wav_filename

        self.seg_tg_name = seg_tg_name

        self.py = []
        for p in py:
            if p[-1].isdigit():
                self.py.append(p[:-1])
            else:
                self.py.append(p)

        self.chrs = []
        for i, ch in enumerate(text_in):
            if py[i] == 'sil':
                self.chrs.append('sil')
            else:
                self.chrs.append(ch)

        self.sign = self.py

        self.basename = wav_filename.split('\\')[-1].split('.')[0]

    def execute_alignment(self):
        def single_alignment(sign, name):
            write_list = []
            for ch in sign:
                if ch == 'sil':
                    write_list.append('#')
                else:
                    write_list.append(ch)
            txt = ' '.join(write_list)
            with open(f'{SPPAS_DIR_NAME}\\{SPPAS_OUTPUT_FOLDER_NAME}\\{name}.txt', 'w', encoding='utf-8') as f:
                f.write(txt)
            # os.chdir(os.getcwd()+'\\'+SPPAS_DIR_NAME)
            args = args_proto[:]
            args[1] = f'{SPPAS_DIR_NAME}\\{SPPAS_OUTPUT_FOLDER_NAME}\\{name}.wav'
            sys.argv.extend(args)
            annotation.execute()
            del sys.argv[-arg_len:]
            # os.chdir(os.getcwd().strip('\\'+SPPAS_DIR_NAME))

        # clear the folder for work
        try:
            names = os.listdir(f'{os.getcwd()}\\{SPPAS_DIR_NAME}\\{SPPAS_OUTPUT_FOLDER_NAME}')
        except FileNotFoundError:
            os.makedirs(f'{os.getcwd()}\\{SPPAS_DIR_NAME}\\{SPPAS_OUTPUT_FOLDER_NAME}', exist_ok=True)
            names = []
        for name in names:
            try:
                os.remove(f'{os.getcwd()}\\{SPPAS_DIR_NAME}\\{SPPAS_OUTPUT_FOLDER_NAME}\\{name}')
            except Exception as e:
                print('wrong delete', e)

        if os.path.exists(self.seg_tg_name):
            seg_list = []
            length_list = []
            name_list = []
            tg = tgio.openTextgrid(os.getcwd()+'\\'+self.seg_tg_name)
            interval_list = tg.tierDict['segment'].entryList
            for i, interval in enumerate(interval_list):  # (start, end, text)
                seg_list.append((interval[0], interval[1]))
                length = int(interval[2].split('_')[-2])
                length_list.append(length)

                name_list.append(self.basename+'_seg_'+str(i+1))
            cwd = os.getcwd()

            sil_inf = {}
            cur_start_i = 0
            for i_l, lent in enumerate(length_list):
                itv_is_silence = True
                local_signs = self.py[cur_start_i:cur_start_i+lent]
                for sign in local_signs:
                    if sign != 'sil':
                        itv_is_silence = False
                        break
                sil_inf[i_l] = itv_is_silence

                cur_start_i += lent

            del_c = 0
            nl_voiced = name_list[:]
            sl_voiced = seg_list[:]
            for i_del in (i_si for i_si in sil_inf if sil_inf[i_si]):
                del nl_voiced[i_del-del_c]
                del sl_voiced[i_del-del_c]
                del_c += 1
            cut(self.wav_filename, [f'{cwd}\\{SPPAS_DIR_NAME}\\{SPPAS_OUTPUT_FOLDER_NAME}\\{name}.wav' for name in nl_voiced], sl_voiced)

            # do align each, if is silence, then make a fake result
            chrs_to_cut = self.sign.copy()
            for i, name in enumerate(name_list):
                # print(chrs_to_cut, length_list[i])
                chr = chrs_to_cut[:length_list[i]]
                del chrs_to_cut[:length_list[i]]
                if sil_inf[i]:
                    range_ = seg_list[i]
                    end = range_[1] - range_[0]

                    fake_tg_ph = tgio.Textgrid()
                    fake_tg_ph.addTier(tgio.IntervalTier('PhonAlign', [(0, end, '#')]))

                    fake_tg_tk = tgio.Textgrid()
                    fake_tg_tk.addTier(tgio.IntervalTier('Tokens', [(0, end, '#')]))

                    fake_tg_ph.save(f'{cwd}\\{SPPAS_DIR_NAME}\\{SPPAS_OUTPUT_FOLDER_NAME}\\{name}-palign.TextGrid')
                    fake_tg_tk.save(f'{cwd}\\{SPPAS_DIR_NAME}\\{SPPAS_OUTPUT_FOLDER_NAME}\\{name}-token.TextGrid')
                else:
                    single_alignment(chr, name)

            # combine
            phon_tier_list = []
            token_tier_list = []
            not_found_list = []
            cwd = os.getcwd()
            for i_name, name in enumerate(name_list):
                try:
                    tg_dict = tgio.openTextgrid(f'{cwd}\\{SPPAS_DIR_NAME}\\{SPPAS_OUTPUT_FOLDER_NAME}\\{name}-palign.TextGrid', readRaw=True).tierDict
                    tg_dict_tokens = tgio.openTextgrid(f'{cwd}\\{SPPAS_DIR_NAME}\\{SPPAS_OUTPUT_FOLDER_NAME}\\{name}-token.TextGrid', readRaw=True).tierDict  # 直接读tokens不行，因为使用的是换行符进行token分界，无法读取
                    phon_tier_list.append(tg_dict['PhonAlign'])
                    token_tier_list.append(tg_dict_tokens['Tokens'])
                except FileNotFoundError as e:
                    not_found_list.append(i_name)
                    print(e)

            if not_found_list:

                return not_found_list

            phon_base_tier = phon_tier_list[0]
            for tier in phon_tier_list[1:]:
                phon_base_tier = phon_base_tier.appendTier(tier)
            token_base_tier = token_tier_list[0]
            for tier in token_tier_list[1:]:
                token_base_tier = token_base_tier.appendTier(tier)

            final_tg = tgio.Textgrid()
            final_tg.addTier(phon_base_tier)
            final_tg.addTier(token_base_tier)
            final_tg.save(f'{cwd}\\{SPPAS_DIR_NAME}\\{SPPAS_OUTPUT_FOLDER_NAME}\\{self.basename}-palign.TextGrid')

        else:
            with open(self.wav_filename, 'rb') as f:
                f_b = f.read()
            with open(f'{SPPAS_DIR_NAME}\\{SPPAS_OUTPUT_FOLDER_NAME}\\{self.basename}.wav', 'wb') as f:
                f.write(f_b)
            single_alignment(self.sign, self.basename)
            cwd = os.getcwd()
            name = self.basename
            tg_dict = tgio.openTextgrid(
                f'{cwd}\\{SPPAS_DIR_NAME}\\{SPPAS_OUTPUT_FOLDER_NAME}\\{name}-palign.TextGrid',
                readRaw=True).tierDict
            tg_dict_tokens = tgio.openTextgrid(
                f'{cwd}\\{SPPAS_DIR_NAME}\\{SPPAS_OUTPUT_FOLDER_NAME}\\{name}-token.TextGrid',
                readRaw=True).tierDict
            final_tg = tgio.Textgrid()
            final_tg.addTier(tg_dict['PhonAlign'])
            final_tg.addTier(tg_dict_tokens['Tokens'])
            final_tg.save(f'{cwd}\\{SPPAS_DIR_NAME}\\{SPPAS_OUTPUT_FOLDER_NAME}\\{self.basename}-palign.TextGrid')

    def transcribe_to(self, dest, only_vowel: bool):
        """
        From sppas output to standard tytalk manual alignment.
        You should make sure the alignments didn't went wrong (ie return with errors). Then this function can be called.
        :param dest: file name
        :param only_vowel: combine all the phonemes except vowels in different characters.
        :return:
        """
        align_dir = f'{os.getcwd()}\\{SPPAS_DIR_NAME}\\{SPPAS_OUTPUT_FOLDER_NAME}\\{self.basename}-palign.TextGrid'
        dest_dir = f'{os.getcwd()}\\{dest}'
        tg = tgio.openTextgrid(align_dir, readRaw=True)
        interval_list = tg.tierDict['PhonAlign'].entryList  # within there are named tuples
        py_list = tg.tierDict['Tokens'].entryList
        try:
            normal_list = normalize(interval_list, py_list, only_vowel)
            dest_tg = tgio.Textgrid()
            dest_tier = tgio.IntervalTier('grid', normal_list)
            dest_tg.addTier(dest_tier)
            dest_tg.save(dest_dir, ignoreBlankSpaces=True)
        except IndexError as e:
            raise e



if __name__ == '__main__':
    os.chdir('D:/Files/OneDrive/pycharmfiles/TyTalk_Shuttle')
    s = Sppas(r'others\sppas\temp_Recording_22.wav', ['yi1', 'shan3', 'yi1', 'shan3', 'liang4', 'jing1', 'jing1', 'sil', 'man3', 'tian1', 'dou1', 'shi4', 'xiao3', 'xing1', 'xing1'])
    s.execute_alignment()
    s.transcribe_to(r'others\sppas\temp_Recording_22.TextGrid')
'''