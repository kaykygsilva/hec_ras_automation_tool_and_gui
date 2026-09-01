# Ferramenta de Automação de Simulações Dam Break no HEC-RAS
# Copyright (C) 2026 Kayky Gabriel dos Santos Silva, Manuella Anaís Rodrigues Fagundes
#
# Este programa é um software livre; você pode redistribuí-lo e/ou
# modificá-lo sob os termos da Licença Pública Geral GNU (GPLv3).

from time import sleep
from win32com.client import selecttlb
import pythoncom
import win32com.client
import re
import pandas as pd
import subprocess
import h5py
import threading
import numpy as np
import queue

from win32com.server import exception

#variables
global_queue = queue.Queue()
waiting_matriz = np.full((50,50,100),None,dtype=object)
event = threading.Event()
hec = None
running = False
numb_simulation_waiting = 0
numb_simulation_done = 0
dir_project = None
plano_alvo = None
#clsid hecras
#id = "{6EED89FF-61FA-4FDF-ADDF-1A634B07DA7D}"
parar_monitor = threading.Event()
#to orgfanize data numb
numb_actlly = 0


"""arquivos de breach em plan: Breach Geom=35,50,55,2.8,2.8,False,0.5,,0.7,2.8
Breach Start=True,69,22SEP2026,04:00,False,69,2,0"""

