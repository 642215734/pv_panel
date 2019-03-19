# -*- coding: UTF-8 -*-
# 算的是上海的数据
# 2019.3.14更新，利用sql导出数据计算
# 组件层面的检测的数据，遍历每一个mpp
# # # # 1.导入data_shanghai_guanduanqi里t与组件的对照表，通过组件数据的分组;
# # 3.每一个逆变器的文件；
# 2.利用相关信息文件夹里的每一个mppt对应的数个组件，进行离群点检测，输出结果。
# C:/Users/lenovo/Desktop/solar/optimizer_data/optimizer_201901_07.csv


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager
from sklearn import svm
from sklearn.neighbors import LocalOutlierFactor
import pandas as pd
import os
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression
from sklearn.externals import joblib
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor, GradientBoostingRegressor
import re
from sklearn.covariance import EllipticEnvelope

mppt1 = [1, 2, 3]
mppt2 = [5, 6, 7]
mppt3 = [9, 10, 11, 12]
path = '../相关信息/上海西门子.xlsx'
table = pd.read_excel(path)

# 输入参数关断器，返回其属于的组串


def find_substring_num(dc_devId):
    substring_num = table[table['dc_devId'] == int(dc_devId)]['substring_num']
    return substring_num


def find_string_inverter_name(dc_devId):
    substring_num = table[table['dc_devId'] == int(dc_devId)]['string_inverter_name']
    return substring_num


# 解析文件名，得到逆变器，关断器，日期
def parse_file_name(file_name):
    date = re.findall('(.{4}-.{2}-.{2})', file_name)[0]
    interver_index = re.findall(' ..... ', file_name)[0]
    shutoff_index = re.findall('[0-9]{12}', file_name)[0]
    return date, interver_index, shutoff_index


# 分析数据
# 1.outlier
def calcu(mppt):
    clf = IsolationForest(behaviour='new',
                          random_state=3, contamination=0.03)

    mppt_test = mppt.iloc[:,0:70]
    try:
        clf.fit(mppt_test)
    except ValueError:
        return None

    y_pred = clf.predict(mppt_test)
    output = mppt[y_pred == -1]
    output=output[['日期', '逆变器', '关断器', '子串号', '组件']]
    print(output)
    print('======')
    return output


# 2.regressor
def calcu2(mppt):
    clf = EllipticEnvelope(contamination=0.01)
    my_mppt1 = mppt.iloc[:, 0:106]
    clf.fit(my_mppt1)
    y_pred = clf.predict(my_mppt1)
    # y_pred = clf.predict(my_mppt1)
    output = mppt[y_pred == -1].iloc[:, 108]
    return output


# 3.formula
def calcu3(mppt):
    mppt_test = mppt.iloc[:,0:70]
    try:
        mppt_test['mean']=mppt_test.mean(axis=1)
    except ValueError:
        return None
    mean_value = mppt_test['mean'].mean()
    a = mppt_test['mean'] < mean_value * 0.72
    output = mppt[a]

    output=output[['日期', '逆变器', '关断器', '子串号', '组件']]
    print(output)
    print('======')
    return output


def parse_file(file_name='C:/Users/lenovo/Desktop/solar/optimizer_data/optimizer_201901_07.csv'):
    output_all = pd.DataFrame()
    df = pd.read_csv(file_name)
    if df.shape[0]<20:
        return pd.DataFrame()
    # 时间列表
    date_unique = df['REV1'].unique()
    opt_unique = df['OPT_NO'].unique()
    channel_unique = df['CHANNEL'].unique()
    for date in date_unique:
        datamppt1 = pd.DataFrame()
        for opt in opt_unique:
            for channel in channel_unique:
                zujian = df[(df[u'REV1'] == date) & (df[u'OPT_NO'] == opt) & (df[u'CHANNEL'] == channel)]
                substring_num = find_substring_num(opt)
                string_inverter_name = find_string_inverter_name(opt)
                new = zujian['INPUT_POWER']
                new = new.reset_index(drop=True)
                if len(list(string_inverter_name))==0:
                    continue
                else:
                    new['逆变器'] = list(string_inverter_name)[0]
                new['日期'] = date
                new['关断器'] = opt
                if len(list(substring_num)) > 0:
                    new['子串号'] = list(substring_num)[0]
                new['组件'] = channel
                # datamppt1=pd.concat([datamppt1,new],axis=1,sort=False)
                datamppt1 = datamppt1.append(new)

        output = calcu3(datamppt1)
        if output.shape[0]<50:

            output_all=pd.concat([output_all,output])
    return output_all


def to_xls(output_all, file_name):
    if not os.path.exists(file_name):
        output_all.to_excel(file_name)


def walk(rootdir):
    g = os.walk(rootdir)
    for path, dir_list, file_list in g:
        return path, file_list


if __name__ == '__main__':
    path,file_names=walk('..\\optimizer_data')
    for i, file in enumerate(file_names):
        file=''.join([path,'\\',file])
        output_all=parse_file(file)
        file_name=''.join(['..\\output_3_13\\output',str(i),'.xls'])
        to_xls(output_all,file_name)


