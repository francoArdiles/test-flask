import re


def validate_rut(dni: str):
    """
     Esta función recibe un dni y evalúa si es válido o no, bajo el estándar
     chileno.

     Args:
         dni (str): RUT con dígito verificador
     """
    if dni == 'null' or dni is None or len(dni) < 3:
        raise ValueError('RUT inválido')

    dni = re.sub(r"[^\w ]", "", dni).upper()
    aux = dni[:-1]
    dv = dni[-1]
    par = zip(str(aux)[::-1],
                [i for i in range(2, 8)] * (1 + int(len(dni) / 6)))
    s = sum(int(a) * int(b) for a, b in par)
    res = 11 - abs(s - int(s / 11) * 11)

    if str(res) == dv or (dv == "K" and res == 10) or (dv == '0' and res == 11):
        return
    else:
        raise ValueError('DNI inválido')
