# -*- coding: utf-8 -*-
"""DataPreprocessing_FeatureExtractionipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/16qLsVjimbbc-D2bgPU3OvQGzc0I_E-B3
"""

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from sklearn.preprocessing import OneHotEncoder
from sklearn.neighbors import LocalOutlierFactor

df1=pd.read_csv('/content/drive/MyDrive/titanic.csv')
df2=pd.read_csv('/content/drive/MyDrive/application_train.csv')

df1.head()

df2.head()

df1.tail()

df2.tail()

df1.info()

df2.info()

df1.columns

df2.columns

"""## FOR TITANIC FILE"""

sns.boxplot(x=df1['Age'])
plt.show()

q1 = df1["Age"].quantile(0.25)
q3 = df1["Age"].quantile(0.75)
iqr = q3 - q1
up = q3 + 1.5 * iqr
low = q1 - 1.5 * iqr

print(df1[(df1["Age"] < low) | (df1["Age"] > up)])

print(df1[(df1["Age"] < low) | (df1["Age"] > up)].any(axis=None))

print(df1[(df1["Age"] < low)].any(axis=None))

def outlier_thresholds(dataframe, col_name, q1=0.25, q3=0.75):
    quartile1 = dataframe[col_name].quantile(q1)
    quartile3 = dataframe[col_name].quantile(q3)
    interquantile_range = quartile3 - quartile1
    up_limit = quartile3 + 1.5 * interquantile_range
    low_limit = quartile1 - 1.5 * interquantile_range
    return low_limit, up_limit

print(outlier_thresholds(df1, "Age"))

low, up = outlier_thresholds(df1, "Fare")
print(df1[(df1["Fare"] < low) | (df1["Fare"] > up)].head())

def check_outlier(dataframe, col_name):
    low_limit, up_limit = outlier_thresholds(dataframe, col_name)
    if dataframe[(dataframe[col_name] > up_limit) | (dataframe[col_name] < low_limit)].any(axis=None):
        return True
    else:
        return False

print(check_outlier(df1, "Age"))    # True  (yes, there is at least 1 outlier.)
print(check_outlier(df1, "Fare"))

def grab_col_names(dataframe, cat_th=10, car_th=20):
    cat_cols = [col for col in dataframe.columns if dataframe[col].dtypes == "O"]
    num_but_cat = [col for col in dataframe.columns if dataframe[col].nunique() < cat_th and dataframe[col].dtypes != "O"]
    cat_but_car = [col for col in dataframe.columns if dataframe[col].nunique() > car_th and dataframe[col].dtypes == "O"]
    cat_cols = cat_cols + num_but_cat
    cat_cols = [col for col in cat_cols if col not in cat_but_car]
    num_cols = [col for col in dataframe.columns if dataframe[col].dtypes != "O" and col not in num_but_cat]

    print(f"Observations: {dataframe.shape[0]}")
    print(f"Variables: {dataframe.shape[1]}")
    print(f"cat_cols: {len(cat_cols)}")
    print(f"num_cols: {len(num_cols)}")
    print(f"cat_but_car: {len(cat_but_car)}")
    print(f"num_but_cat: {len(num_but_cat)}")

    return cat_cols, num_cols, cat_but_car

cat_cols, num_cols, cat_but_car = grab_col_names(df1)
num_cols = [col for col in num_cols if col not in "PassengerId"]
print(num_cols)
for col in num_cols:
    print(col, check_outlier(df1, col))

for col in num_cols:
    print(col, check_outlier(df1, col))

"""# **USE APPLICATION TRAIN**"""

cat_cols, num_cols, cat_but_car = grab_col_names(df2)

num_cols.remove('SK_ID_CURR')

print()
print()

for col in num_cols:
    print(col, check_outlier(df2, col))

def grab_outliers(dataframe, col_name, outlier_index=False, f = 5):
    low, up = outlier_thresholds(dataframe, col_name)

    if dataframe[((dataframe[col_name] < low) | (dataframe[col_name] > up))].shape[0] > 10:
        print(dataframe[((dataframe[col_name] < low) | (dataframe[col_name] > up))].head(f))
    else:
        print(dataframe[((dataframe[col_name] < low) | (dataframe[col_name] > up))])

    if outlier_index:
        out_index = dataframe[((dataframe[col_name] < low) | (dataframe[col_name] > up))].index
        return out_index

age_index = grab_outliers(df1, "Age", True)

print(age_index)

"""### REMOVE OUTLIERS"""

low, up = outlier_thresholds(df1, "Fare")
print(df1.shape)

print(df1[~((df1["Fare"] < low) | (df1["Fare"] > up))].shape)

def remove_outlier(dataframe, col_name):
    low_limit, up_limit = outlier_thresholds(dataframe, col_name)
    df_without_outliers = dataframe[~((dataframe[col_name] < low_limit) | (dataframe[col_name] > up_limit))]
    return df_without_outliers

cat_cols, num_cols, cat_but_car = grab_col_names(df1)
num_cols.remove('PassengerId')

for col in num_cols:
    df1 = remove_outlier(df1,col)

print(df1.shape)

def replace_with_thresholds(dataframe, variable):
    low_limit, up_limit = outlier_thresholds(dataframe, variable)
    dataframe.loc[(dataframe[variable] < low_limit), variable] = low_limit
    dataframe.loc[(dataframe[variable] > up_limit), variable] = up_limit

cat_cols, num_cols, cat_but_car = grab_col_names(df1)

for col in num_cols:
    replace_with_thresholds(df1, col)

for col in num_cols:
    print(col, check_outlier(df1, col))

"""### Local Outlier Factor (LOF)"""

df2 = sns.load_dataset('diamonds')
print(df2.shape)
print(df2.head())

df2 = df2.select_dtypes(include=['float64', 'int64'])
df2 = df2.dropna()
print(df2.shape)
print(df2.head())

for col in df2.columns:
    print(col, check_outlier(df2, col))

low, up = outlier_thresholds(df2, "carat")
print(df2[((df2["carat"] < low) | (df2["carat"] > up))].shape)

low, up = outlier_thresholds(df2, "depth")
print(df2[((df2["depth"] < low) | (df2["depth"] > up))].shape)

clf = LocalOutlierFactor(n_neighbors=20)
clf.fit_predict(df2)
df2_scores = clf.negative_outlier_factor_
print(df2_scores)

print(np.sort(df2_scores)[0:5])

scores = pd.DataFrame(np.sort(df2_scores))
scores.plot(stacked=True, xlim=[0, 20], style='.-')
plt.show()

th = np.sort(df2_scores)[3]
print(th)

print(df2[df2_scores < th])

print(df2.drop(axis=0, labels=df2[df2_scores < th].index).shape)