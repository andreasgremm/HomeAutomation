# import matplotlib.pyplot as plt

from Linear_Analyst import linearAnalyst
from Prepare_Light_Temp_Data import prepareLightTempData

august = prepareLightTempData(
    "csvs/grafana_Helligkeit_August.csv", "csvs/grafana_Temperatur_August.csv"
)
oktober = prepareLightTempData(
    "csvs/grafana_Helligkeit_Oktober.csv",
    "csvs/grafana_Temperatur_Oktober.csv",
)
komplett = prepareLightTempData(
    "csvs/grafana_Helligkeit.csv", "csvs/grafana_Temperatur.csv"
)
komplett.add_NativeTemp("csvs/grafana_Temperatur-nativ.csv")

X = august.get_X()
y = august.get_y()
la1 = linearAnalyst(X, y, "August")
rt = 21.567669
print("Real Temperatur:", rt)
p1 = la1.predict([[20.947368, 135.000000]])
d1 = [abs(i-rt) for i in p1]
print(p1)
print(d1)

X1 = oktober.get_X()
y1 = oktober.get_y()
la2 = linearAnalyst(X1, y1, "Oktober")
p2 = la2.predict([[20.947368, 135.000000]])
d2 = [abs(i-rt) for i in p2]
print(p2)
print(d2)

X2 = komplett.get_X()
y2 = komplett.get_y()
la3 = linearAnalyst(X2, y2, "Komplett")
p3 = la3.predict([[20.947368, 135.000000]])
d3 = [abs(i-rt) for i in p3]
print(p3)
print(d3)

Xn = komplett.get_Xn()
yn = komplett.get_yn()
la4 = linearAnalyst(Xn, yn, "Nativ")

df = linearAnalyst.get_AnalystDataframe()
print(df)
linearAnalyst.write_Excel("test.xlsx")


# regr = linear_model.LinearRegression()
# regr.fit(X, y)
# regr.score(X, y)
# regr.coef_
# regr.intercept_
#
# ransac = linear_model.RANSACRegressor()
# ransac.fit(X, y)
# ransac.score(X, y)
# ransac.estimator_.coef_
# ransac.estimator_.intercept_
#
# regr1 = linear_model.LinearRegression()
# regr1.fit(X1, y1)
# regr1.score(X1, y1)
# regr1.coef_
# regr1.intercept_
#
# ransac1 = linear_model.RANSACRegressor()
# ransac1.fit(X1, y1)
# ransac1.score(X1, y1)
# ransac1.estimator_.coef_
# ransac1.estimator_.intercept_
#
# regr2 = linear_model.LinearRegression()
# regr2.fit(X2, y2)
# regr2.score(X2, y2)
# regr2.coef_
# regr2.intercept_
#
# ransac2 = linear_model.RANSACRegressor()
# ransac2.fit(X2, y2)
# ransac2.score(X2, y2)
# ransac2.estimator_.coef_
# ransac2.estimator_.intercept_
#
# regrN = linear_model.LinearRegression()
# regrN.fit(Xn, yn)
# regrN.score(Xn, yn)
# regrN.coef_
# regrN.intercept_
#
# ransacN = linear_model.RANSACRegressor()
# ransacN.fit(Xn, yn)
# ransacN.score(Xn, yn)
# ransacN.estimator_.coef_
# ransacN.estimator_.intercept_
#
## red_aug=temp_light_aug.drop(columns=['Temperatur.temperatur {room: AUTO}','Temperatur.temperatur {room: Wohnzimmer}', 'Helligkeit.light {room: AUTO}', 'Helligkeit.light {room: Wohnzimmer}'])
## dropedna_aug=red_aug.dropna(subset=['M_Temperatur.m_temperatur {room: AUTO}', 'M_Temperatur.m_temperatur {room: Wohnzimmer}','M_Helligkeit.m_light {room: AUTO}','M_Helligkeit.m_light {room: Wohnzimmer}'])
## temp_aug.head()
## temp_aug.interpolate(method='time').plot()
##  https://pandas.pydata.org/pandas-docs/stable/reference/frame.html
## temp_aug.info()
## tmin=temp_aug.min(skipna=True)
## tmax=temp_aug.max(skipna=True)
## tmax['M_Temperatur.m_temperatur {room: AUTO}']
