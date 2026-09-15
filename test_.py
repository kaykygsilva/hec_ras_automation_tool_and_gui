from win32com.client import selecttlb
import pythoncom
import re
nm = "Geom=78,50,55,2.8,--2.8,False,0.5,,0.7,2.8"
novo_valor = 5674
# Captura 'Geom=', os dígitos do primeiro parâmetro (\d+), e o restante da string (,\d+.*)
change = re.sub(r"(Geom=)\d*(,\d+.*)", rf"\g<1>{novo_valor}\g<2>", nm)
print(change)

"""
tlb = selecttlb.EnumTlbs()
idcls = 0

for i in tlb:
    if re.search(fr"HEC River\s*\w*", i.desc):
        print(i.desc)
        print(i.clsid)
        idcls = i.clsid
        print(i.lcid)


def achar_clsid_por_nome_typelib(nome_coclass=None):
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

clsid = achar_clsid_por_nome_typelib("HECRASController")
print("CLSID final:", clsid)"""


"""tlb = selecttlb.SelectTlb()
if tlb:
    print("CLSID:", tlb.clsid)
    print("Nome:", tlb.desc)
    print("Versão Major:", tlb.major)
    print("Versão Minor:", tlb.minor)
    print("LCID:", tlb.lcid)
    print("Flags:", tlb.flags)
    print("DLL/caminho:", tlb.dll)
else:
    print("Nenhuma biblioteca selecionada (cancelou o diálogo)")

"""

"""from win32com.client import Dispatch
import pythoncom


pasta_secreta = pythoncom.RegOpenKeyEx(
    pythoncom.HKEY_CLASSES_ROOT,
    "CLSID",
    0,
    pythoncom.KEY_READ
)
print(f"Caminho: {pasta_secreta}")"""

"""
matriz_A = np.array([[1,2,3,4], [2,7,8,9], ['Y',9,10,12]])
lin = np.linspace(0,1,15)
print(matriz_A[0,2:])
print(lin)

matriz_range = np.arange(1,10)


n = int(np.sqrt(len(matriz_range)))

if n*n == len(matriz_range):
    print("Forma quadrada")
    matriz_quadrada = np.reshape(matriz_range, (3, 3))
    print(matriz_quadrada)
else:
    print("Não forma quadrada")

document = "Kayak abriu a geladeira"
dd_dict = defaultdict(int)
word = "abriu Kayak abriu a geladeira"

numb = Counter(word)
for word,count in numb.most_common(5):
    print(word,count)

x=3
parity = "par" if x%2==0 else "odd"
print(parity)


squares = [f"tem raiz: {x}" if m.sqrt(x).is_integer() else f"não tem: {x}" for x in range(0,10)]
print(squares)
"""#for word in document:
 #   dd_dict[word] += 1
  #  print(dd_dict)


