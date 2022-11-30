from fpdf import FPDF 


def pdf_kolinja():
    WIDTH = 210
    HEIGHT = 297

    pdf = FPDF()
    pdf.add_page('L')
    pdf.set_font('Arial')
    #pdf.cell(40,10, f'Hello, world')

    pdf.image("static/img/kolinje_logo.png", x=10, y=10, h=30, w=30)

    return pdf.output('static/pdf_temp/kolinje.pdf', 'F')
    