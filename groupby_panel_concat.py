# 对outputshanghai的结果进行归类，按照出现次数排序,并合并到一个表格
# 2.对output_3_13结果汇总DB



import os
import numpy as np
import pandas as pd
import re

def concat(input_file='..\\output_3_13',output_file='..\\output_3_13\\grouped_all_data.xls'):
    np.set_printoptions(suppress=True)
    data=pd.DataFrame()
    def walk(rootdir):
        g = os.walk(rootdir)
        for path, dir_list, file_list in g:
            return path,file_list
    path, file_names = walk(input_file)
    for i, file in enumerate(file_names):
        num=re.findall('[0-9]{1,2}',file)[0]
        file = ''.join([path, '\\', file])
        file_name=output_file

        if file.endswith('xls'):
            df=pd.read_excel(file)
            try:
                grouped=df.groupby('关断器').count()

                grouped=grouped.sort_values(by='日期',ascending=False)
                df=df.drop(['Unnamed: 0'],axis=1)
                grouped=grouped.iloc[:,0:1]
                df=df.set_index(['关断器'])
                result=pd.merge(grouped, df,how='inner',left_index=True,right_index=True)
                result.rename(columns={'Unnamed: 0':'关断器出现次数'}, inplace = True)
                result=result.sort_values(by="关断器出现次数", ascending=False)
                result=result[result['关断器出现次数']>5]
                print(result)
                data=pd.concat([data,result])



            except KeyError:
                continue
    data.to_excel(file_name)

if __name__ == '__main__':
    concat('../DB','../DB/DB.xls')