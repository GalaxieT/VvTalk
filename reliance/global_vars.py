import os

VERSION = '0.0.0'
VERSION_NO = 0

default_settings = {'last_file_location': '', 'last_window_geom': '', 'step_save': True, 'interval': 1500,
                            'consonant_control': False, 'open_after_output': False, 'pbs': 17,
                            'loudness_dir': os.path.join(os.path.expanduser('~'), "Desktop"), 'forced_aligner': 'mfa',
                            'last_ver_num': VERSION_NO, 'save_dub_after_output': False, 'enable_dyn_correction': True,
                                 'output_consonants': False, 'output_format': 'vsqx'}
settings = default_settings

# .vsqx
dots_per_beat = 480  # settled by vocaloid
tempo = 12000  # beats*100 per min
ms_per_dot = 6000000 / tempo / dots_per_beat
vsqx_initial = 1  # 可能是提前几个小节
beginning_dots = dots_per_beat * vsqx_initial * 4  # by dots
pbs = settings['pbs']

def dot_to_ms(dots):
    return int(dots * ms_per_dot + 0.5)


# .svp
cents_per_pit = 100
tempo_svp = 120
dots_per_beat_svp = int(7056*1e5)
ms_per_dot_svp = 60*1000 / tempo_svp / dots_per_beat_svp

def dot_to_ms_svp(dots):
    return int(dots * ms_per_dot_svp + 0.5)


beginning_ms = dot_to_ms(beginning_dots)

