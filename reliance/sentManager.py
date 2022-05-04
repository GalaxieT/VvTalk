"""
只关注操作的结果是什么，而不记录是什么操作导致了这一步结果
'end' 代表目前最新的history的key
id和index，名字起得太烂了，有机会要改一改
架构：维度：句子、索引 -- 对象：某个句子、索引 -- 版本：对象的每一次操作结果
index_container 与 各个句子各自的container并列
多线程是多版本同时 操作
"""
from copy import deepcopy
from multiprocessing.managers import BaseManager
from types import MethodType
from functools import partial


def _append_history(dic, item):
    dic['end'] += 1
    dic[dic['end']] = item


class Sent(dict):
    def __init__(self, init=None):
        if init is None:
            super(Sent, self).__init__(self._prototype_dict())
        elif isinstance(init, dict):  # including Sent
            amended_dict = self._init_amend(init)
            super(Sent, self).__init__(amended_dict)
        elif isinstance(init, list):
            # 向上兼容
            init = {'base': init[0], 'data': init[1], 'ref': init[2]}
            amended_dict = self._init_amend(init)
            super(Sent, self).__init__(amended_dict)

    def _init_amend(self, init):
        amended = self._prototype_dict()
        amended.update(init)
        for k in self._prototype_dict():
            amended[k].extend(self._prototype_dict()[k][len(amended[k]):])
        return amended

    @staticmethod
    def _prototype_dict():
        _prototype_dict = {'base': ['', [], ''], 'data': ['', (), (), (), '', (), ''], 'ref': ['', '', (), '']}
        # 只允许有一层collective
        # ['base']: [字符, [拼音], 拼音来源]
        # 拼音来源：'auto' or 'voice' or '' voice 即此拼音序列来源于对人声模仿标注结果textgrid的读取
        # ['data']: [source, (timing), (pits), (consonants), consonant_control_type, (dyn), dyn_status]
        # timing: 按每个音节元音的时间分布（可能包含后面音节的辅音）
        # source, dyn_status: 'v', 'a', 'wait', 'abort', ''
        # timing不包括静音的信息，sil只用于text与py的对齐
        # pits的横坐标是每dot
        # dyn_status: 'wait', 'abort', 'complete', ''
        # ['ref']: [ref_wav_name, ref_textgrid_name, ref_intensities(dB), seg_textgrid_name]
        # 使用方法：使用复数切片进行赋值，而不是索引一整个区域进行赋值
        return deepcopy(_prototype_dict)

    @classmethod
    def prototype(cls):
        return Sent()


