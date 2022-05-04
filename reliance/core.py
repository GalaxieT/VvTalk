import time

from reliance.sentManager import Sent, sentManager
from reliance.imitation.humanConverter import add_dyn
from reliance.tyTalk import talker
from reliance.output.dub import batch_to_srt_file
from reliance.imitation import imitation
from copy import deepcopy
import reliance.output.vsqxWrite
import reliance.output.svpWrite
import threading
import pickle
import re
import reliance.global_vars
import multiprocessing
import multiprocessing.pool
import os
import shutil

VERSION = reliance.global_vars.VERSION
VERSION_NO = reliance.global_vars.VERSION_NO


class TalkCore:
    def __init__(self, no_projects=False):
        def mkdir(path):
            isExists = os.path.exists(path)
            if not isExists:
                os.makedirs(path)

        self.no_projects = no_projects
        self.root_path = os.getcwd()
        self.temp_relative_path = r'misc\temp'
        self.settings_relative_path = r'misc'
        for path in (r'\projects', r'\resources', r'\outputs', r'\misc', '\\' + self.temp_relative_path,):
            # '\\' + self.temp_relative_path + r'\sppas_temp'):
            mkdir(self.root_path + path)
        self.default_settings = reliance.global_vars.settings
        try:
            with open(self.settings_relative_path + r'\setting', 'rb') as f:
                self.default_settings.update(pickle.load(f))
                self.settings = self.default_settings
        except FileNotFoundError:
            self.settings = self.default_settings
            self.save_settings()
        self.default_height = 61

        self.sents = sentManager()

        self.temp_file = False
        if self.no_projects:
            self.project_name = 'commandline'
        else:
            self.project_name = '未命名'
        self.project_file_location = ''
        self.root = None
        self.unchanged = True  # 标记是否有未保存的修改

        self.max_process = 3
        self._process_pool = multiprocessing.pool.Pool(self.max_process)
        self._process_pool.close()
        self._pool_closed = True
        self.running_subprocess_ids = {}
        # load_new_data时，不清空
        # {flag: serial_number}, flag: str(serial number) + str(timestamp) 用于避免任何可能的重复

        self.talker = talker.Talker()
        self.editor = ItemEditor(self)
        self.ui_update_callback = lambda: None
        self.subprocess_finish_callback = lambda: None

        # self.process_pool = multiprocessing.pool.Pool(1)
        # self.mp_dict = multiprocessing.Manager().dict()
        if VERSION_NO > self.settings['last_ver_num']:
            self.newly_installed = True
        else:
            self.newly_installed = False

        self.clear_temp_folder()

        if not self.no_projects:
            try:
                self.load_from(self.settings['last_file_location'])
            except FileNotFoundError:
                self.load_new_temp()
            except EOFError:
                self.load_new_temp()

    def clear_temp_folder(self):
        namelist = os.listdir(self.temp_relative_path)
        for name in namelist:
            if name.startswith('subprocess_'):
                name = os.path.join(self.temp_relative_path, name)
                if os.path.isdir(name):
                    shutil.rmtree(name)

    def register_subprocess(self):
        if self.running_subprocess_ids:
            sn = max(self.running_subprocess_ids.values()) + 1
        else:
            sn = 0
        id_ = str(sn) + '_' + str(time.time())
        self.running_subprocess_ids[id_] = sn
        if self._pool_closed:
            self._process_pool = multiprocessing.pool.Pool(self.max_process)
            self._pool_closed = False
        return id_, self._process_pool

    def complete_subprocess(self, id_):
        del self.running_subprocess_ids[id_]
        if not len(self.running_subprocess_ids) and not self._pool_closed:
            self._process_pool.close()
            self._pool_closed = True

    def subprocess_pool_join(self):
        self._pool_closed = True
        self._process_pool.close()
        self._process_pool.join()

    def project_file_name(self, extension=True):
        if '\\' in self.project_file_location:
            name = self.project_file_location.split('\\')[-1]
        elif '/' in self.project_file_location:
            name = self.project_file_location.split('/')[-1]
        else:
            name = '未命名'
        if name != '未命名':
            if extension:
                return name
            else:
                return name.split('.')[-2]
        else:
            return name

    def file_relative_path(self, type_, original=''):
        '''
        读取资源文件夹的情况，并返回指定类别下文件应该用的名字
        :param original: original path
        :param type_: 'wav', vsqx or 'TextGrid'
        :return:
        '''
        if os.path.exists(original):
            return original

        if type_ in ('vsqx', 'srt', 'svp'):
            folder = 'outputs'
        else:
            folder = 'resources'
        folder_path = os.getcwd() + '\\' + folder
        filenames = os.listdir(folder_path)
        related_nums = []
        if type_ in ('vsqx', 'srt', 'svp'):
            len_ex = len(type_)
            for filename in filenames:
                if re.match(f'FILENAME\(\d+?\).{type_}'.replace('FILENAME', self.project_file_name(extension=False)),
                            filename):
                    related_nums.append(int(filename.split('(')[-1][:-(len_ex + 2)]))  # 选出数字部分
            if related_nums:
                cur_num = max(related_nums) + 1
            else:
                cur_num = 1
            aimed_name = '{}({}).{}'.format(self.project_file_name(extension=False), cur_num, type_)
        elif type_ == 'wav':
            for filename in filenames:
                if re.match('FILENAME_Recording_\d+?.wav'.replace('FILENAME', self.project_file_name(extension=False)),
                            filename):
                    related_nums.append(int(filename.split('_')[-1][:-4]))  # 选出数字部分
            if related_nums:
                cur_num = max(related_nums) + 1
            else:
                cur_num = 1
            aimed_name = '{}_Recording_{}.wav'.format(self.project_file_name(extension=False), cur_num)
        elif type_ == 'TextGrid':
            for filename in filenames:
                if re.fullmatch(
                        'FILENAME_Annotation_\d+?.TextGrid'.replace('FILENAME',
                                                                    self.project_file_name(extension=False)),
                        filename):
                    related_nums.append(int(filename.split('_')[-1][:-9]))  # 选出数字部分
            if related_nums:
                cur_num = max(related_nums) + 1
            else:
                cur_num = 1
            aimed_name = '{}_Annotation_{}.TextGrid'.format(self.project_file_name(extension=False), cur_num)
        elif type_ == 'TextGrid_segment':
            for filename in filenames:
                if re.fullmatch(
                        'FILENAME_Segment_\d+?.TextGrid'.replace('FILENAME', self.project_file_name(extension=False)),
                        filename):
                    related_nums.append(int(filename.split('_')[-1][:-9]))  # 选出数字部分
            if related_nums:
                cur_num = max(related_nums) + 1
            else:
                cur_num = 1
            aimed_name = '{}_Segment_{}.TextGrid'.format(self.project_file_name(extension=False), cur_num)
        else:
            raise ValueError('variable type_ must be string: "vsqx", "srt", "wav", "TextGrid_segment" or "TextGrid"')

        return folder + '\\' + aimed_name

    def save_settings(self):
        with open(self.settings_relative_path + r'\setting', 'wb') as f:
            pickle.dump(self.settings, f)

    def change_settings_save(self, settings: dict):
        for key, value in settings.items():
            assert key in self.default_settings
            self.settings[key] = value
        self.save_settings()

    @staticmethod
    def sent_prototype():
        return Sent.prototype()

    def need_save(self):
        self.unchanged = False
        if self.settings['step_save']:
            self.save(self.project_file_location)

    def undo(self):
        self.sents.undo()
        if self.settings['step_save']:
            self.save(self.project_file_location)
            self.unchanged = True
        return True

    def redo(self):
        self.sents.redo()
        if self.settings['step_save']:
            self.save(self.project_file_location)
            self.unchanged = True

    def output_dub(self, il):
        index_list = il
        path = self.file_relative_path('srt')
        data = [self.sents[i] for i in index_list]
        data = [[datum['base'][0], datum['base'][1], datum['data'][1]] for datum in data]
        batch_to_srt_file(data, path, self.settings['interval'], self.settings['output_format'])

    def output_tune_file(self, il, forced_dir=None):
        index_list = il
        data = [self.sents[i] for i in index_list]
        try:
            data = [[list(s['base'][0]), s['base'][1], s['data'][1], s['data'][2], s['data'][3], s['data'][5]] for s in
                    data]
            if not self.settings['enable_dyn_correction']:
                for sent in data:
                    sent[5] = ()
        except IndexError:
            try:
                data = [[list(s['base'][0]), s['base'][1], s['data'][1], s['data'][2], s['data'][3]] for s in data]
            except IndexError:
                data = [(list(s['base'][0]), s['base'][1], s['data'][1], s['data'][2]) for s in data]
        format = self.settings['output_format']
        if format == 'vsqx':
            w = reliance.output.vsqxWrite.Writer(data, adjust_consonants=self.settings['output_consonants'],
                                                 interval=self.settings['interval'], height=self.default_height,
                                                 pbs=self.settings['pbs'])
            dest = self.file_relative_path('vsqx')
        elif format == 'svp':
            w = reliance.output.svpWrite.Writer(data, adjust_consonants=self.settings['output_consonants'],
                                                 interval=self.settings['interval'], height=self.default_height,
                                                 )
            dest = self.file_relative_path('svp')
        else:
            raise ValueError(f'unsupported format of output "{format}". 不受支持的输出格式"{format}"')
        if forced_dir is not None:
            dest = forced_dir
        w.write_at(dest)

        return dest

    def save(self, addr):
        if not self.no_projects:
            with open(addr, 'wb') as f:
                pickle.dump((self.project_name, self.sents.present_sents(dc=False), self.temp_file), f)
        self.save_settings()
        self.unchanged = True

    def load_from(self, addr):
        self.new_data()
        try:
            with open(addr, 'rb') as f:
                p = pickle.load(f)
            self.project_name = p[0]

            sents = []
            for item in p[1]:
                sents.append(Sent(item))
            for sent in sents:
                try:
                    if sent['data'][0] == 'wait':
                        sent['data'][0] = 'abort'
                    if sent['data'][6] == 'wait':
                        sent['data'][6] = 'abort'
                except IndexError:
                    pass
            self.sents.load_sents(sents)
            self.temp_file = p[2]
        except FileNotFoundError:
            raise FileNotFoundError('Project file not found in "{}"'.format(addr))
        except EOFError as e:
            raise EOFError('Project file is empty.')
        self.project_file_location = addr
        self.settings['last_file_location'] = self.project_file_location
        self.save_settings()

    def load_new_temp(self):
        self.new_data()
        self.temp_file = True
        self.project_file_location = self.temp_relative_path + r'\temp.tyt'
        self.save(self.project_file_location)
        self.settings['last_file_location'] = self.project_file_location
        self.save_settings()

    def new_data(self):
        self.temp_file = False
        self.sents.clear()
        self.project_name = '未命名'
        self.project_file_location = ''
        self.unchanged = True

    def add_dyn(self, dest, raw_wav_fn, tv_update):
        base = self.sents.present_sent_idx(dest)

        ori = self.sent_prototype()['data'][5:7]
        ori[1] = 'wait'
        wait_sent = deepcopy(base)
        wait_sent['data'][5:7] = ori

        ori_abt = self.sent_prototype()['data'][5:7]
        ori_abt[1] = 'abort'
        abort_sent = deepcopy(base)
        abort_sent['data'][5:7] = ori_abt

        mark = self.sents.wait(dest, wait_sent, abort_sent)

        tv_update(chaos=False)

        def exe():
            sent = self.sents.present_sent_idx(dest)
            ref_db = sent['ref'][2]

            result = tuple(add_dyn(raw_wav_fn, ref_db))
            sent['data'][5:7] = result, 'complete'

            self.sents.complete_change(mark, sent)
            self.need_save()
            tv_update(chaos=False)

        self.settings['loudness_dir'] = raw_wav_fn
        self.need_save()
        threading.Thread(target=exe).start()


