"""
    Detectar si el PDF es el nuevo Estado de Cuenta Universal
"""
import manager
import re
import general_info as ginfo
import general as g
import os
import pandas as pd

universal_pattern = "TU PAGO REQUERIDO ESTE PERIODO"


def is_universal(select_path):
    """
    Detectar si el estado de cuenta corresponde al formato universal.
    :param select_path:
    :return:
    """

    state = manager.state_bank(select_path)
    test_pages = manager.read_pages(state, [0, 1])
    universal = 0
    for line in test_pages:
        s = re.search(universal_pattern, line.upper())
        if s is not None:
            universal = 1
            break
    return universal


def first_clean(pdf):
    """
        Primera Limpieza. Recortar
    :param pdf:
    :return:
    """
    ctent = manager.read_pages(pdf, range(len(pdf.pages)))
    limits = []
    for k, c in enumerate(ctent):
        g = re.search(universal_pattern, c.upper())
        h = re.search("TOTAL ABONOS", c.upper())
        if g is not None or h is not None:
            limits.append(k)
            if h is not None:
                break
    clean_content = ctent[limits[0]:limits[1]]
    return clean_content


def initial_data(path):
    """
        Información Inicial
    :param path:
    :return:
    """
    # bank = kwargs.get("bank", None)
    initialdata = {"Nombre Tarjeta": None,
                   "Nombre": None,
                   "Fecha Corte": None,
                   "Fecha Pago": None,
                   "Limite Credito": None,
                   "Saldo Corte": None,
                   "Pago No Intereses": None}

    initial_keys = {"Fecha de corte": 0,
                    "Fecha límite de pago": 0,
                    "Pago para no generar intereses": 0,
                    "Saldo deudor total": 0,
                    "Límite de crédito": 0}
    
    pdf_test = manager.state_bank(path)
    content = manager.read_pages(pdf_test, [0, 1])
    k = 0
    for k, c in enumerate(content):
        g = re.search(universal_pattern, c.upper())
        if g is not None:
            break
    initial_content = content[k+1:]

    for key in initial_keys.keys():
        for k, line in enumerate(initial_content):
            u = re.search(key, line)
            if u is not None:
                initial_keys[key] = k
    
    # Nombre de Tarjeta
    card_pay_name = initial_content[initial_keys["Pago para no generar intereses"]]
    card_name_loc = card_pay_name.index("Pago para no generar intereses")
    initialdata['Nombre Tarjeta'] = card_pay_name[:card_name_loc]
    
    # Nombre
    initialdata['Nombre'] = initial_content[0]
    
    # Fecha para no pagar intereses
    payment_date = card_pay_name.split(" ")[-1]
    initialdata['Fecha Pago'] = ginfo.money_format(payment_date)
    
    # Fecha de Corte
    cort_day = initial_content[initial_keys["Fecha de corte"]]
    initialdata['Fecha Corte'] = cort_day.split(" ")[-1]
    
    # Limite de Crédito
    credit_limit = initial_content[initial_keys["Límite de crédito"]].split(" ")[-1]
    initialdata['Limite Credito'] = ginfo.money_format(credit_limit)
    
    # Saldo de Corte
    balance = initial_content[initial_keys["Saldo deudor total"]].split(" ")[-1]
    initialdata['Saldo Corte'] = ginfo.money_format(balance)
    
    # Pago para no generar intereses
    payment = initial_content[initial_keys["Pago para no generar intereses"]].split(" ")[-1]
    initialdata['Pago No Intereses'] = ginfo.money_format(payment)
    return initialdata


