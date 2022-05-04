import reliance.global_vars

VERSION = '1.0.1'
VERSION_NO = 13

reliance.global_vars.VERSION = VERSION
reliance.global_vars.VERSION_NO = VERSION_NO

if __name__ == "__main__":

    import multiprocessing
    import os
    import reliance.core
    import reliance.interface.commandline

    run_gui = reliance.interface.commandline.parse_interface()

    multiprocessing.freeze_support()

    if run_gui:
        run = True
        try:
            os.remove('misc\\temp\\lock')
        except PermissionError:
            print('重复调用，不启动')
            run = False
        except FileNotFoundError:
            pass
        if run:
            guard = open('misc\\temp\\lock', 'w')
            print('正在启动程序，请最小化本窗口，操作期间勿直接关闭本窗口，会随主窗口关闭而关闭')
            import reliance.interface.gui
            talk_core = reliance.core.core()
            reliance.interface.gui.tkinter_gui(talk_core)
    else:
        talk_core = reliance.core.core(no_projects=True)
        cmd_ui = reliance.interface.commandline.CmdUI(talk_core)
        cmd_ui.execute_command()

