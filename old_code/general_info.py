import os


def money_format(value):
    return float(value.replace(",", "")[1:])


test_folder = os.path.join("../Banks", "BBVA", "Credito")
files = os.listdir(test_folder)


