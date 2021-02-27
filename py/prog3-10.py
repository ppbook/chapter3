# -*- coding: utf-8 -*-
"""prog3-10.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1lvlJBb1U1p2Ap_w6moX2-8dkDO2Wv_w8
"""

from google.colab import files
files.upload() # kaggle.jsonをアップロード
!mkdir -p ~/.kaggle
!mv kaggle.json ~/.kaggle/
!chmod 600 /root/.kaggle/kaggle.json

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier \
as RandomForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# データの準備
def prepare():
    !kaggle datasets download -d uciml/horse-colic
    !unzip horse-colic.zip

# データの欠損値の補完
def preprocess():
    df_train = pd.read_csv('horse.csv')
    df_train = df_train.replace('NA', 'NaN')
    # 分類に使用する特徴量
    features = ['surgery', 'age', 'rectal_temp',
                'pulse','respiratory_rate',
                'packed_cell_volume','total_protein', 
                'abdomo_protein', 'surgical_lesion',
                'lesion_1','lesion_2','lesion_3','cp_data']
    print(len(df_train))

    # 対象列をデータフレームに格納して、
    # 欠損値を持つ行の数を確認
    df = pd.DataFrame(df_train.loc[:, features],
     columns=features)
    print('# of Missing Values:\n', 
          df.isnull().any(axis=1).value_counts())


    for f in features:
        # カテゴリ特徴量は最頻値で補完
        if f in ['surgery', 'age', 'temp_of_extremities',
            'surgical_lesion', 'cp_data']:
            df_train[f] = df_train[f].fillna(
                                  df_train[f].mode())

        # カテゴリ特徴量以外は平均値で補完
        else:
            df_train[f] = df_train[f].fillna(
                                  df_train[f].mean())


    yesno = {'no':0, 'yes':1}
    # surgery, surgical_lesion, cp_data の
    # 列の値を0,1（no/yes) に置換
    for f in ['surgery', 'surgical_lesion', 'cp_data']:
        df_train[f].replace(yesno, inplace=True) 
    # ageを0,1（young/adult) に置換
    df_train['age'].replace({'young':0, 'adult':1},
                            inplace=True)
    # outcomeを0,1,2（died/euthanized/lived) に置換 
    df_train['outcome'].replace({'died':0, 
                              'euthanized':1,
                              'lived':2}, inplace=True)
    # 欠損値を補完/除去したデータを確認
    print(df_train)
    # 分類に使用するデータを格納
    X_train = df_train.loc[:,features].values
    # outcomeラベルをターゲットに格納
    y_train = df_train['outcome'].values 
    # データフレームに格納して、欠損値を確認
    df = pd.DataFrame(X_train, columns=features)
    print('# of Missing Values:\n', 
          df.isnull().any(axis=1).value_counts())
    # 学習データとテストデータに分ける
    # (train:test = 7:3)
    X_train, X_test, y_train, y_test = train_test_split(
                                       X_train, y_train, 
                                       train_size=0.7, 
                                       random_state=1)
    return X_train, y_train, features

def main():
    prepare()
    X_train, y_train, features = preprocess()
    X_train, X_test, y_train, y_test = train_test_split(
        X_train, y_train, train_size=0.7, random_state=1)
    # ランダムフォレストにより学習する
    model = RandomForest(n_estimators=100, 
                         max_depth=7,
                         random_state=1).fit(
                         X_train, y_train)
    # 学習したモデルでテストデータを評価し、Accuracyを算出
    print('\nAccuracy: {:.3f}'.format(
        model.score(X_test, y_test)))
    y_pred = model.predict(X_test)
    target_names = ['died', 'euthanized', 'lived']
    print(classification_report(y_test, y_pred,
        target_names=target_names))

if __name__ == '__main__':
    main()