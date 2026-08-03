p='c:/Users/BACS_TI_Col/Documents/Desarrollo/ERP_BACS/static/js/formulario.js'
with open(p, 'r', encoding='utf-8') as f:
    lines=f.readlines()
start=1170
end=1200
for i in range(start,end):
    if i < len(lines):
        print(f"{i+1}: {lines[i].rstrip()}")
    else:
        break
