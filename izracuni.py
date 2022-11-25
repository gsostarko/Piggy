class Izracuni():
   
    def IzracunVaganja(sol,papar,ljuta_paprika,slatka_paprika,bijeli_luk,meso):
        rezultat={
        'preracunata_sol' : round(float(meso) * float(sol) /100,1),
        'preracunati_papar' : round(float(meso) * float(papar) /100,1),
        'preracunata_lj_paprika' : round(float(meso) * float(ljuta_paprika) /100,1),
        'preracunata_s_paprika' : round(float(meso) * float(slatka_paprika) /100,1),
        'preracunati_luk' : round(float(meso) * float(bijeli_luk) /100,1),
        }

        return rezultat
        

        