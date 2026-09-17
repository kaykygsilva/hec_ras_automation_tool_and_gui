# Ferramenta de Automação de Simulações Dam Break no HEC-RAS
# Copyright (C) 2026 Kayky Gabriel dos Santos Silva, Manuella Anaís Rodrigues Fagundes
#
# Este programa é um software livre; você pode redistribuí-lo e/ou
# modificá-lo sob os termos da Licença Pública Geral GNU (GPLv3).
import re
import threading
from logging import disable
from tkinter import *
from tkinter import filedialog, font
from tkinter.scrolledtext import ScrolledText

from ttkbootstrap.style import bootstyle

from backend_hecras_1 import Backend
import backend_hecras_1
import ttkbootstrap as ttk
import tkinter as tkk

app = ttk.App(
    title="Dam Break Automation",
)
menubar = ttk.Menu(app)
style = ttk.Style()
event = threading.Event()


class Aplication():
    def __init__(self):
        self.backend = Backend()
        self.thread_ = None
        self.style = style
        self.app = app
        self.tela()
        self.gui()
        app.mainloop()

    def tela(self):
        # app.geometry("1280x920")
        app.resizable(width=True, height=True)
        app.maxsize(1680, 920)
        app.minsize(1280, 700)

    def gui(self, plans=None):
        # creating pane window
        pw = PanedWindow(app, orient="vertical", sashrelief=tkk.RAISED, sashwidth=6)
        pw_2 = PanedWindow(pw, orient="horizontal", sashrelief=tkk.RAISED, sashwidth=6)
        pw_3 = PanedWindow(pw, orient="horizontal", sashrelief=tkk.RAISED, sashwidth=6)

        pw.place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.98)
        # building frames
        # frame 1 hexadecimal #BAE0EE
        frame_1 = Frame(pw_2, highlightbackground="black", highlightthickness=1)
        frame_2 = Frame(pw_3, highlightbackground="black", highlightthickness=1)
        frame_run_info = Frame(pw_2, highlightbackground="black", highlightthickness=1)
        frame_hietograma = Frame(pw_2, highlightbackground="black", highlightthickness=1)
        frame_breach = Frame(pw_3, highlightbackground="black", highlightthickness=1)
        frame_run_window = Frame(pw_3, highlightbackground='black', highlightthickness=1)

        # planedwindows in
        pw_2.add(frame_1, minsize=500)
        pw_2.add(frame_run_info, minsize=500)
        pw_2.add(frame_hietograma, minsize=350)
        pw_3.add(frame_2, minsize=480)
        pw_3.add(frame_breach, minsize=380)
        pw_3.add(frame_run_window, minsize=680)
        # planedwindow root
        pw.add(pw_2, minsize=480)
        pw.add(pw_3, minsize=480)

        def exit_all():
            self.backend.end_hec()
            app.destroy()

        file_menu = ttk.Menu(frame_1, tearoff=False)
        file_menu.add_command(label="New", command=lambda: print("new"))
        file_menu.add_command(label="Open…", command=lambda: print("open"))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=exit_all)
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = ttk.Menu(menubar, tearoff=False)
        edit_menu.add_command(label="Undo", command=lambda: print("undo"))
        menubar.add_cascade(label="Edit", menu=edit_menu)

        app.configure(menu=menubar)  # attach the bar to the window

        # building buttons
        # directory, plan, geometry

        # get the selected plan
        def select_pplan(event):
            indice = plan_bttn.curselection()
            if indice:
                plan = self.backend.select_plan(plan_bttn.get(indice[0]))
                print(f"--{plan}")
                txt_content.configure(text=plan[0], justify='left')
                geom_content.configure(text=plan[1], justify='left')
                unsteady_content.configure(text=plan[2], justify='left')
                resume_variables.set(plan[3])
                # unsteady_window = backend_hecras.()

        def buscar_arquivo():
            global plans
            # Open thw windows window to choose the file
            caminho_arquivo = filedialog.askopenfilename(
                title="Selecione um arquivo",
                filetypes=[("Todos os arquivos", "*.*"), ("Project", "*.prj")]
            )

            # Se o usuário escolher um arquivo (não fechar no 'X' ou cancelar)
            if caminho_arquivo:
                lbl_dir.config(text=f"{caminho_arquivo}")
                plans2 = self.backend.inicializer(caminho_arquivo)
                print(plans2)
                list_final = plans2[2:]
                list_f = []
                for x in range(len(list_final[0])):
                    list_f.append(list_final[0][x])
                list_variables.set(list_f)
                stylee.insert(END, '\n'.join(plans2[:2]))
                stylee.config(state='disabled')

        dir_bttn = Button(frame_1, text="Dir:", command=buscar_arquivo)
        dir_bttn.place(relx=0.01, rely=0.10, relwidth=0.10, relheight=0.1, )
        lbl_dir = Label(frame_1, text="waiting directory...", font=('Arial', 10), anchor='w',
                        highlightbackground="black", highlightthickness=1)
        lbl_dir.place(relx=0.12, rely=0.10, relwidth=0.5, relheight=0.1)

        plans = ['']
        list_variables = Variable(value=plans)
        plan_bttn = Listbox(frame_1, listvariable=list_variables, activestyle='dotbox')
        plan_bttn.place(relx=0.01, rely=0.28, relwidth=0.18, relheight=0.30)
        plan_bttn.bind("<Button 1>", select_pplan)

        txt_projct = Label(frame_1, text='Project: ')
        txt_projct.place(relx=0.32, rely=0.28, relwidth=0.10, relheight=0.07)
        txt_content = Label(frame_1, text='...', highlightcolor='black', justify="left", highlightbackground="black",
                            highlightthickness=1)
        txt_content.place(relx=0.50, rely=0.28, relwidth=0.45, relheight=0.07)

        # geometry title - space
        txt_geom = Label(frame_1, text='Geometry: ')
        txt_geom.place(relx=0.31, rely=0.36, relwidth=0.12, relheight=0.07)
        geom_content = Label(frame_1, text='...', highlightcolor='black', justify="left", highlightbackground="black",
                             highlightthickness=1)
        geom_content.place(relx=0.50, rely=0.36, relwidth=0.45, relheight=0.07)

        # unsteady file
        unsteady_projct = Label(frame_1, text='Unsteady file: ')
        unsteady_projct.place(relx=0.29, rely=0.44, relwidth=0.17, relheight=0.07)
        unsteady_content = Label(frame_1, text='...', highlightcolor='black', justify="left",
                                 highlightbackground="black",
                                 highlightthickness=1)
        unsteady_content.place(relx=0.50, rely=0.44, relwidth=0.45, relheight=0.07)

        # menu bar
        opt_btn = Button(frame_1, text="Options", highlightthickness=0)
        opt_btn.place(relx=0.001, rely=0.0, relwidth=0.11, relheight=0.07)
        manl_btn = Button(frame_1, text="Manual", highlightthickness=0)
        manl_btn.place(relx=0.11, rely=0.0, relwidth=0.11, relheight=0.07)
        mhrd_btn = Button(frame_1, text="Hardware", highlightthickness=0)
        mhrd_btn.place(relx=0.22, rely=0.0, relwidth=0.13, relheight=0.07)

        # frame 2 log
        stylee = ScrolledText(
            master=frame_2,
            highlightcolor=style.colors.primary,
            highlightbackground=style.colors.border,
            highlightthickness=1
        )
        # stylee.place(relx=0.01, rely=0.56, relwidth=0.25, relheight=0.40)
        # relx = 0.02, rely = 0.14, relwidth = 0.22, relheight = 0.13
        stylee.config(state='normal')

        # frame run window
        style.configure("danger.Outline.TButton", font=("Arial", 20), anchor='w')

        label_running = ttk.Button(
            frame_run_window,
            text="OFF",
            bootstyle="danger outline",
        )

        label_running.place(relx=0.81, rely=0.02, relwidth=0.14, relheight=0.14)

        # text variables for the fields
        compt_var = StringVar()
        hydrogp_var = StringVar()
        mapp_var = StringVar()
        detailed_var = StringVar()
        date_start_var = StringVar()
        date_end_var = StringVar()

        # next we have the variables on the window run, orderly

        txt_computation = Label(frame_run_window, text='Computation Interval: ', font=('Arial', 8), anchor='w')
        txt_computation.place(relx=0.02, rely=0.08, relwidth=0.25, relheight=0.07)
        computation_value = Entry(frame_run_window, textvariable=compt_var, highlightcolor='black', justify="left",
                                  highlightbackground="black",
                                  highlightthickness=1)
        computation_value.place(relx=0.28, rely=0.09, relwidth=0.06, relheight=0.05)

        # mappin interval
        txt_mapping = Label(frame_run_window, text='Mapping Output Interval: ', font=('Arial', 8), anchor='w')
        txt_mapping.place(relx=0.02, rely=0.14, relwidth=0.25, relheight=0.1)
        mapping_value = Entry(frame_run_window, textvariable=mapp_var, highlightcolor='black', justify="left",
                              highlightbackground="black",
                              highlightthickness=1)
        mapping_value.place(relx=0.28, rely=0.17, relwidth=0.06, relheight=0.05)

        # unsteady file
        txt_hydrogph = Label(frame_run_window, text='Hydrograph Interval: ', font=('Arial', 8), anchor='w')
        txt_hydrogph.place(relx=0.02, rely=0.23, relwidth=0.33, relheight=0.08)
        hydrograph_content = Entry(frame_run_window, textvariable=hydrogp_var, highlightcolor='black', justify="left",
                                   highlightbackground="black",
                                   highlightthickness=1)
        hydrograph_content.place(relx=0.28, rely=0.25, relwidth=0.06, relheight=0.05)
        # detailed output space
        txt_detailed = Label(frame_run_window, text='Detailed Output Interval: ', font=('Arial', 8),
                             anchor='w')
        txt_detailed.place(relx=0.02, rely=0.32, relwidth=0.33, relheight=0.08)
        detailed_content = Entry(frame_run_window, textvariable=detailed_var, highlightcolor='black', justify="left",
                                 highlightbackground="black",
                                 highlightthickness=1)
        detailed_content.place(relx=0.28, rely=0.34, relwidth=0.06, relheight=0.05)
        # date label change
        # start date
        txt_date_start = Label(frame_run_window, text='Start date: ', font=('Arial', 8),
                               anchor='w')
        txt_date_start.place(relx=0.02, rely=0.41, relwidth=0.20, relheight=0.08)
        date_start_content = Entry(frame_run_window, textvariable=date_start_var, highlightcolor='black',
                                   justify="left",
                                   highlightbackground="black",
                                   highlightthickness=1)
        date_start_content.place(relx=0.22, rely=0.42, relwidth=0.14, relheight=0.05)
        # edn date
        txt_end_start = Label(frame_run_window, text='End date: ', font=('Arial', 8),
                              anchor='w')
        txt_end_start.place(relx=0.02, rely=0.50, relwidth=0.33, relheight=0.08)
        date_end_content = Entry(frame_run_window, textvariable=date_end_var, highlightcolor='black', justify="left",
                                 highlightbackground="black",
                                 highlightthickness=1)
        date_end_content.place(relx=0.22, rely=0.51, relwidth=0.14, relheight=0.05)

        # function to send changes to the file plan
        def send_changes():
            if btn_start.instate(["!disabled"]):
                #  for n in lista_chngs:
                #     if isinstance(n, str):
                #         list_chngok.append(n)
                # if we have an empty value
                print(type(date_start_content.get()))
                print(
                    f"{compt_var.get()}, {mapp_var.get()}, {hydrogp_var.get()}, {detailed_var.get()}, {date_start_var.get()}, {date_end_var.get()}")
                lista_chngs = [compt_var.get(), mapp_var.get(), hydrogp_var.get(), detailed_var.get(),
                               date_start_var.get(), date_end_var.get()]
                print(
                    f"{centerstat_var.get()}, {bottomwdth_var.get()}, {bottomelv_var.get()}, {leftsd_var.get()}, {rightsd_var.get()}, {breachtm_var.get()}, {breachwr_var.get()}, {startingws_var}")
                lista_chngs_breach = [centerstat_var.get(), bottomwdth_var.get(), bottomelv_var.get(), leftsd_var.get(),
                                      rightsd_var.get(),
                                      breachtm_var.get(), breachwr_var.get(), startingws_var]



                status, conteud = self.backend.change_run_window(*lista_chngs)
                self.backend.change_breach_plan(*lista_chngs_breach)
                btn_sendchng.config(text=status)
                btn_sendchng.place(relwidth=0.12)
                resume_variables.set(conteud)
            else:
                #self.backend.running = True
                # backend_hecras.numb_simulation_waiting += 1
                print(
                    f"{compt_var.get()}, {mapp_var.get()}, {hydrogp_var.get()}, {detailed_var.get()}, {date_start_var.get()}, {date_end_var.get()}")
                lista_chngs = [compt_var.get(),mapp_var.get(),hydrogp_var.get(),detailed_var.get(),
                               date_start_var.get(), date_end_var.get()]

                #sending the breach plan parametres
                print(
                    f"{centerstat_var.get()}, {bottomwdth_var.get()}, {bottomelv_var.get()}, {leftsd_var.get()}, {rightsd_var.get()}, {breachtm_var.get()}, {breachwr_var.get()}, {startingws_var}")
                lista_chngs_breach = [centerstat_var.get(), bottomwdth_var.get(), bottomelv_var.get(), leftsd_var.get(), rightsd_var.get(),
                               breachtm_var.get(), breachwr_var.get(), startingws_var]

                self.backend.change_breach_plan(*lista_chngs_breach)
                status, conteud = self.backend.change_run_window(*lista_chngs)
                btn_sendchng.config(text=status)
                btn_sendchng.place(relwidth=0.12)
                resume_variables.set(conteud)


        # def for continous checking
        # it is about the status of simulation: if finished or not

        def veryfy_simultn():
            global n
            if not backend_hecras_1.running and self.backend.RV:
                original_text = self.backend.read_queue()
                raw_lines = "".join(str(item) for item in original_text)
                lines = [line.strip() for line in raw_lines.splitlines() if line.strip()]
                resume_variables.set(lines)

                # cicle of simulaiton
                if backend_hecras_1.numb_actlly < backend_hecras_1.numb_simulation_waiting:
                    backend_hecras_1.numb_actlly += 1
                    call_run()
                btn_start.state(['!disabled'])
                btn_start.config(text="START")
                # write the log results simulation on the label


            else:
                # checking if is verryfing
                # print("Checking")
                app.after(2000, veryfy_simultn)

        # def call_run():
        def call_run():
            try:
                if backend_hecras_1.numb_actlly != 0:
                    for i, contd in enumerate(backend_hecras_1.waiting_matriz[1:, 1, 0]):
                        if isinstance(contd, str):
                            backend_hecras_1.numb_actlly = i + 1
                            self.backend.RV = False
                            self.thread_ = threading.Thread(target=self.backend.run_simulation_test_threading,
                                                            daemon=True)
                            self.thread_.start()
                            btn_start.state(['disabled'])
                            btn_start.config(text="RUNNING!!")
                            btn_start.place(relwidth=0.18)


                else:

                    self.backend.RV = False
                    self.thread_ = threading.Thread(target=self.backend.run_simulation_test_threading, daemon=True)
                    self.thread_.start()
                    btn_start.state(['disabled'])
                    btn_start.config(text="RUNNING!!")
                    btn_start.place(relwidth=0.18)
                    veryfy_simultn()
            except Exception as e:
                print(f"Erro: {e}")

        # label to show the plan file and some information about the simulaiton
        resume = ['']
        resume_variables = Variable(value=resume)
        run_window = Listbox(frame_run_window, listvariable=resume_variables, activestyle='dotbox')
        run_window.place(relx=0.38, rely=0.02, relwidth=0.42, relheight=0.80)
        # txt_runwindow = Label(frame_run_window, text='...', bg='#CFFFA7', font=('Arial', 12),
        # anchor='w', highlightthickness=1, background='white')
        # txt_runwindow.place(relx=0.44, rely=0.02, relwidth=0.30, relheight=0.80)

        btn_sendchng = ttk.Button(
            frame_run_window,
            text="Save", icon="save", bootstyle="success",
            command=send_changes
        )
        btn_sendchng.place(relx=0.02, rely=0.72, relwidth=0.14, relheight=0.11)

        btn_start = ttk.Button(
            frame_run_window,
            text="Start", icon="caret-right-fill", bootstyle="info", command=call_run
        )
        btn_start.place(relx=0.02, rely=0.84, relwidth=0.14, relheight=0.10)

        #breach frame place
        #no constructed yet the send value function to change d file
        #on the file 'backend_hecras' there is the function to change, but not receive anything
        centerstat_var = StringVar()
        bottomwdth_var = StringVar()
        bottomelv_var = StringVar()
        leftsd_var = StringVar()
        rightsd_var = StringVar()
        breachtm_var = StringVar()
        breachwr_var = StringVar()
        startingws_var = StringVar()



        txt_centerstat = Label(frame_breach, text='Center station:', font=('Arial', 10), anchor='w')
        txt_centerstat.place(relx=0.02, rely=0.08, relwidth=0.40, relheight=0.07)
        centerestat_value = Entry(frame_breach, textvariable=centerstat_var, highlightcolor='black', justify="left",
                                  highlightbackground="black",
                                  highlightthickness=1)
        centerestat_value.place(relx=0.50, rely=0.09, relwidth=0.10, relheight=0.07)

        txt_bottomwdth = Label(frame_breach, text='Bottom width:', font=('Arial', 10), anchor='w')
        txt_bottomwdth.place(relx=0.02, rely=0.17, relwidth=0.40, relheight=0.07)
        bottomwdth_value = Entry(frame_breach, textvariable=bottomwdth_var, highlightcolor='black', justify="left",
                                  highlightbackground="black",
                                  highlightthickness=1)
        bottomwdth_value.place(relx=0.50, rely=0.18, relwidth=0.10, relheight=0.07)

        txt_bottomelev = Label(frame_breach, text='Bottom elevation:', font=('Arial', 10), anchor='w')
        txt_bottomelev.place(relx=0.02, rely=0.26, relwidth=0.40, relheight=0.07)
        bottomelv_value = Entry(frame_breach, textvariable=bottomelv_var, highlightcolor='black', justify="left",
                                  highlightbackground="black",
                                  highlightthickness=1)
        bottomelv_value.place(relx=0.50, rely=0.27, relwidth=0.10, relheight=0.07)

        txt_leftsd = Label(frame_breach, text='Left side slope: ', font=('Arial', 10), anchor='w')
        txt_leftsd.place(relx=0.02, rely=0.34, relwidth=0.40, relheight=0.07)
        leftsd_value = Entry(frame_breach, textvariable=leftsd_var, highlightcolor='black', justify="left",
                                  highlightbackground="black",
                                  highlightthickness=1)
        leftsd_value.place(relx=0.50, rely=0.35, relwidth=0.10, relheight=0.07)

        txt_rightsd = Label(frame_breach, text='Right side slope: ', font=('Arial', 10), anchor='w')
        txt_rightsd.place(relx=0.02, rely=0.42, relwidth=0.40, relheight=0.07)
        rightsd_value = Entry(frame_breach, textvariable=rightsd_var, highlightcolor='black', justify="left",
                                  highlightbackground="black",
                                  highlightthickness=1)
        rightsd_value.place(relx=0.50, rely=0.44, relwidth=0.10, relheight=0.07)

        txt_breachtm = Label(frame_breach, text='Breach time:', font=('Arial', 10), anchor='w')
        txt_breachtm.place(relx=0.02, rely=0.50, relwidth=0.40, relheight=0.07)
        breachtm_value = Entry(frame_breach, textvariable=breachtm_var, highlightcolor='black', justify="left",
                                  highlightbackground="black",
                                  highlightthickness=1)
        breachtm_value.place(relx=0.50, rely=0.52, relwidth=0.10, relheight=0.07)

        txt_breachwr = Label(frame_breach, text='Breach weir: ', font=('Arial', 10), anchor='w')
        txt_breachwr.place(relx=0.02, rely=0.58, relwidth=0.40, relheight=0.07)
        breachwr_value = Entry(frame_breach, textvariable=breachwr_var, highlightcolor='black', justify="left",
                                  highlightbackground="black",
                                  highlightthickness=1)
        breachwr_value.place(relx=0.50, rely=0.60, relwidth=0.10, relheight=0.07)

        txt_startngws = Label(frame_breach, text='Starting WS: ', font=('Arial', 10), anchor='w')
        txt_startngws.place(relx=0.02, rely=0.66, relwidth=0.40, relheight=0.07)
        startingws_value = Entry(frame_breach, textvariable=startingws_var, highlightcolor='black', justify="left",
                                  highlightbackground="black",
                                  highlightthickness=1)
        startingws_value.place(relx=0.50, rely=0.68, relwidth=0.10, relheight=0.07)


if __name__ == "__main__":
    app = Aplication()