class ItemEditor:
    def __init__(self, core: TalkCore):
        self.core = core
        # self.imitation

    def append_item(self, idx, text):
        sent = self.core.sent_prototype()
        result = self.core.talker.get_py(text)
        sent['base'][0] = result[1]
        sent['base'][1] = result[0]
        sent['base'][2] = 'auto'
        self.core.sents.add_sent(sent, idx)
        self.core.need_save()
        self.core.ui_update_callback()

    @staticmethod
    def run_pipeline(imit):
        data = imit.auto_pipeline()
        return data

    def _imitate_pipeline(self, idx):
        """
        For once only, use batch_imitate_pipeline for batch usage
        """
        idx = idx
        core = self.core

        def multi_pre(dest):
            base = core.sents.present_sent_idx(dest)

            ori = core.sent_prototype()['data']
            ori[0] = 'wait'
            wait_sent = deepcopy(base)
            wait_sent['data'] = ori

            ori_abt = core.sent_prototype()['data']
            ori_abt[0] = 'abort'
            abort_sent = deepcopy(base)
            abort_sent['data'] = ori_abt

            mark = core.sents.wait(dest, wait_sent, abort_sent)
            id_, pol = core.register_subprocess()
            core.ui_update_callback()
            return mark, id_, pol

        def set_filename(dest: int, rec='', tg='', seg_tg='', independent_operation=True):
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
            if independent_operation:
                core.sents.change_sent_idx(dest, dest_sent)
                core.need_save()
            else:
                return dest_sent

        # 给主线程callback来处理的操作
        def finish(result_data):
            # core.sent related
            def finish_with_data(data):
                mark = mark_
                ori = core.sent_prototype()['data']
                ori[0:5] = ['v', data[0], data[1], [], '']
                # dest_sent = core.sents.present_sent_idx(dest)
                dest_sent = set_filename(idx, wavname, tgname, seg_tgname, independent_operation=False)
                dest_sent['data'] = ori  # 'v' for voice
                if data[2] is not None:
                    cleaned_ori_py = []
                    sil_idxs = []
                    for i, py_ in enumerate(dest_sent['base'][1]):
                        if py_ == 'sil':
                            sil_idxs.append(i)
                        else:
                            cleaned_ori_py.append(py_)
                    # if len(cleaned_ori_py) != len(data[2]):
                    #     messagebox.showinfo(f'分析提示', f'第{dest + 1}句 标注字数与预设字数不同，可能有错误')
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
                # MessageBeep()

            finish_with_data(result_data)
            core.complete_subprocess(id_)
            core.need_save()
            core.ui_update_callback()
            core.subprocess_finish_callback()
            # update

        # item (sent) data
        item = core.sents.present_sent_idx(idx)
        text, py, _ = item['base']
        wavname = core.file_relative_path('wav', original=item['ref'][0])
        tgname = core.file_relative_path('TextGrid', original=item['ref'][1])

        try:
            ori_segname = item['ref'][3]
        except IndexError:
            ori_segname = ''
        seg_tgname = core.file_relative_path('TextGrid_segment', original=ori_segname)

        mark_, id_, pool = multi_pre(idx)  # 此后无法对sent中的句子做出有效改动
        imi = imitation.ImitationManager(text, py, wavname, tgname, seg_tgname, id_name=id_)

        def ec(e):
            raise Exception(e.__cause__)

        pool.apply_async(func=self.run_pipeline, args=(imi,), callback=finish, error_callback=ec)
        # process = multiprocessing.Process(target=self.run_pipeline, args=(imi, idx, mark))
        # process.start()

    def batch_imitate_pipeline(self, idxs, join=False):

        for i, idx in enumerate(idxs):
            self._imitate_pipeline(idx)

        if join:
            self.core.subprocess_pool_join()

    def fast_auto(self, idxs, speed=1.):
        # 阻塞
        dest_sents = []
        for i, text in enumerate(idxs):
            main_idx = idxs[i]
            sent = self.core.sents.present_sent_idx(main_idx)
            previous_source = sent['base'][2]
            text = str(sent['base'][0])
            if previous_source != 'auto':
                # 如果不是自动生成的，那么就是voice或全新的，这两种情况下都需要重新生成拼音
                py_arranged = []
            else:
                py_arranged = [(i, p) for i, p in enumerate(sent['base'][1])]

            results = self.core.talker.get_result(text, speed=speed, pyc=py_arranged, pbs=self.core.settings['pbs'])

            chrs, pys, pits, timings = ''.join(results['chr']), results['py'], results['pit'], results['timing']
            sent['base'][0] = chrs
            sent['base'][1] = pys
            ori = self.core.sent_prototype()['data']
            ori[0:5] = ['a', tuple(timings), tuple(pits), (), '']  # 'a' for automatic
            sent['data'] = ori
            dest_sents.append(sent)
        result = self.core.sents.change_sent_idx_s({idxs[i]: sent for i, sent in enumerate(dest_sents)})
        return result


class ProcessManager(multiprocessing.managers.BaseManager):
    pass


def core(no_projects=False):
    # ProcessManager.register('TyTalkCore', TalkCore)
    # pm = ProcessManager()
    # pm.start()
    # c = pm.TyTalkCore()
    # print(dir(c))
    return TalkCore(no_projects)