whether_cons = {'a': False, 'ai': False, 'an': False, 'ang': False, 'ao': False, 'ba': True, 'bai': True, 'ban': True, 'bang': True, 'bao': True, 'bei': True, 'ben': True, 'beng': True, 'bi': True, 'bian': True, 'biao': True, 'bie': True, 'bin': True, 'bing': True, 'bo': True, 'bu': True, 'ca': True, 'cai': True, 'can': True, 'cang': True, 'cao': True, 'ce': True, 'cen': True, 'ceng': True, 'cha': True, 'chai': True, 'chan': True, 'chang': True, 'chao': True, 'che': True, 'chen': True, 'cheng': True, 'chi': True, 'chong': True, 'chou': True, 'chu': True, 'chuai': True, 'chuan': True, 'chuang': True, 'chui': True, 'chun': True, 'chuo': True, 'ci': True, 'cong': True, 'cou': True, 'cu': True, 'cuan': True, 'cui': True, 'cun': True, 'cuo': True, 'da': True, 'dai': True, 'dan': True, 'dang': True, 'dao': True, 'de': True, 'dei': True, 'den': True, 'deng': True, 'di': True, 'dia': True, 'dian': True, 'diao': True, 'die': True, 'ding': True, 'diu': True, 'dong': True, 'dou': True, 'du': True, 'duan': True, 'dui': True, 'dun': True, 'duo': True, 'e': False, 'ei': False, 'en': False, 'eng': False, 'er': False, 'fa': True, 'fan': True, 'fang': True, 'fei': True, 'fen': True, 'feng': True, 'fo': True, 'fou': True, 'fu': True, 'ga': True, 'gai': True, 'gan': True, 'gang': True, 'gao': True, 'ge': True, 'gei': True, 'gen': True, 'geng': True, 'gong': True, 'gou': True, 'gu': True, 'gua': True, 'guai': True, 'guan': True, 'guang': True, 'gui': True, 'gun': True, 'guo': True, 'ha': True, 'hai': True, 'han': True, 'hang': True, 'hao': True, 'he': True, 'hei': True, 'hen': True, 'heng': True, 'hong': True, 'hou': True, 'hu': True, 'hua': True, 'huai': True, 'huan': True, 'huang': True, 'hui': True, 'hun': True, 'huo': True, 'ji': True, 'jia': True, 'jian': True, 'jiang': True, 'jiao': True, 'jie': True, 'jin': True, 'jing': True, 'jiong': True, 'jiu': True, 'ju': True, 'juan': True, 'jue': True, 'jun': True, 'ka': True, 'kai': True, 'kan': True, 'kang': True, 'kao': True, 'ke': True, 'kei': True, 'ken': True, 'keng': True, 'kong': True, 'kou': True, 'ku': True, 'kua': True, 'kuai': True, 'kuan': True, 'kuang': True, 'kui': True, 'kun': True, 'kuo': True, 'la': True, 'lai': True, 'lan': True, 'lang': True, 'lao': True, 'le': True, 'lei': True, 'leng': True, 'li': True, 'lia': True, 'lian': True, 'liang': True, 'liao': True, 'lie': True, 'lin': True, 'ling': True, 'liu': True, 'lo': True, 'long': True, 'lou': True, 'lu': True, 'luan': True, 'lue': True, 'lun': True, 'luo': True, 'lv': True, 'lve': True, 'ma': True, 'mai': True, 'man': True, 'mang': True, 'mao': True, 'me': True, 'mei': True, 'men': True, 'meng': True, 'mi': True, 'mian': True, 'miao': True, 'mie': True, 'min': True, 'ming': True, 'miu': True, 'mo': True, 'mou': True, 'mu': True, 'na': True, 'nai': True, 'nan': True, 'nang': True, 'nao': True, 'ne': True, 'nei': True, 'nen': True, 'neng': True, 'ni': True, 'nian': True, 'niang': True, 'niao': True, 'nie': True, 'nin': True, 'ning': True, 'niu': True, 'nong': True, 'nou': True, 'nu': True, 'nuan': True, 'nue': True, 'nuo': True, 'nv': True, 'o': False, 'ou': False, 'pa': True, 'pai': True, 'pan': True, 'pang': True, 'pao': True, 'pei': True, 'pen': True, 'peng': True, 'pi': True, 'pian': True, 'piao': True, 'pie': True, 'pin': True, 'ping': True, 'po': True, 'pou': True, 'pu': True, 'qi': True, 'qia': True, 'qian': True, 'qiang': True, 'qiao': True, 'qie': True, 'qin': True, 'qing': True, 'qiong': True, 'qiu': True, 'qu': True, 'quan': True, 'que': True, 'qun': True, 'r': False, 'ran': True, 'rang': True, 'rao': True, 're': True, 'ren': True, 'reng': True, 'ri': True, 'rong': True, 'rou': True, 'ru': True, 'rua': True, 'ruan': True, 'rui': True, 'run': True, 'ruo': True, 'sa': True, 'sai': True, 'san': True, 'sang': True, 'sao': True, 'se': True, 'sen': True, 'seng': True, 'sha': True, 'shai': True, 'shan': True, 'shang': True, 'shao': True, 'she': True, 'shei': True, 'shen': True, 'sheng': True, 'shi': True, 'shou': True, 'shu': True, 'shua': True, 'shuai': True, 'shuan': True, 'shuang': True, 'shui': True, 'shun': True, 'shuo': True, 'si': True, 'song': True, 'sou': True, 'su': True, 'suan': True, 'sui': True, 'sun': True, 'suo': True, 'ta': True, 'tai': True, 'tan': True, 'tang': True, 'tao': True, 'te': True, 'tei': True, 'teng': True, 'ti': True, 'tian': True, 'tiao': True, 'tie': True, 'ting': True, 'tong': True, 'tou': True, 'tu': True, 'tuan': True, 'tui': True, 'tun': True, 'tuo': True, 'wa': False, 'wai': False, 'wan': False, 'wang': False, 'wei': False, 'wen': False, 'weng': False, 'wo': False, 'wu': False, 'xi': True, 'xia': True, 'xian': True, 'xiang': True, 'xiao': True, 'xie': True, 'xin': True, 'xing': True, 'xiong': True, 'xiu': True, 'xu': True, 'xuan': True, 'xue': True, 'xun': True, 'ya': False, 'yan': False, 'yang': False, 'yao': False, 'ye': False, 'yi': False, 'yin': False, 'ying': False, 'yo': False, 'yong': False, 'you': False, 'yu': False, 'yuan': False, 'yue': False, 'yun': False, 'za': True, 'zai': True, 'zan': True, 'zang': True, 'zao': True, 'ze': True, 'zei': True, 'zen': True, 'zeng': True, 'zha': True, 'zhai': True, 'zhan': True, 'zhang': True, 'zhao': True, 'zhe': True, 'zhei': True, 'zhen': True, 'zheng': True, 'zhi': True, 'zhong': True, 'zhou': True, 'zhu': True, 'zhua': True, 'zhuai': True, 'zhuan': True, 'zhuang': True, 'zhui': True, 'zhun': True, 'zhuo': True, 'zi': True, 'zong': True, 'zou': True, 'zu': True, 'zuan': True, 'zui': True, 'zun': True, 'zuo': True}


if __name__ == '__main__':
    print(ms_per_dot*120)