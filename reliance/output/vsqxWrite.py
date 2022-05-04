from reliance.global_vars import ms_per_dot, tempo

DICTION = {'a': 'a', 'ai': 'aI', 'an': 'a_n', 'ang': 'AN', 'ao': 'AU', 'shi': 's` i`', 'liu': 'l i@U', 'ge': 'k 7',
           'ba': 'p a', 'bai': 'p aI', 'ban': 'p a_n', 'bang': 'p AN', 'bao': 'p AU', 'bei': 'p ei', 'ben': 'p @_n',
           'beng': 'p @N', 'bi': 'p i', 'bian': 'p iE_n', 'biao': 'p iAU', 'bie': 'p iE_r', 'bin': 'p i_n',
           'bing': 'p iN', 'po': 'p_h o', 'bo': 'p o', 'bu': 'p u', 'san': 's a_n', 'si': 's i\\', 'ca': 'ts_h a',
           'cai': 'ts_h aI', 'can': 'ts_h a_n', 'cang': 'ts_h AN', 'cao': 'ts_h AU', 'ce': 'ts_h 7', 'cen': 'ts_h @_n',
           'ceng': 'ts_h @N', 'cha': 'ts`_h a', 'chai': 'ts`_h aI', 'chan': 'ts`_h a_n', 'chang': 'ts`_h AN',
           'zhang': 'ts` AN', 'chao': 'ts`_h AU', 'che': 'ts`_h 7', 'chen': 'ts`_h @_n', 'cheng': 'ts`_h @N',
           'chi': 'ts`_h i`', 'chong': 'ts`_h UN', 'chou': 'ts`_h @U', 'chu': 'ts`_h u', 'chuai': 'ts`_h uaI',
           'chuan': 'ts`_h ua_n', 'chuang': 'ts`_h uAN', 'chui': 'ts`_h uei', 'chun': 'ts`_h u@_n', 'chuo': 'ts`_h uo',
           'ci': 'ts_h i\\', 'cong': 'ts_h UN', 'cou': 'ts_h @U', 'cu': 'ts_h u', 'cuan': 'ts_h ua_n',
           'cui': 'ts_h uei', 'cun': 'ts_h u@_n', 'cuo': 'ts_h uo', 'er': '@`', 'da': 't a', 'dai': 't aI',
           'dan': 't a_n', 'dang': 't AN', 'dao': 't AU', 'de': 't 7', 'deng': 't @N', 'di': 't i', 'dian': 't iE_n',
           'diao': 't iAU', 'die': 't iE_r', 'ding': 't iN', 'diu': 't i@U', 'dong': 't UN', 'dou': 't @U', 'du': 't u',
           'duan': 't ua_n', 'dui': 't uei', 'dun': 't u@_n', 'duo': 't uo', 'e': '7', 'en': '@_n', 'jiu': 'ts\\ i@U',
           'fa': 'f a', 'fan': 'f a_n', 'fang': 'f AN', 'fei': 'f ei', 'fen': 'f @_n', 'feng': 'f @N', 'fu': 'f u',
           'fou': 'f @U', 'ga': 'k a', 'gai': 'k aI', 'gan': 'k a_n', 'gang': 'k AN', 'gao': 'k AU', 'gei': 'k ei',
           'gen': 'k @_n', 'geng': 'k @N', 'gong': 'k UN', 'gou': 'k @U', 'gu': 'k u', 'gua': 'k ua', 'guai': 'k uaI',
           'guan': 'k ua_n', 'guang': 'k uAN', 'gui': 'k uei', 'gun': 'k u@_n', 'guo': 'k uo', 'ha': 'x a',
           'hai': 'x aI', 'han': 'x a_n', 'xing': 's\\ iN', 'hang': 'x AN', 'hao': 'x AU', 'he': 'x 7', 'hei': 'x ei',
           'hen': 'x @_n', 'heng': 'x @N', 'hong': 'x UN', 'hou': 'x @U', 'hu': 'x u', 'hua': 'x ua', 'huai': 'x uaI',
           'huan': 'x ua_n', 'huang': 'x uAN', 'hui': 'x uei', 'hun': 'x u@_n', 'huo': 'x uo', 'ji': 'ts\\ i',
           'jia': 'ts\\ ia', 'jian': 'ts\\ iE_n', 'jiang': 'ts\\ iAN', 'jiao': 'ts\\ iAU', 'jie': 'ts\\ iE_r',
           'jin': 'ts\\ i_n', 'jing': 'ts\\ iN', 'qing': 'ts\\_h iN', 'jiong': 'ts\\ iUN', 'ju': 'ts\\ y',
           'juan': 'ts\\ y{_n', 'jue': 'ts\\ yE_r', 'jun': 'ts\\ y_n', 'ka': 'k_h a', 'kai': 'k_h aI', 'kan': 'k_h a_n',
           'kang': 'k_h AN', 'kao': 'k_h AU', 'ke': 'k_h 7', 'ken': 'k_h @_n', 'keng': 'k_h @N', 'kong': 'k_h UN',
           'kou': 'k_h @U', 'ku': 'k_h u', 'kua': 'k_h ua', 'kuai': 'k_h uaI', 'kuan': 'k_h ua_n', 'kuang': 'k_h uAN',
           'kui': 'k_h uei', 'kun': 'k_h u@_n', 'kuo': 'k_h uo', 'wu': 'u', 'la': 'l a', 'lai': 'l aI', 'lan': 'l a_n',
           'lang': 'l AN', 'lao': 'l AU', 'le': 'l 7', 'lei': 'l ei', 'leng': 'l @N', 'li': 'l i', 'lia': 'l ia',
           'lian': 'l iE_n', 'liang': 'l iAN', 'liao': 'l iAU', 'lie': 'l iE_r', 'lin': 'l i_n', 'ling': 'l iN',
           'long': 'l UN', 'lou': 'l @U', 'lu': 'l u', 'lv': 'l y', 'luan': 'l ua_n', 'lve': 'l yE_r', 'lun': 'l u@_n',
           'luo': 'l uo', 'ma': 'm a', 'mai': 'm aI', 'man': 'm a_n', 'mang': 'm AN', 'mao': 'm AU', 'me': 'm 7',
           'mei': 'm ei', 'men': 'm @_n', 'meng': 'm @N', 'mi': 'm i', 'mian': 'm iE_n', 'miao': 'm iAU',
           'mie': 'm iE_r', 'min': 'm i_n', 'ming': 'm iN', 'mo': 'm o', 'mou': 'm @U', 'mu': 'm u', 'na': 'n a',
           'nai': 'n aI', 'nan': 'n a_n', 'nang': 'n AN', 'nao': 'n AU', 'nei': 'n ei', 'nen': 'n @_n', 'neng': 'n @N',
           'ni': 'n i', 'nian': 'n iE_n', 'niang': 'n iAN', 'niao': 'n iAU', 'nie': 'n iE_r', 'nin': 'n i_n',
           'ning': 'n iN', 'niu': 'n i@U', 'nong': 'n UN', 'nu': 'n u', 'nv': 'n y', 'nuan': 'n ua_n', 'nve': 'n yE_r',
           'nuo': 'n uo', 'yi': 'i', 'ou': '@U', 'qi': 'ts\\_h i', 'pa': 'p_h a', 'pai': 'p_h aI', 'pan': 'p_h a_n',
           'pang': 'p_h AN', 'pao': 'p_h AU', 'pei': 'p_h ei', 'pen': 'p_h @_n', 'peng': 'p_h @N', 'pi': 'p_h i',
           'pian': 'p_h iE_n', 'piao': 'p_h iAU', 'pie': 'p_h iE_r', 'pin': 'p_h i_n', 'ping': 'p_h iN',
           'pou': 'p_h @U', 'pu': 'p_h u', 'qia': 'ts\\_h ia', 'qian': 'ts\\_h iE_n', 'qiang': 'ts\\_h iAN',
           'qiao': 'ts\\_h iAU', 'qin': 'ts\\_h i_n', 'qiong': 'ts\\_h iUN', 'qiu': 'ts\\_h i@U', 'qu': 'ts\\_h y',
           'quan': 'ts\\_h y{_n', 'que': 'ts\\_h yE_r', 'qun': 'ts\\_h y_n', 'ran': 'z` a_n', 'rang': 'z` AN',
           'rao': 'z` AU', 're': 'z` 7', 'ren': 'z` @_n', 'reng': 'z` @N', 'ri': 'z` i`', 'rong': 'z` UN',
           'rou': 'z` @U', 'ru': 'z` u', 'ruan': 'z` ua_n', 'rui': 'z` uei', 'run': 'z` u@_n', 'ruo': 'z` uo',
           'sa': 's a', 'sai': 's aI', 'sang': 's AN', 'sao': 's AU', 'se': 's 7', 'sen': 's @_n', 'seng': 's @N',
           'sha': 's` a', 'shai': 's` aI', 'shan': 's` a_n', 'shang': 's` AN', 'shao': 's` AU', 'she': 's` 7',
           'shen': 's` @_n', 'sheng': 's` @N', 'shou': 's` @U', 'shu': 's` u', 'shua': 's` ua', 'shuai': 's` uaI',
           'shuan': 's` ua_n', 'shuang': 's` uAN', 'shui': 's` uei', 'shun': 's` u@_n', 'shuo': 's` uo', 'song': 's UN',
           'sou': 's @U', 'su': 's u', 'suan': 's ua_n', 'sui': 's uei', 'sun': 's u@_n', 'suo': 's uo', 'ta': 't_h a',
           'tai': 't_h aI', 'tan': 't_h a_n', 'tang': 't_h AN', 'tao': 't_h AU', 'te': 't_h 7', 'teng': 't_h @N',
           'ti': 't_h i', 'tian': 't_h iE_n', 'tiao': 't_h iAU', 'tie': 't_h iE_r', 'ting': 't_h iN', 'tong': 't_h UN',
           'tou': 't_h @U', 'tu': 't_h u', 'tuan': 't_h ua_n', 'tui': 't_h uei', 'tun': 't_h u@_n', 'wa': 'ua',
           'wai': 'uaI', 'wan': 'ua_n', 'wang': 'uAN', 'wei': 'uei', 'wen': 'u@_n', 'weng': 'u@N', 'wo': 'uo',
           'xi': 's\\ i', 'xia': 's\\ ia', 'xian': 's\\ iE_n', 'xiang': 's\\ iAN', 'xiao': 's\\ iAU', 'xie': 's\\ iE_r',
           'xin': 's\\ i_n', 'xiong': 's\\ iUN', 'xiu': 's\\ i@U', 'xu': 's\\ y', 'xuan': 's\\ y{_n', 'xue': 's\\ yE_r',
           'xun': 's\\ y_n', 'ya': 'ia', 'yan': 'iE_n', 'yang': 'iAN', 'yao': 'iAU', 'ye': 'iE_r', 'yin': 'i_n',
           'ying': 'iN', 'you': 'i@U', 'yong': 'iUN', 'yu': 'y', 'yuan': 'y{_n', 'yue': 'yE_r', 'yun': 'y_n',
           'za': 'ts a', 'zai': 'ts aI', 'zan': 'ts a_n', 'zang': 'ts AN', 'zao': 'ts AU', 'ze': 'ts 7', 'zei': 'ts ei',
           'zen': 'ts @_n', 'zeng': 'ts @N', 'zha': 'ts` a', 'zhai': 'ts` aI', 'zhan': 'ts` a_n', 'zhao': 'ts` AU',
           'zhe': 'ts` 7', 'zhen': 'ts` @_n', 'zheng': 'ts` @N', 'zhi': 'ts` i`', 'zhong': 'ts` UN', 'zhou': 'ts` @U',
           'zhu': 'ts` u', 'zhua': 'ts` ua', 'zhuai': 'ts` uaI', 'zhuan': 'ts` ua_n', 'zhuang': 'ts` uAN',
           'zhui': 'ts` uei', 'zhun': 'ts` u@_n', 'zhuo': 'ts` uo', 'zi': 'ts i\\', 'zong': 'ts UN', 'zou': 'ts @U',
           'zu': 'ts u', 'zuan': 'ts ua_n', 'zui': 'ts uei', 'zun': 'ts u@_n', 'zuo': 'ts uo', 'shei': 's` ei',
           'chua': 'ts`_h ua', 'dei': 't ei', 'den': 't @_n', 'ne': 'n 7', 'dia': 't ia', 'fo': 'f o', 'lo': 'l o',
           'miu': 'm i@U', 'nou': 'n @U', 'o': 'o', 'qie': 'ts\\_h iE_r', 'tuo': 't_h uo', 'zhei': 'ts` ei', 'ei': 'ei',
           'kei': 'k_h ei'}
