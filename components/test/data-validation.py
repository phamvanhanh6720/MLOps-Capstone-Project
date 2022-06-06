import sys
sys.path.append("..")

if __name__ == '__main__':
    from data_validation import validate_data
    validate_data(project='mlops-test')
    print('done')
