import sys
import argparse
import reliance.core


def parse_interface():
    args = sys.argv
    print(args)
    if len(args) > 1 and args[1] == 'cmd':
        run_gui = False
    else:
        print('调用命令行功能必须使用cmd命令，例如:\n>>> tytalk.exe cmd auto -t 我一把把把把住了。')
        run_gui = True

    return run_gui


class CmdUI:
    def __init__(self, core: reliance.core.TalkCore):
        self.core = core
        self.output_dir = None

    def execute_command(self):
        parser = argparse.ArgumentParser('调用命令行功能必须使用cmd命令，例如:\n>>> vvTalk.exe cmd auto -t 我一把把把把住了。\n默认输出在根目录\\outputs文件夹中')
        parser.add_argument('ui')
        parser.add_argument('operation', help='（必要）操作命令: "auto"或"auto_fast"')
        parser.add_argument('-f', '--file', help='朗读文字的文件地址 (utf8编码)')
        parser.add_argument('-t', '--text', help='朗读文字（覆盖--file参数）')
        parser.add_argument('-fm', '--format', help='指定输出格式: "vsqx"(默认)或"svp"', default='vsqx')
        parser.add_argument('-o', '--output', help='指定输出文件地址', default=None)
        args = parser.parse_args()

        operation = args.operation
        if args.text:
            text = args.text
        else:
            with open(args.file, encoding='utf-8') as f:
                text = f.read()
        if args.format not in ('vsqx', 'svp'):
            parser.error(f'--format参数必须传入"vsqx"或"svp", 而不是"{args.format}"')
        else:
            self.core.settings.update({'output_format': args.format})
        if operation == 'auto':
            self.imi_pipeline(text)
        if operation == 'auto_fast':
            self.auto_fast(text)
        self.output_dir = args.output

    def imi_pipeline(self, text):
        self.core.editor.append_item(0, text)
        self.core.editor.batch_imitate_pipeline([0], join=True)
        self.core.output_tune_file([0], forced_dir=self.output_dir)

    def auto_fast(self, text):
        self.core.editor.append_item(0, text)
        self.core.editor.fast_auto([0])
        self.core.output_tune_file([0], forced_dir=self.output_dir)


