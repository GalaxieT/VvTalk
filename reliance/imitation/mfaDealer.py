# mfa输入：源文件所在目录，dict和model各自目录，输出目录
# mfa模型没有ei5和iao5
import os

import praatio.utilities.constants
from praatio import textgrid

DIR = {'storage': 'misc\\mfa\\MFA',
       'temp': 'misc\\temp\\mfa_temp\\',
       'working': 'misc\\temp\\mfa_temp\\working',
       'diction': 'misc\\mfa\\mfa_model_v20.dict',
       # 'diction': 'misc/mfa/mandarin-for-montreal-forced-aligner-pre-trained-model.dict',
       'model': 'misc\\mfa\\mandarin_mfa.zip',
       # 'model': 'misc/mfa/mandarin.zip',
       'source': 'misc\\temp\\mfa_temp\\source',
       'output': 'misc\\temp\\mfa_temp\\output',
       'config': 'misc\\mfa\\config.yaml',
       # 'install_bat': 'misc\\mfa\\install_mfa_data.bat'
       }
# cd到mfa资源目录，利用工作目录让修改后的mfa脚本确定所需资源文件夹的绝对位置
batch_start = 'cd misc\\mfa' \
              + '\n' + os.path.abspath('misc\\python\\python.exe') + ' ' + \
              os.path.abspath('misc\\python\\Scripts\\mfa.exe') + ' '

mfa_root_environ_name = 'MFA_ROOT_DIR'
os.environ[mfa_root_environ_name] = os.path.abspath(DIR['storage'])
from montreal_forced_aligner.command_line.mfa import create_parser, run_align_corpus

