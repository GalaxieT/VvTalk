"""
依据句法结构推测语义展开的过程，以评价各个音节的正式度并划分基础节奏（未在最后一层受音节数量影响时）。
"""
from aip import AipNlp
import pickle
import pydotplus
import os
from PIL import Image
import math
os.environ["PATH"] += os.pathsep + r'D:\Program Files\Graphviz\bin'
cx_dic = {'Ag': '形语素', 'a': '形容词', 'ad': '副形词', 'an': '名形词', 'b': '区别词', 'c': '连词', 'dg': '副语素', 'd': '副词', 'e': '叹词', 'f': '方位词', 'g': '语素', 'h': '前接成分', 'i': '成语', 'j': '简称略语', 'k': '后接成分', 'l': '习用语', 'm': '数词', 'Ng': '名语素', 'n': '名词', 'nr': '人名', 'ns': '地名', 'nt': '机构团体', 'nz': '其他专名', 'o': '拟声词', 'p': '介词', 'q': '量词', 'r': '代词', 's': '处所词', 'tg': '时语素', 't': '时间词', 'u': '助词', 'vg': '动语素', 'v': '动词', 'vd': '副动词', 'vn': '名动词', 'w': '标点符号', 'x': '非语素字', 'y': '语气词', 'z': '状态词', 'un': '未知词'}
yc_dic = {'ATT': '定中关系', 'QUN': '数量关系（quantity）', 'COO': '并列关系（coordinate）', 'APP': '同位关系（appositive）', 'ADJ': '附加关系（adjunct）', 'VOB': '动宾关系（verb-object）', 'POB': '介宾关系（preposition-object）', 'SBV': '主谓关系（subject-verb）', 'SIM': '比拟关系（similarity）', 'TMP': '时间关系（temporal）', 'LOC': '处所关系（locative）', 'DE': '“的”字结构', 'DI': '“地”字结构', 'DEI': '“得”字结构', 'SUO': '“所”字结构', 'BA': '“把”字结构', 'BEI': '“被”字结构', 'ADV': '状中结构（adverbial）', 'CMP': '动补结构（complement）', 'DBL': '兼语结构（double）', 'CNJ': '关联词（conjunction）', 'CS': '关联结构(conjunctive structure)', 'MT': '语态结构（mood-tense）', 'VV': '连谓结构（verb-verb）', 'HED': '核心（head）', 'FOB': '前置宾语（fronting object）', 'DOB': '双宾语（double object）', 'TOP': '主题（topic）', 'IS': '独立结构（independent structure）', 'IC': '独立分句（independent clause）', 'DC': '依存分句（dependent clause）', 'VNV ': '叠词关系（verb-no-verb or verb-one-verb)', 'YGC': '一个词', 'WP': '标点'}

text = '噜嗦地讲着埃及话'
client = AipNlp('18561004', 'pYNIu5ocRxj82BkaI5CZzR8I', 'AehSQG7Uji17o0vWBqWPVj5lBqMMrRNn')
result = client.depParser(text)
with open('result.pkl', 'wb') as f:
    pickle.dump(result, f)

# with open('result.pkl', 'rb') as f:
#     result = pickle.load_from(f)

items = result['items']
items_d = {item['id']: item for item in items}
continuing = True
# flow_rely = {id_: 1 for id_ in items_d}
# stack_rely = {id_: 0 for id_ in items_d}
# while continuing:
#     continuing = False
#     for id_ in items_d:
#         if flow_rely[id_]:
#             try:
#                 flow_rely[items_d[id_]['head']] += flow_rely[id_]
#             except KeyError:  # 根依赖
#                 pass
#             stack_rely[id_] += flow_rely[id_]
#             flow_rely[id_] = 0
#             continuing = True

children = {id_: [] for id_ in items_d}
for id_ in items_d:
    try:
        children[items_d[id_]['head']].append(id_)
    except KeyError:  # 根词
        pass
utterred = {id_: False for id_ in items_d}
disconnected = {id_: False for id_ in items_d}


def get_children_num(id_, out=None):
    """
    :return: [expressed_num, inexpressed_num]
    """
    if not out:
        out = [0, 0]
    if utterred[id_] and not disconnected[id_]:
        out[0] += 1
    else:
        out[1] += 1
    rely_ids = children[id_]
    for rely_id in rely_ids:
        get_children_num(rely_id, out)
    return out

