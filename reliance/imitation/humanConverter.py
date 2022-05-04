import tkinter.ttk as ttk
from tkinter import *
from tkinter import messagebox, filedialog, font
from reliance.imitation.audioTools import Recorder, to_one_channel_file
from reliance.imitation.play import Player
from reliance.imitation.praatDealer import start_edit, create_seg_tg, get_seg_lengths
# from reliance.sppasDealer import Sppas
import reliance
from reliance.imitation.mfaDealer import Mfa, MfaImported
from reliance.global_vars import vsqx_initial
from reliance.tyTalk.talker import Talker
import time
import reliance.imitation.voiceAnaysis.analyzer as av
import pickle
import os
import threading
import multiprocessing
import wave
import winsound
import reliance.imitation.tts
import multiprocessing.pool

JULIUS_PATH = 'C://Windows//julius.exe'


def add_dyn(raw_wav_fn, aim_array, initial=vsqx_initial):  # 大约有两秒整的提前
    return av.dyn_correct(raw_wav_fn, aim_array, initial)


def _render_output(func, storage_dict, *args):
    result = func(args[0], args[1], consonant_control=args[2])
    for r in result:
        storage_dict.append(r)


# class Converter:
#     """
#     developing
#     the core silent converter
#     """
#     def __init__(self, core=None, dest=int(), tex='', py=(), wavname='', tgname='', seg_tgname='', multi_pre_func=None,
#                  finish_func=None, close_func=None, set_filename_func=None, newly_installed=None):
#         self.filenames = {'wav': wavname, 'annotation': tgname, 'segment': seg_tgname}
#         self.pre_set_data_func = multi_pre_func
#         self.set_data_func = finish_func
#         self.set_filename_func = set_filename_func
#         self.text = tex
#         self.py = py
#         self.dest = dest
#         self.vtalker = av.vtalker()
#         if tgname:
#             self.vtalker.textgrid_name = tgname


