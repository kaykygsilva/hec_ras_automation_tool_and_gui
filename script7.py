# Ferramenta de Automação de Simulações Dam Break no HEC-RAS
# Copyright (C) 2026 Kayky Gabriel dos Santos Silva, Manuella Anaís Rodrigues Fagundes
#
# Este programa é um software livre; você pode redistribuí-lo e/ou
# modificá-lo sob os termos da Licença Pública Geral GNU (GPLv3).

from time import sleep
import pythoncom
import win32com.client
import re
import pandas as pd
import subprocess
import time
import os
import h5py
import threading
import numpy as np
import queue

#variables
global_queue = queue.Queue()
event = threading.Event()
hec = None
running = False
numb_simulation_done = 0
numb_simulation_waiting = 0
dir_project = None
id = None
parar_monitor = threading.Event()
#matrzi to store the files
waiting_matriz = np.full((10,10,100),None,dtype=object)

"""arquivos de breach em plan: Breach Geom=35,50,55,2.8,2.8,False,0.5,,0.7,2.8
Breach Start=True,69,22SEP2026,04:00,False,69,2,0"""


def inicializer(id):
    try:
        print("Inicializando o RAS...")
        hec_bruto = win32com.client.Dispatch(id)
        hec = win32com.client.CastTo(hec_bruto, '_HECRASController')

        # Puxando a versão do jeito correto
        print(f"{'-' * 20}RAS inicializado com sucesso!{'-' * 20}\n Versão: {hec.HECRASVersion()}")

        open_project(hec)


    except Exception as e:
        print(f"Erro: {e}")


def open_project(hec):
    hec.ShowRas()
    plano_alvo = None
    global dir_project
    global waiting_matriz
    thread_ = None
    if dir_project is None and running==False:
        while True:
            #openning project
            # #so, hec.Project_Open() doesnt return 'true' or 'false' but None.
            # I checked with re by self affinity but the result of no found directory is: empty (' '), using hec.CurrentProjectTitle()
            dir_project = input("\nInsira o caminho do projeto: \ndir:")
            hec.Project_Open(f"{dir_project}")
            if re.match(r"\s", hec.CurrentProjectTitle()):
                #print(f"Projeto ativo: {hec.CurrentProjectTitle()}")
                print("\n NÃO ENCONTRADO - Insira o caminho do projeto novamente\n")
            else:
                print( "PROJETO ENCONTRADO - AGUARDE...")
                break

        raw_plan = hec.Plan_Names(None, None, None)
        plan_count, plan_names, *restos = raw_plan


        opt_plano = input(f"Planos disponíveis: {plan_names}\n Selecione o plano alvo : ")
        while opt_plano not in plan_names:
            print(f" {opt_plano} nao se encontra na lista de planos")
            opt_plano = input(" Selecione o plano alvo novamente: ")

        plano_alvo = opt_plano
        hec.Plan_SetCurrent(plano_alvo)
        bco = hec.CurrentPlanFile()
        print(f"-{bco}-")
        waiting_matriz[0, 1, 0] = bco

    thread_ = threading.Thread(target=run_simulation_test_threading,args=(dir_project,plano_alvo), daemon=True)
    while True:

        chosen = int(input(
            f"\n{"-" * 20}BEM-VINDO{"-" * 20}\nOp ções disponíveis: \n 1 - Change Run Window\n 2 - Run Simulation\n 3- Exit() \n Option: "))

        while True:
            if chosen not in range(1,5):
                print("Invalid option. Please, select again: ")
                chosen = int(input("\nCurrent options: \n 1 - Change Run Window\n 2 - Run Simulation\n 3- Exit() \n Option: "))
            else:
                break
        #change_guid(hec, plano_alvo)
        match chosen:
            case 1:
                change_run_window(hec, plano_alvo)
            case 2:
                print("Verifying if there is simulations currently running...")
                thread_.start()
                time.sleep(2)
                print(f"Running: {running}")

            case 3:
                if event.is_set():
                    read_queue()
                    event.clear()
                else:
                    print("Event not done yet")
            case 4:
                end_hec(hec)
                exit()


    """else:
        thread_ = threading.Thread(target=run_simulation_test_threading, args=(dir_project, plano_alvo), daemon=True)

        print(f"-{running}/*/*")
        while True:
            if event.is_set():
                print(F"SIMULACAO Nº {numb_simulation_done} FINALIZADA")

            chosen = int(input(f"\nOpções disponíveis:\n 1 - Change Run Window\n 2 - Run Simulation\n 3- Exit() \n Option: "))
            try:
                match chosen:
                    case 1:
                        change_run_window(hec, plano_alvo)
                    case 2:
                        thread_.start()
                        hec.Compute_ShowComputationWindow()
                    case 3:
                        end_hec(hec)
                        break
            except Exception as e:
                print(f"ERRO: {e}")"""

