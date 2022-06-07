from components.data_extraction import extract_data
from components.data_validation import validate_data
from components.data_preparation import prepare_data
from components.training import train

project = 'mlops-fullpipeline'
extract_data(project=project)
validate_data(project=project)
prepare_data(project=project)
train(project=project)