def config_state_bank(path):
    """
        Configuración Previa Extracción de Datos
    :param path:
    :return:
    """
    pdf = manager.state_bank(path)
    content = first_clean(pdf)  # Primera Limpieza de datos

    end_first_page = g.locate_codes("PROGRAMA DE BENEFICIOS DE LA TARJETA", content)
    bank_state_not_first_page = content[end_first_page[0]:]
    # print(file)
    # print(BANK_STATE_NOT_FIRST_PAGE)

    sections = []
    for k, line in enumerate(bank_state_not_first_page):
        if not all(char.isalpha() or char.isspace() for char in line):
            continue
        if line == "BBVA BBVA":  # Fallo de Generación BBVA
            continue
        if line == line.upper():
            sections.append(k)

    state_sections = {bank_state_not_first_page[s]: s for s in sections}
    sections.append(len(bank_state_not_first_page))

    # print(state_sections)
    # print(sections)
    # print(BANK_STATE_NOT_FIRST_PAGE[sections[0]:sections[1]])

    bank_state_blocks = {cat: bank_state_not_first_page[sections[t]:sections[t + 1]]
                         for t, cat in enumerate(state_sections.keys())}
    return state_sections, bank_state_blocks


# PROGRAMA DE BENEFICIOS DE LA TARJETA
def benefits_bank(content_block):
    block = content_block["PROGRAMA DE BENEFICIOS DE LA TARJETA"]
    block_title = block[0]
    block_subtitle = block[1]
    # BBVA
    # if bank == "BBVA"
    points = pd.DataFrame(index=["Saldo Inicial", "Puntos Generados", "Puntos Utilizados", "Puntos Vencidos",
                                 "Saldo Final"], columns=["Puntos"])
    for e in block:
        e_comma = e.replace(",", "")
        if all(n.isdigit() or n.isspace() for n in e_comma):
            points.loc[:, "Puntos"] = e_comma.split(" ")
            break
    return points


# if "PROGRAMA DE BENEFICIOS DE LA TARJETA" in state_sections.keys():
def bank_rates(content_block):
    block = content_block['SALDO SOBRE EL QUE SE CALCULARON LOS INTERESES DEL PERIODO']
    # block_title = block[0]
    # index_title = "Tipo de intereses (Calculados con las metodologías pactadas en el contrato de adhesión)"
    rates = pd.DataFrame(index=["Ordinarios", "Moratorios", "De saldo revolvente a tasa preferencial",
                                "De compras y cargos diferidos a meses con intereses",
                                "Por disposiciones de efectivo",
                                "Por disposiciones de efectivo de otras líneas de crédito"],
                         columns=["Saldo base", "Dias Periodo", "Tasa de interés anual", "Monto"])
    for v in rates.index:
        # print(v)
        for line, t in enumerate(block):
            lc = re.search(v, t)
            if lc is not None:
                raw_data = block[line].replace(v, "")
                data = raw_data[1:].split(" ")
                rates.loc[v, :] = data
                break
    return rates


# if 'SALDO SOBRE EL QUE SE CALCULARON LOS INTERESES DEL PERIODO' in state_sections.keys():
def dist_payments(content_block):
    block = content_block['DISTRIBUCIÓN DE TU ÚLTIMO PAGO']
    # block_title = block[0]
    dist_payment = pd.DataFrame(index=["Pagos y abonos", "Gasto", "Meses sin Intereses", "Meses con Intereses",
                                       "Intereses y Comisiones", "IVA", "Saldo a favor"], columns=["Cantidad"])
    for t in block:
        text = t.replace("+", "").replace("-", "").replace("=", "").replace(",", "").replace("$", "")
        if all(u.isdigit() or u.isspace() or u == "." for u in text):
            ammounts = text.split(" ")
            text = [s for s in ammounts if s != ""]
            dist_payment.loc[:, "Cantidad"] = text
    return dist_payment

# if 'DISTRIBUCIÓN DE TU ÚLTIMO PAGO' in state_sections.keys():


#


