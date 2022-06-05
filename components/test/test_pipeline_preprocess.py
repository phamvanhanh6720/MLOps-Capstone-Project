import sys
sys.path.append("..")
from components import data_preprocess
if __name__ =="__main__":
    df_train, df_val, df_test = data_preprocess.pipeline_preprocessing()