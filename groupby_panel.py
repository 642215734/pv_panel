# 对outputshanghai的结果进行归类，按照出现次数排序



import os
import numpy as np
import pandas as pd
import re
np.set_printoptions(suppress=True)

def walk(rootdir):
    g = os.walk(rootdir)
    for path, dir_list, file_list in g:
        return path,file_list
path, file_names = walk('..\\output_shanghai')
for i, file in enumerate(file_names):
    num=re.findall('[0-9]{1,2}',file)[0]
    file = ''.join([path, '\\', file])
    file_name=''.join(['..\\new\\grouped'+num+'.xls'])

    if file.endswith('csv'):
        df=pd.read_csv(file)
        try:
            grouped=df.groupby('关断器').count()

            grouped=grouped.sort_values(by='日期',ascending=False)
            df=df.drop(['Unnamed: 0'],axis=1)
            grouped=grouped.iloc[:,0:1]
            df=df.set_index(['关断器'])
            result=pd.merge(grouped, df,how='inner',left_index=True,right_index=True)
            result.rename(columns={'Unnamed: 0':'关断器出现次数'}, inplace = True)
            result=result.sort_values(by="关断器出现次数", ascending=False)
            print(result)

            result.to_excel(file_name)
        except KeyError:
            continue