CONSONANTS = {'sh': 's`', 'l': 'l', 'g': 'k', 'b': 'p', 'p': 'p_h', 's': 's', 'c': 'ts_h', 'ch': 'ts`_h', 'zh': 'ts`',
              'd': 't', 'j': 'ts\\', 'f': 'f', 'h': 'x', 'x': 's\\', 'q': 'ts\\_h', 'k': 'k_h', 'm': 'm', 'n': 'n',
              'r': 'z`', 't': 't_h', 'z': 'ts'}
VOWELS = {'a': 'a', 'ai': 'aI', 'an': 'a_n', 'ang': 'AN', 'ao': 'AU', 'i': 'i\\', 'iu': 'i@U', 'e': '7', 'ei': 'ei',
          'en': '@_n', 'eng': '@N', 'ian': 'iE_n', 'iao': 'iAU', 'ie': 'iE_r', 'in': 'i_n', 'ing': 'iN', 'o': 'o',
          'u': 'u', 'ong': 'UN', 'ou': '@U', 'uai': 'uaI', 'uan': 'ua_n', 'uang': 'uAN', 'ui': 'uei', 'un': 'u@_n',
          'uo': 'uo', 'er': '@`', 'ua': 'ua', 'ia': 'ia', 'iang': 'iAN', 'iong': 'iUN', 'ue': 'yE_r', 'wu': 'u',
          'v': 'y', 've': 'yE_r', 'yi': 'i', 'wa': 'ua', 'wai': 'uaI', 'wan': 'ua_n', 'wang': 'uAN', 'wei': 'uei',
          'wen': 'u@_n', 'weng': 'u@N', 'wo': 'uo', 'ya': 'ia', 'yan': 'iE_n', 'yang': 'iAN', 'yao': 'iAU',
          'ye': 'iE_r', 'yin': 'i_n', 'ying': 'iN', 'you': 'i@U', 'yong': 'iUN', 'yu': 'y', 'yuan': 'y{_n',
          'yue': 'yE_r', 'yun': 'y_n'}