# (辅音音素数量，总音素数量)
phone_lengths = {'n': (0, 1), 'sp': (0, 1), 'spn': (0, 1), 'a': (0, 2), 'ai': (0, 2), 'an': (0, 3), 'ang': (0, 3), 'ao': (0, 2), 'ba': (1, 2), 'bai': (1, 2), 'ban': (1, 3), 'bang': (1, 3), 'bao': (1, 3), 'bei': (1, 2), 'ben': (1, 3), 'beng': (1, 3), 'bi': (1, 2), 'bian': (1, 4), 'biao': (1, 3), 'bie': (1, 3), 'bin': (1, 3), 'bing': (1, 3), 'bo': (1, 3), 'bu': (1, 2), 'ca': (1, 2), 'cai': (1, 2), 'can': (1, 3), 'cang': (1, 3), 'cao': (1, 2), 'ce': (1, 2), 'cen': (1, 3), 'ceng': (1, 3), 'cha': (1, 2), 'chai': (1, 2), 'chan': (1, 3), 'chang': (1, 3), 'chao': (1, 2), 'che': (1, 2), 'chen': (1, 3), 'cheng': (1, 3), 'chi': (1, 2), 'chong': (1, 3), 'chou': (1, 2), 'chu': (1, 2), 'chuai': (1, 3), 'chuan': (1, 4), 'chuang': (1, 4), 'chui': (1, 3), 'chun': (1, 4), 'chuo': (1, 3), 'ci': (1, 2), 'cong': (1, 3), 'cou': (1, 2), 'cu': (1, 2), 'cuan': (1, 4), 'cui': (1, 3), 'cun': (1, 4), 'cuo': (1, 3), 'da': (1, 2), 'dai': (1, 2), 'dan': (1, 3), 'dang': (1, 3), 'dao': (1, 2), 'de': (1, 2), 'dei': (1, 2), 'den': (1, 3), 'deng': (1, 3), 'di': (1, 2), 'dia': (1, 3), 'dian': (1, 4), 'diao': (1, 3), 'die': (1, 3), 'ding': (1, 3), 'diu': (1, 3), 'dong': (1, 3), 'dou': (1, 2), 'du': (1, 2), 'duan': (1, 4), 'dui': (1, 3), 'dun': (1, 4), 'duo': (1, 3), 'e': (0, 2), 'ei': (0, 2), 'en': (0, 3), 'eng': (0, 2), 'er': (0, 3), 'fa': (1, 2), 'fan': (1, 3), 'fang': (1, 3), 'fei': (1, 2), 'fen': (1, 3), 'feng': (1, 3), 'fo': (1, 3), 'fou': (1, 2), 'fu': (1, 2), 'ga': (1, 2), 'gai': (1, 2), 'gan': (1, 3), 'gang': (1, 3), 'gao': (1, 2), 'ge': (1, 2), 'gei': (1, 2), 'gen': (1, 3), 'geng': (1, 3), 'gong': (1, 3), 'gou': (1, 2), 'gu': (1, 2), 'gua': (1, 3), 'guai': (1, 3), 'guan': (1, 4), 'guang': (1, 4), 'gui': (1, 3), 'gun': (1, 4), 'guo': (1, 3), 'ha': (1, 2), 'hai': (1, 2), 'han': (1, 3), 'hang': (1, 3), 'hao': (1, 2), 'he': (1, 2), 'hei': (1, 2), 'hen': (1, 3), 'heng': (1, 3), 'hong': (1, 3), 'hou': (1, 2), 'hu': (1, 2), 'hua': (1, 3), 'huai': (1, 3), 'huan': (1, 4), 'huang': (1, 4), 'hui': (1, 3), 'hun': (1, 4), 'huo': (1, 3), 'ji': (1, 2), 'jia': (1, 3), 'jian': (1, 4), 'jiang': (1, 4), 'jiao': (1, 3), 'jie': (1, 3), 'jin': (1, 3), 'jing': (1, 3), 'jiong': (1, 4), 'jiu': (1, 3), 'ju': (1, 2), 'juan': (1, 4), 'jue': (1, 3), 'jun': (1, 3), 'ka': (1, 2), 'kai': (1, 2), 'kan': (1, 3), 'kang': (1, 3), 'kao': (1, 2), 'ke': (1, 2), 'kei': (1, 2), 'ken': (1, 3), 'keng': (1, 3), 'kong': (1, 3), 'kou': (1, 2), 'ku': (1, 2), 'kua': (1, 3), 'kuai': (1, 3), 'kuan': (1, 4), 'kuang': (1, 4), 'kui': (1, 3), 'kun': (1, 4), 'kuo': (1, 3), 'la': (1, 2), 'lai': (1, 2), 'lan': (1, 3), 'lang': (1, 3), 'lao': (1, 2), 'le': (1, 2), 'lei': (1, 2), 'leng': (1, 3), 'li': (1, 2), 'lia': (1, 4), 'lian': (1, 4), 'liang': (1, 4), 'liao': (1, 3), 'lie': (1, 3), 'lin': (1, 3), 'ling': (1, 3), 'liu': (1, 3), 'lo': (1, 2), 'long': (1, 3), 'lou': (1, 2), 'lu': (1, 2), 'luan': (1, 4), 'lue': (1, 3), 'lun': (1, 4), 'luo': (1, 3), 'lv': (1, 2), 'lve': (1, 3), 'ma': (1, 2), 'mai': (1, 2), 'man': (1, 3), 'mang': (1, 3), 'mao': (1, 2), 'me': (1, 2), 'mei': (1, 2), 'men': (1, 3), 'meng': (1, 3), 'mi': (1, 2), 'mian': (1, 4), 'miao': (1, 3), 'mie': (1, 3), 'min': (1, 3), 'ming': (1, 3), 'miu': (1, 3), 'mo': (1, 3), 'mou': (1, 2), 'mu': (1, 3), 'na': (1, 2), 'nai': (1, 2), 'nan': (1, 3), 'nang': (1, 3), 'nao': (1, 2), 'ne': (1, 2), 'nei': (1, 2), 'nen': (1, 3), 'neng': (1, 3), 'ni': (1, 2), 'nian': (1, 4), 'niang': (1, 4), 'niao': (1, 3), 'nie': (1, 3), 'nin': (1, 3), 'ning': (1, 3), 'niu': (1, 3), 'nong': (1, 3), 'nou': (1, 2), 'nu': (1, 2), 'nuan': (1, 4), 'nue': (1, 3), 'nuo': (1, 3), 'nv': (1, 2), 'o': (0, 2), 'ou': (0, 2), 'pa': (1, 2), 'pai': (1, 2), 'pan': (1, 3), 'pang': (1, 3), 'pao': (1, 2), 'pei': (1, 2), 'pen': (1, 3), 'peng': (1, 3), 'pi': (1, 2), 'pian': (1, 4), 'piao': (1, 3), 'pie': (1, 3), 'pin': (1, 3), 'ping': (1, 3), 'po': (1, 3), 'pou': (1, 2), 'pu': (1, 2), 'qi': (1, 2), 'qia': (1, 3), 'qian': (1, 4), 'qiang': (1, 4), 'qiao': (1, 3), 'qie': (1, 3), 'qin': (1, 3), 'qing': (1, 3), 'qiong': (1, 4), 'qiu': (1, 3), 'qu': (1, 2), 'quan': (1, 4), 'que': (1, 3), 'qun': (1, 3), 'r': (0, 1), 'ran': (1, 3), 'rang': (1, 3), 'rao': (1, 2), 're': (1, 2), 'ren': (1, 3), 'reng': (1, 3), 'ri': (0, 1), 'rong': (1, 3), 'rou': (1, 2), 'ru': (1, 2), 'rua': (1, 3), 'ruan': (1, 4), 'rui': (1, 3), 'run': (1, 4), 'ruo': (1, 3), 'sa': (1, 2), 'sai': (1, 2), 'san': (1, 3), 'sang': (1, 3), 'sao': (1, 2), 'se': (1, 2), 'sen': (1, 3), 'seng': (1, 3), 'sha': (1, 2), 'shai': (1, 2), 'shan': (1, 3), 'shang': (1, 3), 'shao': (1, 2), 'she': (1, 2), 'shei': (1, 2), 'shen': (1, 3), 'sheng': (1, 3), 'shi': (1, 2), 'shou': (1, 2), 'shu': (1, 2), 'shua': (1, 3), 'shuai': (1, 3), 'shuan': (1, 4), 'shuang': (1, 4), 'shui': (1, 3), 'shun': (1, 4), 'shuo': (1, 3), 'si': (1, 2), 'song': (1, 3), 'sou': (1, 2), 'su': (1, 2), 'suan': (1, 4), 'sui': (1, 3), 'sun': (1, 4), 'suo': (1, 3), 'ta': (1, 2), 'tai': (1, 2), 'tan': (1, 3), 'tang': (1, 3), 'tao': (1, 2), 'te': (1, 2), 'tei': (1, 2), 'teng': (1, 3), 'ti': (1, 2), 'tian': (1, 4), 'tiao': (1, 3), 'tie': (1, 3), 'ting': (1, 3), 'tong': (1, 3), 'tou': (1, 2), 'tu': (1, 2), 'tuan': (1, 4), 'tui': (1, 3), 'tun': (1, 4), 'tuo': (1, 3), 'wa': (0, 2), 'wai': (0, 2), 'wan': (0, 3), 'wang': (0, 3), 'wei': (0, 2), 'wen': (0, 3), 'weng': (0, 3), 'wo': (0, 2), 'wu': (0, 1), 'xi': (1, 2), 'xia': (1, 3), 'xian': (1, 4), 'xiang': (1, 4), 'xiao': (1, 3), 'xie': (1, 3), 'xin': (1, 3), 'xing': (1, 3), 'xiong': (1, 4), 'xiu': (1, 3), 'xu': (1, 2), 'xuan': (1, 4), 'xue': (1, 3), 'xun': (1, 3), 'ya': (0, 2), 'yan': (0, 3), 'yang': (0, 3), 'yao': (0, 2), 'ye': (0, 2), 'yi': (0, 1), 'yin': (0, 2), 'ying': (0, 2), 'yo': (0, 2), 'yong': (0, 3), 'you': (0, 2), 'yu': (0, 1), 'yuan': (0, 3), 'yue': (0, 2), 'yun': (0, 2), 'za': (1, 2), 'zai': (1, 2), 'zan': (1, 3), 'zang': (1, 3), 'zao': (1, 3), 'ze': (1, 2), 'zei': (1, 2), 'zen': (1, 3), 'zeng': (1, 3), 'zha': (1, 2), 'zhai': (1, 2), 'zhan': (1, 3), 'zhang': (1, 3), 'zhao': (1, 2), 'zhe': (1, 2), 'zhei': (1, 2), 'zhen': (1, 3), 'zheng': (1, 3), 'zhi': (1, 2), 'zhong': (1, 3), 'zhou': (1, 2), 'zhu': (1, 2), 'zhua': (1, 3), 'zhuai': (1, 2), 'zhuan': (1, 4), 'zhuang': (1, 4), 'zhui': (1, 3), 'zhun': (1, 4), 'zhuo': (1, 3), 'zi': (1, 2), 'zong': (1, 3), 'zou': (1, 2), 'zu': (1, 2), 'zuan': (1, 4), 'zui': (1, 3), 'zun': (1, 4), 'zuo': (1, 3), 'sil': (0, 1), 'kiu': (1, 3), 'nve': (1, 3), 'nia': (1, 3)}
# phone_lengths = {'n': (0, 2), 'sp': (0, 1), 'spn': (0, 1), 'a': (0, 1), 'ai': (0, 1), 'an': (0, 2), 'ang': (0, 2),
#                  'ao': (0, 1), 'ba': (1, 2), 'bai': (1, 2), 'ban': (1, 3), 'bang': (1, 3), 'bao': (1, 2), 'bei': (1, 2),
#                  'ben': (1, 3), 'beng': (1, 3), 'bi': (1, 2), 'bian': (1, 3), 'biao': (1, 2), 'bie': (1, 2),
#                  'bin': (1, 3), 'bing': (1, 3), 'bo': (1, 2), 'bu': (1, 2), 'ca': (1, 2), 'cai': (1, 2), 'can': (1, 3),
#                  'cang': (1, 3), 'cao': (1, 2), 'ce': (1, 2), 'cen': (1, 3), 'ceng': (1, 3), 'cha': (1, 2),
#                  'chai': (1, 2), 'chan': (1, 3), 'chang': (1, 3), 'chao': (1, 2), 'che': (1, 2), 'chen': (1, 3),
#                  'cheng': (1, 3), 'chi': (1, 2), 'chong': (1, 3), 'chou': (1, 2), 'chu': (1, 2), 'chuai': (1, 2),
#                  'chuan': (1, 3), 'chuang': (1, 3), 'chui': (1, 2), 'chun': (1, 3), 'chuo': (1, 2), 'ci': (1, 2),
#                  'cong': (1, 3), 'cou': (1, 2), 'cu': (1, 2), 'cuan': (1, 3), 'cui': (1, 2), 'cun': (1, 3),
#                  'cuo': (1, 2), 'da': (1, 2), 'dai': (1, 2), 'dan': (1, 3), 'dang': (1, 3), 'dao': (1, 2), 'de': (1, 2),
#                  'dei': (1, 2), 'den': (1, 3), 'deng': (1, 3), 'di': (1, 2), 'dia': (1, 2), 'dian': (1, 3),
#                  'diao': (1, 2), 'die': (1, 2), 'ding': (1, 3), 'diu': (1, 2), 'dong': (1, 3), 'dou': (1, 2),
#                  'du': (1, 2), 'duan': (1, 3), 'dui': (1, 2), 'dun': (1, 3), 'duo': (1, 2), 'e': (0, 1), 'ei': (0, 1),
#                  'en': (0, 2), 'eng': (0, 2), 'er': (0, 2), 'fa': (1, 2), 'fan': (1, 3), 'fang': (1, 3), 'fei': (1, 2),
#                  'fen': (1, 3), 'feng': (1, 3), 'fo': (1, 2), 'fou': (1, 2), 'fu': (1, 2), 'ga': (1, 2), 'gai': (1, 2),
#                  'gan': (1, 3), 'gang': (1, 3), 'gao': (1, 2), 'ge': (1, 2), 'gei': (1, 2), 'gen': (1, 3),
#                  'geng': (1, 3), 'gong': (1, 3), 'gou': (1, 2), 'gu': (1, 2), 'gua': (1, 2), 'guai': (1, 2),
#                  'guan': (1, 3), 'guang': (1, 3), 'gui': (1, 2), 'gun': (1, 3), 'guo': (1, 2), 'ha': (1, 2),
#                  'hai': (1, 2), 'han': (1, 3), 'hang': (1, 3), 'hao': (1, 2), 'he': (1, 2), 'hei': (1, 2),
#                  'hen': (1, 3), 'heng': (1, 3), 'hong': (1, 3), 'hou': (1, 2), 'hu': (1, 2), 'hua': (1, 2),
#                  'huai': (1, 2), 'huan': (1, 3), 'huang': (1, 3), 'hui': (1, 2), 'hun': (1, 3), 'huo': (1, 2),
#                  'ji': (1, 2), 'jia': (1, 2), 'jian': (1, 3), 'jiang': (1, 3), 'jiao': (1, 2), 'jie': (1, 2),
#                  'jin': (1, 3), 'jing': (1, 3), 'jiong': (1, 3), 'jiu': (1, 2), 'ju': (1, 2), 'juan': (1, 3),
#                  'jue': (1, 2), 'jun': (1, 3), 'ka': (1, 2), 'kai': (1, 2), 'kan': (1, 3), 'kang': (1, 3),
#                  'kao': (1, 2), 'ke': (1, 2), 'kei': (1, 2), 'ken': (1, 3), 'keng': (1, 3), 'kong': (1, 3),
#                  'kou': (1, 2), 'ku': (1, 2), 'kua': (1, 2), 'kuai': (1, 2), 'kuan': (1, 3), 'kuang': (1, 3),
#                  'kui': (1, 2), 'kun': (1, 3), 'kuo': (1, 2), 'la': (1, 2), 'lai': (1, 2), 'lan': (1, 3),
#                  'lang': (1, 3), 'lao': (1, 2), 'le': (1, 2), 'lei': (1, 2), 'leng': (1, 3), 'li': (1, 2),
#                  'lia': (1, 2), 'lian': (1, 3), 'liang': (1, 3), 'liao': (1, 2), 'lie': (1, 2), 'lin': (1, 3),
#                  'ling': (1, 3), 'liu': (1, 2), 'lo': (1, 2), 'long': (1, 3), 'lou': (1, 2), 'lu': (1, 2),
#                  'luan': (1, 3), 'lue': (1, 2), 'lun': (1, 3), 'luo': (1, 2), 'lv': (1, 2), 'lve': (1, 2), 'ma': (1, 2),
#                  'mai': (1, 2), 'man': (1, 3), 'mang': (1, 3), 'mao': (1, 2), 'me': (1, 2), 'mei': (1, 2),
#                  'men': (1, 3), 'meng': (1, 3), 'mi': (1, 2), 'mian': (1, 3), 'miao': (1, 2), 'mie': (1, 2),
#                  'min': (1, 3), 'ming': (1, 3), 'miu': (1, 2), 'mo': (1, 2), 'mou': (1, 2), 'mu': (1, 2), 'na': (1, 2),
#                  'nai': (1, 2), 'nan': (1, 3), 'nang': (1, 3), 'nao': (1, 2), 'ne': (1, 2), 'nei': (1, 2),
#                  'nen': (1, 3), 'neng': (1, 3), 'ni': (1, 2), 'nian': (1, 3), 'niang': (1, 3), 'niao': (1, 2),
#                  'nie': (1, 2), 'nin': (1, 3), 'ning': (1, 3), 'niu': (1, 2), 'nong': (1, 3), 'nou': (1, 2),
#                  'nu': (1, 2), 'nuan': (1, 3), 'nue': (1, 2), 'nuo': (1, 2), 'nv': (1, 2), 'o': (0, 1), 'ou': (0, 1),
#                  'pa': (1, 2), 'pai': (1, 2), 'pan': (1, 3), 'pang': (1, 3), 'pao': (1, 2), 'pei': (1, 2),
#                  'pen': (1, 3), 'peng': (1, 3), 'pi': (1, 2), 'pian': (1, 3), 'piao': (1, 2), 'pie': (1, 2),
#                  'pin': (1, 3), 'ping': (1, 3), 'po': (1, 2), 'pou': (1, 2), 'pu': (1, 2), 'qi': (1, 2), 'qia': (1, 2),
#                  'qian': (1, 3), 'qiang': (1, 3), 'qiao': (1, 2), 'qie': (1, 2), 'qin': (1, 3), 'qing': (1, 3),
#                  'qiong': (1, 3), 'qiu': (1, 2), 'qu': (1, 2), 'quan': (1, 3), 'que': (1, 2), 'qun': (1, 3),
#                  'r': (0, 2), 'ran': (1, 3), 'rang': (1, 3), 'rao': (1, 2), 're': (1, 2), 'ren': (1, 3), 'reng': (1, 3),
#                  'ri': (1, 2), 'rong': (1, 3), 'rou': (1, 2), 'ru': (1, 2), 'rua': (1, 2), 'ruan': (1, 3),
#                  'rui': (1, 2), 'run': (1, 3), 'ruo': (1, 2), 'sa': (1, 2), 'sai': (1, 2), 'san': (1, 3),
#                  'sang': (1, 3), 'sao': (1, 2), 'se': (1, 2), 'sen': (1, 3), 'seng': (1, 3), 'sha': (1, 2),
#                  'shai': (1, 2), 'shan': (1, 3), 'shang': (1, 3), 'shao': (1, 2), 'she': (1, 2), 'shei': (1, 2),
#                  'shen': (1, 3), 'sheng': (1, 3), 'shi': (1, 2), 'shou': (1, 2), 'shu': (1, 2), 'shua': (1, 2),
#                  'shuai': (1, 2), 'shuan': (1, 3), 'shuang': (1, 3), 'shui': (1, 2), 'shun': (1, 3), 'shuo': (1, 2),
#                  'si': (1, 2), 'song': (1, 3), 'sou': (1, 2), 'su': (1, 2), 'suan': (1, 3), 'sui': (1, 2),
#                  'sun': (1, 3), 'suo': (1, 2), 'ta': (1, 2), 'tai': (1, 2), 'tan': (1, 3), 'tang': (1, 3),
#                  'tao': (1, 2), 'te': (1, 2), 'tei': (1, 2), 'teng': (1, 3), 'ti': (1, 2), 'tian': (1, 3),
#                  'tiao': (1, 2), 'tie': (1, 2), 'ting': (1, 3), 'tong': (1, 3), 'tou': (1, 2), 'tu': (1, 2),
#                  'tuan': (1, 3), 'tui': (1, 2), 'tun': (1, 3), 'tuo': (1, 2), 'wa': (0, 1), 'wai': (0, 1),
#                  'wan': (0, 2), 'wang': (0, 2), 'wei': (0, 1), 'wen': (0, 2), 'weng': (0, 2), 'wo': (0, 1),
#                  'wu': (0, 1), 'xi': (1, 2), 'xia': (1, 2), 'xian': (1, 3), 'xiang': (1, 3), 'xiao': (1, 2),
#                  'xie': (1, 2), 'xin': (1, 3), 'xing': (1, 3), 'xiong': (1, 3), 'xiu': (1, 2), 'xu': (1, 2),
#                  'xuan': (1, 3), 'xue': (1, 2), 'xun': (1, 3), 'ya': (0, 1), 'yan': (0, 2), 'yang': (0, 2),
#                  'yao': (0, 1), 'ye': (0, 1), 'yi': (0, 1), 'yin': (0, 2), 'ying': (0, 2), 'yo': (0, 1), 'yong': (0, 2),
#                  'you': (0, 1), 'yu': (0, 1), 'yuan': (0, 2), 'yue': (0, 1), 'yun': (0, 2), 'za': (1, 2), 'zai': (1, 2),
#                  'zan': (1, 3), 'zang': (1, 3), 'zao': (1, 2), 'ze': (1, 2), 'zei': (1, 2), 'zen': (1, 3),
#                  'zeng': (1, 3), 'zha': (1, 2), 'zhai': (1, 2), 'zhan': (1, 3), 'zhang': (1, 3), 'zhao': (1, 2),
#                  'zhe': (1, 2), 'zhei': (1, 2), 'zhen': (1, 3), 'zheng': (1, 3), 'zhi': (1, 2), 'zhong': (1, 3),
#                  'zhou': (1, 2), 'zhu': (1, 2), 'zhua': (1, 2), 'zhuai': (1, 2), 'zhuan': (1, 3), 'zhuang': (1, 3),
#                  'zhui': (1, 2), 'zhun': (1, 3), 'zhuo': (1, 2), 'zi': (1, 2), 'zong': (1, 3), 'zou': (1, 2),
#                  'zu': (1, 2), 'zuan': (1, 3), 'zui': (1, 2), 'zun': (1, 3), 'zuo': (1, 2), 'sil': (0, 1), 'kiu': (1, 0),
#            'nve': (1, 2), 'nia': (1, 2)}
offset = 0  # seconds


