import pandas as pd
import os
import glob
import sys

# %%


def same_dfs(file1, file2):
    rn_dict = {
        "day0 pre-enrichment (MACSlib)":"pre-enrichment (MACSlib)"
    }
    df1 = pd.read_csv(file1).sort_values('seq', ascending=False).reset_index(drop=True).rename(columns=rn_dict)
    df2 = pd.read_csv(file2).sort_values('seq', ascending=False).reset_index(drop=True).rename(columns=rn_dict)
    print("file1: {}".format(file1))
    print("file2: {}".format(file2))
    print("dataframes equal? {}".format(df1.equals(df2)))
    if df1.equals(df2):
        return [df1,df2]

def diff_scan(df1, df2, cols):
    for i in cols:
        print((new1[i]-old1[i]).value_counts())




olddir = './supplementary_data_files/'
newdir = './supplementary_data_files-check/'


ofiles=[f for f in glob.glob(olddir+"*")]
nfiles=[f for f in glob.glob(newdir+"*")]


dfs = []
for i in ofiles:
    for n in nfiles:
        if os.path.basename(i) == os.path.basename(n):
            temp=same_dfs(
                i,
                n
            )
            dfs.append(temp)


df1 = dfs[0][0]
df2 = dfs[0][1]


cols = list(df1.columns)
