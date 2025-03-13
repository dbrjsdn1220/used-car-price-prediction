import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LinearRegression

# 분석할 데이터
# --------------------------------------------------------
df_car = pd.read_csv("cars.csv", encoding='cp949')

# 가격에 연식이 미치는 영향이 크므로 차이를 주기
df_car['연식'] = (df_car['연식'] - 1985) ** 5

# 차량 기본 가격 추가
price = [5890, 6478, 7907, 3645, 2489, 2842, 3877, 3024, 3090]
new_price = []
for car in np.array(df_car):
    if car[0] == 0:
        new_price.append(price[0])
    elif car[0] == 1.0:
        new_price.append(price[1])
    elif car[0] == 2.0:
        new_price.append(price[2])
    elif car[0] == 3.0:
        new_price.append(price[3])
    elif car[0] == 4.0:
        new_price.append(price[4])
    elif car[0] == 5.0:
        new_price.append(price[5])
    elif car[0] == 6.0:
        new_price.append(price[6])
    elif car[0] == 7.0:
        new_price.append(price[7])
    elif car[0] == 8.0:
        new_price.append(price[8])

df_car['기본가격'] = new_price

print(df_car.columns)
print(df_car)
# --------------------------------------------------------

# Linear Regression 모델 만들기
# --------------------------------------------------------
X = np.array(df_car.drop(['가격(단위: 만)'], axis=1, inplace=False))
Y = np.array(df_car['가격(단위: 만)'])

# 데이터 양이 적으므로 k겹 교차검증
kf = KFold(n_splits=5, shuffle=True, random_state=1)
list_rmse = []
all_Y_pred = []
all_Y_test = []

for train_index, test_index in kf.split(X):
    X_train, X_test = X[train_index], X[test_index]
    Y_train, Y_test = Y[train_index], Y[test_index]

    # 모델 학습
    model = LinearRegression()
    model.fit(X_train, Y_train)

    Y_pred = model.predict(X_test)
    # 가끔 음수 값이 나와서 절대값 처리
    Y_pred = np.abs(Y_pred)

    all_Y_pred.extend(Y_pred)
    all_Y_test.extend(Y_test)

    mse = mean_squared_error(Y_test, Y_pred)
    list_rmse += [math.sqrt(mse)]

# K겹 교차검증 결과 출력
print('K겹 교차검증(옵션/연식 수정, 기본가 추가)')
print('5개 평균: %f\n' % np.mean(list_rmse))
for i in range(len(list_rmse)):
    print('[%d]RMSE: %f' % (i, list_rmse[i]))
# --------------------------------------------------------

# 실제값과 예측값 산포도 그래프
# --------------------------------------------------------
plt.scatter(all_Y_test, all_Y_pred, color='blue', alpha=0.6)
plt.plot([min(all_Y_test), max(all_Y_test)], [min(all_Y_test), max(all_Y_test)], color='black', linestyle='--')
plt.xlabel('Actual Price')
plt.ylabel('Predicted Price')
plt.title('Actual vs Predicted Price (FINAL)')
plt.show()
# --------------------------------------------------------
