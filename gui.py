# Ferramenta de Automação de Simulações Dam Break no HEC-RAS
# Copyright (C) 2026 Kayky Gabriel dos Santos Silva, Manuella Anaís Rodrigues Fagundes
#
# Este programa é um software livre; você pode redistribuí-lo e/ou
# modificá-lo sob os termos da Licença Pública Geral GNU (GPLv3).

from tkinter import *

root = Tk()

class Aplication():
    def __init__(self):
        self.root = root
        self.tela()
        self.gui()
        root.mainloop()
    def tela(self):
        root.title("Dam Break Simulations")
        root.configure(background="#1e5263")
        root.geometry("500x500")
        root.resizable(width=True, height=True)
        root.maxsize(800, 800)
        root.minsize(400, 400)
    def gui(self):
        #building frames
        frame_1 = Frame(root, bg="white", highlightbackground="black", highlightthickness=1)
        frame_1.place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.5)
        frame_2 = Frame(root, bg="white", highlightbackground="black", highlightthickness=1)
        frame_2.place(relx=0.01, rely=0.52, relwidth=0.98, relheight=0.47)

        #building buttons
        #directory, plan, geometry
        dir_bttn = Button(frame_1, text="Dir:")
        dir_bttn.place(relx=0.01, rely=0.10, relwidth=0.10, relheight=0.1)
        lbl_dir = Label(frame_1, text="waiting directory...", highlightcolor='gray', highlightbackground="black", highlightthickness=1)
        lbl_dir.place(relx=0.12, rely=0.10, relwidth=0.4,relheight=0.1)

        test_items = ['waiting plans...','waiting plans...', 'waiting plans...']
        list_variables = Variable(value=test_items)
        plan_bttn = Listbox(listvariable=list_variables)
        plan_bttn.place(relx=0.02, rely=0.14, relwidth=0.17, relheight=0.13)


        #menu bar
        opt_btn = Button(frame_1, text="Options")
        opt_btn.place(relx=0.001, rely=0.0, relwidth=0.11, relheight=0.07)
        manl_btn = Button(frame_1, text="Manual")
        manl_btn.place(relx=0.11, rely=0.0, relwidth=0.11, relheight=0.07)
        mhrd_btn = Button(frame_1, text="Hardware")
        mhrd_btn.place(relx=0.22, rely=0.0, relwidth=0.13, relheight=0.07)


Aplication()