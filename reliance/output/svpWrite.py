import json
from reliance.global_vars import ms_per_dot_svp, tempo_svp, cents_per_pit
from reliance.global_vars import ms_per_dot
from reliance.global_vars import whether_cons

# 相对于vsqx的DICTION，多
DICTION = {'zhi': 'ts` i`', 'chi': 'ts`h i`', 'shi': 's` i`', 'ri': 'z` i`', 'zi': 'ts i\\', 'ci': 'tsh i\\',
           'si': 's i\\', 'ba': 'p a', 'pa': 'ph a', 'ma': 'm a', 'fa': 'f a', 'da': 't a', 'ta': 'th a', 'na': 'n a',
           'la': 'l a', 'ga': 'k a', 'ka': 'kh a', 'ha': 'x a', 'zha': 'ts` a', 'cha': 'ts`h a', 'sha': 's` a',
           'za': 'ts a', 'ca': 'tsh a', 'sa': 's a', 'bo': 'p uo', 'po': 'ph uo', 'mo': 'm uo', 'fo': 'f uo',
           'lo': 'l o', 'me': 'm 7', 'de': 't 7', 'te': 'th 7', 'ne': 'n 7', 'le': 'l 7', 'ge': 'k 7', 'ke': 'kh 7',
           'he': 'x 7', 'zhe': 'ts` 7', 'che': 'ts`h 7', 'she': 's` 7', 're': 'z` 7', 'ze': 'ts 7', 'ce': 'tsh 7',
           'se': 's 7', 'bai': 'p a :\\i', 'pai': 'ph a :\\i', 'mai': 'm a :\\i', 'dai': 't a :\\i', 'tai': 'th a :\\i',
           'nai': 'n a :\\i', 'lai': 'l a :\\i', 'gai': 'k a :\\i', 'kai': 'kh a :\\i', 'hai': 'x a :\\i',
           'zhai': 'ts` a :\\i', 'chai': 'ts`h a :\\i', 'shai': 's` a :\\i', 'zai': 'ts a :\\i', 'cai': 'tsh a :\\i',
           'sai': 's a :\\i', 'bei': 'p e :\\i', 'pei': 'ph e :\\i', 'mei': 'm e :\\i', 'fei': 'f e :\\i',
           'dei': 't e :\\i', 'nei': 'n e :\\i', 'lei': 'l e :\\i', 'gei': 'k e :\\i', 'kei': 'kh e :\\i',
           'hei': 'x e :\\i', 'zhei': 'ts` e :\\i', 'shei': 's` e :\\i', 'zei': 'ts e :\\i', 'bao': 'p AU',
           'pao': 'ph AU', 'mao': 'm AU', 'dao': 't AU', 'tao': 'th AU', 'nao': 'n AU', 'lao': 'l AU', 'gao': 'k AU',
           'kao': 'kh AU', 'hao': 'x AU', 'zhao': 'ts` AU', 'chao': 'ts`h AU', 'shao': 's` AU', 'rao': 'z` AU',
           'zao': 'ts AU', 'cao': 'tsh AU', 'sao': 's AU', 'pou': 'ph @U', 'mou': 'm @U', 'fou': 'f @U', 'dou': 't @U',
           'tou': 'th @U', 'nou': 'n @U', 'lou': 'l @U', 'gou': 'k @U', 'kou': 'kh @U', 'hou': 'x @U', 'zhou': 'ts` @U',
           'chou': 'ts`h @U', 'shou': 's` @U', 'rou': 'z` @U', 'zou': 'ts @U', 'cou': 'tsh @U', 'sou': 's @U',
           'ban': 'p a :n', 'pan': 'ph a :n', 'man': 'm a :n', 'fan': 'f a :n', 'dan': 't a :n', 'tan': 'th a :n',
           'nan': 'n a :n', 'lan': 'l a :n', 'gan': 'k a :n', 'kan': 'kh a :n', 'han': 'x a :n', 'zhan': 'ts` a :n',
           'chan': 'ts`h a :n', 'shan': 's` a :n', 'ran': 'z` a :n', 'zan': 'ts a :n', 'can': 'tsh a :n',
           'san': 's a :n', 'ben': 'p @ :n', 'pen': 'ph @ :n', 'men': 'm @ :n', 'fen': 'f @ :n', 'den': 't @ :n',
           'nen': 'n @ :n', 'gen': 'k @ :n', 'ken': 'kh @ :n', 'hen': 'x @ :n', 'zhen': 'ts` @ :n', 'chen': 'ts`h @ :n',
           'shen': 's` @ :n', 'ren': 'z` @ :n', 'zen': 'ts @ :n', 'cen': 'tsh @ :n', 'sen': 's @ :n', 'bang': 'p A N',
           'pang': 'ph A N', 'mang': 'm A N', 'fang': 'f A N', 'dang': 't A N', 'tang': 'th A N', 'nang': 'n A N',
           'lang': 'l A N', 'gang': 'k A N', 'kang': 'kh A N', 'hang': 'x A N', 'zhang': 'ts` A N', 'chang': 'ts`h A N',
           'shang': 's` A N', 'rang': 'z` A N', 'zang': 'ts A N', 'cang': 'tsh A N', 'sang': 's A N', 'beng': 'p @ N',
           'peng': 'ph @ N', 'meng': 'm @ N', 'feng': 'f @ N', 'deng': 't @ N', 'teng': 'th @ N', 'neng': 'n @ N',
           'leng': 'l @ N', 'geng': 'k @ N', 'keng': 'kh @ N', 'heng': 'x @ N', 'zheng': 'ts` @ N', 'cheng': 'ts`h @ N',
           'sheng': 's` @ N', 'reng': 'z` @ N', 'zeng': 'ts @ N', 'ceng': 'tsh @ N', 'seng': 's @ N', 'bi': 'p i',
           'pi': 'ph i', 'mi': 'm i', 'di': 't i', 'ti': 'th i', 'ni': 'n i', 'li': 'l i', 'ji': 'ts\\ i',
           'qi': 'ts\\h i', 'xi': 's\\ i', 'dia': 't ia', 'lia': 'l ia', 'jia': 'ts\\ ia', 'qia': 'ts\\h ia',
           'xia': 's\\ ia', 'bie': 'p ie', 'pie': 'ph ie', 'mie': 'm ie', 'die': 't ie', 'tie': 'th ie', 'nie': 'n ie',
           'lie': 'l ie', 'jie': 'ts\\ ie', 'qie': 'ts\\h ie', 'xie': 's\\ ie', 'biao': 'p iAU', 'piao': 'ph iAU',
           'miao': 'm iAU', 'diao': 't iAU', 'tiao': 'th iAU', 'niao': 'n iAU', 'liao': 'l iAU', 'jiao': 'ts\\ iAU',
           'qiao': 'ts\\h iAU', 'xiao': 's\\ iAU', 'miu': 'm i@U', 'diu': 't i@U', 'niu': 'n i@U', 'liu': 'l i@U',
           'jiu': 'ts\\ i@U', 'qiu': 'ts\\h i@U', 'xiu': 's\\ i@U', 'bian': 'p iE :n', 'pian': 'ph iE :n',
           'mian': 'm iE :n', 'dian': 't iE :n', 'tian': 'th iE :n', 'nian': 'n iE :n', 'lian': 'l iE :n',
           'jian': 'ts\\ iE :n', 'qian': 'ts\\h iE :n', 'xian': 's\\ iE :n', 'bin': 'p i :n', 'pin': 'ph i :n',
           'min': 'm i :n', 'nin': 'n i :n', 'lin': 'l i :n', 'jin': 'ts\\ i :n', 'qin': 'ts\\h i :n',
           'xin': 's\\ i :n', 'niang': 'n iA N', 'liang': 'l iA N', 'jiang': 'ts\\ iA N', 'qiang': 'ts\\h iA N',
           'xiang': 's\\ iA N', 'bing': 'p i N', 'ping': 'ph i N', 'ming': 'm i N', 'ding': 't i N', 'ting': 'th i N',
           'ning': 'n i N', 'ling': 'l i N', 'jing': 'ts\\ i N', 'qing': 'ts\\h i N', 'xing': 's\\ i N', 'bu': 'p u',
           'pu': 'ph u', 'mu': 'm u', 'fu': 'f u', 'du': 't u', 'tu': 'th u', 'nu': 'n u', 'lu': 'l u', 'gu': 'k u',
           'ku': 'kh u', 'hu': 'x u', 'ju': 'ts\\ y', 'qu': 'ts\\h y', 'xu': 's\\ y', 'zhu': 'ts` u', 'chu': 'ts`h u',
           'shu': 's` u', 'ru': 'z` u', 'zu': 'ts u', 'cu': 'tsh u', 'su': 's u', 'gua': 'k ua', 'kua': 'kh ua',
           'hua': 'x ua', 'zhua': 'ts` ua', 'chua': 'ts`h ua', 'shua': 's` ua', 'duo': 't uo', 'tuo': 'th uo',
           'nuo': 'n uo', 'luo': 'l uo', 'guo': 'k uo', 'kuo': 'kh uo', 'huo': 'x uo', 'zhuo': 'ts` uo',
           'chuo': 'ts`h uo', 'shuo': 's` uo', 'ruo': 'z` uo', 'zuo': 'ts uo', 'cuo': 'tsh uo', 'suo': 's uo',
           'guai': 'k ua :\\i', 'kuai': 'kh ua :\\i', 'huai': 'x ua :\\i', 'zhuai': 'ts` ua :\\i',
           'chuai': 'ts`h ua :\\i', 'shuai': 's` ua :\\i', 'dui': 't ue :\\i', 'tui': 'th ue :\\i', 'gui': 'k ue :\\i',
           'kui': 'kh ue :\\i', 'hui': 'x ue :\\i', 'zhui': 'ts` ue :\\i', 'chui': 'ts`h ue :\\i', 'shui': 's` ue :\\i',
           'rui': 'z` ue :\\i', 'zui': 'ts ue :\\i', 'cui': 'tsh ue :\\i', 'sui': 's ue :\\i', 'duan': 't ua :n',
           'tuan': 'th ua :n', 'nuan': 'n ua :n', 'luan': 'l ua :n', 'guan': 'k ua :n', 'kuan': 'kh ua :n',
           'huan': 'x ua :n', 'juan': 'ts\\ y{ :n', 'quan': 'ts\\h y{ :n', 'xuan': 's\\ y{ :n', 'zhuan': 'ts` ua :n',
           'chuan': 'ts`h ua :n', 'shuan': 's` ua :n', 'ruan': 'z` ua :n', 'zuan': 'ts ua :n', 'cuan': 'tsh ua :n',
           'suan': 's ua :n', 'dun': 't u@ :n', 'tun': 'th u@ :n', 'lun': 'l u@ :n', 'gun': 'k u@ :n',
           'kun': 'kh u@ :n', 'hun': 'x u@ :n', 'jun': 'ts\\ yE :n', 'qun': 'ts\\h yE :n', 'xun': 's\\ yE :n',
           'zhun': 'ts` u@ :n', 'chun': 'ts`h u@ :n', 'shun': 's` u@ :n', 'run': 'z` u@ :n', 'zun': 'ts u@ :n',
           'cun': 'tsh u@ :n', 'sun': 's u@ :n', 'guang': 'k uA N', 'kuang': 'kh uA N', 'huang': 'x uA N',
           'zhuang': 'ts` uA N', 'chuang': 'ts`h uA N', 'shuang': 's` uA N', 'dong': 't U N', 'tong': 'th U N',
           'nong': 'n U N', 'long': 'l U N', 'gong': 'k U N', 'kong': 'kh U N', 'hong': 'x U N', 'zhong': 'ts` U N',
           'chong': 'ts`h U N', 'rong': 'z` U N', 'zong': 'ts U N', 'cong': 'tsh U N', 'song': 's U N', 'nv': 'n y',
           'lv': 'l y', 'nve': 'n yE', 'lve': 'l yE', 'jue': 'ts\\ yE', 'que': 'ts\\h yE', 'xue': 's\\ yE',
           'jiong': 'ts\\ iU N', 'qiong': 'ts\\h iU N', 'xiong': 's\\ iU N', 'a': 'a', 'o': 'o', 'e': '7',
           'ai': 'a :\\i', 'ei': 'e :\\i', 'ao': 'AU', 'ou': '@U', 'an': 'a :n', 'en': '@ :n', 'ang': 'A N',
           'er': 'a r\\`', 'yi': 'i', 'wu': 'u', 'yu': 'y', 'ya': 'j ia', 'ye': 'j ie', 'yao': 'j iAU', 'you': 'j i@U',
           'yan': 'j iE :n', 'yin': 'j i :n', 'yang': 'j iA N', 'ying': 'j i N', 'wa': 'w ua', 'wo': 'w uo',
           'wai': 'w ua :\\i', 'wei': 'w ue :\\i', 'wan': 'w ua :n', 'wen': 'w u@ :n', 'wang': 'w uA N',
           'weng': 'w u@ N', 'yue': 'j yE', 'yuan': 'j y{ :n', 'yun': 'j yE :n', 'yong': 'j iU N'}


