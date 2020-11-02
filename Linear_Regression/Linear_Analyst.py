from sklearn import linear_model
import pandas as pd


class linearAnalyst(object):
    __linearAnalystNames = []
    __linearAnalystValues = []

    @staticmethod
    def get_AnalystList():
        return zip(
            linearAnalyst.__linearAnalystNames,
            linearAnalyst.__linearAnalystValues,
        )

    @staticmethod
    def get_AnalystDataframe():
        dfdata = [val() for val in linearAnalyst.__linearAnalystValues]
        df = pd.DataFrame.from_records(
            dfdata, index=linearAnalyst.__linearAnalystNames
        )
        return df

    @staticmethod
    def write_Excel(filename):
        df = linearAnalyst.get_AnalystDataframe()
        with pd.ExcelWriter(filename) as writer:
            df.to_excel(writer)

    def __init__(self, X, y, name=None):
        self.name = name
        self.regr = linear_model.LinearRegression()
        self.regr.fit(X, y)
        self.__regrScore = self.regr.score(X, y)
        self.ransac = linear_model.RANSACRegressor()
        self.ransac.fit(X, y)
        self.__ransacScore = self.ransac.score(X, y)
        if name:
            linearAnalyst.__linearAnalystNames.append(name)
            linearAnalyst.__linearAnalystValues.append(self.valuesJson)

    def valuesJson(self):
        return dict(
            regrScore=self.__regrScore,
            regrCoef=self.regr.coef_,
            regrIntercept=self.regr.intercept_,
            ransacScore=self.__ransacScore,
            ransacCoef=self.ransac.estimator_.coef_,
            ransacIntercept=self.ransac.estimator_.intercept_,
        )

    def predict(self, P):
        p1 = self.regr.predict(P)
        p2 = self.ransac.predict(P)
        return (p1, p2)