class Backend():

    def __init__(self):
        self.RV = False

    #to inicialize the api com

    def localize_lcid(self, nome_coclass=None):

        tlb = selecttlb.EnumTlbs()

        for i in tlb:
            if re.search(fr"HEC River\s*\w*", i.desc):
                print(i.desc)
                print(i.clsid)
                print(i.lcid)

        for tlb in selecttlb.EnumTlbs():
            if re.search(fr"HEC River\s*\w*", tlb.desc, re.IGNORECASE):
                try:
                    major = int(tlb.major)
                    minor = int(tlb.minor)
                    lcid = int(tlb.lcid)

                    typelib = pythoncom.LoadRegTypeLib(tlb.clsid, major, minor, lcid)
                except pythoncom.com_error:
                    continue

                for i in range(typelib.GetTypeInfoCount()):
                    if typelib.GetTypeInfoType(i) == pythoncom.TKIND_COCLASS:
                        info = typelib.GetTypeInfo(i)
                        attr = info.GetTypeAttr()
                        nome, *_ = typelib.GetDocumentation(i)
                        if nome_coclass is None or nome.lower() == nome_coclass.lower():
                            print(f"Typelib: {tlb.desc} | Coclass: {nome} | CLSID: {attr.iid}")
                            return str(attr.iid)
        return None

    def inicializer(slef, caminhofl):
        global id
        global hec
        #id = "RAS70.HECRASController"
        try:


            print("Inicializando o RAS...")
            id = Backend().localize_lcid("HECRASController")
            hec_bruto = win32com.client.Dispatch(id)
            hec = win32com.client.CastTo(hec_bruto, '_HECRASController')

            # Puxando a versão do jeito correto
            print(f"{'-' * 20}RAS inicializado com sucesso!{'-' * 20}\n Versão: {hec.HECRASVersion()}")
            #hec.ShowRas()
            x = [f'HECRAS inicializado com sucesso',f'Versão: {hec.HECRASVersion()}', Backend().open_project(hec, caminhofl) ]
            return x


        except Exception as e:
            return  f"Erro: {e}"
    #open the project and send the plans
    def open_project(self,hec, camnh):
        #hec.ShowRas()
        global dir_project
        global waiting_matriz

        thread_ = None
        if dir_project is None and running==False:
            while True:
                #openning project
                # #so, hec.Project_Open() doesnt return 'true' or 'false' but None.
                # I checked with re by self affinity but the result of no found directory is: empty (' '), using hec.CurrentProjectTitle()
                dir_project = camnh
                hec.Project_Open(f"{dir_project}")
                if re.match(r"\s", hec.CurrentProjectTitle()):
                    #print(f"Projeto ativo: {hec.CurrentProjectTitle()}")
                    print("\n NÃO ENCONTRADO - Insira o caminho do projeto novamente\n")
                else:
                    raw_plan = hec.Plan_Names(None, None, None)
                    plan_count, plan_names, *restos = raw_plan
                    print(plan_count,plan_names)
                    return plan_names
                    break
    #def for select the plans
    def select_plan(self,opt_plano):
        global plano_alvo
        plano_alvo = opt_plano
        hec.Plan_SetCurrent(plano_alvo)
        bco = hec.CurrentPlanFile()
        geom = hec.CurrentGeomFile()
        unsteady = hec.CurrentUnSteadyFile()
        print(f"-{unsteady}-")
        waiting_matriz[0,1,1] = bco
        with open(bco, 'r', encoding='utf-8', errors='ignore') as f:
             waiting_matriz[0, 1, 0] = f.read()
        return  bco,geom,unsteady, waiting_matriz[0,1,0].split()

       

    def change_guid(self, file):
        if running == True:
            try:
                print("changing")
                change = re.sub(fr"Short Identifier=\d*\w*(\s*)",rf"\g<1>_{numb_actlly}_",file)
                return change
            except Exception as e:
                print(f"ERRO: {e}")
                return file


    #there is a problem here
    #take a look at
    #change data, cause its something wrong

    def change_run_window(self, *lista):
        #plano = plano_alvo
        #print("runinininin")
        #date structure in file splited
        #\'Date=07SEP2026,00:00,07SEP2026,05:00\'
        #date = re.search(r'Date=(\d+\w+\d+\),(\d*),(\d+\w+\d+),(\d*)
        #if <date variables> != None
        #change = re.sub(
        if running == True:
            # with open(plan_dir,'r', encoding='utf-8', errors='ignore') as f:
            global numb_simulation_waiting
            global waiting_matriz

            numb_simulation_waiting+=1
            try:
                print("beginning the editing while running")
                #print(waiting_matriz[numb_simulation_waiting - 1, 1, 0])
                #open the waiting matriz and find in the last file - if the first editing, find in the original file
                computation = re.search(r"Computation Interval=(\d+\w+)",
                                        waiting_matriz[numb_simulation_waiting - 1, 1, 0])
                profile = re.search(r"Instantaneous Interval=(\d+\w+)",
                                    waiting_matriz[numb_simulation_waiting - 1, 1, 0])
                mapping = re.search(r"Mapping Interval=(\d+\w+)",
                                    waiting_matriz[numb_simulation_waiting - 1, 1, 0])
                hydrograph = re.search(r"Output Interval=(\d+\w+)",
                                       waiting_matriz[numb_simulation_waiting - 1, 1, 0])

                date_start = lista[4].upper()
                date_end = lista[5].upper()

                if computation:
                    computation_result = computation.group(1)
                if profile:
                    profile_result = profile.group(1)
                if mapping:
                    mapping_result = mapping.group(1)
                if hydrograph:
                    hydrograph_result = hydrograph.group(1)

                if isinstance(lista[0], str):
                    change = re.sub(r"(Computation Interval=)\d+(\w+)", rf"\g<1>{lista[0]}\g<2>",
                                    waiting_matriz[0, 1, 0])
                else:
                    change = waiting_matriz[0, 1, 0]
                if isinstance(lista[1], str):
                    change = re.sub(r"(Instantaneous Interval=)\d+(\w+)", rf"\g<1>{lista[1]}\g<2>", change)
                if isinstance(lista[2], str):
                    change = re.sub(r"(Mapping Interval=)\d+(\w+)", rf"\g<1>{lista[2]}\g<2>", change)
                if isinstance(lista[3], str):
                    change = re.sub(r"(Output Interval=)\d+(\w+)", rf"\g<1>{lista[3]}\g<2>", change)
                if isinstance(lista[4], str):
                    change = re.sub(r"Date=(\d+\w+\d+),(\d*),(\d+\w+\d+),(\d*)",
                                    rf"{lista[4]},\g<2>,\g<3>,\g<4>", change)
                if isinstance(lista[5], str):
                    change = re.sub(r"Date=(\d+\w+\d+),(\d*),(\d+\w+\d+),(\d*)",
                                    rf"\g<1>,\g<2>,{lista[5]},\g<4>",
                                    change)

                # change = re.sub(fr"{list(change.split('\n'))[20]}", f"{list(change.split('\n'))[20]}_{numb_simulation_done}", change)

                change = Backend().change_guid(change)
                #print(change)
                waiting_matriz[numb_simulation_waiting,1,0] = change
                print(change)
                return  "DONE!!", change


            except Exception as e:
                print(f"-ERRO-: {e}")
                # print(list(arquivo_bco.split('\n')))

            # file_split = list(arquivo_bco.split("\n"))

            # positions: comput 35+1, output interval 36+1, instantaneous interval 37+1, mapping interval 38+1,ID 16º
            # get with search the ocurrance and salved it


        else:
            # with open(plan_dir,'r', encoding='utf-8', errors='ignore') as f:
            try:
                print(waiting_matriz[0,1,0])
            # file_split = list(arquivo_bco.split("\n"))

                # positions: comput 22, profile 24, hydrograph 25
                # get with search the ocurrance and salved it
                computation = re.search(r"Computation Interval=(\d+)\w+", waiting_matriz[0,1,0])
                profile = re.search(r"Instantaneous Interval=(\d+)\w+", waiting_matriz[0,1,0])
                mapping = re.search(r"Mapping Interval=(\d+)\w+", waiting_matriz[0,1,0])
                hydrograph = re.search(r"Output Interval=(\d+)\w+", waiting_matriz[0,1,0])

                date_start = lista[4].upper()
                date_end = lista[5].upper()

                if computation:
                    computation_result = computation.group(1)
                if profile:
                    profile_result = profile.group(1)
                if mapping:
                    mapping_result = mapping.group(1)
                if hydrograph:
                    hydrograph_result = hydrograph.group(1)

                if isinstance(lista[0], str):
                    change = re.sub(r"(Computation Interval=)\d+(\w+)", rf"\g<1>{lista[0]}\g<2>",
                                    waiting_matriz[0, 1, 0])
                else:
                    change = waiting_matriz[0, 1, 0]
                if isinstance(lista[1], str):
                    change = re.sub(r"(Instantaneous Interval=)\d+(\w+)", rf"\g<1>{lista[1]}\g<2>", change)
                if isinstance(lista[2], str):
                    change = re.sub(r"(Mapping Interval=)\d+(\w+)", rf"\g<1>{lista[2]}\g<2>", change)
                if isinstance(lista[3], str):
                    change = re.sub(r"(Output Interval=)\d+(\w+)", rf"\g<1>{lista[3]}\g<2>", change)
                if isinstance(lista[4], str):
                    change = re.sub(r"Date=(\d+\w+\d+),(\d*),(\d+\w+\d+),(\d*)",
                                    rf"{lista[4]},\g<2>,\g<3>,\g<4>", change)
                if isinstance(lista[5], str):
                    change = re.sub(r"Date=(\d+\w+\d+),(\d*),(\d+\w+\d+),(\d*)",
                                    rf"\g<1>,\g<2>,{lista[5]},\g<4>",
                                    change)

                try:
                    bco = hec.CurrentPlanFile()
                    with open(bco, 'w', encoding='utf-8', errors='ignore') as f:
                        f.write(change)

                    # change_guid(hec,plano)
                    #hec.ShowRas()
                    waiting_matriz[0, 1, 0] = change
                    hec.Project_Open(dir_project)
                    hec.Plan_SetCurrent(bco)
                    return "DONE!!", change
                except Exception as e:
                    return f"ERRO: {e}"
                print(change)
                waiting_matriz[(0,0,1)] = change
                hec.QuitRas()
            except Exception as e:
                print(f"ERRO: {e}")

    def run_simulation_test_threading(self):
        global running
        global parar_monitor
        global id
        global hec
        global running
        global waiting_matriz
        global numb_simulation_done
        global numb_simulation_waiting


        pythoncom.CoInitialize()
        try:
            print("uhmm")
            #oppening a new instance of hecras
            hec_bruto = win32com.client.Dispatch(id)
            hec_2 = win32com.client.CastTo(hec_bruto, '_HECRASController')

            #the run button on the frontend still disabled while is running
            #so in the beggining 'if' statement was necessary, but now no more
            try:


                hec_2.Project_Open(f"{dir_project}")
                with open(waiting_matriz[0,1,1], 'w', encoding='utf-8', errors='ignore') as f:
                    f.write(waiting_matriz[numb_actlly,1,0])
                hec_2.Plan_SetCurrent(waiting_matriz[0,1,1])
                hec_2.Project_Save()

                running = True
                numb_simulation_done += 1
                NMsg, TabMsg, block = None, None, True
                hec_2.Compute_ShowComputationWindow()
                print(f"\n-{threading.current_thread().name}-\n")
                self.RV, NMsg, TabMsg, block = hec_2.Compute_CurrentPlan(NMsg, TabMsg, block)

                # when the simultn over, send the logs to the function
                # and in the frontend we check by other function
                if self.RV:
                    print("começou a enviar os logs")
                    event.set()
                    global_queue.put("\nMensagens do RAS-RV:\n")
                    global_queue.put(self.RV)

                    global_queue.put("\nMensagens do RAS-NMSG:\n")
                    global_queue.put(NMsg)

                    global_queue.put("\nMensagens do RAS-TABMSG:\n")
                    global_queue.put(TabMsg)

                    global_queue.put("\nMensagens do RAS:\n")
                    global_queue.put(block)

                    global_queue.put("\n__SIMULACAO FINALIZADA")
                    running = False

                    def end_hec(hec_2):
                        print("Limpando memória e matando processos fantasmas...")
                        if hec_2 is not None:
                            try:
                                hec_2.QuitRas()
                            except Exception as e:
                                pass  # Ignora erro caso já esteja fechado

                            # Destrói os objetos COM para soltar os arquivos
                        hec_2.QuitRas()
                        del hec_2
                        print("Script finalizado!")

                    end_hec(hec_2)




                # if block == True the result is:
                # (True, 3, ('Starting Unsteady Computations', 'Computing', 'Computations Completed'))
                # Starting Unsteady Computations
                print(self.RV, NMsg, TabMsg)


                #geom = hec.CurrentGeomHDFFile()
                #with h5py.File(fr"{geom}", "r") as f:
                 #   vlm = f['Geometry']['Storage Areas']['Volume Elevation Values'][()]
                  #  att = f['Geometry']['Storage Areas']['Attributes'][()]
                   # vlm_data = pd.DataFrame(vlm)

                    #print(vlm_data)
                #there is a problem here, is not running more


                #geom = hec.CurrentGeomHDFFile()
                #with h5py.File(fr"{geom}", "r") as f:
                 #   vlm = f['Geometry']['Storage Areas']['Volume Elevation Values'][()]
                  #  att = f['Geometry']['Storage Areas']['Attributes'][()]
                   # vlm_data = pd.DataFrame(vlm)

                    #print(vlm_data)
            except Exception as e:
                print(f"ERRO: {e}")

        except Exception as e:
            global_queue.put(f"ERRO: {e}")
        finally:
            pythoncom.CoUninitialize()


    def read_queue(self):
        global global_queue
        k = []

        while not global_queue.empty():
            try:
                item = global_queue.get_nowait()
                k.append(item)
            except queue.Empty:
                break


        return k


    def end_hec(self):
        global hec
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

        inicializer(id)
