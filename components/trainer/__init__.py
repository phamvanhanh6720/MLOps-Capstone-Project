from sklearn.linear_model import LinearRegression
from xgboost.sklearn import XGBRegressor
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
import pandas as pd
import numpy as np
from configs.config import logger
from configs.config import *
from components import data_preprocess
import optuna
import pickle


def experiment_some_model() -> None:
    df_train, _, df_test = data_preprocess.pipeline_preprocessing()
    X_train = df_train.drop(["price"],axis=1)
    y_train = df_train["price"]
    X_test = df_test.drop(["price"],axis=1)
    y_test = df_test["price"]
    regressors = [
        LinearRegression(),
        XGBRegressor(),
        RandomForestRegressor(),
        ExtraTreesRegressor(), 
        GradientBoostingRegressor()
    ]
    res = pd.DataFrame(columns=['Model', 'RMSE', 'R-Squared'])
    RMSE = []
    R2 = []
    
    for num, regressor in enumerate(regressors):
        reg = regressor.fit(X_train, y_train)
        pred = reg.predict(X_test)
        rmse = np.sqrt(mean_squared_error(pred, y_test))
        r2 = r2_score(pred, y_test)
        RMSE.append(str(np.around(rmse)))
        R2.append(str(round(r2, 4)*100) + '%')
    res['Model'] = ['LinearRegression', 'XGBRegressor', 'RandomForestRegressor', 'ExtraTreesRegressor', 'GradientBoostingRegressor']
    res['RMSE'] = RMSE
    res['R-Squared'] = R2
    logger.info('Done experiment !')
    print(res)


def objective(trial):
        df_train, _, df_test = data_preprocess.pipeline_preprocessing()
        X_train = df_train.drop(["price"],axis=1)
        y_train = df_train["price"]
        X_test = df_test.drop(["price"],axis=1)
        y_test = df_test["price"]
        n_estimators = int(trial.suggest_int('n_estimators', 10, 300))
        max_depth = int(trial.suggest_int('max_depth', 1, 32))
        max_features = int(trial.suggest_int('max_features', 5, 30))
        reg = RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth, max_features=max_features, random_state=1998)
        reg.fit(X_train, y_train)
        pred = reg.predict(X_test)
        rmse = np.sqrt(mean_squared_error(pred, y_test))
        print('rmse: ',rmse)
        return r2_score(pred, y_test)


def optimzer(is_test=False):
    # Preprocess data
    df_train, df_val, df_test = data_preprocess.pipeline_preprocessing()
    n_trials = 50
    if is_test:
        n_trials = 5
        df_train = df_train[:100]
        df_val = df_val[:100]
        df_test = df_test[:100]
        
    X_train = df_train.drop(["price"],axis=1)
    y_train = df_train["price"]
    X_val = df_val.drop(["price"],axis=1)
    y_val = df_val["price"]
    X_test = df_test.drop(["price"],axis=1)
    y_test = df_test["price"]
    
    # Tuning model
    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=n_trials)
    trial = study.best_trial
    best_parameter = trial.params
    
    #get best model
    n_estimators = best_parameter['n_estimators']
    max_depth = best_parameter['max_depth']
    max_features = best_parameter['max_features']
    reg = RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth, max_features=max_features, random_state=1998)
    reg.fit(X_train, y_train)
    pred = reg.predict(X_test)
    rmse = np.sqrt(mean_squared_error(pred, y_test))
    pred_val = reg.predict(X_val)
    rmse = np.sqrt(mean_squared_error(pred_val, y_val))
    if not is_test:
        pickle.dump(reg, open(PATH_BEST_MODEL, 'wb')) 
        logger.info("Save best model !")
    print('rmse_test ',rmse)
    print('r2_test ',r2_score(pred, y_test))
    print('rmse_val ',rmse)
    print('r2_val ',r2_score(pred_val, y_val))
    