class BaseSentManager:
    def __init__(self):  # 也可以由list可变对象的特质来完成snapshot-container的特征
        self.load_times = 0  # 区分一次运行中，不同的项目组。上次的结果不能应用到这次的项目中。
        self._max_length = 50
        self.snapshots = []  # [{sentID/'index': idx}], only changed items will be in. Records which version is in use for each sentence (and index).
        self.cur_snapshot_idx = -1
        self.sent_container = {}  # {sentID: {end, sentHistory}}
        self.id_index_container = {'end': -1}
        # {end, [index]} index records the order and the existence of the sentences.

        self.blocking = {}  # {sentID: (history_id, aborted_sent)}

        self.next_new_sent_id = 0

        self.load_sents([])  # 完成上面那些容器的初始化

    def __getitem__(self, index):
        return self.present_sent_idx(index)

    def __setitem__(self, key, value):
        raise ValueError('"Manager" object cannot be rendered any item.')

    def _wait_for_change(self, id_, waiting_sent, aborted_sent):
        self._clear_after()

        shot = {}
        _append_history(self.sent_container[id_], waiting_sent)
        shot[id_] = self.sent_container[id_]['end']
        self._append_snapshot(shot)

        history_idx = self.sent_container[id_]['end']
        self.blocking[id_] = (history_idx, aborted_sent)

        return history_idx

    def wait(self, idx, waiting_sent, aborted_sent):
        id_ = self._idx_to_id(idx)
        history_idx = self._wait_for_change(id_, waiting_sent, aborted_sent)
        return id_, history_idx, self.load_times

    def complete_change(self, inf, result_sent=None, finally_call=None, args=()):
        id_, history_idx, lt = inf[0], inf[1], inf[2]
        """
        完成并更新延迟的更改，若传入None，则视为强制结束正在计算中的更改，以预先设置好的模板句来代替
        """
        try:
            waiting = False
            if self.blocking[id_][0] == history_idx and self.load_times == lt:
                waiting = True
        except KeyError:
            waiting = False

        if not waiting:
            return False

        if result_sent is not None:
            self.sent_container[id_][history_idx] = result_sent
        else:
            self.sent_container[id_][history_idx] = self.blocking[id_][1]

        del self.blocking[id_]

        if finally_call is not None:
            return finally_call(*args)

    def is_waiting(self, idx):
        return self._idx_to_id(idx) in self.blocking

    def blocked_inf_idx(self, idx):
        id_ = self._idx_to_id(idx)
        if id_ in self.blocking:
            return id_, self.blocking[id_][0], self.load_times
        return None

    def set_max_length(self, l):
        self._max_length = l
        cur_length = len(self.snapshots)
        abandoned_num = cur_length-self._max_length
        if abandoned_num > 0:
            if abandoned_num > self.cur_snapshot_idx:
                self._clear_after(self.cur_snapshot_idx+len(self.snapshots)-1-abandoned_num)
                abandoned_num = self.cur_snapshot_idx
            to_compress = self.snapshots[0:abandoned_num+1]
            for abd in to_compress:
                to_compress[0].update(abd)
            self.snapshots[abandoned_num] = to_compress[0]
            del self.snapshots[0: abandoned_num]
            self.cur_snapshot_idx -= abandoned_num

    def load_sents(self, sents):
        """
        var sents: [Sent,]
        """
        self.load_times += 1

        init_index = []
        init_snapshot = {}
        init_sent_container = {}
        init_sent_id = 0
        for i, sent in enumerate(sents):
            init_index.append(init_sent_id)
            init_sent_container[init_sent_id] = {'end': 0, 0: sent}
            init_snapshot[init_sent_id] = 0
            init_sent_id += 1
        init_snapshot['index'] = 0
        self.snapshots = [init_snapshot]  # [{sentID/'index': idx}], only changed items will be in. Records which version is in use for each sentence (and index).
        self.cur_snapshot_idx = 0
        self.sent_container = init_sent_container  # {sentID: [sentHistory]}
        self.id_index_container = {'end': 0, 0: init_index}  # {'end', [index]} index records the order and the existence of the sentences.

        self.next_new_sent_id = init_sent_id
        self.blocking.clear()

    def _global_current_snapshot(self):
        global_shot = {}
        for shot in self.snapshots[:self.cur_snapshot_idx+1]:
            global_shot.update(shot)
        return global_shot

    def _current_snapshot(self, key):
        idx = None
        for shot in self.snapshots[:self.cur_snapshot_idx+1]:
            try:
                idx = shot[key]
            except KeyError:
                pass
        return idx

    def _clear_after(self, i=None):
        if i is None:
            i = self.cur_snapshot_idx
        shots = self.snapshots[i + 1:]

        for shot in shots:
            for k, idx in shot.items():
                try:
                    try:
                        mark = self.blocking[k]
                        if mark[0] == idx:
                            del self.blocking[k]
                    except:
                        pass
                    del self.sent_container[k][idx]  # 在sent层面，句子的这次改变结果不再留档
                except KeyError:
                    if k == 'index':
                        del self.id_index_container[idx]  # 在index层面宣称index的这次改变结果不再留档
        sent_id_to_del = []
        for k in self.sent_container:
            del self.sent_container[k]['end']
            if self.sent_container[k]:  # 如果sent还有版本的话
                self.sent_container[k]['end'] = max(self.sent_container[k])
            else:  # 如果sent已经没有需要留档的版本
                sent_id_to_del.append(k)
        for i_to_d in sent_id_to_del:
            del self.sent_container[i_to_d]

        del self.id_index_container['end']
        self.id_index_container['end'] = max(self.id_index_container)
        del self.snapshots[i + 1:]

    def _append_snapshot(self, shot: dict):
        """
        Make sure you called _clear_after before you call this, in order to append the snapshot in the ending of the
        list of shots.
        A base snapshot will be reserved in the 0 index, updating for each deletion.
        """
        self.snapshots.append(shot)
        self.cur_snapshot_idx += 1
        if self.cur_snapshot_idx > self._max_length - 1:
            self.snapshots[0].update(self.snapshots[1])
            self.snapshots[1] = self.snapshots[0]
            del self.snapshots[0]
            self.cur_snapshot_idx -= 1

    def _idx_to_id(self, idx):
        index = self.id_index_container[self._current_snapshot('index')][:]
        try:
            return index[idx]
        except IndexError:
            raise IndexError

    def _id_to_idx(self, id_):
        index = self.id_index_container[self._current_snapshot('index')][:]
        try:
            return index.index(id_)
        except ValueError:
            raise IndexError('no such id')

    def present_sents(self, dc=True):
        """
        Show current sentence information. Should not use it to modify the sentences.
        """
        result = []
        snapshot = self._global_current_snapshot()
        index = self.id_index_container[snapshot['index']]
        for id_ in index:
            sent_history = self.sent_container[id_]
            result.append(sent_history[snapshot[id_]])

        if dc:
            return deepcopy(result)
        else:
            return result

    def present_sent_idx(self, idx, dc=True):
        """
        Show current sentence information by required index. Should not use it to modify the sentences.
        """
        id_ = self._idx_to_id(idx)
        if dc:
            return deepcopy(self.sent_container[id_][self._current_snapshot(id_)])
        else:
            return self.sent_container[id_][self._current_snapshot(id_)]

    def _change_index(self, new):
        """Attention: call self._clear_after before calling this."""
        _append_history(self.id_index_container, new)
        self._append_snapshot({'index': self.id_index_container['end']})

    def move(self, from_: int, to_: int):
        self._clear_after()
        index = self.id_index_container[self._current_snapshot('index')][:]
        id_ = index.pop(from_)
        index.insert(to_, id_)
        self._change_index(index)

    def _change_sents_id(self, changed_sents: dict):
        """
        Attention: this function does not change the value of self.next_new_sent_id, which means you should change it manually.

        You cannot use this function to add new sentences.
        :param changed_sents:
        :return:
        """
        self._clear_after()
        # index_changed = False
        shot = {}
        # cur_index = self.id_index_container[self._current_snapshot('index')][:]
        # indexes = list(new_index_nums)
        for k, v in changed_sents.items():
            try:
                _append_history(self.sent_container[k], v)
            except KeyError:
                print('Change result_sent KeyError', k, v)
                # self.sent_container[k] = [v]
                # if indexes:
                #     cur_index.insert(indexes.pop(0), k)
                # else:
                #     cur_index.append(k)
                # index_changed = True
            shot[k] = self.sent_container[k]['end']
        # if index_changed:
        #     self.id_index_container.append(cur_index)
        #     shot['index'] = self.id_index_container['end']
        self._append_snapshot(shot)

    def change_sent_idx_s(self, changed_sents: dict):
        """
        You cannot use this function to add new sents. Use add_sent instead.
        None of the sents shall be blocked, or all the sents cannot be changed.
        :param changed_sents: {idx: result_sent}
        :return: whether successfully changed: information about the blocked sent if unsuccessful
        """
        id_sents = {}
        for idx in changed_sents:
            id_ = self._idx_to_id(idx)
            try:
                result = idx, (id_, self.blocking[id_][0], self.load_times)
                print(Exception('Error: trying to modify blocked sents in sentManager.change_sent_idx_s'))
                return result
            except KeyError:
                pass
        for idx, sent in changed_sents.items():
            id_ = self._idx_to_id(idx)
            id_sents[id_] = sent
        self._change_sents_id(id_sents)
        return None

    def change_sent_idx(self, idx, changed_sent):
        """
        You cannot use this function to add new sents. Use add_sent instead.
        """
        return self.change_sent_idx_s({idx: changed_sent})

    def _del_sents_id(self, id_list):
        self._clear_after()
        index = self.id_index_container[self._current_snapshot('index')][:]
        for id_ in id_list:
            index.remove(id_)
        self._change_index(index)

    def del_sent_idx(self, i):
        self._del_sents_id([self._idx_to_id(i)])

    def del_sent_s(self, idxes):
        id_list = [self._idx_to_id(idx) for idx in idxes]
        self._del_sents_id(id_list)

    def _new_sent_id(self):
        self.next_new_sent_id += 1
        return self.next_new_sent_id - 1

    def add_sent(self, sent, idx=-1):
        self._clear_after()
        id_ = self._new_sent_id()
        index = self.id_index_container[self._current_snapshot('index')][:]
        index.insert(idx, id_)
        _append_history(self.id_index_container, index)

        self.sent_container[id_] = {'end': 0, 0: sent}

        shot = {id_: 0, 'index': self.id_index_container['end']}
        self._append_snapshot(shot)

    def add_sent_s(self, idx_sent_dict: dict):
        self._clear_after()
        shot = {}
        index = self.id_index_container[self._current_snapshot('index')][:]
        idx_sent = sorted(idx_sent_dict.items(), key=lambda x: x[0])
        for idx, sent in idx_sent:
            id_ = self._new_sent_id()
            index.insert(idx, id_)
            self.sent_container[id_] = {'end': 0, 0: sent}
            shot[id_] = 0
        _append_history(self.id_index_container, index)
        shot['index'] = self.id_index_container['end']
        self._append_snapshot(shot)

    # def insert(self, idx, result_sent):
    #     self.add_sent()

    def undo(self):
        if self.cur_snapshot_idx == 0:
            return False
        self.cur_snapshot_idx -= 1
        return True

    def redo(self):
        if self.cur_snapshot_idx == len(self.snapshots) - 1:
            return False
        self.cur_snapshot_idx += 1
        return True

    def clear(self):
        self.load_sents([])


class ProcessManager(BaseManager):
    pass

def sentManager():
    # ProcessManager.register('SentManager', BaseSentManager)
    # pm = ProcessManager()
    # pm.start()
    # sm = pm.SentManager()
    # # 自定义manager不能继承原类的内部方法，必须利用动态类型的特点重新绑定
    # # 绑定的对象是类而不是实例（因为类是后期构造出来的,赋值过程无法追溯到这一构造出的分支类），但method本身的形参object(self)必须是实例本身
    # # 因为被绑定的方法中包含实例的其他方法self.abc(x)，如果作为被绑定作为类方法的话，就无法默认填入abc(self, x)中的self了
    # type(sm).__getitem__ = MethodType(BaseSentManager.__getitem__, type(sm))

    return BaseSentManager()
    # return sm