class Writer:
    def __init__(self, data, adjust_consonants=False, height=65, interval=1000, pbs=17, final=1500):
        self.adjust_consonants = adjust_consonants
        interval = int(interval / ms_per_dot)
        final = int(final / ms_per_dot)
        dot_counter = 0
        self.note_texts = []
        self.pit_texts = []
        self.its_texts = []
        for datum in data:
            ch = datum[0]
            py = datum[1]
            timing = list(datum[2])
            pits = datum[3]
            # print(adjust_consonants)

            csn = datum[4]

            its = datum[5]
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
                phs = vl.split(' ')  # 在vsqx词典中，韵母一定只有一个音素符号
                if len(phs) > 1:
                    if k[1] == 'h':
                        c = k[:2]  # consonant
                        v = k[2:]  # vowel
                    else:
                        c = k[0]
                        v = k[1:]
                    cp = phs[0]
                    vp = phs[1]
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
                # 非必要的条目只留一个，再少会报错
                if i in ph_lock:
                    lock_text = ' lock="1"'
                else:
                    lock_text = ''
                note = f"""\t\t\t<note>
\t\t\t\t<t>{round(time_inf[0]) + dot_counter}</t>
\t\t\t\t<dur>{round(time_inf[1]) - 1}</dur>
\t\t\t\t<n>{height}</n>
\t\t\t\t<v>{64}</v>
\t\t\t\t<y><![CDATA[{lrc}]]></y>
\t\t\t\t<p{lock_text}><![CDATA[{ph}]]></p>
\t\t\t\t<nStyle>
\t\t\t\t\t<v id="accent">50</v>
\t\t\t\t</nStyle>
\t\t\t</note>
"""
                self.note_texts.append(note)
            for i_write, pit in enumerate(pits):
                # 压缩无用参数指令
                if pits[i_write - 1][1] == pit[1] and i_write:
                    continue
                p = pit[1] / pbs * 8190
                if p > 8190:
                    p = 8190
                elif p < -8190:
                    p = -8190
                pit_text = f'\t\t\t<cc><t>{int(pit[0]) + dot_counter}</t><v id="P">{int(p)}</v></cc>\n'
                self.pit_texts.append(pit_text)
            for i_write, it in enumerate(its):
                try:  # 压缩重复参数指令
                    if its[i_write - 1][1] == it[1] and i_write:
                        continue
                except IndexError:
                    pass
                p = it[1]
                if p > 127:
                    p = 127
                elif p < 0:
                    p = 0
                its_text = f'\t\t\t<cc><t>{int(it[0]) + dot_counter}</t><v id="D">{int(p)}</v></cc>\n'
                self.its_texts.append(its_text)
            if timing:
                timing_total = round(timing[-1][0] + timing[-1][1])
            else:
                timing_total = 0
            if pits:
                pits_total = round(pits[-1][0])
            else:
                pits_total = 0
            dot_counter += max(timing_total, pits_total) + interval
        self.file_head = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<vsq4 xmlns="http://www.yamaha.co.jp/vocaloid/schema/vsq4/"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://www.yamaha.co.jp/vocaloid/schema/vsq4/ vsq4.xsd">
	<vender><![CDATA[Yamaha corporation]]></vender>
	<version><![CDATA[4.0.0.3]]></version>
	<vVoiceTable>
		<vVoice>
			<bs>4</bs>
			<pc>0</pc>
			<id><![CDATA[BK8H76TAEHXWSKDB]]></id>
			<name><![CDATA[Luotianyi_CHN_Meng]]></name>
			<vPrm>
				<bre>0</bre>
				<bri>0</bri>
				<cle>0</cle>
				<gen>0</gen>
				<ope>0</ope>
			</vPrm>
		</vVoice>
	</vVoiceTable>
	<mixer>
		<masterUnit>
			<oDev>0</oDev>
			<rLvl>0</rLvl>
			<vol>0</vol>
		</masterUnit>
		<vsUnit>
			<tNo>0</tNo>
			<iGin>0</iGin>
			<sLvl>-898</sLvl>
			<sEnable>0</sEnable>
			<m>0</m>
			<s>0</s>
			<pan>64</pan>
			<vol>0</vol>
		</vsUnit>
		<monoUnit>
			<iGin>0</iGin>
			<sLvl>-898</sLvl>
			<sEnable>0</sEnable>
			<m>0</m>
			<s>0</s>
			<pan>64</pan>
			<vol>0</vol>
		</monoUnit>
		<stUnit>
			<iGin>0</iGin>
			<m>0</m>
			<s>0</s>
			<vol>-129</vol>
		</stUnit>
	</mixer>
	<masterTrack>
		<seqName><![CDATA[Untitled0]]></seqName>
		<comment><![CDATA[New VSQ File]]></comment>
		<resolution>480</resolution>
		<preMeasure>0</preMeasure>
		<timeSig><m>0</m><nu>4</nu><de>4</de></timeSig>
		<tempo><t>0</t><v>''' + str(tempo) + '''</v></tempo>
	</masterTrack>
	<vsTrack>
		<tNo>0</tNo>
		<name><![CDATA[Track]]></name>
		<comment><![CDATA[Track]]></comment>
		<vsPart>
			<t>1920</t>
			<playTime>''' + str(dot_counter + final) + '''</playTime>
			<name><![CDATA[NewPart]]></name>
			<comment><![CDATA[New Musical Part]]></comment>
			<sPlug>
				<id><![CDATA[ACA9C502-A04B-42b5-B2EB-5CEA36D16FCE]]></id>
				<name><![CDATA[VOCALOID2 Compatible Style]]></name>
				<version><![CDATA[3.0.0.1]]></version>
			</sPlug>
			<pStyle>
				<v id="accent">50</v>
				<v id="bendDep">8</v>
				<v id="bendLen">0</v>
				<v id="decay">50</v>
				<v id="fallPort">0</v>
				<v id="opening">127</v>
				<v id="risePort">0</v>
			</pStyle>
			<singer>
				<t>0</t>
				<bs>4</bs>
				<pc>0</pc>
			</singer>
\t\t\t<cc><t>1</t><v id="S">''' + str(pbs) + '''</v></cc>\n'''
        self.file_tail = '''
        </vsPart>
	</vsTrack>
	<monoTrack>
	</monoTrack>
	<stTrack>
	</stTrack>
	<aux>
		<id><![CDATA[AUX_VST_HOST_CHUNK_INFO]]></id>
		<content><![CDATA[VlNDSwAAAAADAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=]]></content>
	</aux>
</vsq4>
'''

    def write_at(self, location):
        with open(location, 'w', encoding='utf-8') as f:
            f.write(self.file_head)
            for pt in self.pit_texts:
                f.write(pt)
            for it in self.its_texts:
                f.write(it)
            for nt in self.note_texts:
                f.write(nt)
            f.write(self.file_tail)
