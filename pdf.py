from fpdf import FPDF 
import os
from pymongo import MongoClient
from prettyprinter import pprint
from bson.objectid import ObjectId


client = MongoClient(os.environ.get("MONGODB_URI"))
db = client.kolinje

def pdf_kolinja(id):

    print(id)
    id_kolinja = []
    
    for i in db.kolinja.find({},{"_id": ObjectId(id)}):
        id_kolinja.append(i)
    for j in id_kolinja:
        print(j)
        lista = list(db.kolinja.find({"_id":j['_id']},{"naziv_kolinja":1 , "vaganja.tezina_mesa":1, "vaganja.sol":1, "vaganja.papar":1,"vaganja.ljuta_paprika":1,"vaganja.slatka_paprika":1,"vaganja.bijeli_luk":1,}))
    #print(lista)
    for k in lista:
        lista_vaganja = (k['vaganja'])
    
    cell_data = []
    itterator = 1
    for q in lista_vaganja:
        
        cell_data.append(
            [str(itterator),
            str(round(q['sol'],1)), 
            str(round(q['papar'],1)), 
            str(round(q['ljuta_paprika'],1)),
            str(round(q['slatka_paprika'],1)),
            str(round(q['bijeli_luk'],1)), 
            str(round(q['tezina_mesa'],1)),
            str(round(q['tezina_mesa']*q['sol']/100,1)),
            str(round(q['tezina_mesa']*q['papar']/100,1)),
            str(round(q['tezina_mesa']*q['ljuta_paprika']/100,1)),
            str(round(q['tezina_mesa']*q['slatka_paprika']/100,1)),
            str(round(q['tezina_mesa']*q['bijeli_luk']/100),1)])
        itterator = itterator + 1
    sum_sol = 0
    sum_papar = 0
    sum_ljuta_p = 0
    sum_slatka_p = 0
    sum_bijeli_luk = 0
    sum_meso = 0
    for i in range(len(cell_data)):
        sum_meso = sum_meso + float(cell_data[i][6])
        sum_sol = sum_sol + float(cell_data[i][7])
        sum_papar = sum_papar + float(cell_data[i][8])
        sum_ljuta_p = sum_ljuta_p + float(cell_data[i][9])
        sum_slatka_p = sum_slatka_p + float(cell_data[i][10])
        sum_bijeli_luk = sum_bijeli_luk + float(cell_data[i][11])
    ukupno_meso = sum_meso+sum_sol+sum_papar+sum_ljuta_p+sum_slatka_p+sum_bijeli_luk 
    #print(cell_data)
    pdf = FPDF('L', 'mm', 'A4')
    pdf.add_page()
    pdf.set_font('helvetica', '',12)
    #pdf.cell(40,10, f'Hello, world')

    pdf.image("static/img/kolinje_logo.png", x=10, y=10, h=30, w=30)

    pdf.cell(210)
    pdf.cell(0,10, f'ID: {k["_id"]}', ln=True)
    pdf.cell(210)
    pdf.cell(0,10, f'Naziv kolinja: {k["naziv_kolinja"]}', ln=True)

    
    pdf.set_font('helvetica', 'B', 16)
    pdf.cell(0,20, f'Vagarski list', 0, 1, 'C')


    header=(
        ('#', 'Sol (%)', 'Papar (%)', 'Ljuta paprika (%)', 'Slatka paprika (%)', 'Bijeli luk (%)', 'Meso (g)' ,'Sol (g)', 'Papar (g)', 'Ljuta paprika (g)', 'Slatka paprika (g)', 'Bijeli luk (g)')
    )
   

    #### TABLICA
    pdf.set_font('helvetica', 'B', 10)
    line_height = pdf.font_size * 3
    col_width = pdf.epw / 12
    for row in header:
        pdf.multi_cell(col_width, line_height, row, border = 1, align='C', new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size)
    pdf.ln(line_height)

    pdf.set_font('helvetica', '', 10)
    line_height = pdf.font_size * 2.5
    for row in cell_data:
        for datum in row: 
            pdf.multi_cell(col_width, line_height, datum, border = 1, align='C', new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size)
        pdf.ln(line_height)

    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(col_width*5, line_height, f'')
    pdf.cell(col_width, line_height, f'Ukupno (g):', 1, 0, 'C')
    pdf.cell(col_width, line_height, f'{round(sum_meso,1)}', 1, 0, 'C')
    pdf.cell(col_width, line_height, f'{round(sum_sol,1)}', 1, 0, 'C')
    pdf.cell(col_width, line_height, f'{round(sum_papar,1)}', 1, 0, 'C')
    pdf.cell(col_width, line_height, f'{round(sum_ljuta_p,1)}', 1, 0, 'C')
    pdf.cell(col_width, line_height, f'{round(sum_slatka_p,1)}', 1, 0, 'C')
    pdf.cell(col_width, line_height, f'{round(sum_bijeli_luk,1)}', 1, 0, 'C')
    pdf.ln(line_height)
    pdf.cell(col_width*9, line_height, f'')
    pdf.cell(col_width*2, line_height, f'SVEUKUPNO (g):',1,0,'L')
    pdf.cell(col_width, line_height, f'{round(ukupno_meso,1)}',1,0,'C')

    return pdf.output(f'static/pdf_temp/kolinje.pdf', 'F')
    