import sys
sys.path.append("..")

if __name__ == '__main__':
    from training import train
    train(project='mlops-test')
    print('done')
