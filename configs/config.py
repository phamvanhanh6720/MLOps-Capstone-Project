
# configs/config.py
# Configurations.

import logging
import sys
from pathlib import Path
from unicodedata import category
from rich.logging import RichHandler
import logging.config as lcfg
# Directories
BASE_DIR = Path(__file__).parent.parent.absolute()
CONFIG_DIR = Path(BASE_DIR, "configs")
LOGS_DIR = Path(BASE_DIR, "logs")
DATA_DIR = Path(BASE_DIR, "data")
STORES_DIR = Path(BASE_DIR, "stores")


# Local stores
MODEL_REGISTRY = Path(STORES_DIR, "model")
TRANSFORM_STORE = Path(STORES_DIR, "transform")


#path
PATH_TRAIN_DATA = Path(DATA_DIR, 'train_data.csv') 
PATH_VALID_DATA = Path(DATA_DIR, 'val_data.csv') 
PATH_TEST_DATA = Path(DATA_DIR, 'test_data.csv')
PATH_TRANSFORM_BRANCH = Path(TRANSFORM_STORE,'branch.pkl')
PATH_TRANSFORM_MODEL = Path(TRANSFORM_STORE,'model.pkl')
PATH_TRANSFORM_OTHERS = Path(TRANSFORM_STORE,'others.pkl')
PATH_BEST_MODEL = Path(MODEL_REGISTRY,'best_model.job')
category_other = ['external_color','internal_color','origin', 'gearbox', 'wheel_drive', 'car_type']


# Create dirs
LOGS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
STORES_DIR.mkdir(parents=True, exist_ok=True)
MODEL_REGISTRY.mkdir(parents=True, exist_ok=True)
TRANSFORM_STORE.mkdir(parents=True, exist_ok=True)

# Logger
logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "minimal": {"format": "%(message)s"},
        "detailed": {
            "format": "%(levelname)s %(asctime)s [%(filename)s:%(funcName)s:%(lineno)d]\n%(message)s\n"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "minimal",
            "level": logging.DEBUG,
        },
        "info": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": Path(LOGS_DIR, "info.log"),
            "maxBytes": 10485760,  # 1 MB
            "backupCount": 10,
            "formatter": "detailed",
            "level": logging.INFO,
        },
        "error": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": Path(LOGS_DIR, "error.log"),
            "maxBytes": 10485760,  # 1 MB
            "backupCount": 10,
            "formatter": "detailed",
            "level": logging.ERROR,
        },
    },
    "loggers": {
        "root": {
            "handlers": ["console", "info", "error"],
            "level": logging.INFO,
            "propagate": True,
        },
    },
}
lcfg.dictConfig(logging_config)
logger = logging.getLogger("root")
logger.handlers[0] = RichHandler(markup=True)


# config data
CONFIG_DATA ={
    "numeric":{
        "year":{
            "lower_limit": 2007,
            "upper_limit":float('inf')
        },
        "km_driven":{
            "lower_limit": 0,
            "upper_limit":1e9
        },
        "num_seats": {
            "lower_limit": 0,
            "upper_limit":30
        },
        "engine_capacity":{
            "lower_limit": 0,
            "upper_limit": 10
        }
    },
    "category":{
        "origin":['domestic', 'imported'],
        "wheel_drive":['FWD', 'RWD', '4WD', 'AWD'],
        "car_type":['sedan', 'crossover', 'hatchback', 'pickup', 'suv', 'van', 'coupe',
                    'truck', 'convertible', 'wagon'],
        "gearbox":['automatic', 'manual']
    }
}


numeric_features = ['year','price','km_driven','num_seats','engine_capacity']
category_features = ['branch','model','origin','external_color','internal_color','gearbox','wheel_drive','car_type']
FEATURES = numeric_features + category_features