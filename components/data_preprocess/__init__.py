import pandas as pd
from configs.config import *
import category_encoders as ce
from scipy import stats
import numpy as np
import utils

def detect_outline(df: pd.DataFrame, feature: str, lower_limit: float=0, upper_limit: float=float('inf')) -> pd.DataFrame:
    ''' Remove outline of features
    '''
    return df[(df[feature] < upper_limit) & (df[feature] > lower_limit)]


def filter_numeric_feature(df: pd.DataFrame) -> pd.DataFrame:
    '''Remove outline for feature numeric
    '''
    df  = detect_outline(df = df, feature = 'year', lower_limit = CONFIG_DATA['numeric']['year']['lower_limit'])
    df = detect_outline(df = df, feature = 'km_driven', upper_limit=CONFIG_DATA['numeric']['km_driven']['upper_limit'])
    df = detect_outline(df = df, feature = 'num_seats', upper_limit=CONFIG_DATA['numeric']['num_seats']['upper_limit'])
    df = detect_outline(df = df, feature = 'engine_capacity', upper_limit=CONFIG_DATA['numeric']['engine_capacity']['upper_limit'])
    return df


def filter_category_feature(df: pd.DataFrame) -> pd.DataFrame:
    '''Remove outline for feature category
    '''
    df = df.loc[df.origin.apply(lambda x:  x in CONFIG_DATA['category']['origin'])]
    df = df.loc[df.wheel_drive.apply(lambda x:  x in CONFIG_DATA['category']['wheel_drive'])]
    df = df.loc[df.car_type.apply(lambda x:  x in CONFIG_DATA['category']['car_type'])]
    df = df.loc[df.gearbox.apply(lambda x:  x in CONFIG_DATA['category']['gearbox'])]
    return df


def filter_outline_target(df: pd.DataFrame, z_score: float=2.8) -> pd.DataFrame:
    df = df[(np.abs(stats.zscore(df.price)) < z_score)]
    return df


class Transform:
    def __init__(self, df_train, df_test, df_val) -> None:
        self.df_train = df_train
        self.df_test = df_test
        self.df_val = df_val
        
        #init encoder
        self.encoder_branch = ce.JamesSteinEncoder()
        self.encoder_model = ce.JamesSteinEncoder()
        self.encoder_others = ce.OrdinalEncoder()


    def fit(self) -> None:
        self.encoder_branch.fit(self.df_train['branch'],self.df_train['price'])
        self.encoder_model.fit(self.df_train['model'],self.df_train['price'])
        self.encoder_others.fit(self.df_train[category_other])


    def transform(self) -> None:
        self.df_train['branch'] = self.encoder_branch.transform(self.df_train['branch'])
        self.df_train['model'] = self.encoder_model.transform(self.df_train['model'])
        self.df_train[category_other] = self.encoder_others.transform(self.df_train[category_other])

        self.df_test['branch'] = self.encoder_branch.transform(self.df_test['branch'])
        self.df_test['model'] = self.encoder_model.transform(self.df_test['model'])
        self.df_test[category_other] = self.encoder_others.transform(self.df_test[category_other])

        self.df_val['branch'] = self.encoder_branch.transform(self.df_val['branch'])
        self.df_val['model'] = self.encoder_model.transform(self.df_val['model'])
        self.df_val[category_other] = self.encoder_others.transform(self.df_val[category_other])

    
    def save(self) -> None:
        utils.save_pkl(self.encoder_branch, PATH_TRANSFORM_BRANCH)
        utils.save_pkl(self.encoder_model, PATH_TRANSFORM_MODEL)
        utils.save_pkl(self.encoder_others, PATH_TRANSFORM_OTHERS)



def pipeline_preprocessing():
    # Load data
    df_train = pd.read_csv(PATH_TRAIN_DATA)
    df_test = pd.read_csv(PATH_TEST_DATA)
    df_valid = pd.read_csv(PATH_VALID_DATA)
    logger.info('Load dataset Done!')

    # Process missing data
    mode = df_train.wheel_drive.mode()[0]
    mean = float(int(df_train.engine_capacity.mean()))
    df_train['wheel_drive'].fillna(value=mode, inplace=True)
    df_valid['wheel_drive'].fillna(value=mode, inplace=True)
    df_test['wheel_drive'].fillna(value=mode, inplace=True)
    df_train['engine_capacity'].fillna(value=mean, inplace=True)
    df_valid['engine_capacity'].fillna(value=mean, inplace=True)
    df_test['engine_capacity'].fillna(value=mean, inplace=True)
    logger.info('Process missing done!')

    # Filter outline
    df_train = filter_outline_target(df_train)
    df_test = filter_outline_target(df_test)
    df_valid = filter_outline_target(df_valid)

    df_train = filter_category_feature(filter_numeric_feature(df_train))
    df_test = filter_category_feature(filter_numeric_feature(df_test))
    df_valid = filter_category_feature(filter_numeric_feature(df_valid))
    logger.info('Process outline done!')

    # Transform data
    transform = Transform(df_train, df_test, df_valid)
    transform.fit()
    transform.transform()
    transform.save()
    logger.info('Transform data done!')
    logger.info(f'len trainset: {len(df_train)}, len validset: {len(df_valid)}, len testset: {len(df_test)}')
    return transform.df_train[FEATURES], transform.df_val[FEATURES], transform.df_test[FEATURES]

