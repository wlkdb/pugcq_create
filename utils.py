# *encoding=utf-8
import os
import scipy.stats as stats
import pandas as pd


def cal_cc(list1, list2, abs=True):
    srocc, pvalue = stats.spearmanr(list1, list2)
    plcc, pvalue = stats.pearsonr(list1, list2)
    if abs & (srocc < 0):
        srocc = -srocc
        plcc = -plcc
    return srocc, plcc


def get_file_name(file_path, extension=True):
    file_name = os.path.split(str(file_path))[-1]
    if not extension:
        file_name = os.path.splitext(file_name)[0]
    return file_name


def check_dir(dir_path):
    path_list = dir_path.split("/")
    now_path = ""
    for path in path_list:
        now_path += path + "/"
        if not os.path.exists(now_path):
            os.makedirs(now_path)


def get_file_list(input_path, sub=".xls"):
    if os.path.isdir(input_path):
        file_list = []
        for root, dirs, files in os.walk(input_path):
            print("root = ", root)
            for file in files:
                file_list.append(os.path.join(root, file))
    else:
        file_list = [input_path]
    if sub:
        file_list = [f for f in file_list if f.find(sub) >= 0]
    return file_list


def read_sheet(file, sheet_name=0, index_col=None, header=0):
    extension = os.path.splitext(file)[-1]
    if extension == ".csv":
        if index_col is None:
            index_col = False
        data = pd.read_csv(file, index_col=index_col, header=header, encoding="gbk")
    else:
        data = pd.read_excel(file, index_col=index_col, sheet_name=sheet_name, header=header)
    return data
