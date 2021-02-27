# -*- coding: utf-8 -*-
"""prog3-18.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1SbdKkegEK19uDBbalNcgSVerjJq9il0P
"""

from google.colab import files
files.upload() # kaggle.jsonをアップロード
!mkdir -p ~/.kaggle
!mv kaggle.json ~/.kaggle/
!chmod 600 /root/.kaggle/kaggle.json

# BorutaPyのインストール
!pip install Boruta
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report as clf_report
from sklearn.ensemble import RandomForestClassifier
# BorutaPyクラスのインポート
from boruta import BorutaPy

# データの準備
def prepare():
    !kaggle datasets download -d \
    dipam7/student-grade-prediction
    !unzip student-grade-prediction.zip

    # ポルトガル語学校の学生の成績の予測データセット
    df = pd.read_csv('student-mat.csv')

    # 欠損値を除去
    df = df.dropna()
    # 性別を数値に変換
    df['sex'] = df['sex'].map({'F': 0, 'M': 1}).astype(int)
    # 使用する特徴量
    features = ['sex', 'age','Medu', 'Fedu', 'traveltime', 
                'studytime', 'failures', 'famrel', 
                'freetime', 'goout', 'Dalc',
                'Walc', 'health', 'absences']
    X_train = df.loc[:,features].values
    # 成績ラベルG2（0 to 20)
    y_train = df['G2'].ravel()

    # ビニングにより成績を2クラスに変換
    bins = [-1, 10, 20]
    labels = ['bad', 'good']
    y_cut = pd.cut(y_train, bins=bins, labels=labels)
    print(y_cut)
    y_train = [c for c in y_cut.codes]
    return X_train, y_train, features, labels


# Borutaによる特徴選択
def feature_select_by_Boruta(rfc, X_train, y_train, features):
    # Boruta による特徴選択を定義
    feat_selector = BorutaPy(rfc, n_estimators='auto',
   verbose=0, random_state=1)
    # 関連する特徴量の選択
    feat_selector.fit(X_train, y_train)
    # 選択された特徴量のチェック
    result = feat_selector.support_
    print('=====Selected Features=====')
    for i,tf in enumerate(result):
        if tf == True:
            print('%s' % features[i])
    # 特徴量のランキング
    ranking = feat_selector.ranking_
    rank = {}
    for i in range(len(ranking)):
        rank[i] = ranking[i]
    print('======Feature Ranking======')
    for k,v in sorted(rank.items(), key=lambda x:x[1]):
        print('[%d]\t%s' % (v, features[k]))
    # 選択された特徴量のみのデータに変換
    X_filtered = feat_selector.transform(X_train) 
    return X_filtered, feat_selector

def main():
    X_train, y_train, features, target_names = prepare()
    X_train, X_test, y_train, y_test = \
    train_test_split(X_train, y_train,
                     random_state=0, train_size=0.8)
    rfc = RandomForestClassifier(n_jobs=-1, class_weight='balanced', max_depth=5)
    # Borutaによる特徴選択
    X_filtered, feat_selector = feature_select_by_Boruta(
                          rfc, X_train, y_train, features)
    # 特徴選択せずにランダムフォレストで学習・予測
    print('Result: all features')
    rfc.fit(X_train, y_train)
    y_pred = rfc.predict(X_test)
    print(clf_report(y_test, y_pred, 
                     target_names= target_names)) 

    # 特徴選択の結果を用いてランダムフォレストで学習・予測
    print('Result: selected features')
    rfc_boruta = RandomForestClassifier(n_jobs=-1, 
                  class_weight='balanced', max_depth=5)
    rfc_boruta.fit(X_filtered, y_train)
    X_test_filtered = feat_selector.transform(X_test)
    y_pred_boruta = rfc_boruta.predict(X_test_filtered)
    print(clf_report(y_test, y_pred_boruta, 
                      target_names =target_names))

if __name__ == '__main__':
    main()