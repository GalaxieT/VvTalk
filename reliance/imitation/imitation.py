# 在每次方法调用后返回修改的信息，在被调用处更新
import reliance.imitation.tts
import reliance.imitation.audioTools
import reliance.imitation.praatDealer
import reliance.imitation.mfaDealer
import reliance.imitation.voiceAnaysis.analyzer
import os


class ImitationManager:
    def __init__(self, text, py, wavname, tgname, seg_tgname, id_name=None):
        """
        para id_: id for identifying different subprocesses, None if not run in subprocess
        """
        # item inf
        self.text = text
        self.py = py
        self.filenames = {'wav': wavname, 'annotation': tgname, 'segment': seg_tgname}
        self.id_name = id_name

        self.vtalker = reliance.imitation.voiceAnaysis.analyzer.vtalker(id_name)

        # status flags
        self.install = False
        self.main_running = True
        self.auto_marking = False
        self.importing = False
        self.tg_need_create = not os.path.exists(self.filenames['annotation'])

    def tts_voice(self, location=r'misc/temp/tts_temp/tts.wav'):
        reliance.imitation.tts.render(self.text, location)

    def import_voice(self, location):
        def func():
            reliance.imitation.audioTools.to_one_channel_file(location, self.filenames['wav'])
            if not self.main_running:
                return
            self.importing = False

        self.importing = True
        func()
        reliance.imitation.praatDealer.create_seg_tg(self.filenames['wav'],
                                                     self.filenames['segment'],
                                                     [self.text],
                                                     just_len=len(self.py))

    def auto_mark(self):
        dest_name_list = self.filenames['annotation'].split('.')
        dest_name_list[-2] = dest_name_list[-2] + '_auto'
        dest_name = '.'.join(dest_name_list)

        aligner = reliance.imitation.mfaDealer.MfaImported(self.filenames['wav'], self.filenames['segment'], self.py, self.text,
                                                   install=self.install, id_name=self.id_name)

        def mark():
            try:
                cwd = os.getcwd()
                aligner.execute_alignment()
                os.chdir(cwd)
                if not self.main_running:
                    return
            except Exception as e:
                self.auto_marking = False
                # messagebox.showerror('自动标注错误(生成)', f'自动标注发生错误\n可能是由于拼音和符号未对齐，音频太长、发音不清晰或音质太差\n请尝试重新录音或切分，或使用手动标注')
                raise e
            try:
                aligner.transcribe_to(dest_name)
            except Exception as e:
                self.auto_marking = False
                # messagebox.showerror('自动标注错误(转写)', '自动标注结果错误，可能是由于音频太长、发音不清晰或音质太差，请使用切分将每个分段的音频保持在30秒以内（10秒内最佳）\n也可直接开始手动标注')
                raise e
            with open(dest_name, 'rb') as f:
                data = f.read()
            with open(self.filenames['annotation'], 'wb') as f:
                f.write(data)
            self.vtalker.auto_tg_name = self.vtalker.textgrid_name = dest_name
            self.tg_need_create = False
            self.auto_marking = False

            # winsound.MessageBeep()

        self.auto_marking = True
        mark()

    def output(self):

        result = self.vtalker.get_result(self.filenames['wav'])
        return result

    def auto_pipeline(self):
        """
        pipeline: tts生成语音、（冗余）根据语音数据和文本生成分段textgrid(不分开，即只分一段）、根据生成的分段textgrid开始对齐标注
        """
        if self.id_name is not None:
            location = f'misc/temp/subprocess_{self.id_name}/tts_temp/tts.wav'
        else:
            location = 'misc/temp/tts_temp/tts.wav'
        if not os.path.exists(os.path.dirname(location)):
            os.makedirs(os.path.dirname(location))
        self.tts_voice(location)
        self.import_voice(location)
        self.auto_mark()

        result = self.output()
        return result