def change_guid(hec,plano):
    if running == True:
        dirct, short_nam = hec.Plan_GetFilename(plano)
        numb_plan = re.findall(r'\d+', dirct)
        bco = f"{dirct[:-3]}p{numb_plan[-1]}"
        # print(bco)
        # 'Short Identifier=08                                                              '
        print("Funcionando")
        with open(bco, 'r', encoding='utf-8', errors='ignore') as f:
            arquivo_bco = f.read()
        change = re.sub(fr"Short Identifier=\d+(\s+)",rf"\g<1>{numb_simulation_done} ",arquivo_bco)


        try:
            with open(bco, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(change)
        except Exception as e:
            print(f"ERRO: {e}")

        hec.Plan_SetCurrent(plano)
        hec.Project_Save()


def change_run_window(hec, plano):
    computation_result, profile_result, hydrograph_result = "", "", ""

    #print("runinininin")
    if running == True:
        # with open(plan_dir,'r', encoding='utf-8', errors='ignore') as f:
        global numb_simulation_waiting
        global waiting_matriz
        #only to prevent

        while True:
            #keeping the loop until exit()
            editing_or_creatingnew = int(input("Option: 1- Novos dados 2- Modificação 3- Menu anterior"))


            match editing_or_creatingnew:

                case 1:
                    numb_simulation_waiting += 1

                    bco =  waiting_matriz[0,1,0]
                    if bco is None:
                        print("No data on initial matriz")

                    try:
                        # make a txt with d log .bXX and open
                        with open(bco, 'r', encoding='utf-8', errors='ignore') as f:
                            arquivo_bco = f.read()
                            waiting_matriz[numb_simulation_done-1, 1,numb_simulation_waiting] = arquivo_bco
                            print(f" Funcionando... Dado já na matriz {waiting_matriz[numb_simulation_done-1,1,numb_simulation_waiting]}")

                    except Exception as e:
                        print(f"-ERRO-: {e}")
                        # print(list(arquivo_bco.split('\n')))

                    # file_split = list(arquivo_bco.split("\n"))

                    # positions: comput 35+1, output interval 36+1, instantaneous interval 37+1, mapping interval 38+1,ID 16º
                    # get with search the ocurrance and salved it
                    computation = re.search(r"Computation Interval=(\d+\w+)", waiting_matriz[numb_simulation_done-1,1,numb_simulation_waiting])
                    profile = re.search(r"Instantaneous Interval=(\d+\w+)",  waiting_matriz[numb_simulation_done-1,1,numb_simulation_waiting])
                    mapping = re.search(r"Mapping Interval=(\d+\w+)",  waiting_matriz[numb_simulation_done-1,1,numb_simulation_waiting])
                    hydrograph = re.search(r"Output Interval=(\d+\w+)",  waiting_matriz[numb_simulation_done-1,1,numb_simulation_waiting])
                    if computation:
                        computation_result = computation.group(1)
                    if profile:
                        profile_result = profile.group(1)
                    if mapping:
                        mapping_result = mapping.group(1)
                    if hydrograph:
                        hydrograph_result = hydrograph.group(1)

                    comput_numb = int(input(f"Digite o novo valor Computation Interval (atual: {computation_result}): "))
                    profile_numb = int(input(f"Digite o novo valor Detailed Output (atual:{profile_result}): "))
                    mapping_numb = int(input(f"Digite o novo Mapping Interval (atual:{mapping_result}): "))
                    hydrograph_numb = int(input(f"Digite o novo Hydrograph Interval (atual:{hydrograph_result}): "))

                    change = re.sub(r"(Computation Interval=)\d+(\w+)", rf"\g<1>{comput_numb}\g<2>",  waiting_matriz[numb_simulation_done-1,1,numb_simulation_waiting])
                    change = re.sub(r"(Instantaneous Interval=)\d+(\w+)", rf"\g<1>{profile_numb}\g<2>", change)
                    change = re.sub(r"(Mapping Interval=)\d+(\w+)", rf"\g<1>{mapping_numb}\g<2>", change)
                    change = re.sub(r"(Output Interval=)\d+(\w+)", rf"\g<1>{hydrograph_numb}\g<2>", change)
                    #change = re.sub(fr"{list(change.split('\n'))[20]}", f"{list(change.split('\n'))[20]}_{numb_simulation_done}", change)

                    waiting_matriz[(numb_simulation_done-1, 1,numb_simulation_waiting)] = change
                    print(waiting_matriz[numb_simulation_done - 1, 1, numb_simulation_waiting])



                case 2:

                    while True:
                        choi = int(input(f"Wich position number of editing (quant. of editings at d moment: {numb_simulation_waiting}: "))
                        if choi not in range(numb_simulation_waiting+1):
                            print("Posicao invalida")
                        else:
                            break

                    bco = waiting_matriz[numb_simulation_done-1, 1, choi]
                    if bco is None:
                        print("No data on initial matriz")
                        # print(list(arquivo_bco.split('\n')))

                        # file_split = list(arquivo_bco.split("\n"))

                        # positions: comput 35+1, output interval 36+1, instantaneous interval 37+1, mapping interval 38+1,ID 16º
                        # get with search the ocurrance and salved it
                    computation = re.search(r"Computation Interval=(\d+\w+)",bco)
                    profile = re.search(r"Instantaneous Interval=(\d+\w+)",
                                        bco)
                    mapping = re.search(r"Mapping Interval=(\d+\w+)",
                                        bco)
                    hydrograph = re.search(r"Hydrograph Interval=(\d+\w+)",
                                           bco)
                    if computation:
                        computation_result = computation.group(1)
                    if profile:
                        profile_result = profile.group(1)
                    if mapping:
                        mapping_result = mapping.group(1)
                    if hydrograph:
                        hydrograph_result = hydrograph.group(1)

                    comput_numb = int(input(f"Digite o novo valor Computation Interval (atual: {computation_result}): "))
                    profile_numb = int(input(f"Digite o novo valor Detailed Output (atual:{profile_result}): "))
                    mapping_numb = int(input(f"Digite o novo Mapping Interval (atual:{mapping_result}): "))
                    hydrograph_numb = int(input(f"Digite o novo Hydrograph Interval (atual:{hydrograph_result}): "))

                    change = re.sub(r"(Computation Interval=)\d+(\w+)", rf"\g<1>{comput_numb}\g<2>",
                                    bco)
                    change = re.sub(r"(Instantaneous Interval=)\d+(\w+)", rf"\g<1>{profile_numb}\g<2>", change)
                    change = re.sub(r"(Mapping Interval=)\d+(\w+)", rf"\g<1>{mapping_numb}\g<2>", change)
                    change = re.sub(r"(Output Interval=)\d+(\w+)", rf"\g<1>{hydrograph_numb}\g<2>", change)
                    # change = re.sub(fr"{list(change.split('\n'))[20]}", f"{list(change.split('\n'))[20]}_{numb_simulation_done}", change)

                    waiting_matriz[(numb_simulation_done - 1, 1, choi)] = change
                    print(waiting_matriz[numb_simulation_done - 1, 1, choi])

                case 3:
                    break

            """try:
                with open(bco, 'w', encoding='utf-8', errors='ignore') as f:
                    f.write(change)
                #change_guid(hec,plano)
            except Exception as e:
                print(f"ERRO: {e}")
            print(change)
             """


    else:
        # with open(plan_dir,'r', encoding='utf-8', errors='ignore') as f:
        try:
            dirct, short_nam = hec.Plan_GetFilename(plano)
            numb_plan = re.findall(r'\d+', dirct)
            bco = f"{dirct[:-3]}p{numb_plan[-1]}"
            print(bco)
            waiting_matriz[0,1,1] = bco
            # make a txt with d log .bXX and open
            with open(bco, 'r', encoding='utf-8', errors='ignore') as f:
                arquivo_bco = f.read()
                print(list(arquivo_bco.split('\n')))
        except Exception as e:
            print(f"ERRO: {e}")
        # file_split = list(arquivo_bco.split("\n"))

        # positions: comput 22, profile 24, hydrograph 25
        # get with search the ocurrance and salved it
        computation = re.search(r"Computation Interval=(\d+)\w+", arquivo_bco)
        profile = re.search(r"Instantaneous Interval=(\d+)\w+", arquivo_bco)
        mapping = re.search(r"Mapping Interval=(\d+)\w+", arquivo_bco)
        hydrograph = re.search(r"Output Interval=(\d+)\w+", arquivo_bco)
        if computation:
            computation_result = computation.group(1)
        if profile:
            profile_result = profile.group(1)
        if mapping:
            mapping_result = mapping.group(1)
        if hydrograph:
            hydrograph_result = hydrograph.group(1)

        comput_numb = int(input(f"Digite o novo valor Computation Interval (atual: {computation_result}): "))
        profile_numb = int(input(f"Digite o novo valor Profile (atual:{profile_result}): "))
        mapping_numb = int(input(f"Digite o novo Mapping Interval (atual:{mapping_result}): "))
        hydrograph_numb = int(input(f"Digite o novo Hydrograph Interval (atual:{hydrograph_result}): "))

        change = re.sub(r"(Computation Interval=)\d+(\w+)", rf"\g<1>{comput_numb}\g<2>", arquivo_bco)
        change = re.sub(r"(Instantaneous Interval=)\d+(\w+)", rf"\g<1>{profile_numb}\g<2>", change)
        change = re.sub(r"(Mapping Interval=)\d+(\w+)", rf"\g<1>{mapping_numb}\g<2>", change)
        change = re.sub(r"(Output Interval=)\d+(\w+)", rf"\g<1>{hydrograph_numb}\g<2>", change)
        # change = re.sub(fr"{list(change.split('\n'))[20]}", f"{list(change.split('\n'))[20]}_{numb_simulation_done}", change)

        try:
            with open(bco, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(change)
            # change_guid(hec,plano)
        except Exception as e:
            print(f"ERRO: {e}")
        print(change)
        waiting_matriz[(0,0,1)] = change
        hec.QuitRas()

    hec.ShowRas()
    hec.Project_Open(dir_project)
    hec.Plan_SetCurrent(plano)
    open_project(hec)


def run_simulation_test_threading(project,plan):
    global running
    global parar_monitor
    global id
    global hec
    global running

    pythoncom.CoInitialize()
    try:
        hec_bruto = win32com.client.Dispatch(id)
        hec_2 = win32com.client.CastTo(hec_bruto, '_HECRASController')

        #("Verifying if there is simulation currently running...")

        if running:
            print(f"\n{"-"*20}There is one simulation currently running...{"-"*20}\n")
            #end_hec(hec)

        else:
            hec_2.Project_Open(f"{project}")
            hec_2.Plan_SetCurrent(plan)
            hec_2.Project_Save()

            running = True
            global numb_simulation_done
            numb_simulation_done +=1
            NMsg, TabMsg, block = None, None, True
            hec_2.Compute_ShowComputationWindow()
            global_queue.put(f"\n-{threading.current_thread().name}-\n")
            RV, NMsg, TabMsg, block = hec_2.Compute_CurrentPlan(NMsg, TabMsg, block)

            # print(f"{hec.PlanOutput_IsCurrent(None,None,None)}"
            if TabMsg:
                event.set()
                global_queue.put("\nMensagens do RAS-RV:\n")
                global_queue.put(RV)

                global_queue.put("\nMensagens do RAS-NMSG:\n")
                global_queue.put(NMsg)

                global_queue.put("\nMensagens do RAS-TABMSG:\n")
                global_queue.put(TabMsg)

                global_queue.put("\nMensagens do RAS:\n")
                global_queue.put(block)

                global_queue.put("\n__SIMULACAO FINALIZADA")

            running=False
            #end_hec(hec_2)


        """
        geom = hec.CurrentGeomHDFFile()
        with h5py.File(fr"{geom}", "r") as f:
            vlm = f['Geometry']['Storage Areas']['Volume Elevation Values'][()]
            att = f['Geometry']['Storage Areas']['Attributes'][()]
            vlm_data = pd.DataFrame(vlm)
        
            print(vlm_data)
        """
    except Exception as e:
        global_queue.put(f"ERRO: {e}")
    finally:
        pythoncom.CoUninitialize()

def read_queue():
    global global_queue

    while not global_queue.empty():
        try:
            msg = global_queue.get_nowait()
            print(msg)
        except queue.Empty:
            break

"""def running_verify():
    global running
    global parar_monitor
    global id
    #necessary for threa+COM
    pythoncom.CoInitialize()
    try:


        if running == True:
            print("There is one simulation currently running...")
        else:
            print("There is no simulation currently running...")
        while not parar_monitor.is_set():
            try:
                print(f"///{hec.Compute_Complete}")
                print(f"///{hec.Compute_Cancel}")
                if hec.Compute_Complete():
                    print(F"SIMULACAO Nº {numb_simulation_done} FINALIZADA. INICIANDO PRÓXIMA...")
                    running = False
                    break
            except Exception as e:
                print(f"ERRO: {e}")

            time.sleep(2)
        
    finally:
        pythoncom.CoUninitialize()"""

def change_cota_volum():
    print("Iniciando cota volum...")



def end_hec(hec):
    print("Limpando memória e matando processos fantasmas...")
    if hec is not None:
        try:
            hec.QuitRas()
        except Exception as e:
            pass  # Ignora erro caso já esteja fechado

        # Destrói os objetos COM para soltar os arquivos
    hec.QuitRas()
    del hec
    print("Script finalizado!")
    

if __name__ == '__main__':
    id = "{6EED89FF-61FA-4FDF-ADDF-1A634B07DA7D}"
    inicializer(id)