class ConverterGUI:
    def __init__(self, core=None, dest=int(), tex='', py=(), wavname='', tgname='', seg_tgname='', multi_pre_func=None,
                 finish_func=None, close_func=None, set_filename_func=None, newly_installed=None,
                 gui_root=None):  # core: MainContainer
        """

        :param core:
        :param dest: 目标句子在列表中的位置，只用于回调函数，本不必传进本对象中，属于冗余项
        """
        self.gui_root = gui_root
        if core is None:
            raise ValueError('参数core必须传入一个（MainContainer）对象')
        else:
            self.root = Toplevel(self.gui_root)
            self.individual = False
            self.settings_relative_path = core.settings_relative_path + r'\converter_setting'
        try:
            with open(self.settings_relative_path, 'rb') as f:
                pass
        except FileNotFoundError:
            settings = [2, 2]
            with open(self.settings_relative_path, 'wb') as f:
                pickle.dump(settings, f)
        self.root.focus()
        self.root.lift()
        self.root.attributes('-topmost', 1)
        self.filenames = {'wav': wavname, 'annotation': tgname, 'segment': seg_tgname}
        self.root.title('人声')
        self.core = core
        self.pre_set_data_func = multi_pre_func
        self.set_data_func = finish_func
        self.before_close_func = close_func
        self.set_filename_func = set_filename_func
        self.text = tex
        self.ori_py = py
        self.py = self.ori_py
        self.dest = dest
        self._render_func = _render_output
        self.root.geometry('280x130+800+450')
        self.vtalker = av.vtalker()
        if tgname:
            self.vtalker.textgrid_name = tgname
        self.praat_saved = True  # if false then the tg is being edited
        self.importing = False
        self.auto_marking = False
        self.main_running = True

        self.seg_editing = False
        self.seg_existing = os.path.exists(self.filenames['segment'])
        self.tg_need_create = not os.path.exists(self.filenames['annotation'])  # 为了区分目前存在的标注文件是否是对应录音的文件

        self.root.resizable(0, 0)
        self.ending_func = []

        self.install = newly_installed

        self.base_frame = Frame(self.root)
        base_frame = self.base_frame
        base_frame.pack()
        rec_frame = Frame(base_frame)
        tg_frame = Frame(base_frame)
        out_frame = Frame(base_frame)
        Label(rec_frame).pack()
        rec_frame_top = Frame(rec_frame)
        rec_frame_top.pack()
        br = Button(rec_frame_top, text='录音', command=self._record)
        br.pack(side=LEFT)
        bi = Button(rec_frame_top, text='导入', command=self._record_import)
        bi.pack(side=RIGHT)
        btts = Button(rec_frame, text='自动生成', command=self._tts)
        btts.pack()
        rec_str = StringVar()
        Label(rec_frame, textvariable=rec_str).pack(side=BOTTOM)
        tg_frame_top = Frame(tg_frame)
        tg_frame_top.pack()
        bauto = Button(tg_frame_top, text='自动标注', command=self._auto_mark)
        # bauto = Button(tg_frame_top, text='简易标记', command=self._replay_mark)  # renamed variable
        bauto.pack(side=LEFT)
        bseg = Button(tg_frame_top, text='切分', command=self._seg)
        bseg.pack(side=RIGHT)
        Label(tg_frame, text='或').pack()
        tg_frame_bottom = Frame(tg_frame)
        tg_frame_bottom.pack()
        bp = Button(tg_frame_bottom, text='新建标记', command=self._make_tg)
        bp.pack(side=LEFT)
        bp_i = Button(tg_frame_bottom, text='导入', command=self._textgrid_import)
        bp_i.pack(side=RIGHT)
        Label(tg_frame).pack()
        anno_var = StringVar(value='标注')
        lanno = Label(tg_frame, textvariable=anno_var)
        lanno.pack(side=BOTTOM)
        bo = Button(out_frame, text='启动分析', command=self._output)
        bo.pack()
        self.out_var = IntVar(value=2)
        auto_out_rb = Radiobutton(out_frame, variable=self.out_var, value=0, text='自动')
        # auto_out_rb.pack()
        tg_out_rb = Radiobutton(out_frame, variable=self.out_var, value=1, text='手动')
        # tg_out_rb.pack()
        Label(out_frame, text='输出').pack(side=BOTTOM)

        rec_frame.pack(side=LEFT, fill=Y)
        ttk.Separator(base_frame, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=2)
        tg_frame.pack(side=LEFT, fill=Y)
        ttk.Separator(base_frame, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=2)
        out_frame.pack(side=LEFT, fill=Y)

        self.br = br
        self.bp_i = bp_i
        self.bauto = bauto
        self.bo = bo
        self.bp = bp
        self.bseg = bseg

        self.text_tl = Toplevel(self.root)
        self.text_tl.resizable(0, 500)
        self.text_tl.geometry('580x100+200+100')
        self.text_tl.title('文字内容')

        def unset_top(event=None):
            menubar.delete(0, END)
            menubar.add_command(label='顶置', command=set_top)
            self.text_tl.attributes('-topmost', 0)

        def set_top(event=None):
            menubar.delete(0, END)
            menubar.add_command(label='取消顶置', command=unset_top)
            self.text_tl.attributes('-topmost', 1)

        menubar = Menu(self.text_tl, tearoff=False)
        menubar.delete(0, END)
        menubar.add_command(label='顶置', command=set_top)

        def rightKey(event):
            menubar.post(event.x_root, event.y_root)

        self.text_tl.bind("<Button-3>", rightKey)

        scroll = Scrollbar(self.text_tl)
        ft = font.Font(size=13)
        txt = Text(self.text_tl, yscrollcommand=scroll.set, font=ft, width=62)
        txt.insert('insert', self.text)
        txt.config(state=DISABLED)
        scroll.config(command=txt.yview)
        txt.pack(fill=BOTH, side=LEFT)
        scroll.pack(fill=BOTH, side=LEFT)

        def refresh():
            if self.importing:
                rec_str.set('录音：导入中')
                br['state'] = DISABLED
                bi['state'] = DISABLED
                btts['state'] = DISABLED
                self.bauto['state'] = DISABLED
                self.bp['state'] = DISABLED
                self.bp_i['state'] = DISABLED
                self.bo['state'] = DISABLED
                tg_out_rb['state'] = DISABLED
                auto_out_rb['state'] = DISABLED
            elif self.auto_marking:
                anno_var.set('标注：生成中')
                br['state'] = DISABLED
                bi['state'] = DISABLED
                btts['state'] = DISABLED
                self.bauto['state'] = DISABLED
                self.bp['state'] = DISABLED
                self.bp_i['state'] = DISABLED
                self.bo['state'] = DISABLED
                tg_out_rb['state'] = DISABLED
                auto_out_rb['state'] = DISABLED
                self.bseg['state'] = DISABLED
            else:
                br['state'] = NORMAL
                bi['state'] = NORMAL
                btts['state'] = NORMAL
                if not os.path.exists(self.filenames['wav']):
                    wav_existing = False
                    # self.tg_need_create = True
                    self.bauto['state'] = DISABLED
                    self.bp['state'] = DISABLED
                    self.bp_i['state'] = DISABLED
                    rec_str.set('录音：未完成')
                else:
                    wav_existing = True
                    self.bauto['state'] = NORMAL
                    self.bp['state'] = NORMAL
                    self.bp_i['state'] = NORMAL
                    rec_str.set('录音：  完成')
                if self.vtalker.textgrid_name \
                        and os.path.exists(self.vtalker.textgrid_name) \
                        and not self.tg_need_create:
                    textgrid_existing = True
                else:
                    textgrid_existing = False
                # if (not self.vtalker.boundaries_inf and not textgrid_existing) or not wav_existing:
                if (not self.vtalker.auto_tg_name and not textgrid_existing) or not wav_existing:
                    self.bo['state'] = DISABLED
                    tg_out_rb['state'] = DISABLED
                    auto_out_rb['state'] = DISABLED
                    anno_var.set('标注')
                    if self.praat_saved:
                        self.bp.config(text='新建标注')
                        anno_var.set('标注')
                else:
                    if textgrid_existing:
                        tg_out_rb['state'] = NORMAL
                        if self.praat_saved:
                            self.bp.config(text='编辑标注')
                            anno_var.set('标注')
                        # if not self.vtalker.boundaries_inf:
                        if not self.vtalker.auto_tg_name:
                            self.out_var.set(1)
                            auto_out_rb['state'] = DISABLED
                    # if self.vtalker.boundaries_inf:
                    if self.vtalker.auto_tg_name:
                        auto_out_rb['state'] = NORMAL
                        if not textgrid_existing:
                            self.out_var.set(0)
                            tg_out_rb['state'] = DISABLED
                            self.bp.config(text='新建标注')
                            anno_var.set('标注')
                if textgrid_existing and self.praat_saved:  # 使用按钮状态判断是否完成标注
                    self.bo['state'] = NORMAL
                    anno_var.set('标注')
                if not self.praat_saved:
                    self.bo['state'] = DISABLED
                    br['state'] = DISABLED
                    bi['state'] = DISABLED
                    btts['state'] = DISABLED
                    self.bauto['state'] = DISABLED
                    self.bp_i['state'] = DISABLED
                    self.bo['state'] = DISABLED
                    tg_out_rb['state'] = DISABLED
                    auto_out_rb['state'] = DISABLED
                    self.bp.config(text='保存标注')
                    anno_var.set('标注：编辑中')
                if self.seg_editing:
                    self.bo['state'] = DISABLED
                    br['state'] = DISABLED
                    bi['state'] = DISABLED
                    btts['state'] = DISABLED
                    self.bauto['state'] = DISABLED
                    self.bp_i['state'] = DISABLED
                    self.bo['state'] = DISABLED
                    tg_out_rb['state'] = DISABLED
                    auto_out_rb['state'] = DISABLED
                    self.bp['state'] = DISABLED
                    self.bseg['state'] = NORMAL
                    self.bseg.config(text='保存')
                else:
                    if self.bauto['state'] == DISABLED:
                        self.bseg['state'] = DISABLED
                    else:
                        self.bseg['state'] = NORMAL

            self.root.after(50, refresh)

        refresh()

        self.root.protocol('WM_DELETE_WINDOW', self.exit_)
        self.root.focus()
        self.root.lift()

    def exit_(self):
        if self.auto_marking:
            if not messagebox.askyesno('自动标注中', '正在进行自动标注，是否退出并放弃？', master=self.root):
                return
        for func in self.ending_func:
            func()
        self.before_close_func()
        self.main_running = False
        self.root.destroy()
        self.gui_root.lift()  # "core" doesn't have any ".root"
        self.gui_root.focus()

    def _record(self):
        self.root.attributes('-disabled', 1)
        start_time = [float()]
        boundaries = []
        boundText = StringVar(value='等待开始')

        bMaster = self.br
        bMaster['state'] = DISABLED
        tl = Toplevel(self.root)
        tl.geometry('220x120')
        tl.resizable(0, 0)
        tl.focus()
        MainF = Frame(tl)
        MainF.pack()
        # txt = Text(MainF)  # 适配问题，不弄了
        # txt.insert("insert", self.text)
        # txt['state'] = DISABLED
        # txt.pack()

        choice = IntVar()
        with open(self.settings_relative_path, 'rb') as f:
            settings = pickle.load(f)
        choice.set(settings[0])
        left_panel = Frame(MainF)

        def menu():
            def save(event=None):
                settings[0] = event.widget['value']
                with open(self.settings_relative_path, 'wb') as f:
                    pickle.dump(settings, f)

            with open(self.settings_relative_path, 'rb') as f:
                choice.set(pickle.load(f)[0])

            tl2 = Toplevel(tl)
            tl2.geometry('160x60')
            tl2.resizable(0, 0)
            tl2.focus()
            r1 = Radiobutton(tl2, text='单按', variable=choice, value=0)
            r2 = Radiobutton(tl2, text='按抬', variable=choice, value=1)
            r3 = Radiobutton(tl2, text='双按', variable=choice, value=2)
            r1.bind('<Button-1>', save)
            r2.bind('<Button-1>', save)
            r3.bind('<Button-1>', save)

            r1.pack(side='left')
            r2.pack(side='left')
            r3.pack(side='left')

        # left_panel.grid(column=0, sticky=W)
        Label(left_panel, textvariable=boundText).pack()
        setting_button = Button(left_panel, text='设置标记方法', command=menu)
        setting_button.pack()

        recorder = Recorder(of=self.filenames['wav'])
        self.ending_func.append(recorder.abort)
        status = StringVar()

        def recording():
            if recorder.rec_flag:
                status.set('录音中')
            else:
                status.set('未录音')
            tl.after(50, recording)

        recording()

        def start_record(event=None):
            boundText.set('标记数：{}'.format(len(boundaries)))
            btn1.grid_forget()
            btn3.grid(row=2, column=0, columnspan=2)
            btn2.grid(row=1, column=0, columnspan=2)
            recorder.start()
            start_time[0] = time.time()  # 避免局部变量
            btn1['state'] = DISABLED
            tl.unbind('<Return>')
            tl.bind('<Return>', lambda e: btn2.invoke())
            # tl.bind('<KeyPress-Down>', add_bound)
            # if choice.get() == 2:
            #     tl.bind('<Right>', add_bound)
            # elif choice.get() == 1:
            #     tl.bind('<KeyRelease-Down>', add_bound)
            setting_button['state'] = DISABLED

        tl.bind('<Return>', start_record)

        def complete_record():
            recorder.complete()
            self._update_record_inf()
            exit_()

        def restart_record():
            btn2.grid_forget()
            btn3.grid_forget()
            boundaries.clear()
            start_time[0] = float()
            boundText.set('等待开始')
            btn1.grid(row=1, column=0, columnspan=2)
            btn1['state'] = NORMAL
            setting_button['state'] = NORMAL
            tl.unbind('<Down>')
            tl.unbind('<Return>')
            tl.bind('<Return>', lambda e: btn1.invoke())

            recorder.abort()

        right_panel = Frame(MainF)
        btn1 = Button(right_panel, text='开始录制', command=start_record)
        label = Label(right_panel, textvariable=status)
        btn2 = Button(right_panel, text='完成录制', command=complete_record)
        btn3 = Button(right_panel, text='取消重录', command=restart_record)

        # ttk.Separator(MainF, orient=VERTICAL).grid(row=0, column=1, ipady=50, padx=5)
        right_panel.pack()
        Label(right_panel, text='状态：').grid(row=0, column=0, sticky=W)
        label.grid(row=0, column=1, sticky=E)
        btn1.grid(row=1, column=0, columnspan=2)

        # def add_bound(event):
        #     if recorder.rec_flag:
        #         boundaries.append(time.time() - start_time[0])
        #         boundText.set('标记数：{}'.format(len(boundaries)))

        def exit_():
            self.root.attributes('-disabled', 0)
            bMaster['state'] = NORMAL
            self.bo['state'] = NORMAL
            recorder.abort()
            tl.destroy()

        tl.protocol('WM_DELETE_WINDOW', exit_)

    def _record_import(self):
        default = os.path.join(os.path.expanduser('~'), "Desktop")
        location = filedialog.askopenfilename(title='打开',
                                              filetypes=[('WAV音频文件', '*.wav')],
                                              initialdir=default)
        self._import_from(location)
        self.root.lift()
        self.root.focus()

    def _import_from(self, location, tts=False, in_pipeline=False):
        if location:
            def func():
                to_one_channel_file(location, self.filenames['wav'])
                if not self.main_running:
                    return
                self.importing = False

                if tts and False:
                    self.py = Talker().get_py(self.text)[0]
                else:
                    self.py = self.ori_py
                self._update_record_inf()

            self.importing = True
            if in_pipeline:
                func()
            else:
                threading.Thread(target=func).start()

    def _update_record_inf(self):
        self.set_filename_func(dest=self.dest, rec=self.filenames['wav'])
        self.tg_need_create = True
        self.vtalker.textgrid_name = None
        self.vtalker.auto_tg_name = None
        create_seg_tg(self.filenames['wav'], self.filenames['segment'], [self.text], just_len=len(self.py))

    def _tts(self, in_pipeline=False):
        location = 'misc/temp/tts_temp/tts.wav'
        if not os.path.exists(os.path.dirname(location)):
            os.makedirs(os.path.dirname(location))
        reliance.imitation.tts.render(self.text, location)
        self._import_from(location, tts=True, in_pipeline=in_pipeline)

    def _make_tg(self, reopen=False, use_praat=True):
        def complete_edit():

            if os.path.exists(self.filenames['annotation']):
                self.set_filename_func(dest=self.dest, tg=self.filenames['annotation'])
                self.vtalker.textgrid_name = self.filenames['annotation']
                self.tg_need_create = False
            else:
                if use_praat:
                    messagebox.showerror('无标注文件', '保存失败。未找到标注文件，请在标注后按“continue”进行保存')
                return
            try:
                os.remove('temp.praat')
            except:
                pass
            self.praat_saved = True
            self.bp.config(text='编辑标注', command=self._make_tg)

        if use_praat:
            self.praat_saved = False
            start_edit(self.filenames['wav'], self.filenames['annotation'], self.tg_need_create, reopen)
            self.bp.config(text='保存编辑', command=complete_edit)
        else:
            complete_edit()

    def _textgrid_import(self, source=None):
        default = os.path.join(os.path.expanduser('~'), "Desktop")
        if source is None:
            location = filedialog.askopenfilename(title='打开',
                                                  filetypes=[('Praat标注文件', '*.TextGrid')],
                                                  initialdir=default)
        else:
            location = source

        if location:
            with open(location, 'rb') as f:
                data = f.read()
            with open(self.filenames['annotation'], 'wb') as f:
                f.write(data)
            self.vtalker.textgrid_name = self.filenames['annotation']
            self.set_filename_func(dest=self.dest, tg=self.filenames['annotation'])
            self.tg_need_create = False
        self.root.lift()
        self.root.focus()

    def _replay_mark(self):
        self.root.attributes('-disabled', 1)
        if not os.path.exists(self.filenames['wav']):
            messagebox.showerror('没有录音', '还没有录音文件，请先录音或导入')
            self.root.focus()
            self.root.attributes('-disabled', 0)
            return
        start_time = [float()]
        boundaries = []
        bias = -250

        speed = {0: 0.1, 1: 0.3, 2: 0.5, 3: 1.0}

        bMaster = self.bauto
        bMaster['state'] = DISABLED
        tl = Toplevel(self.root)
        tl.geometry('220x140')
        tl.resizable(0, 0)
        tl.focus()
        MainF = Frame(tl)
        MainF.pack()
        Label(tl, text='字开始时按↓键，字结束时按→键\n可以省略').pack()

        speed_time = IntVar()
        boundText = StringVar(value='速率 {}'.format(speed[speed_time.get()]))
        with open(self.settings_relative_path, 'rb') as f:
            settings = pickle.load(f)
        speed_time.set(settings[1])
        left_panel = Frame(MainF)

        def menu():
            def save_set(event=None):
                speed_time.set(choice.get())
                settings[1] = speed_time.get()
                with open(self.settings_relative_path, 'wb') as f:
                    pickle.dump(settings, f)
                player.set_speed(speed[speed_time.get()])
                boundText.set('速率 {}'.format(speed[speed_time.get()]))
                tl2.destroy()

            choice = IntVar()
            choice.set(speed_time.get())
            tl2 = Toplevel(tl)
            tl2.geometry('160x140')
            tl2.resizable(0, 0)
            tl2.focus()
            f1 = Frame(tl2)
            f2 = Frame(tl2)

            r1 = Radiobutton(f1, text='x0.1', variable=choice, value=0)
            r2 = Radiobutton(f1, text='x0.3', variable=choice, value=1)
            r3 = Radiobutton(f1, text='x0.5', variable=choice, value=2)
            r4 = Radiobutton(f1, text='x1.0', variable=choice, value=3)

            f1.pack(side=LEFT)
            f2.pack(side=RIGHT)
            Label(f2, text='保存后稍等').pack()
            Button(f2, text='保存设置', command=save_set).pack()
            r1.pack()
            r2.pack()
            r3.pack()
            r4.pack()

        left_panel.grid(column=0, sticky=W)
        Label(left_panel, textvariable=boundText).pack()
        setting_button = Button(left_panel, text='设置慢放倍率', command=menu)
        setting_button.pack()

        player = Player(fn=self.filenames['wav'])
        player.set_speed(speed[speed_time.get()])
        self.ending_func.append(player.stop)
        status = StringVar()

        def playing():
            if player.play_flag:
                status.set('播放中')
            elif player.natural_end:
                status.set('已播完')
                if boundaries:
                    if boundaries[-1][1] != 'end':
                        add_end()
            else:
                status.set('未播放')
            tl.after(50, playing)

        playing()

        def start_play(event=None):
            boundText.set('标记数：{}'.format(len(boundaries)))
            btn1.grid_forget()
            btn3.grid(row=2, column=0, columnspan=2)
            btn2.grid(row=1, column=0, columnspan=2)
            player.start()
            start_time[0] = time.time()  # 避免局部变量
            btn1['state'] = DISABLED
            tl.unbind('<Return>')
            tl.bind('<KeyPress-Down>', add_start)
            tl.bind('<KeyPress-Right>', add_end)
            tl.bind('<Return>', lambda e: btn2.invoke())
            # if choice.get() == 2:
            #     tl.bind('<Right>', add_start)
            # elif choice.get() == 1:
            #     tl.bind('<KeyRelease-Down>', add_start)
            setting_button['state'] = DISABLED

        tl.bind('<Return>', start_play)

        def complete_play(event=None, write=False):
            if boundaries and player.play_flag:  # 自然终止的end已经加入了
                if boundaries[-1][1] != 'end':
                    add_end()
            if boundaries[0][1] != 'start':
                add_start(loc=0)

            boundaries_insert = []
            last_label = ''
            for i, boundary in enumerate(boundaries):
                if boundary[1] == last_label == 'start':
                    boundaries_insert.append((i, 'end'))
                elif boundary[1] == last_label == 'end':
                    boundaries_insert.append((i, 'start'))
                last_label = boundary[1]
            # print(boundaries_insert)
            inserted_count = 0
            for boundary_insert in boundaries_insert:
                actual_index = boundary_insert[0] + inserted_count
                if boundary_insert[1] == 'start':
                    boundaries.insert(actual_index, (boundaries[actual_index - 1][0], 'start'))
                elif boundary_insert[1] == 'end':
                    boundaries.insert(actual_index, (boundaries[actual_index][0], 'end'))
                inserted_count += 1

            player.stop()
            boundaries.insert(0, bias)
            if write:
                with open('boundaries.txt', 'w') as f:
                    f.write(str(boundaries[0]))
                    f.write('\n'.join([str(b[0]) + ' ' + b[1] for b in boundaries[1:]]))
            else:
                self.vtalker.boundaries_inf = boundaries
            exit_()

        def restart_play():
            btn2.grid_forget()
            btn3.grid_forget()
            boundaries.clear()
            start_time[0] = float()
            boundText.set('速率 {}'.format(speed[speed_time.get()]))
            btn1.grid(row=1, column=0, columnspan=2)
            btn1['state'] = NORMAL
            setting_button['state'] = NORMAL
            tl.unbind('<Down>')
            tl.unbind('<Return>')
            tl.bind('<Return>', lambda e: btn1.invoke())

            player.stop()

        right_panel = Frame(MainF)
        btn1 = Button(right_panel, text='开始标记', command=start_play)
        label = Label(right_panel, textvariable=status)
        btn2 = Button(right_panel, text='完成标记', command=complete_play)
        btn3 = Button(right_panel, text='取消重标', command=restart_play)

        ttk.Separator(MainF, orient=VERTICAL).grid(row=0, column=1, ipady=50, padx=5)
        right_panel.grid(row=0, column=2, sticky=E)
        Label(right_panel, text='状态：').grid(row=0, column=0, sticky=W)
        label.grid(row=0, column=1, sticky=E)
        btn1.grid(row=1, column=0, columnspan=2)

        def add_start(event=None, loc=None):
            if player.play_flag:
                if loc is None:
                    boundaries.append(((time.time() - start_time[0]) * speed[speed_time.get()], 'start'))
                else:
                    boundaries.append((loc, 'start'))
                boundText.set('标记数：{}'.format(len(boundaries)))

        def add_end(event=None, loc=None):
            if player.play_flag:
                if loc is None:
                    boundaries.append(((time.time() - start_time[0]) * speed[speed_time.get()], 'end'))
                else:
                    boundaries.append((loc, 'end'))
                boundText.set('标记数：{}'.format(len(boundaries)))

        def exit_():
            self.root.attributes('-disabled', 0)
            bMaster['state'] = NORMAL
            self.bo['state'] = NORMAL
            player.stop()
            tl.destroy()

        tl.protocol('WM_DELETE_WINDOW', exit_)

    def _auto_mark(self, in_pipeline=False):  # 直接覆盖手动标注
        if self.core.settings['forced_aligner'] == 'sppas' and not os.path.exists(JULIUS_PATH):
            os.system('start c://Windows')
            os.system('start misc')
            messagebox.showinfo('注册标注器',
                                '初次使用自动标注，请将"misc"文件夹中的标注器"julius.exe"手动复制到"C://Windows"文件夹中。\n\nJulius是开源的自动标注软件:\nCopyright (c) 2005-2015 \nJulius project team, Lee Lab., Nagoya Institute of Technology\n\nCopyright (c) 2008 \nRyuichi Nisimura')
            self.root.lift()
            return
        # if len(self.py) != len(self.text):
        #     messagebox.showerror('拼音和文字未对齐', '拼音和文字数量不同，无法自动对齐。\n可以回到主界面，点击“编辑文本”重新生成拼音。')
        #     return

        # only_vowels = messagebox.askyesno('是否简易标注', '是否只标注整个音节（不标注辅音，更快完成标注对齐）')
        only_vowels = False

        with wave.open(self.filenames['wav'], 'r') as f:
            length_second = f.getnframes() / f.getframerate()
        # if length_second > 20 and not self.seg_existing:
        #     messagebox.showinfo('需要切分', '音频大于20秒，请先进行切分哦')
        #     self.root.lift()
        #     return
        if not self.tg_need_create and not in_pipeline:
            if not messagebox.askyesno('覆盖', '是否覆盖已经存在的标注？', master=self.root):
                self.root.lift()
                return
            self.root.lift()
        dest_name_list = self.filenames['annotation'].split('.')
        dest_name_list[-2] = dest_name_list[-2] + '_auto'
        dest_name = '.'.join(dest_name_list)
        if self.core.settings['forced_aligner'] == 'sppas':
            pass
            # aligner = Sppas(self.filenames['wav'], self.filenames['segment'], self.py, self.text)
        else:
            aligner = MfaImported(self.filenames['wav'], self.filenames['segment'], self.py, self.text, install=self.install)

        def mark():
            try:
                cwd = os.getcwd()
                aligner.execute_alignment()
                os.chdir(cwd)
                if not self.main_running:
                    return
            except Exception as e:
                self.auto_marking = False
                messagebox.showerror('自动标注错误(生成)', f'自动标注发生错误\n可能是由于拼音和符号未对齐，音频太长、发音不清晰或音质太差\n请尝试重新录音或切分，或使用手动标注')
                raise e
            try:
                aligner.transcribe_to(dest_name, only_vowels)
            except Exception as e:
                self.auto_marking = False
                messagebox.showerror('自动标注错误(转写)',
                                     '自动标注结果错误，可能是由于音频太长、发音不清晰或音质太差，请使用切分将每个分段的音频保持在30秒以内（10秒内最佳）\n也可直接开始手动标注')
                raise e
            with open(dest_name, 'rb') as f:
                data = f.read()
            with open(self.filenames['annotation'], 'wb') as f:
                f.write(data)
            self.vtalker.auto_tg_name = dest_name
            self.tg_need_create = False
            self.auto_marking = False
            self._make_tg(reopen=False, use_praat=False)
            winsound.MessageBeep()

        self.auto_marking = True
        if in_pipeline:
            mark()
        else:
            threading.Thread(target=mark).start()

    def _seg(self):
        def new_seg(seg_lengths=None):
            if seg_lengths is None:
                content = self.text
            else:
                ori = self.text
                text_segs = []
                cur_start_idx = 0
                for lenth in seg_lengths:
                    text_segs.append(ori[cur_start_idx: cur_start_idx + lenth])
                    cur_start_idx += lenth
                content = '\n'.join(text_segs)
            tl = Toplevel(self.root)
            tl.title('文本分段')
            root_loc = self.root.geometry().split('+')[1:3]
            tl.geometry(f'420x390+{int(root_loc[0]) + 100}+{int(root_loc[1]) + 50}')
            self.root.attributes('-disabled', 1)

            with wave.open(self.filenames['wav'], 'r') as f:
                length_second = f.getnframes() / f.getframerate()
            recommend = max(int(length_second / 15), 1)

            def close():
                self.root.attributes('-disabled', 0)
                self.root.focus()
                tl.destroy()

            tl.protocol('WM_DELETE_WINDOW', close)
            tl.attributes('-toolwindow', 1)
            tl.attributes('-topmost', 1)
            txt = Text(tl, height=13, width=50, spacing3=12)
            txt.insert('insert', content)
            txt.pack(fill=BOTH)
            txt.focus()

            def save(event=None):

                # def save_py(event=None):
                #     text_py = txt_py.get(1.0, "end")
                #     texts_py = [x for x in text_py.split('\n') if x]
                #     lengths_py = [len(t) for t in texts_py]
                #     last_start_py = 0
                #     pys_py = []
                #     for l_py in lengths_py:
                #         pys_py.append(self.py[last_start_py:last_start_py + l_py])
                #         last_start_py += l_py
                #         if last_start_py > len(self.py):
                #             break

                def insert_newline(tex):
                    txl = list(tex)
                    sil_idxs = []
                    for i, py_ in enumerate(self.py):
                        if py_ == 'sil':
                            sil_idxs.append(i)

                    counter = 0
                    for sil_idx in sil_idxs:
                        txl.insert(sil_idx + counter, '\n')
                        counter += 1
                        txl.insert(sil_idx + counter + 1, '\n')
                        counter += 1

                    return ''.join(txl)

                text = txt.get(1.0, "end").strip()
                if '\n' not in text:
                    answer = messagebox.askyesnocancel('自动切分', '未手动分段，将按照sil自动切分，选否则视全部内容为一个段落')
                    if answer is None:
                        return
                    elif answer:
                        text = insert_newline(text)
                    else:
                        pass
                texts = [x for x in text.split('\n') if x]
                lengths = [len(t) for t in texts]

                if not sum(lengths) == len(self.py):
                    messagebox.showerror('长度不匹配', '文字数量与拼音数量不符，无法继续切分')
                    return
                create_seg_tg(self.filenames['wav'], self.filenames['segment'], texts)
                self.set_filename_func(dest=self.dest, seg_tg=self.filenames['segment'])
                edit_seg()

                self.root.attributes('-disabled', 0)
                tl.destroy()

                # create another Toplevel
                # last_start = 0
                # pys = []
                # for l in lengths:
                #     pys.append(self.py[last_start:last_start + l])
                #     last_start += l
                #     if last_start > len(self.py):
                #         break
                # content_py = '\n'.join(pys)
                # tl_py = Toplevel(tl)
                # tl_py.attributes('-toolwindow', 1)
                # tl_py.attributes('-topmost', 1)
                # tl_py.title('确认分段')
                # tl_loc = tl.geometry().split('+')[1:3]
                # tl_py.geometry(f'420x390+{int(tl_loc[0]) + 100}+{int(tl_loc[1]) + 50}')
                # txt_py = Text(tl_py, height=25, width=50)
                # txt_py.insert('insert', content_py)
                # txt_py.pack(fill=BOTH)
                # txt_py.focus()

                # Label(tl_py, text='分割可能有误，请确认拼音分割结果，以换行分隔').pack()
                # b_py = Button(tl_py, text='确认', command=save_py)
                # b_py.pack()
                # 保存到tg文件里。在文字等更改后仍然保存。需要在tg中使用文字而不是拼音以方便标注时的识别。实际上利用的是文字的个数对齐拼音。
                # 所以在切分前一定要保证拼音和汉字的对齐关系，然后一直切文字而不是拼音。把根据tg分段识别再合并（在最终输出tg的阶段）的功能放在sppasDealer里
                # 在切分开的两侧都记录有几个静音符号，合成时去核对，应当有几个就修正为几个

            def press_refresh(event=None):
                text = txt.get(1.0, "end")
                paras = text.split('\n')

                def update_para_num():
                    pn = 0
                    for para in paras:
                        if para:
                            pn += 1
                    label_txt_var.set(f'{pn}段(应多于{recommend})，以换行分隔，勿做其他编辑~')

                update_para_num()

            label_txt_var = StringVar()
            press_refresh()
            Label(tl, textvariable=label_txt_var).pack()

            txt.bind('<KeyPress>', press_refresh)

            b = Button(tl, text='确认', command=save)
            b.pack(side=BOTTOM)

        def edit_seg():
            self.seg_editing = True
            start_edit(self.filenames['wav'], self.filenames['segment'], False, False)

            def save(event=None):
                self.seg_editing = False
                self.seg_existing = True
                self.bseg.config(text='切分', command=self._seg)
                try:
                    os.remove('temp.praat')
                except:
                    pass

            self.bseg.config(text='保存', command=save)

        if self.seg_existing:
            choice = messagebox.askyesnocancel('切分已存在',
                                               '已经进行过切分，是否继续编辑先前的切分标注？\n\n是：查看编辑先前的时间标注\n否：完全重新进行文字分段和时间标注\n取消：查看先前的文字分段，重新标注时间')
            if choice is None:
                lengths = get_seg_lengths(self.filenames['segment'])
                new_seg(lengths)
            elif choice:
                edit_seg()
            else:
                new_seg()
        else:
            new_seg()

    def _output(self):
        # result = self.vtalker.get_result(self.filenames['wav'], 1,
        #                                  consonant_control=self.core.settings['consonant_control'])
        # self.set_data_func(self.dest, result, mark)
        mark, p_id, pool = self.pre_set_data_func(self.dest)
        self.vtalker.id_name = p_id
        mp_list = multiprocessing.Manager().list()

        # threading.Thread(target=render_data).start()
        def ec(e):
            raise e

        # 把可以被pickle的函数作为参数传入，不直接使用类的方法，绕过去
        pool.apply_async(self._render_func,
                         (self.vtalker.get_result, mp_list, self.filenames['wav'], 1,
                          self.core.settings['consonant_control']),
                         callback=lambda x: self.set_data_func(self.dest, mp_list, mark, p_id),
                         error_callback=ec)  # 本质上是pickle后释放到新空间的。
        self.exit_()

    def auto_pipeline(self):
        self.text_tl.destroy()
        self.root.title('单线程过程...')
        self._tts(in_pipeline=True)
        self._auto_mark(in_pipeline=True)
        self._output()

    def run(self):
        self.root.mainloop()

    def tl(self):
        return self.root

