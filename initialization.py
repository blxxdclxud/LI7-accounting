from json import load, dump

var_data = None


def read_file():
    with open("/home/sender/LI7-accounting/"  + "variables.json", 'rt') as var_file:
        global var_data
        var_data = load(var_file)


def write_file(obj):
    with open("/home/sender/LI7-accounting/"  + "variables.json", 'wt') as var_file:
        dump(obj, var_file)
    read_file()
