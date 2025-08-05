import os
import numpy as np


def select_random_state_bank(input_folder="Banks", **kwargs):
    """
        Selecciona un estado de cuenta aleatorio para pruebas
    :param input_folder:
    :return:
    """
    fbak = kwargs.get("force_bak", None)
    np.random.seed(42)
    baks = os.listdir(input_folder)
    select_bak = np.random.choice(baks)
    while select_bak == ".gitignore":
        select_bak = np.random.choice(baks)
    select_bak = str(select_bak)
    if fbak is not None:
        select_bak = fbak
    state_types = os.path.join(input_folder, select_bak)
    st_types = os.listdir(state_types)
    n_types = len(st_types)
    select_type = 0 if np.random.random() < 1/n_types else 1
    file_path = os.path.join(state_types, st_types[select_type])
    files = os.listdir(file_path)
    file = np.random.choice(files)
    test_path = os.path.join(file_path, file)
    return test_path

# Select a file
file = select_random_state_bank(force_bak="BBVA")


print(file)
