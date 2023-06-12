import tkinter as tk
import tkinter.font as font
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfilename
from lib.TGAmain import TGAgTg, TGAmlTg
from io import StringIO
import sys
import threading


class TGAgui:

    def __init__(self):

        self.quit = False
        self.mode = 1
        self.running = False

        self.process = None

        sys.stdout = self.buffer = StringIO()

        def _setup_master():

            master = tk.Tk()
            master.title("TGA - Telegram Group Adder")
            master.geometry("450x400")
            master.resizable(False, False)

            return master

        self.master = _setup_master()
        self.master.protocol('WM_DELETE_WINDOW', self._exit)

        self.style = ttk.Style(self.master)

        self.sessions_fname_txtv = tk.StringVar()

        self._run()

        return

    def _exit(self):

        self.master.quit()
        self.master.destroy()

        self.quit = True

        return

    def _run(self):

        old_output = ""
        old_mode = 0

        self._build_const_widgets()
        self._render_const_widgets()

        while True:

            if self.quit:

                break

            if old_mode != self.mode:

                self._create_variables()

                self._build_widgets()
                self._render_widgets()

                old_mode = self.mode

            self.master.update()
            self.master.update_idletasks()

            output = str(self.buffer.getvalue())

            if output != old_output:

                for w in self.output_scrollable_frame.winfo_children():
                    w.destroy()

                tk.Label(self.output_scrollable_frame,
                         text=output,
                         font=font.Font(size=9, family='Consolas'),
                         background='black',
                         foreground='white',
                         wraplength=self.output_internal_frame.winfo_width()).pack()

                old_output = output

        return

    def _build_const_widgets(self):

        self.master_frame = ttk.Frame(self.master)

        self.mode_btns_frame = tk.Frame(self.master_frame)

        self.gtg_mode_btn = tk.Button(self.mode_btns_frame,
                                      text="Group to Group",
                                      relief=tk.SUNKEN,
                                      command=self._switch_mode,
                                      font=font.Font(size=12))

        self.mltg_mode_btn = tk.Button(self.mode_btns_frame,
                                       text="Member List to Group",
                                       relief=tk.FLAT,
                                       state=tk.DISABLED,
                                       command=self._switch_mode,
                                       font=font.Font(size=12))

        self.const_widget_frame = ttk.Frame(self.master_frame)

        self.run_stop_btns_frame = ttk.Frame(self.const_widget_frame)

        self.run_stop_btns_subframe = ttk.Frame(self.run_stop_btns_frame)

        self.run_btn = ttk.Button(self.run_stop_btns_subframe,
                                  text='Run',
                                  command=self._switch_run_stop_btns)
        self.stop_btn = ttk.Button(self.run_stop_btns_subframe,
                                   text='Stop', state=tk.DISABLED,
                                   command=self._switch_run_stop_btns)

        self.sessions_fname_frame = ttk.Frame(self.const_widget_frame)

        self.sessions_fname_lframe = ttk.LabelFrame(self.sessions_fname_frame,
                                                    text='Sessions file name')

        self.sessions_fname_open_btn = ttk.Button(self.sessions_fname_lframe,
                                                  text='Open',
                                                  command=self._get_sessions_fname,
                                                  width=5)

        self.sessions_fname_entry = ttk.Entry(self.sessions_fname_lframe,
                                              width=25,
                                              textvariable=self.sessions_fname_txtv)

        self.fields_frame = ttk.Frame(self.master_frame)

        return

    def _render_const_widgets(self):

        self.master_frame.pack(fill=tk.BOTH, expand=True)

        self.mode_btns_frame.pack(side=tk.TOP, fill=tk.X)

        self.gtg_mode_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.mltg_mode_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        self.const_widget_frame.pack(side=tk.TOP, fill=tk.X)

        self.run_stop_btns_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.run_stop_btns_subframe.pack(padx=20, pady=25)

        self.run_btn.pack(side=tk.LEFT, padx=5)
        self.stop_btn.pack(side=tk.RIGHT, padx=5)

        self.sessions_fname_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        self.sessions_fname_lframe.pack(padx=20, pady=10)

        self.sessions_fname_open_btn.pack(side=tk.LEFT, padx=5)
        self.sessions_fname_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5, pady=5)

        self.fields_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        return

    def _get_sessions_fname(self):

        self.sessions_fname_txtv.set(askopenfilename())

        for widget in self.as_scrollable_frame.winfo_children():
            widget.destroy()

        self.process.set_session_fname(str(self.sessions_fname_txtv.get()))

        s_num = len(open(str(self.sessions_fname_txtv.get()), 'r').readlines())

        def _make_labda(_s_id):
            return lambda: self._toggle_session(_s_id)

        self.active_sessions = [ttk.Checkbutton(self.as_scrollable_frame, text=s_id+1,
                                                command=_make_labda(s_id+1))
                                for s_id in range(s_num if self.process is not None else 0)]

        c = y = x = 0
        for s_cb in self.active_sessions:

            if c > 5:
                x = c = 0
                y += 1

            s_cb.grid(row=y, column=x, padx=3)
            s_cb.state(['!alternate', 'selected'])

            c += 1
            x += 1

        return

    def _toggle_session(self, s_id):

        if s_id not in self.process.paused_sessions:

            self.process.paused_sessions.append(s_id)

        else:

            self.process.paused_sessions.remove(s_id)

        return

    def _switch_mode(self):

        if self.mode == 1:

            self.mode = 0
            self.process = TGAgTg()

            self.gtg_mode_btn['state'] = 'disabled'
            self.mltg_mode_btn['state'] = 'normal'

            self.gtg_mode_btn['relief'] = 'flat'
            self.mltg_mode_btn['relief'] = 'sunken'

        else:

            self.mode = 1
            self.process = TGAmlTg()

            self.gtg_mode_btn['state'] = 'normal'
            self.mltg_mode_btn['state'] = 'disabled'

            self.gtg_mode_btn['relief'] = 'sunken'
            self.mltg_mode_btn['relief'] = 'flat'

        for widgets in self.fields_frame.winfo_children():
            widgets.destroy()

        self.run_btn["state"] = "normal"
        self.stop_btn["state"] = "disabled"
        self.running = False

        return

    def _switch_run_stop_btns(self):

        if self.running is True:

            self.run_btn["state"] = "normal"
            self.stop_btn["state"] = "disabled"

            self.running = False

            self.process.exit()

        else:

            self.run_btn["state"] = "disabled"
            self.stop_btn["state"] = "normal"

            self.running = True

            self.process.load_sessions()

            thread = threading.Thread(target=self._run_process)

            print("Starting process thread...")

            thread.start()

        return

    def _run_process(self):

        self.process = TGAgTg() if self.mode == 0 else TGAmlTg()

        if self.mode == 1:

            self.process.run()

        return

    def _create_variables(self):

        if self.mode == 1:

            self.ml_fname_txtv = tk.StringVar()

            self.dg_txtv = tk.StringVar()

            self.min_timer_txtv = tk.StringVar(value=str(self.process.timer[0]))

            self.max_timer_txtv = tk.StringVar(value=str(self.process.timer[1]))

        return

    def _build_widgets(self):

        if self.mode == 1:

            self.ml_dg_frame = ttk.Frame(self.fields_frame)

            self.ml_frame = ttk.Frame(self.ml_dg_frame)

            self.ml_lframe = ttk.LabelFrame(self.ml_frame,
                                            text='Member List file name')

            self.ml_open_btn = ttk.Button(self.ml_lframe,
                                          text='Open',
                                          command=self._get_ml_fname,
                                          width=5)

            self.ml_entry = ttk.Entry(self.ml_lframe,
                                      width=25,
                                      textvariable=self.ml_fname_txtv)

            self.dg_frame = ttk.Frame(self.ml_dg_frame)

            self.dg_lframe = ttk.LabelFrame(self.dg_frame,
                                            text='Destination Group name')

            self.dg_entry = ttk.Entry(self.dg_lframe,
                                      validate="focusout",
                                      validatecommand=self._set_destination_group,
                                      width=10,
                                      textvariable=self.dg_txtv)

            self.td_as_frame = ttk.Frame(self.fields_frame)

            self.td_frame = ttk.Frame(self.td_as_frame)

            self.td_lframe = ttk.LabelFrame(self.td_frame, text='Time Delay')

            self.min_label = ttk.Label(self.td_lframe, text='Min')
            self.max_label = ttk.Label(self.td_lframe, text='Max')
            self.min_entry = ttk.Entry(self.td_lframe, width=5,
                                       textvariable=self.min_timer_txtv,
                                       validate='focusout',
                                       validatecommand=self._set_min_delay)
            self.max_entry = ttk.Entry(self.td_lframe, width=5,
                                       textvariable=self.max_timer_txtv,
                                       validate='focusout',
                                       validatecommand=self._set_max_delay)

            self.as_frame = ttk.Frame(self.td_as_frame)

            self.as_lframe = ttk.LabelFrame(self.as_frame, text='Active Sessions')

            self.as_internal_frame = ttk.Frame(self.as_lframe)

            self.as_canvas = tk.Canvas(self.as_internal_frame, highlightthickness=0)
            self.as_scrollbar = ttk.Scrollbar(self.as_internal_frame, command=self.as_canvas.yview)
            self.as_scrollable_frame = ttk.Frame(self.as_canvas)
            self.as_scrollable_frame.bind(
                "<Configure>",
                lambda e: self.as_canvas.configure(
                    scrollregion=self.as_canvas.bbox(tk.ALL)
                )
            )
            self.as_canvas.create_window((0, 0), window=self.as_scrollable_frame, anchor=tk.NW)
            self.as_canvas.configure(yscrollcommand=self.as_scrollbar.set)

            self.output_frame = ttk.Frame(self.fields_frame)

            self.output_lframe = ttk.LabelFrame(self.output_frame, text="Output")

            self.output_internal_frame = ttk.Frame(self.output_lframe)

            self.output_canvas = tk.Canvas(self.output_internal_frame, background='black', highlightthickness=0)
            self.output_scrollbar = ttk.Scrollbar(self.output_internal_frame, command=self.output_canvas.yview)
            self.output_scrollable_frame = ttk.Frame(self.output_canvas)
            self.output_scrollable_frame.bind(
                "<Configure>",
                lambda e: self.output_canvas.configure(
                    scrollregion=self.output_canvas.bbox(tk.ALL)
                )
            )
            self.output_canvas.create_window((0, 0), window=self.output_scrollable_frame, anchor=tk.NW)
            self.output_canvas.configure(yscrollcommand=self.output_scrollbar.set)

        return

    def _render_widgets(self):

        if self.mode == 1:

            self.ml_dg_frame.pack(side=tk.TOP, fill=tk.X)

            self.ml_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

            self.ml_lframe.pack(padx=20, pady=10)

            self.ml_open_btn.pack(side=tk.LEFT, padx=5)

            self.ml_entry.pack(side=tk.RIGHT, padx=5, pady=5)

            self.dg_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

            self.dg_lframe.pack(padx=20, pady=10)

            self.dg_entry.pack(fill=tk.X, padx=5, pady=5)

            self.td_as_frame.pack(side=tk.TOP, fill=tk.X)

            self.td_frame.pack(side=tk.LEFT, expand=False, fill=tk.BOTH)

            self.td_lframe.pack(padx=20, pady=10)

            self.min_label.grid(row=0, column=0, ipadx=2, ipady=2)
            self.min_entry.grid(row=0, column=1, padx=3, pady=3)
            self.max_label.grid(row=1, column=0, ipadx=2, ipady=2)
            self.max_entry.grid(row=1, column=1, padx=3, pady=3)

            self.as_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

            self.as_lframe.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

            self.as_internal_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            self.master.update()

            self.as_canvas.place(width=self.as_internal_frame.winfo_width(), height=self.as_internal_frame.winfo_height())

            self.as_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            self.output_frame.pack(expand=True, fill=tk.BOTH)

            self.output_lframe.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

            self.output_internal_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            self.master.update()

            self.output_canvas.place(width=self.output_internal_frame.winfo_width(), height=self.output_internal_frame.winfo_height())

            self.output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        return

    def _get_ml_fname(self):

        self.ml_fname_txtv.set(askopenfilename())

        self.process.set_members_fname(str(self.ml_fname_txtv.get()))

        return

    def _set_destination_group(self):

        self.process.set_destination_group(str(self.dg_txtv.get()))

        return

    def _set_min_delay(self):

        self.process.timer[0] = int(self.min_timer_txtv.get())

        return

    def _set_max_delay(self):

        self.process.timer[1] = int(self.max_timer_txtv.get())

        return


def main():

    TGAgui()

    return


if __name__ == "__main__":

    main()