def expenses(content_block):
    block = content_block['DESGLOSE DE MOVIMIENTOS']
    # print(block)
    payment_index = g.locate_codes(r"TARJETA (t|A|a|T)", block)
    print(payment_index)
    payment_cats = set([block[k] for k in payment_index])
    payment_index.append(len(block))
    print(payment_cats)
    payment_moves = {pc: [] for pc in payment_cats}
    # print("PAY", payment_moves)
    for k in range(len(payment_index) - 1):
        q = block[payment_index[k]: payment_index[k + 1]]
        payment_moves[q[0]] += q
    pay_mov_keys = list(payment_moves.keys())
    # print("A", pay_mov_keys)
    clasf_cards = pd.DataFrame(index=range(len(pay_mov_keys)), columns=["Modalidad", "Tipo", "Numero"])
    mods = ["MESES SIN INTERESES", "NO A MESES"]
    for m in mods:
        for k, v in enumerate(pay_mov_keys):
            if re.search(m, v):
                loc_type = v.index("Tarjeta")
                card = v[loc_type:]
                card = card.split(" ")
                clasf_cards.loc[k] = [m, card[1][:-1], card[-1]]

    content = {"-".join(clasf_cards.loc[codes]): [] for codes in clasf_cards.index}

    for ck, con_keys in enumerate(content.keys()):
        cons = con_keys.split("-")
        for pay_keys in payment_moves.keys():
            if all(re.search(c, pay_keys) for c in cons):
                payment_moves[con_keys] = payment_moves[pay_keys]
                del payment_moves[pay_keys]
                break
    msi_pattern = r"\d{2}-\w{3}-\d{2}"
    exp_pattern = r"\d{2}-\w{3}-\d{2} \d{2}-\w{3}-\d{2}"
    raw_data = {}
    for key in payment_moves.keys():
        data = []
        for line in payment_moves[key]:
            pattern = msi_pattern if re.search(r"SIN INTERESES", key) else exp_pattern
            if re.search(pattern, line):
                data.append(line)
        raw_data[key] = data
    msi_df = pd.DataFrame(columns=["Tipo Tarjeta", "Número Tarjeta", "Fecha", "Descripción", "Monto",
                                   "Saldo Pendiente", "Pago requerido", "Pago", "Tasa Interés"])
    exp_df = pd.DataFrame(columns=["Tipo Tarjeta", "Número Tarjeta", "Fecha Operación", "Fecha Cargo",
                                   "Descripción", "Monto"])
    raw_keys = list(raw_data.keys())
    for rwk in raw_keys:
        card_mod, card_type, card_number = rwk.split("-")
        content = raw_data[rwk]
        if re.search("MESES SIN INTERESES", rwk):
            # print("MESES SIN INTERESES")
            df = msi_df.copy()
            for s, line in enumerate(content):
                desc_start = re.search(msi_pattern, line).span()[1]
                desc_end = line.index("$")
                description = line[desc_start:desc_end]
                date = line[:desc_start]
                stats = line[desc_end:].replace(",", "")
                pays_steps_pattern = "\d{1,2} de \d{1,2}"
                pays_steps = re.search(pays_steps_pattern, stats).span()
                # try:
                #     print("A", stats)
                #     pays_steps = re.search(pays_steps_pattern, stats).span()
                # except AttributeError as e:
                #     print("B", stats)
                #     pays_steps = (29, 37)
                steps = stats[pays_steps[0]:pays_steps[1]]
                amounts = stats[:pays_steps[0]].split()
                rates = stats[pays_steps[1]:]
                df.loc[s] = [card_type, card_number, date, description] + amounts + [steps, rates]
            msi_df = pd.concat([msi_df, df], ignore_index=True)
        else:
            # print("PAGO A MESES")
            df = exp_df.copy()
            for s, line in enumerate(content):
                desc_start = re.search(exp_pattern, line).span()[1]
                desc_end = line.index("$")
                description = line[desc_start:desc_end]
                ammount = line[desc_end:]
                dates = line.split(" ")[:2]
                df.loc[s, :] = [card_type, card_number] + dates + [description] + [ammount]
            exp_df = pd.concat([exp_df, df], ignore_index=True)
    return exp_df, msi_df


universal_tests = pd.read_csv("UniversalState.csv")
folder_test = "Banks\\BBVA\\Credito"

for select_file in range(universal_tests.shape[0]):
    file = os.path.join(folder_test, universal_tests.loc[select_file, "filename"])
    state_sections, bank_state_blocks = config_state_bank(file)
    print(state_sections)
    if 'DESGLOSE DE MOVIMIENTOS' in state_sections.keys():
        print(universal_tests.loc[select_file, "filename"])
        exp_df, msi_df = expenses(bank_state_blocks)
        msi_df.to_excel(f"{select_file}_MSI.xlsx")
        exp_df.to_excel(f"{select_file}_EXP.xlsx")