def get_distance(ia, ib, default=2):
    """
    求a到b的距离（b-a，距离逆箭头方向增加，即箭头方向为距离的负方向）
    :return 带正负号的距离，若不在同一树，则返回默认距离
    """

    def get_children(id, out=None, cnt=0):
        if not out:
            out = []
        cnt += 1
        direct = children[id]
        for child in direct:
            out.append((child, cnt))
            get_children(child, out, cnt)
        return out
    def get_masters(id, out=None, cnt=0):
        if id == 0:
            return out
        if not out:
            out = []
        cnt += 1
        direct = items_d[id]['head']
        out.append((direct, cnt))
        get_masters(direct, out, cnt)
        return out
    dist = 0
    ia_inf = dict(get_children(ia))
    ib_inf = dict(get_children(ib))
    if ia in ib_inf:
        dist = -ib_inf[ia]
    elif ib in ia_inf:
        dist = ia_inf[ib]
    else:  # 并行修饰情况
        m_ia_inf = get_masters(ia)  # 用list保持顺序
        m_ia_list = [inf[0] for inf in m_ia_inf]
        m_ib_inf = get_masters(ib)
        m_ib_inf_d = dict(m_ib_inf)
        for mst_b in m_ib_inf:
            if mst_b[0] in m_ia_list:
                dist = - m_ib_inf_d[mst_b[0]]
                break
    # print(items_d[ia], dist)
    return dist
# 按照语序，渲染，以依赖链接为单位

def get_discontinuity(fa, fb, fl, i):
    def sigmoid(x, ex=1):
        return 1 / (1 + math.exp(-x*ex))

    ib = i + 1

    if items_d[ib]['deprel'] in ('DE', 'DI', 'DEI'):
        fa = 1

    if fl > 0:
        fl = fl / 2
    else:
        fl = - fl
    # print(items_d[i]['word'], fl, fb, math.log(sigmoid((-1 / fl) + 0.5*math.log(fb), 2)))
    return sigmoid(1.5 * (3 * math.log(fa, 20) + 0.4 * math.log(sigmoid((-1 / fl) + 0.5 * math.log(fb), 2))))
discontinuity = {}
relation_inf = {}  # {id:(A_inf, B_inf, distance)}
for id_ in list(items_d)[:-1]:
    utterred[id_] = True
    relation_inf.update({id_: (get_children_num(id_)[0], get_children_num(id_ + 1)[1], get_distance(id_, id_+1))})
    inf = relation_inf[id_]
    dis = round(get_discontinuity(inf[0], inf[1], inf[2], id_), 2)
    discontinuity.update({id_: dis})
    if dis > 0.7:
        for i in range(1, id_+1):
            disconnected[i] = True
for x, y in relation_inf.items():
    print(items_d[x]['word'])
    print(y, ' - ', discontinuity[x])
print(sum(discontinuity.values())/len(discontinuity))


# for id in relation_inf:
#     inf = relation_inf[id]
#     print(items_d[id]['word'])
#     print(inf, ' - ', round(get_discontinuity(inf[0], inf[1], inf[2]), 2))
# inf = relation_inf[4]
# print(inf, ' - ', round(get_discontinuity(inf[0], inf[1], inf[2]), 2))




for item in result['items']:
    item['deprel'] = item['deprel'] + '|' + yc_dic[item['deprel']]

def make_point(cln):
    dot = []
    for item in cln['items']:
        id_ = item['id']
        head = item['head']
        deprel = item['deprel']
        dot.append('{} -> {} [label="{}"]'.format(id_, head, deprel))
        dot.append('{}[label="{}"]'.format(id_, item['word']))
    text = """digraph graphname {
    subgraph clusterA {
        rankdir=TB
        node [shape=plaintext,style=filled, fontname="Microsoft YaHei"]
        edge [fontname="Microsoft YaHei"]
        %s
        }
    }
        """ % '\n'.join(dot)
    print(text)
    return text


graph = pydotplus.graph_from_dot_data(make_point(result))
with open('pic.png', 'wb') as f:
    f.write(graph.create_png())
pic2 = Image.open('pic.png')
pic2.show()

"""
import matplotlib.pyplot as plt
graph = pydotplus.graph_from_dot_data(dot)
with open('pic.png', 'wb') as f:
    f.write(graph.create_png())

im = plt.imread('pic.png')
plt.imshow(im)
plt.show()
"""