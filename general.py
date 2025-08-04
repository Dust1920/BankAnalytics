import re


def rename_dict(old_names, new_names, dic: dict):
    if len(old_names) != len(new_names):
        return dic
    for k in range(len(old_names)):
        dic[old_names[k]] = dic[new_names[k]]
        del dic[old_names[k]]
    return dic


def locate_codes(code, content):
    """

    :param code:
    :param content:
    :return:
    """
    # bank = kwargs.get("bank", None)
    code_index = []
    for k, line in enumerate(content):
        s = re.search(code, line.upper())
        if s is not None:
            code_index.append(k)
    return code_index
