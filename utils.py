import pickle

def save_pkl(data, path):
    output = open(path, 'wb')
    pickle.dump(data, output)
    output.close()

def load_pkl(path):
    pkl_file = open(path, 'rb')
    return pickle.load(pkl_file)