def get_svp(notes, pits):
    structure = {
        "library": [],
        "renderConfig": {
            "destination": "./",
            "filename": "\u672a\u547d\u540d",
            "numChannels": 1,
            "aspirationFormat": "noAspiration",
            "bitDepth": 16,
            "sampleRate": 44100,
            "exportMixDown": True
        },
        "time": {
            "meter": [
                {
                    "index": 0,
                    "numerator": 4,
                    "denominator": 4
                }
            ],
            "tempo": [
                {
                    "position": 0,
                    "bpm": tempo_svp
                }
            ]
        },
        "version": 120,
        "tracks": [
            {
                "name": "\u672a\u547d\u540d\u97f3\u8f68",
                "groups": [],
                "dispColor": "ff7db235",
                "dispOrder": 0,
                "renderEnabled": False,
                "mixer": {
                    "gainDecibel": 0.0,
                    "pan": 0.0,
                    "mute": False,
                    "solo": False,
                    "display": True
                },
                "mainGroup": {
                    "name": "main",
                    "uuid": "cde12fc8-2e33-4688-b6dd-5956e24e857f",
                    "parameters": {
                        "pitchDelta": {
                            "mode": "linear",
                            "points": []
                        },
                        "vibratoEnv": {
                            "mode": "cubic",
                            "points": []
                        },
                        "loudness": {
                            "mode": "cubic",
                            "points": []
                        },
                        "tension": {
                            "mode": "cubic",
                            "points": []
                        },
                        "breathiness": {
                            "mode": "cubic",
                            "points": []
                        },
                        "voicing": {
                            "mode": "cubic",
                            "points": []
                        },
                        "gender": {
                            "mode": "cubic",
                            "points": []
                        },
                        "toneShift": {
                            "mode": "cubic",
                            "points": []
                        }
                    },
                    "notes": [
                    ]
                },
                "mainRef": {
                    "groupID": "cde12fc8-2e33-4688-b6dd-5956e24e857f",
                    "blickOffset": 0,
                    "pitchOffset": 0,
                    "isInstrumental": False,
                    "database": {
                        "name": "MEDIUM5\u00b7Chiyu (Lite)",
                        "language": "mandarin",
                        "phoneset": "xsampa",
                        "languageOverride": "",
                        "phonesetOverride": "",
                        "backendType": "SVR2Standard"
                    },
                    "dictionary": "",
                    "voice": {}
                },
            }
        ]
    }
    pit_list = []
    for pit in pits:
        pit_list.extend(pit)

    for i, note in enumerate(notes[:-1]):
        next_onset = notes[i+1]['onset']
        if next_onset - (note['onset'] + note['duration']) < 0.05*1000 / ms_per_dot_svp:
            note['duration'] = next_onset - note['onset']
    note_list = notes

    structure['tracks'][0]['mainGroup']['parameters']['pitchDelta']['points'] = pit_list
    structure['tracks'][0]['mainGroup']['notes'] = note_list
    return json.dumps(structure)


