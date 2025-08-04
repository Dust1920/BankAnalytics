import pdfplumber
import os
import general_info as ginfo
import re


def state_bank(filepath):
    """
        Leer un estado de cuenta.
    :param filepath:
    :return:
    """
    pdf = pdfplumber.open(filepath)
    return pdf


def read_pdf(select_year, select_month, select_bank, select_card):
    """
        Leer PDF (Estado de Cuenta) para procesamiento.
    :param select_year:
    :param select_month:
    :param select_bank:
    :param select_card:
    :return:
    """
    folder = os.path.join("Banks", select_bank, select_card)  # Folder
    files = os.listdir(folder)  # Estados de Cuentas
    selected_file = ""
    for f in files:
        text = f.split(".")[0].split(" ")[1]
        if text == f"{select_month}{str(select_year)[2:]}":
            selected_file = os.path.join(folder, f)
    pdf = pdfplumber.open(selected_file)
    return pdf


def read_page(pdf, page):
    """
        Leer pagina de un PDF.
    :param pdf:
    :param page:
    :return:
    """
    page = pdf.pages[page]
    content = page.extract_text(x_tolerance=3, y_tolerance=3, x_density=7.25, y_density=13)
    text = content.split("\n")
    return text


def read_pages(pdf, interval):
    """
        Leer un conjunto de paginas de un PDF.
    :param pdf:
    :param interval:
    :return:
    """
    text = []
    for page in interval:
        text += read_page(pdf, page)
    return text


def find_bak(sample):
    """
        Detectar Bancos o Instituciones Financieras
    :param sample:
    :return:
    """
    all_baks = ginfo.BANKS + ginfo.FINTECH
    stop = 0
    for ab in all_baks:
        for lines in sample:
            s = re.search(ab, lines)
            if s is not None:
                stop = 1
                break
        if stop:
            break
    return ab

