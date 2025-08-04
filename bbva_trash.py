


"""
    Modelo 0: Nuevo Logo, Introducción, Clásica
    Modelo 1: Nuevo Logo, No Introducción, Universal
    Modelo 2: Nuevo Logo, No Introducción, Universal
    Modelo 3: Nuevo Logo, No Introducción, Clásica
    Modelo 4: Nuevo Logo, No Introducción, Universal
"""

# print(KEYS)


def select_model(pdf):
    """
        Seleccionar modelo para leer el estado de cuenta.
    :param pdf:
    :return:
    """
    page0 = read_page(pdf, 0)
    value = page0[0].split(" ")[0]
    if value == "Estado":
        msel = 0
        return msel
    if value in ["TE", "Descubre"]:
        msel = 1
        return msel
    if value == "Página":
        msel = 2
        return msel
    else:
        msel = 3
        return msel


def initial_data(year, month):
    set_model = read_pdf(year, month)
    ml = select_model(set_model)
    ml_page = {
        0: 0,
        1: 1,
        2: 1,
        3: 1
    }
    if ml == 0:
        # print("Modelo Clásico")
        i_data = read_page(set_model, 0)
        # Datos Crudos Iniciales
        card_name = i_data[1]
        person_name = i_data[5]
        cort_date = i_data[21]
        payment_date = i_data[22]
        credit_limit = i_data[23]
        clos_bal = i_data[46]
        payment = i_data[24]

        # print(card_name, person_name, cort_date, payment_date, credit_limit, payment)
        INITIAL_DATA["Nombre Tarjeta"] = card_name  # Nombre de tarjeta
        INITIAL_DATA["Nombre"] = person_name  # Nombre

        cort_date = cort_date.split(" ")[-1]
        INITIAL_DATA["Fecha Corte"] = cort_date

        payment_date = payment_date.split(" ")[-1]
        INITIAL_DATA["Fecha Pago"] = payment_date

        cred_limit_pattern = r"\.\d\d"
        cred_limit_pos = re.search(cred_limit_pattern, credit_limit).span()[1]
        cred_limit_f = credit_limit[:cred_limit_pos].split(" ")[-1]
        credit_limit = Info.money_format(cred_limit_f)
        INITIAL_DATA["Limite Credito"] = credit_limit

        clos_bal_pos = re.search(cred_limit_pattern, clos_bal).span()[1]
        clos_bal_f = clos_bal[:clos_bal_pos].split(" ")[-1]
        clos_bal = Info.money_format(clos_bal_f)
        INITIAL_DATA["Saldo Corte"] = clos_bal

        payment = payment.split(" ")[-1]
        INITIAL_DATA["Pago No Intereses"] = Info.money_format(payment)
    else:
        i_data = read_page(set_model, 1)
        if ml == 3:
            # print("Modelo Clásico")
            # Datos Crudos Iniciales
            card_name = i_data[1]
            person_name = i_data[5]
            cort_date = i_data[21]
            payment_date = i_data[22]
            credit_limit = i_data[23]
            clos_bal = i_data[46]
            payment = i_data[24]

            # print(card_name, person_name, cort_date, payment_date, credit_limit, payment)
            INITIAL_DATA["Nombre Tarjeta"] = card_name  # Nombre de tarjeta
            INITIAL_DATA["Nombre"] = person_name  # Nombre

            cort_date = cort_date.split(" ")[-1]
            INITIAL_DATA["Fecha Corte"] = cort_date

            payment_date = payment_date.split(" ")[-1]
            INITIAL_DATA["Fecha Pago"] = payment_date

            cred_limit_pattern = r"\.\d\d"
            cred_limit_pos = re.search(cred_limit_pattern, credit_limit).span()[1]
            cred_limit_f = credit_limit[:cred_limit_pos].split(" ")[-1]
            credit_limit = Info.money_format(cred_limit_f)
            INITIAL_DATA["Limite Credito"] = credit_limit

            clos_bal_pos = re.search(cred_limit_pattern, clos_bal).span()[1]
            clos_bal_f = clos_bal[:clos_bal_pos].split(" ")[-1]
            clos_bal = Info.money_format(clos_bal_f)
            INITIAL_DATA["Saldo Corte"] = clos_bal

            payment = payment.split(" ")[-1]
            INITIAL_DATA["Pago No Intereses"] = Info.money_format(payment)
        else:
            # print("Modelo Universal")
            name = i_data[2]
            card_name_ifm = i_data[9]  # Nombre Tarjeta / Pago para no generar intereses
            cort_date = i_data[5]
            payment_date = i_data[8]
            limit_credit = i_data[47]
            clos_bal_pin = "Saldo deudor total"
            bal_pin = 45
            while True:
                s = re.search(clos_bal_pin, i_data[bal_pin])
                if s is not None:
                    break
                bal_pin += 1
                if bal_pin == len(i_data):
                    break
            clos_bal = i_data[bal_pin]
            # print(clos_bal)

            INITIAL_DATA["Nombre"] = name

            pattern_name = "Pago"
            name_pos = re.search(pattern_name, card_name_ifm).span()[0]
            name_block = card_name_ifm[:name_pos]
            INITIAL_DATA["Nombre Tarjeta"] = name_block

            INITIAL_DATA["Nombre"] = name

            cort_date = cort_date.split(" ")[-1]
            INITIAL_DATA["Fecha Corte"] = cort_date

            payment_date = payment_date.split(" ")[-1]
            INITIAL_DATA["Fecha Pago"] = payment_date

            limit_credit = limit_credit.split(" ")[-1]
            limit_credit_f = Info.money_format(limit_credit[1:])
            INITIAL_DATA["Limite Credito"] = limit_credit_f

            clos_bal = clos_bal.split(" ")[-1]
            clos_bal_f = Info.money_format(clos_bal[1:])
            INITIAL_DATA["Saldo Corte"] = clos_bal_f

            payment = card_name_ifm.split(" ")[-1]
            payment_f = Info.money_format(payment[1:])
            INITIAL_DATA["Pago No Intereses"] = payment_f
    return INITIAL_DATA


"""
for y in [2023, 2024, 2025]:
    for m in Info.MONTHS:
        try:
            initial = initial_data(y, m)
            print(initial)
        except:
            print(y, m)
"""


def clean_analytics(year, month):
    set_model = read_pdf(year, month)
    ml = select_model(set_model)
    print(ml)
    page = []

    END_PAGE = "BBVA MEXICO, S.A., INSTITUCION DE BANCA MULTIPLE, GRUPO FINANCIERO BBVA MEXICO"

    if ml == 0:
        i_body = 1
    else:
        i_body = 2
        if ml == 3:
            n_pages = len(set_model.pages)
            for pag in range(i_body, n_pages):
                page += read_page(set_model, pag)
            for l, line in enumerate(page):
                s = re.search(END_PAGE, line)
                if s is not None:
                    del page[l:l+3]
            return page


clean_analytics(2024, "Enero")