class Writer:
    def __init__(self, data, adjust_consonants=False, height=65, interval=1000, final=1500):
        self.adjust_consonants = adjust_consonants
        self.notes = []
        self.pits = []
        interval = int(interval / ms_per_dot_svp)
        final = int(final / ms_per_dot_svp)
        dot_counter = 0
        for datum in data:
            ch = datum[0]
            py = datum[1]

            timing = []
            timing_vsqx = list(datum[2])
            for start, length in timing_vsqx:
                start = start * ms_per_dot / ms_per_dot_svp
                length = length * ms_per_dot / ms_per_dot_svp
                timing.append((start, length))

            pits = []
            pits_vsqx = datum[3]
            for time_, value in pits_vsqx:
                time_ = time_ * ms_per_dot / ms_per_dot_svp
                value = value * cents_per_pit
                pits.append((time_, value))

            csn_vsqx = datum[4]
            csn = [(time_ * ms_per_dot / ms_per_dot_svp, bol) for time_, bol in csn_vsqx]

            # its_vsqx = datum[5]

            i_to_del = []
            for i, phone in enumerate(py):
                if phone == 'sil':
                    i_to_del.append(i)
                else:
                    if py[i][-1] in '01234?':
                        py[i] = py[i][:-1]

            del_count = 0
            for i in i_to_del:
                del py[i - del_count]
                del_count += 1

            def divide_py(piny):
                # divide to cons and vow, and their corresponding phonemes
                k = piny
                try:
                    vl = DICTION[k]
                except KeyError:
                    return ('', ''), ('', '')
                if whether_cons.get(k, False):
                    if k[1] == 'h':
                        c = k[:2]  # consonant
                        v = k[2:]  # vowel
                    else:
                        c = k[0]
                        v = k[1:]
                    phs = vl.split(' ')
                    cp = phs[0]
                    vp = ' '.join(phs[1:])
                else:
                    c = ''
                    cp = ''
                    v = k
                    vp = vl
                return (c, cp), (v, vp)

            ph_lock = []
            if csn and len(csn) != len(py):
                print(f'{" ".join(py[:5])}标注有错误')
                csn = None

            data_to_write = []  # [(lrc, ph, timing)]
            if not csn or isinstance(csn[0], int):
                csn = [(0, False) for x in timing]
            for i, timing_phone in enumerate(timing):
                csn_inf = csn[i]
                csn_len = csn_inf[0]
                start_phone, len_phone = timing_phone

                if self.adjust_consonants:
                    if csn_len:
                        cons_timing = (start_phone - csn_len, csn_len)
                        cons_inf, vow_inf = divide_py(py[i])
                        cons_py, cons_ph = cons_inf
                        ph_lock.extend((len(data_to_write), len(data_to_write) + 1))
                        data_to_write.append((cons_py, cons_ph, cons_timing))

                        vow_py, vow_ph = vow_inf
                    else:
                        vow_py, vow_ph = py[i], DICTION.get(py[i], 'a')
                    try:
                        if csn[i + 1][1]:  # 这个音节的元音融合包含下一个音节的辅音
                            vowel_timing = (start_phone, len_phone - csn[i + 1][0])
                        else:
                            vowel_timing = (start_phone, len_phone)
                    except IndexError:
                        vowel_timing = (start_phone, len_phone)
                    data_to_write.append((vow_py, vow_ph, vowel_timing))
                else:
                    data_to_write.append((py[i], DICTION.get(py[i], 'a'), timing_phone))

            for i, dt in enumerate(data_to_write):
                lrc = dt[0]
                ph = dt[1]
                time_inf = dt[2]
                note = {
                    "onset": round(time_inf[0]) + dot_counter,
                    "duration": round(time_inf[1]) - 1,
                    "lyrics": lrc,
                    "phonemes": ph,
                    "pitch": height,
                    "detune": 0,
                    "attributes": {}
                }
                self.notes.append(note)
            for i_write, pit in enumerate(pits):
                # 压缩无用参数指令
                if pits[i_write - 1][1] == pit[1] and i_write:
                    continue
                self.pits.append(pit)

            # intensity
            # for i_write, it in enumerate(its):
            #     try:  # 压缩重复参数指令
            #         if its[i_write - 1][1] == it[1] and i_write:
            #             continue
            #     except IndexError:
            #         pass
            #     p = it[1]
            #     if p > 127:
            #         p = 127
            #     elif p < 0:
            #         p = 0
            #     its_text = f'\t\t\t<cc><t>{int(it[0]) + dot_counter}</t><v id="D">{int(p)}</v></cc>\n'

            if timing:
                timing_total = round(timing[-1][0] + timing[-1][1])
            else:
                timing_total = 0
            if pits:
                pits_total = round(pits[-1][0])
            else:
                pits_total = 0
            dot_counter += max(timing_total, pits_total) + interval

    def write_at(self, location):
        text = get_svp(self.notes, self.pits)
        with open(location, 'w', encoding='utf8') as f:
            f.write(text)
