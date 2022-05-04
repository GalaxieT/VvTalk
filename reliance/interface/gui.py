from reliance.imitation.humanConverter import ConverterGUI
from reliance.sentSeg import seg
from tkinter import *
from tkinter import filedialog
from tkinter import ttk, messagebox
from copy import deepcopy
import re
from winsound import MessageBeep
import os
import reliance

VERSION = reliance.global_vars.VERSION
VERSION_NO = reliance.global_vars.VERSION_NO

title_name = 'vvTalk (个人非商用)'

def tkinter_gui(core: reliance.core.TalkCore):
    core.subprocess_finish_callback = MessageBeep
    root = Tk()
    root.title('{} - {}'.format(core.project_file_name(), title_name))
    fr1 = Frame(root)
    root.minsize(500, 360)
    root.geometry('+200+300')
    if core.settings['last_window_geom']:
        root.geometry(core.settings['last_window_geom'])
    sb = Scrollbar(fr1, )
    sb.pack(side=RIGHT, fill=Y)
    title = ['1', '2', '3', '4', '5']
    tv = ttk.Treeview(fr1, columns=title, yscrollcommand=sb.set, show='headings')
    tv.column('1', width=200, anchor='center')
    tv.column('2', width=80, anchor='center')
    tv.column('3', width=50, anchor='center')
    tv.column('4', width=50, anchor='center')
    tv.column('5', width=50, anchor='center')

    tv.heading('1', text='汉字')
    tv.heading('2', text='拼音')
    tv.heading('3', text='标记')
    tv.heading('4', text='辅音')
    tv.heading('5', text='音量')

    def close():
        if not core.unchanged:
            decision = ask_and_save()
            if decision is None:
                return
        # if core.sents.blocking:
        #     decision_block = blocked_ask()
        #     if decision_block:
        #         abort
        #     else:
        #         return
        core.settings['last_window_geom'] = root.geometry()
        core.save_settings()
        root.destroy()

    root.protocol('WM_DELETE_WINDOW', close)

    def select_all(event=None):
        tv.selection_set(tv.get_children())

    tv.bind('<Control-A>', select_all)
    tv.bind('<Control-a>', select_all)

    def refresh():
        star = '*'
        if core.unchanged:
            star = ''
        root.title('{} {} - {}'.format(core.project_file_name(), star, title_name))
        root.after(50, refresh)

    refresh()

    def tv_update(chaos=True):  # if not chaos, keep the selection after the update
        # print(core.history_index)
        # for his in core.histories:
        #     print(his)
        idxs = []
        if not chaos:
            ids = tv.selection()
            idxs = [tv.index(id_) for id_ in ids]
        chi = tv.get_children()
        if chi:
            for ch in chi:
                tv.delete(ch)

        def display_consonant(x):
            if not x:
                return '无'
            elif x == 'manual':
                return '手动'
            elif x == 'auto':
                return '自动'
            else:
                return '未知'

        def display_intensity(x):
            if not x:
                return '无'
            elif x == 'wait':
                return '正在分析'
            elif x == 'abort':
                return '分析取消'
            elif x == 'complete':
                return '完成'
            else:
                return '未知'

        for i, sent in enumerate(core.sents.present_sents(dc=False)):
            try:
                its = display_intensity(sent['data'][6])
            except IndexError:
                its = '未知'
            if sent['data'][0] == 'a':
                tv.insert('', i, values=(
                    sent['base'][0], ' '.join(sent['base'][1]), '自动', display_consonant(sent['data'][4]), its))
            elif sent['data'][0] == 'v':
                tv.insert('', i,
                          values=(
                              sent['base'][0], ' '.join(sent['base'][1]), '人声', display_consonant(sent['data'][4]),
                              its))
            elif sent['data'][0] == 'wait':
                tv.insert('', i, values=(sent['base'][0], ' '.join(sent['base'][1]), '(人声)分析中', '正在分析', its))
            elif sent['data'][0] == 'abort':
                tv.insert('', i, values=(sent['base'][0], ' '.join(sent['base'][1]), '取消', '分析取消', its))
            elif not sent['data'][0]:
                tv.insert('', i,
                          values=(
                              sent['base'][0], ' '.join(sent['base'][1]), '无', display_consonant(sent['data'][4]), its))
            else:  # 向上兼容
                tv.insert('', i,
                          values=(sent['base'][0], ' '.join(sent['base'][1]), sent['data'][0], '未知', its))
        chi2 = tv.get_children()
        tv.selection_set([chi2[idx] for idx in idxs])

    core.ui_update_callback = tv_update
    tv_update()

    sb.config(command=tv.yview)
    tv.pack(side=LEFT, fill=BOTH, expand=True)

    def blocked_ask(idx=None):
        content = ''
        if idx is not None:
            content = f'“{core.sents.present_sent_idx(idx, dc=False)["base"][0][:5]}…”'
        return messagebox.askyesno('占用中', f'句子{content}'
                                          f'正在被分析占用, 是否终止分析来继续本次操作？')

    def ask_and_save():
        result = messagebox.askyesnocancel('未保存', '是否保存改动？')
        if result is None:
            return None
        elif result:
            save_result = save_file()
            if save_result:
                return True
            else:
                return None
        else:
            return False

    def new_file():
        if not core.unchanged or core.temp_file:
            decision = ask_and_save()
            if decision is None:
                return
        core.load_new_temp()
        tv_update()

    def open_file():
        if not core.unchanged or core.temp_file:
            decision = ask_and_save()
            if decision is None:
                return
        default = os.getcwd() + r'\projects'
        location = filedialog.askopenfilename(title='打开',
                                              filetypes=[('vvTalk项目文件', '*.tyt'), ('All Files', '*')],
                                              initialdir=default)
        if not location:
            return
        core.load_from(location)
        tv_update()

    def save_file(event=None, keep_temp=False):
        if core.temp_file:
            if not keep_temp:
                result = save_file_as()
            else:
                core.save(core.project_file_location)
                result = True
        elif core.project_file_location:
            core.save(core.project_file_location)
            result = True
        else:
            result = save_file_as()

        return result

    def save_file_as():
        if not core.temp_file:
            default = core.project_file_location
        else:
            default = ''
        if not default:
            default = os.getcwd() + r'\projects'
        new_location = filedialog.asksaveasfilename(title='保存为',
                                                    filetypes=[('vvTalk项目文件', '*.tyt'), ('All Files', '*')],
                                                    initialdir=default, defaultextension='tyt',
                                                    initialfile='新vvTalk项目')
        if not new_location:
            return False
        core.temp_file = False
        core.save(new_location)
        core.load_from(new_location)
        tv_update()
        return True

    menubar = Menu(root)
    file_menu = Menu(menubar, tearoff=0)
    file_menu.add_command(label='新建', command=new_file)
    file_menu.add_command(label='打开', command=open_file)
    file_menu.add_command(label='保存', command=save_file)
    file_menu.add_command(label='另存为', command=save_file_as)
    settings_menu = Menu(menubar, tearoff=0)

    def editor_setting():
        tl = Toplevel(root)
        tl.title('编辑器选项')
        root_loc = root.geometry().split('+')[1:3]
        tl.geometry(f'250x280+{int(root_loc[0]) + 100}+{int(root_loc[1]) + 50}')
        tl.resizable(0, 0)

        step_save_var = BooleanVar(value=core.settings['step_save'])
        step_save_fr = Frame(tl)
        Checkbutton(step_save_fr, text='实时保存', variable=step_save_var).pack()

        interval_var = StringVar(value=str(core.settings['interval']))
        interval_fr = Frame(tl)
        Label(interval_fr, text='每句的间隔时间').pack(side=LEFT)
        e = Entry(interval_fr, textvariable=interval_var, width=4)
        e.pack(side=LEFT)
        Label(interval_fr, text='ms (-1000~3000)').pack(side=LEFT)

        pbs_var = StringVar(value=str(core.settings['pbs']))
        pbs_fr = Frame(tl)
        Label(pbs_fr, text='输出文件的PBS值：').pack(side=LEFT)
        Entry(pbs_fr, textvariable=pbs_var, width=4).pack(side=LEFT)

        dyn_var = BooleanVar(value=core.settings['enable_dyn_correction'])
        dyn_fr = Frame(tl)
        Checkbutton(dyn_fr, text='将音量修正输出到dyn（实验功能）', variable=dyn_var).pack()

        consonant_var = BooleanVar(value=core.settings['output_consonants'])
        consonant_fr = Frame(tl)
        Checkbutton(consonant_fr, text='辅音拆音（仅人声）', variable=consonant_var).pack()

        format_var = StringVar(value=core.settings['output_format'])
        format_fr = Frame(tl)
        Label(format_fr, text='输出格式：').pack(side=LEFT)
        formats = ['vsqx', 'svp']
        ttk.Combobox(format_fr, state='readonly', cursor='arrow', textvariable=format_var, values=formats).pack(side=LEFT)

        def save_exit():
            try:
                interval = int(interval_var.get())
                if not -1000 <= interval <= 3000:
                    raise ValueError
            except ValueError:
                messagebox.showerror('输入错误', '时间间隔错误，需要-1000到3000的整数')
                tl.focus()
                e.focus()
                e.select_range(0, 'end')
                return
            try:
                pbs = int(pbs_var.get())
                if not 1 <= pbs <= 24:
                    raise ValueError
            except ValueError:
                messagebox.showerror('输入错误', 'PBS错误，需要1到24的整数')
                tl.focus()
                e.focus()
                e.select_range(0, 'end')
                return

            core.change_settings_save({'step_save': step_save_var.get(),
                                       'interval': interval, 'pbs': pbs,
                                       'enable_dyn_correction': dyn_var.get(),
                                       'output_consonants': consonant_var.get(),
                                       'output_format': format_var.get()})
            tl.destroy()

        step_save_fr.pack(pady=5)
        ttk.Separator(tl, orient=HORIZONTAL).pack(fill=X)
        interval_fr.pack(pady=5)
        ttk.Separator(tl, orient=HORIZONTAL).pack(fill=X)
        pbs_fr.pack(pady=5)
        ttk.Separator(tl, orient=HORIZONTAL).pack(fill=X)
        dyn_fr.pack(pady=5)
        ttk.Separator(tl, orient=HORIZONTAL).pack(fill=X)
        consonant_fr.pack(pady=5)
        ttk.Separator(tl, orient=HORIZONTAL).pack(fill=X)
        format_fr.pack(pady=5)
        ttk.Separator(tl, orient=HORIZONTAL).pack(fill=X)
        Button(tl, text='保存并退出', command=save_exit).pack(pady=5)

    def converter_setting():
        tl = Toplevel(root)
        tl.title('人声转换选项')
        root_loc = root.geometry().split('+')[1:3]
        tl.geometry(f'250x230+{int(root_loc[0]) + 100}+{int(root_loc[1]) + 50}')
        tl.resizable(0, 0)

        name = core.settings['forced_aligner']
        if name == 'sppas':
            aligner = 1
        else:
            aligner = 0
        aligner_var = IntVar(value=aligner)
        aligner_fr = Frame(tl)
        Label(aligner_fr, text='对齐工具').pack(side=LEFT)
        rb_m = Radiobutton(aligner_fr, variable=aligner_var, value=0, text='mfa')
        rb_s = Radiobutton(aligner_fr, variable=aligner_var, value=1, text='sppas')
        rb_s['state'] = DISABLED

        rb_m.pack(side=LEFT)
        rb_s.pack(side=LEFT)

        cons_ctrl_var = BooleanVar(value=core.settings['consonant_control'])
        cons_ctrl_fr = Frame(tl)
        Checkbutton(cons_ctrl_fr, text='启用自动人声辅音识别\n（使用自动标注时失效）\n(实验功能，需要在辅音之前画分割）', variable=cons_ctrl_var).pack()

        def save_exit():
            aligner_num = aligner_var.get()
            if aligner_num == 1:
                aligner_ = 'sppas'
            else:
                aligner_ = 'mfa'
            core.settings.update({'forced_aligner': aligner_, 'consonant_control': cons_ctrl_var.get()})
            core.save_settings()
            tl.destroy()

        aligner_fr.pack(pady=5)
        ttk.Separator(tl, orient=HORIZONTAL).pack(fill=X)
        cons_ctrl_fr.pack(pady=5)
        Button(tl, text='保存并退出', command=save_exit).pack(pady=5)

    settings_menu.add_command(label='编辑器…', command=editor_setting)
    settings_menu.add_command(label='人声转换…', command=converter_setting)
    help_menu = Menu(menubar, tearoff=0)

    def help_file():
        if os.path.exists('vvTalk使用说明.pdf'):
            os.startfile('vvTalk使用说明.pdf')
        else:
            messagebox.showerror('错误', '未找到帮助文件\nvvTalk使用说明.pdf\n请重新下载或向作者咨询啦')

    help_menu.add_command(label='帮助文档', command=help_file)

    def about_win():
        messagebox.showinfo(title='关于vvTalk (TyTalk)',
                            message=f'作者：星河潜溪 @ bilibili\n版本：{VERSION} ({VERSION_NO})\n授权：仅限非营利性作品使用；非个人作品请在作品简介注明使用了vvTalk\n'
                                    f'联系：B站私信，建议与bug反馈请私信留言\n\n希望有所帮助，请勿用于错误用途，作者不承担相应后果哦\n')

    help_menu.add_command(label='关于', command=about_win)
    menubar.add_cascade(label='项目', menu=file_menu)
    menubar.add_cascade(label='设置', menu=settings_menu)
    menubar.add_cascade(label='帮助', menu=help_menu)
    root.config(menu=menubar)

    fr2 = Frame(root)
    arrange_var = IntVar()
    cb_arr = Checkbutton(fr2, text='拖动调序', variable=arrange_var)

    def remove():
        ids = tv.selection()
        if not ids:
            return
        idx_list = sorted([tv.index(id_) for id_ in ids])
        core.sents.del_sent_s(idx_list)
        core.need_save()
        tv_update()

    b_del = Button(fr2, text='删除', command=remove)

    def para_insert():
        ids = tv.selection()
        if not ids:
            idx = len(tv.get_children())
        else:
            idx = tv.index(ids[-1]) + 1
        root.attributes('-disabled', 1)
        tl = Toplevel(root)
        tl.title('批量插入')

        def save():
            text = txt.get(1.0, 'end')
            text_list = seg(text)
            sent_dict = {}
            for i, text in enumerate(text_list):
                sent = core.sent_prototype()
                result = core.talker.get_py(text)
                sent['base'][0] = result[1]
                sent['base'][1] = result[0]
                sent['base'][2] = 'auto'
                sent_dict[idx + i] = sent
            core.sents.add_sent_s(sent_dict)
            core.need_save()
            tv_update()
            close()

        def close():
            root.attributes('-disabled', 0)
            root.focus()
            tl.destroy()

        tl.protocol('WM_DELETE_WINDOW', close)

        txt = Text(tl)
        b = Button(tl, text='确认', command=save)
        txt.focus()
        txt.pack()
        b.pack()

    b_pi = Button(fr2, text='批量插入', command=para_insert)

    def insert():
        ids = tv.selection()
        if not ids:
            idx = len(tv.get_children())
        else:
            idx = tv.index(ids[-1]) + 1
        root.attributes('-disabled', 1)
        tl = Toplevel(root)
        tl.title('插入文本')

        def save():
            text = txt.get(1.0, 'end')
            sent = core.sent_prototype()
            result = core.talker.get_py(text)
            sent['base'][0] = result[1]
            sent['base'][1] = result[0]
            sent['base'][2] = 'auto'
            core.sents.add_sent(sent, idx)
            core.need_save()
            tv_update()
            close()

        def close():
            root.attributes('-disabled', 0)
            root.focus()
            tl.destroy()
            try:
                tv.selection_set(tv.get_children()[idx])
            except IndexError:
                pass

        tl.protocol('WM_DELETE_WINDOW', close)

        txt = Text(tl)
        b = Button(tl, text='确认', command=save)
        txt.focus()
        txt.pack()
        b.pack()

    b_ins = Button(fr2, text='插入', command=insert)

    def draw_back(event=None):
        core.undo()
        tv_update()

    b_draw = Button(fr2, text='撤销', command=draw_back)

    def recover(event=None):
        core.redo()
        tv_update()

    b_re = Button(fr2, text='重做', command=recover)

    cb_arr.pack()
    b_ins.pack()
    b_pi.pack()
    b_del.pack()
    Label(fr2).pack()
    b_draw.pack()
    b_re.pack()

    def edit_text():  # 只编辑第一个的文本
        ids = tv.selection()
        if not ids:
            return
        root.attributes('-disabled', 1)
        id_ = ids[0]
        idx = tv.index(id_)
        content = core.sents.present_sent_idx(idx, False)['base'][0]
        tl = Toplevel(root)
        tl.title('编辑文本')
        root_loc = root.geometry().split('+')[1:3]
        tl.geometry(f'420x250+{int(root_loc[0]) + 100}+{int(root_loc[1]) + 50}')

        def close():
            root.attributes('-disabled', 0)
            root.focus()
            tl.destroy()

        tl.protocol('WM_DELETE_WINDOW', close)
        tl.attributes('-toolwindow', 1)
        tl.attributes('-topmost', 1)
        txt = Text(tl, height=15, width=50)
        txt.insert('insert', content)
        # txt = Entry(tl, textvariable=content)
        # txt.select_range(0, len(content.get()))
        # txt.icursor(len(content.get()))
        txt.pack(fill=BOTH)
        txt.focus()

        def save(event=None):
            # text = content.get()
            text = txt.get(1.0, "end")
            ori_sent = core.sents.present_sent_idx(idx)
            result = core.talker.get_py(text)
            # py_output = pinyin(text, style=Style.TONE3, errors='')
            # py_output = [part[0] for part in py_output if part[0]]  # 二维列表降维
            # for i, py in enumerate(py_output):
            #     if py[-1] not in '1234':
            #         py_output[i] = py + '0'
            ori_sent['base'][0] = result[1]
            ori_sent['base'][1] = result[0]
            ori_sent['base'][2] = 'auto'
            ori_sent['data'] = core.sent_prototype()['data']
            result = core.sents.change_sent_idx(idx, ori_sent)
            if result:
                choice = blocked_ask(result[0])
                if choice:
                    core.sents.complete_change(result[1])
                    tv_update(False)
                    save()
                    return
                else:
                    return
            # core.sents[idx][2] = ['', '']
            tv_update(chaos=False)
            core.need_save()
            root.attributes('-disabled', 0)
            root.focus()
            tl.destroy()

        txt.bind('<Return>', save)
        b = Button(tl, text='确认', command=save)
        b.pack(side=BOTTOM)

    def edit_py():
        ids = tv.selection()
        if not ids:
            return
        root.attributes('-disabled', 1)
        id_ = ids[0]
        idx = tv.index(id_)
        sent = core.sents.present_sent_idx(idx)
        content_chr = list(sent['base'][0])
        content_py = list(sent['base'][1])
        tl = Toplevel(root)
        tl.attributes('-toolwindow', 1)
        tl.resizable(0, 0)
        tl.focus()
        root_loc = root.geometry().split('+')[1:3]
        tl.geometry(f'270x600+{int(root_loc[0]) + 100}+{int(root_loc[1]) + 50}')
        tl.title('编辑拼音')

        def close():
            root.attributes('-disabled', 0)
            root.focus()
            tl.destroy()

        # content_chr = [str(i)+' '+ch for i, ch in enumerate(content_chr)]

        if len(content_chr) >= len(content_py):
            content_py.extend(['' for i in range(len(content_chr) - len(content_py))])
        else:
            content_chr.extend(['' for i in range(len(content_py) - len(content_chr))])

        tl.protocol('WM_DELETE_WINDOW', close)
        txt_fr = Frame(tl)
        scroll = Scrollbar(txt_fr)
        txt_num = Text(txt_fr, height=40, width=12, yscrollcommand=scroll.set, spacing1=5)
        txt_num.insert('insert', '\n'.join(str(x) for x in range(1, max(len(content_py), len(content_chr)) + 1)))
        txt_chr = Text(txt_fr, height=40, width=8, yscrollcommand=scroll.set, spacing1=5)
        txt_chr.insert('insert', '\n'.join(content_chr))
        txt = Text(txt_fr, height=40, width=10, yscrollcommand=scroll.set, spacing1=5)
        txt.insert('insert', '\n'.join(content_py))

        # str_vars = []
        # for i, t_ch in enumerate(content_chr):
        #     e_ch = Label(txt, text=t_ch, width=4, justify=RIGHT)
        #     e_ch.config(state=DISABLED)
        #     txt.window_create('insert', window=Label(txt, text=f'{i + 1}', width=2))
        #     txt.window_create('insert', window=e_ch)
        #     try:
        #         e_py_var = StringVar(value=content_py[i])
        #     except IndexError:
        #         e_py_var = StringVar(value='')
        #     str_vars.append(e_py_var)
        #     e_py = Entry(txt, textvariable=e_py_var, width=10)
        #     txt.window_create('insert', window=e_py)
        #     txt.insert('insert', '\n')

        scroll.config(command=lambda a, b: (txt.yview(a, b), txt_chr.yview(a, b)))
        txt_chr.config(state=DISABLED)

        def sync_yview():
            y = scroll.get()[0]
            txt.yview('moveto', y)
            txt_chr.yview('moveto', y)
            txt_num.yview('moveto', y)
            tl.after(50, sync_yview)

        tl.after(50, sync_yview)

        def save(event=None):
            def check_valid(t: str):
                if re.findall('[^a-z0-4\n]', t):
                    return False
                if t:
                    if t[0].isdigit():
                        return False
                    if t[-1] not in '01234':
                        if t != 'sil':
                            return False
                    for c in t[:-1]:
                        if c.isdigit():
                            return False
                else:
                    return False
                return True

            cleaned_items = []
            py_list = txt.get(1.0, 'end').split('\n')[:-1]  # 排除掉多get到的一个\n
            for i_, py in enumerate(py_list):
                if not check_valid(py):
                    cleaned_items.clear()
                    error_ch = sent['base'][0][i_]
                    messagebox.showerror(title='格式错误', message=f'错误位置：第{i_ + 1}个，“{error_ch}”字\n规则：\n不发声符号以sil标记\n'
                                                               f'轻声为0\n例：吃包子？ chi1 bao1 zi0 sil')
                    return
                else:
                    cleaned_items.append(py)

            ori_sent = core.sents.present_sent_idx(idx)
            ori_sent['base'][1] = cleaned_items
            ori_sent['data'] = core.sent_prototype()['data']
            result = core.sents.change_sent_idx(idx, ori_sent)
            if result:
                choice = blocked_ask(result[0])
                if choice:
                    core.sents.complete_change(result[1])
                    tv_update(False)
                    save()
                    return
                else:
                    return
            # core.sents[idx][2] = ['', '']
            root.attributes('-disabled', 0)
            root.focus()
            tv_update(chaos=False)
            core.need_save()
            tl.destroy()

        txt_fr.pack(side=LEFT)
        txt_num.pack(fill=Y, side=LEFT)
        txt_chr.pack(fill=Y, side=LEFT)
        txt.pack(fill=Y, side=LEFT)
        scroll.pack(fill=Y, side=LEFT)
        button_fr = Frame(tl)
        b = Button(button_fr, text='确认', command=save)
        button_fr.pack(fill=BOTH, side=LEFT, anchor=CENTER)
        b.pack(fill=X, anchor=CENTER, side=RIGHT)

    def auto(event=None, ids=None, callback=None):
        if ids is None:  # 不是被调用，而是由按钮直接触发
            ids = tv.selection()
        if not ids:
            if callback is not None:
                callback()
            return
        root.attributes('-disabled', 1)
        tl = Toplevel(root)
        tl.title('自动调教选项')
        tl.attributes('-toolwindow', 1)
        tl.attributes('-topmost', 1)
        # root_loc = root.geometry().split('+')[1:3]
        tl.geometry(f'200x70+800+400')
        tl.resizable(width=False, height=False)
        txt_var = StringVar(value='1.0')
        fr = Frame(tl)
        Label(fr, text='语速：').pack(side=LEFT)
        e = Entry(fr, textvariable=txt_var, width=4)
        e.pack(side=LEFT)
        Label(fr, text='倍(0.1~5.0)').pack(side=LEFT)

        def close():
            root.unbind('<Button-1>')
            root.attributes('-disabled', 0)
            root.focus()
            tl.destroy()

        tl.protocol('WM_DELETE_WINDOW', close)

        def exexute_tune(event=None):
            try:
                speed = float(txt_var.get())
                if not 0.1 <= speed <= 5.0:
                    raise ValueError
            except ValueError:
                messagebox.showerror('输入错误', '输入错误，需要输入0.1到5.0的整数或小数')
                tl.focus()
                e.focus()
                e.select_range(0, 'end')
                return
            idxes = [tv.index(id_) for id_ in ids]
            result = core.editor.fast_auto(idxes, speed=speed)
            if result:
                choice = blocked_ask(result[0])
                if choice:
                    core.sents.complete_change(result[1])
                    tv_update(False)
                    exexute_tune()  # 重新执行
                    return
                else:
                    return
            tv_update(chaos=False)
            core.need_save()
            if callback is not None:
                callback()
            close()

        fr.pack()
        Button(tl, text='确认转换', command=exexute_tune).pack()

        e.focus()
        e.select_range(0, 'end')
        e.bind('<Return>', exexute_tune)

    def manual(auto_pipeline=False):  # 只有在完成分析后才视为一个操作
        ids = tv.selection()
        if not ids:
            return
        root.attributes('-disabled', 1)
        id_ = ids[0]
        idx = tv.index(id_)
        block_inf = core.sents.blocked_inf_idx(idx)
        if block_inf is not None:
            choice = blocked_ask(idx)
            if choice:
                core.sents.complete_change(block_inf)
                tv_update(False)
                manual()
                return
            else:
                root.attributes('-disabled', 0)
                return
        # text = tv.item(id_)['values'][0]
        sent = core.sents.present_sent_idx(idx)
        text = sent['base'][0]
        py = tuple(sent['base'][1])

        if len(text) != len(py):
            messagebox.showinfo('提醒', '文字字符数量与拼音数量不同，可能导致拼音的标注发生错位\n同时，切分功能不可用')

        def multi_pre(dest):
            base = core.sents.present_sent_idx(dest)
            p_id, pol = core.register_subprocess()

            ori = core.sent_prototype()['data']
            ori[0] = 'wait'
            wait_sent = deepcopy(base)
            wait_sent['data'] = ori

            ori_abt = core.sent_prototype()['data']
            ori_abt[0] = 'abort'
            abort_sent = deepcopy(base)
            abort_sent['data'] = ori_abt

            mark = core.sents.wait(dest, wait_sent, abort_sent)
            tv_update(chaos=False)
            return mark, p_id, pol

        def finish_with_data(dest: int, data, mark, id_name):
            ori = core.sent_prototype()['data']
            ori[0:5] = ['v', data[0], data[1], [], '']
            dest_sent = core.sents.present_sent_idx(dest)
            dest_sent['data'] = ori  # 'v' for voice
            if data[2] is not None:
                cleaned_ori_py = []
                sil_idxs = []
                for i, py_ in enumerate(dest_sent['base'][1]):
                    if py_ == 'sil':
                        sil_idxs.append(i)
                    else:
                        cleaned_ori_py.append(py_)
                if len(cleaned_ori_py) != len(data[2]):
                    messagebox.showinfo(f'分析提示', f'第{dest + 1}句 标注字数与预设字数不同，可能有错误')
                py_result = []
                for i, p in enumerate(data[2]):
                    if not p:
                        try:
                            p = cleaned_ori_py[i]
                        except IndexError:
                            p = ''
                    py_result.append(p)
                # for idx_ in sil_idxs:
                #     py_result.insert(idx_, 'sil')
                dest_sent['base'][1] = py_result
                dest_sent['base'][2] = 'voice'
            if data[3] is not None:
                dest_sent['data'][3] = data[3][0]
                dest_sent['data'][4] = data[3][1]
            if data[4] is not None:  # intensity
                dest_sent['ref'][2] = data[4]

            core.sents.complete_change(mark, dest_sent)
            core.complete_subprocess(id_name)
            core.need_save()
            core.subprocess_finish_callback()
            tv_update(chaos=False)

        def set_filename(dest: int, rec='', tg='', seg_tg=''):
            dest_sent = core.sents.present_sent_idx(dest)
            if rec:
                dest_sent['ref'][0] = rec
            if tg:
                dest_sent['ref'][1] = tg
            if seg_tg:
                try:
                    dest_sent['ref'][3] = seg_tg
                except IndexError as e:
                    if len(dest_sent['ref']) == 3:
                        dest_sent['ref'] = dest_sent['ref'][:] + [seg_tg]
                    else:
                        raise e
            core.sents.change_sent_idx(dest, dest_sent)
            core.need_save()
            tv_update(chaos=False)

        def before_close():
            root.attributes('-disabled', 0)

        wavname = core.file_relative_path('wav', original=sent['ref'][0])
        tgname = core.file_relative_path('TextGrid', original=sent['ref'][1])
        try:
            ori = sent['ref'][3]
        except IndexError:
            ori = ''
        seg_tgname = core.file_relative_path('TextGrid_segment', original=ori)

        cg = ConverterGUI(core=core, dest=idx, tex=text,
                          py=py,
                          wavname=wavname,
                          tgname=tgname,
                          seg_tgname=seg_tgname,
                          multi_pre_func=multi_pre,
                          finish_func=finish_with_data,
                          close_func=before_close,
                          set_filename_func=set_filename,
                          newly_installed=core.newly_installed,
                          gui_root=root)
        if auto_pipeline:
            cg.auto_pipeline()

        # root_loc = root.geometry().split('+')[1:3]
        # cg.tl().geometry(f'+800+450')

    def auto_imit():
        ids = tv.selection()
        if not ids:
            return
        idxs = [tv.index(id_) for id_ in ids]
        to_exe = []
        to_info = []
        for idx in idxs:
            block_inf = core.sents.blocked_inf_idx(idx)
            if block_inf is not None:
                continue
            sent = core.sents.present_sent_idx(idx)
            text = sent['base'][0]
            py = tuple(sent['base'][1])
            if len(text) != len(py):
                to_info.append(idx)
            to_exe.append(idx)
        if to_info:
            messagebox.showinfo('提醒', f'第{"、".join([str(i + 1) for i in to_info])}句文字字符数量与拼音数量不同，可能导致拼音的标注发生错位')
        if to_exe:
            core.editor.batch_imitate_pipeline(to_exe, )

            # manual(True)

    label_time_left = [0]

    def inform(text='', time=1500, variable=label_time_left):  # 利用py函数可变默认参数只加载一次的特性
        def get_hidden(expected, t=''):
            if expected != label_time_left[0]:  # 避免重复计时
                return
            if t:
                l_out_var.set(t)
            unit = 50
            mark = label_time_left[0] - unit
            if mark < 0:
                l_out.pack_forget()
                label_time_left[0] = 0
            else:
                label_time_left[0] = mark
                root.after(unit, get_hidden, mark)

        variable[0] = time
        l_out.pack(side=BOTTOM)
        get_hidden(time, text)

    def output():
        ids = tv.selection()
        if not ids:
            return
        idxs = [tv.index(id_) for id_ in ids]
        ids_to_auto = []
        for idx in idxs:
            if core.sents.is_waiting(idx):
                inform(f'第{idx + 1}句\n无法输出')
                return
        for i, idx in enumerate(idxs):
            if core.sents.present_sent_idx(idx)['data'][0] == core.sent_prototype()['data'][0]:
                ids_to_auto.append(ids[i])

        def execute_output():
            idxs.sort()
            dest = core.output_tune_file(idxs)
            inform('已输出到\n/outputs')
            if core.settings.get('save_dub_after_output', 0):
                core.output_dub(idxs)
            if core.settings.get('open_after_output', 0):
                os.startfile(dest)

        auto(ids=ids_to_auto, callback=execute_output)

    def set_intensity():
        ids = tv.selection()
        if not ids:
            return
        idxs = [tv.index(id_) for id_ in ids]
        idx = idxs[0]
        sent = core.sents.present_sent_idx(idx, dc=False)
        try:
            if not sent['ref'][2]:
                raise IndexError
        except IndexError:
            inform('没有获取\n参考声强')
            return
        block_inf = core.sents.blocked_inf_idx(idx)
        if block_inf is not None:
            choice = blocked_ask(idx)
            if choice:
                core.sents.complete_change(block_inf)
                tv_update(False)
                set_intensity()
                return
            else:
                root.attributes('-disabled', 0)
                return
        default = core.settings['loudness_dir']
        location = filedialog.askopenfilename(title='打开',
                                              filetypes=[('WAV音频文件', '*.wav')],
                                              initialdir=default)
        if not location:
            return
        core.add_dyn(idx, location, tv_update)
        tv_update(chaos=False)

    def set_open():
        core.change_settings_save({'open_after_output': open_var.get()})

    def set_dub():
        core.change_settings_save({'save_dub_after_output': dub_var.get()})

    def open_outputs():
        os.system('start outputs')

    fr3 = Frame(root)
    b_text = Button(fr3, text='编辑文本', command=edit_text)  # 保存后自动生成拼音
    b_py = Button(fr3, text='编辑拼音', command=edit_py)
    b_auto = Button(fr3, text='快速调教', command=auto)
    b_auto_imit = Button(fr3, text='自动示读', command=auto_imit)
    b_manu = Button(fr3, text='高级示读', command=manual)
    b_its = Button(fr3, text='音量修正', command=set_intensity)
    l_out_var = StringVar()
    l_out = Label(fr3, textvariable=l_out_var)
    b_out = Button(fr3, text='输出所选', command=output)
    open_var = IntVar()
    open_var.set(core.settings.get('open_after_output', 0))
    cb_open = Checkbutton(fr3, text='并打开', variable=open_var, command=set_open)
    dub_var = IntVar()
    dub_var.set(core.settings.get('save_dub_after_output', 0))
    cb_dub = Checkbutton(fr3, text='字幕', variable=dub_var, command=set_dub)
    b_path = Button(fr3, text='打开目录', command=open_outputs)

    b_text.pack(side=TOP)
    b_py.pack(side=TOP)
    ttk.Separator(fr3, orient=HORIZONTAL).pack(pady=2, side=TOP, fill=X)
    b_auto.pack(side=TOP)
    b_auto_imit.pack(side=TOP)
    b_manu.pack(side=TOP)
    ttk.Separator(fr3, orient=HORIZONTAL).pack(pady=2, side=TOP, fill=X)
    b_its.pack(side=TOP)
    b_path.pack(side=BOTTOM)
    cb_open.pack(side=BOTTOM)
    cb_dub.pack(side=BOTTOM)
    b_out.pack(side=BOTTOM)

    fr2.pack(side=LEFT, fill=Y)
    fr1.pack(side=LEFT, fill=BOTH, expand=True)
    fr3.pack(side=RIGHT, fill=Y)

    # 拖动排序
    start_i = [0]

    def bDown(event):
        if not arrange_var.get():
            return
        tv_father = event.widget
        if tv_father.identify_row(event.y) not in tv_father.selection():
            tv_father.selection_set(tv_father.identify_row(event.y))
        start_i[0] = tv.index(tv_father.identify_row(event.y))

    def bUp(event):
        if not arrange_var.get():
            return
        tv_father = event.widget
        if tv_father.identify_row(event.y) in tv_father.selection():
            tv_father.selection_set(tv_father.identify_row(event.y))
        end_i = tv.index(tv_father.identify_row(event.y))
        core.sents.move(start_i[0], end_i)
        tv_update(chaos=False)
        core.need_save()
        start_i[0] = 0

    def bMove(event):
        if not arrange_var.get():
            return
        tv_father = event.widget
        moveto = tv_father.index(tv_father.identify_row(event.y))
        for s in tv_father.selection():
            tv_father.move(s, '', moveto)

    tv.bind("<ButtonPress-1>", bDown)
    tv.bind("<ButtonRelease-1>", bUp, add='+')
    tv.bind("<B1-Motion>", bMove, add='+')

    root.bind('<Control-s>', save_file)
    root.bind('<Control-S>', save_file)

    root.bind('<Control-z>', draw_back)
    root.bind('<Control-Z>', draw_back)

    root.bind('<Control-y>', recover)
    root.bind('<Control-Y>', recover)

    root.mainloop()  # 会触发其他library里面的tk组件
