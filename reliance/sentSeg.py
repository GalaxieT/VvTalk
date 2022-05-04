import re


def seg(t: str):
    sent_list = []
    text = t
    cur_sent = ''
    for c in text:
        cur_sent = cur_sent + c
        if re.match('[。：:；;？！?!…\n\r]+', c):
            if c in '\n\r':
                cur_sent = cur_sent[:-1]
            if cur_sent:
                sent_list.append(cur_sent)
            cur_sent = ''
    if cur_sent:
        sent_list.append(cur_sent)
    return sent_list
