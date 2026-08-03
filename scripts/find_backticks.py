p='c:/Users/BACS_TI_Col/Documents/Desarrollo/ERP_BACS/static/js/formulario.js'
s=open(p,encoding='utf-8').read()
for i,ch in enumerate(s):
    if ch=='`':
        line=s.count('\n',0,i)+1
        col=i - s.rfind('\n',0,i)
        print(i, 'line',line,'col',col)
