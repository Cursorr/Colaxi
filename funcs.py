import json
import re


def config():
    with open("config.json", "r") as f:
        conf = json.load(f)
        return conf


def my_format(string, **kwargs):
    var = lambda variables: lambda match: str(variables[match[1]]) if match[1] in variables else match[0]
    return re.sub(r"{(\w+)}", var(kwargs), string)


def convert(time):
    pos = ["s", "m", "h", "d"]
    time_dic = {"s":1, "m": 60, "h": 3600, "d": 3600 *24}
    i = {"s": "Secondes", "m": "Minutes", "h": "Heures", "d": "Jours"}
    unit = time[-1]
    if unit not in pos:
        return -1
    try:
        val = int(time[:-1])

    except:
        return -2

    if val == 1:
        return val * time_dic[unit], i[unit][:-1]
    else:
        return val * time_dic[unit], i[unit]