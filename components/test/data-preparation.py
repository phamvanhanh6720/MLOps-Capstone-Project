import sys
sys.path.append("..")

if __name__ == '__main__':
    from data_preparation import prepare_data
    prepare_data(project='mlops-test')
    print('done')

