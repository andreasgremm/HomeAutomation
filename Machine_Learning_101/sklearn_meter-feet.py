
Met = [
   [100],
   [1000],
   [4000]
]

Feet = [
   [328],
   [3280],
   [13121]
]

from sklearn.linear_model import LinearRegression

model = LinearRegression (fit_intercept = False)
print(model.fit(Met,Feet))
#LinearRegression(copy_X=True, fit_intercept=False, n_jobs=1, normalize=False)
print(model.coef_)
print(2000*3.28023516)
print(model.predict([
   [150],
   [280]
]))