class Mfa:
    def __init__(self, wav_filename, seg_tg_name, py, text_in, install=False, id_name=None):
        self.wav_filename = wav_filename

        self.seg_tg_name = seg_tg_name

        self.py = py  # vvTalk标准下的拼音
        self.sign = []  # mfa标准下的拼音
        past_tone = ''
        for p in py:
            if p[-1].isdigit():
                if p[-1] == '0':
                    if past_tone in '12':
                        p = p[:-1] + '6'
                    elif past_tone == '3':
                        p = p[:-1] + '7'
                    elif past_tone == '4':
                        p = p[:-1] + '8'
                    else:
                        p = p[:-1] + '5'
                self.sign.append(p)
            else:
                if p != 'sil':  # 由于某种原因没有音调标注的拼音
                    self.sign.append(p + '1')
                else:
                    self.sign.append(p)  # 'sil'

        self.DIR = {}
        self.DIR.update(DIR)
        self.id_name = id_name
        self._make_temp_dir()

        self.basename = wav_filename.split('\\')[-1].split('.')[0]
        self.temp_basename = 'temp'
        self.output_basename = None
        self.tier_name = 'phones'  # could be 'segment - phones' for previous versions of mfa

    def _make_temp_dir(self):
        if self.id_name is not None:
            temp_names = {
                'temp': f'misc\\temp\\subprocess_{self.id_name}\\mfa_temp',
                'working': f'misc\\temp\\subprocess_{self.id_name}\\mfa_temp\\working',
                'source': f'misc\\temp\\subprocess_{self.id_name}\\mfa_temp\\source',
                'output': f'misc\\temp\\subprocess_{self.id_name}\\mfa_temp\\output',
            }
            for name in temp_names.values():
                if not os.path.exists(name):
                    os.makedirs(name)
            self.DIR.update(temp_names)

    def _before_alignment(self):
        # clear the folder for work
        try:
            names_source = os.listdir(f'{os.getcwd()}\\{self.DIR["source"]}')
        except FileNotFoundError:
            os.makedirs(f'{os.getcwd()}\\{self.DIR["source"]}', exist_ok=True)
            names_source = []
        for name in names_source:
            try:
                os.remove(f'{os.getcwd()}\\{self.DIR["source"]}\\{name}')
            except Exception as e:
                print('wrong delete', e)

        try:
            names_output = os.listdir(f'{os.getcwd()}\\{self.DIR["output"]}')
        except FileNotFoundError:
            os.makedirs(f'{os.getcwd()}\\{self.DIR["output"]}', exist_ok=True)
            names_output = []
        for name in names_output:
            try:
                os.remove(f'{os.getcwd()}\\{self.DIR["output"]}\\{name}')
            except Exception as e:
                print('wrong delete', e)

        with open(self.wav_filename, 'rb') as f1:
            with open(f'{os.getcwd()}\\{self.DIR["source"]}\\{self.temp_basename}.wav', 'wb') as f2:
                f2.write(f1.read())

        if os.path.exists(self.seg_tg_name):
            tg = textgrid.openTextgrid(os.getcwd() + '\\' + self.seg_tg_name, includeEmptyIntervals=True)
            interval_list = tg.tierDict['segment'].entryList
            signs = self.sign[:]
            for i, interval in enumerate(interval_list):
                length = int(interval[2].split('_')[-2])
                without_sil = [x for x in signs[:length] if x != 'sil']
                if without_sil:
                    content = ' '.join(without_sil)
                else:
                    content = 'sil'
                del signs[:length]
                interval = praatio.utilities.constants.Interval(interval[0], interval[1], content)
                interval_list[i] = interval
            tg.save(f'{os.getcwd()}\\{self.DIR["source"]}\\' + self.temp_basename + '.textgrid', 'short_textgrid',
                    includeBlankSpaces=False)
            self.output_basename = self.temp_basename
            # self.tier_name = 'segment - phones'
        else:
            with open(f'{os.getcwd()}\\{self.DIR["source"]}\\' + self.temp_basename + '.txt', 'w',
                      encoding='utf-8') as f:
                f.write(' '.join(self.sign))
            # self.output_basename = 'source-'+self.temp_basename
            self.output_basename = self.temp_basename
            # self.tier_name = 'phones'

    def _call_mfa(self):
        cwd = os.getcwd()

        def barg(ori):
            return f'\"{cwd}\\{ori}\"'

        para_args = ['align', barg(self.DIR['source']), barg(self.DIR['diction']), barg(self.DIR['model']),
                     barg(self.DIR['output']), '-t', barg(self.DIR['working']), '--config_path',
                     barg(self.DIR['config']), '--clean', '--disable_mp']

        batch = batch_start + ' '.join(para_args)
        with open(f'{self.DIR["temp"]}\\run.bat', 'w') as f:
            f.write(batch)
        os.system(f'{self.DIR["temp"]}\\run.bat')  # join until the script ends
        # start misc
        print('mfa_finished')

    def execute_alignment(self):
        self._before_alignment()
        self._call_mfa()

    def transcribe_to(self, dest, only_vowel: bool = False):
        """
        From mfa output to standard tytalk manual alignment.
        :return:
        """
        # referring to reliance.sppasDealer.normalize
        def normalize():
            sil_i = []
            tier_phon = interval_list[:]
            output = []
            itv = praatio.utilities.constants.Interval
            for i, interval_phon in enumerate(tier_phon):
                if interval_phon[2] in ('sp', 'sil', ''):
                    output.append(itv(interval_phon[0], interval_phon[1], 'sil'))
                    sil_i.append(i)
            del_count = 0
            for s_i in sil_i:
                del tier_phon[s_i - del_count]
                del_count += 1
            py = []  # 去除所有sil，因为拼音的sil与标注的sil不对应，已经失去意义
            for py_long in self.py:
                if py_long != 'sil':
                    py.append(py_long)
            # mfa会将未识别出准确音素但确实存在的音节标为spn
            # if not only_vowel:
            if True:
                for p in py:
                    if p != 'sil':
                        if p[-1].isdigit():
                            py_base = p[:-1]
                        else:
                            py_base = p
                        length = phone_lengths.get(py_base, (0, 1))
                        cur_phoneme = tier_phon[0]
                        if cur_phoneme[2] == 'spn':
                            length = (0, 1)

                        if length[0] == 1:
                            cons = tier_phon[0]
                            output.append(itv(cons[0], cons[1], 'con'))
                            vows = tier_phon[1:length[1]]
                            output.append(itv(vows[0][0], vows[-1][1], p))
                        else:  # no consonant
                            vows = tier_phon[0:length[1]]
                            output.append(itv(vows[0][0], vows[-1][1], p))
                        del tier_phon[:length[1]]
            # else:
            #     # 如果需要输出已经合并好、不含辅音的分割结果
            # first = True
            # for idx, p in enumerate(py_base):
            #     try:
            #         next_cons_len = phone_lengths.get(py_base[idx + 1], (0, 1))[0]
            #     except IndexError:
            #         next_cons_len = 0
            #
            #     length = phone_lengths.get(p, (0, 1))
            #     if first and length[0] == 1:
            #         cons = tier_phon[0]
            #         output.append((itv(cons[0], cons[1], 'sil')))
            #         del tier_phon[0]
            #     first = False
            #
            #     cur_phoneme = tier_phon[0]
            #     if cur_phoneme[2] == 'spn':
            #         length = (0, 1)
            #     if next_cons_len:
            #         if tier_phon[length[1]-length[0]][2] == 'spn':
            #             actual_length = wrapping_length = length[1] - length[0]
            #         else:
            #             wrapping_length = length[1] - length[0] + next_cons_len  # 当前元音要涵盖的音素个数（包括之后的辅音）
            #             wrapping_phonemes_interval = tier_phon[0:wrapping_length]
            #             # print(wrapping_phonemes_interval, idx, py_base[idx + 1])
            #             self_last = wrapping_phonemes_interval[-next_cons_len-1]
            #             next_first = wrapping_phonemes_interval[-next_cons_len]
            #             if self_last[1] == next_first[0]:  # 时间相同
            #                 actual_length = wrapping_length
            #             else:
            #                 actual_length = length[1] - length[0]
            #                 output.append(itv(next_first[0], wrapping_phonemes_interval[-1][1], 'sil'))  # 将不连续的下一辅音置为静音
            #     else:
            #         actual_length = wrapping_length = length[1] - length[0]
            #
            #     phonemes = tier_phon[0:actual_length]
            #     output.append(itv(phonemes[0][0], phonemes[-1][1], p))
            #     del tier_phon[:wrapping_length]

            output.sort(key=lambda x: x[0])
            return output

        align_dir = f'{os.getcwd()}\\{self.DIR["output"]}\\{self.output_basename}.TextGrid'
        dest_dir = f'{os.getcwd()}\\{dest}'
        tg = textgrid.openTextgrid(align_dir, includeEmptyIntervals=True)
        interval_list = tg.tierDict[self.tier_name].entryList  # within there are named tuples
        try:
            normal_list = normalize()
            dest_tg = textgrid.Textgrid()
            dest_tier = textgrid.IntervalTier('grid', normal_list)
            ori_max = dest_tier.maxTimestamp
            dest_tier.editTimestamps(offset, reportingMode='silence')
            changed_max = dest_tier.maxTimestamp
            if changed_max - ori_max:
                dest_tier = dest_tier.eraseRegion(ori_max, changed_max, collisionMode='truncate')
            dest_tg.addTier(dest_tier)
            dest_tg.save(dest_dir, 'short_textgrid', False)
        except Exception as e:
            raise e


class MfaImported(Mfa):
    def _call_mfa(self):

        def barg(ori):
            return os.path.abspath(ori)

        fake_args = ['align', barg(self.DIR['source']), barg(self.DIR['diction']), barg(self.DIR['model']),
                     barg(self.DIR['output']), '-t', barg(self.DIR['working']), '--clean', '--disable_mp', '--overwrite', '--quiet']
                     # barg(self.DIR['output']), '-t', barg(self.DIR['working']), '--config_path', barg(self.DIR['config']), '--clean', '--disable_mp', '--overwrite', '--quiet']

        parser = create_parser()
        args, unknown = parser.parse_known_args(fake_args)
        run_align_corpus(args, unknown)

