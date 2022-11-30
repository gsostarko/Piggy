from fpdf import FPDF 


def pdf_kolinja():

    pdf = FPDF('L', 'mm', 'A4')
    pdf.add_page()
    pdf.set_font('helvetica', '',12)
    #pdf.cell(40,10, f'Hello, world')

    pdf.image("static/img/kolinje_logo.png", x=10, y=10, h=30, w=30)

    pdf.cell(210)
    pdf.cell(0,10, f'ID: 6385d7b731e7653a472e21f2', ln=True)
    pdf.cell(210)
    pdf.cell(0,10, f'Naziv kolinja: Demo', ln=True)

    
    pdf.set_font('helvetica', 'B', 16)
    pdf.cell(0,20, f'Zapis kolinja', 0, 1, 'C')


    header=(
        ('#', 'Sol (%)', 'Papar (%)', 'Ljuta paprika (%)', 'Slatka paprika (%)', 'Bijeli luk (%)', 'Meso (g)' ,'Sol (g)', 'Papar (g)', 'Ljuta paprika (g)', 'Slatka paprika (g)', 'Bijeli luk (g)', 'Ukupno smjese (g)'),
        ('1', '1.0', '1.0', '1.0', '1.0', '1.0', '1000.0' ,'10.0', '10.0', '10.0', '10.0', '10.0', '1050.0'),
        ('2', '1.0', '1.0', '1.0', '1.0', '1.0', '500.0' ,'5.0', '5.0', '5.0', '5.0', '5.0', '525.0'),
        ('3', '1.0', '1.0', '1.0', '1.0', '1.0', '200.0' ,'2.0', '2.0', '2.0', '2.0', '2.0', '210.0'),
        ('4', '1.0', '1.0', '1.0', '1.0', '1.0', '300.0' ,'3.0', '3.0', '3.0', '3.0', '3.0', '315.0'),
        ('5', '1.0', '1.0', '1.0', '1.0', '1.0', '700.0' ,'7.0', '7.0', '7.0', '7.0', '7.0', '735.0'),
        ('6', '1.0', '1.0', '1.0', '1.0', '1.0', '800.0' ,'8.0', '8.0', '8.0', '8.0', '8.0', '840.0'),
        ('7', '1.0', '1.0', '1.0', '1.0', '1.0', '350.0' ,'3.5', '3.5', '3.5', '3.5', '3.5', '367.5'),
    )
   

    #### TABLICA
    pdf.set_font('helvetica', 'B', 10)
    line_height = pdf.font_size * 3
    col_width = pdf.epw / 13
    for row in header:
        for datum in row: 
            pdf.multi_cell(col_width, line_height, datum, border = 1, align='C', new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size)
        pdf.ln(line_height)

    

    return pdf.output('static/pdf_temp/kolinje.pdf', 'F')
    