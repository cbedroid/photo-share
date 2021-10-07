import os
import pickle

PATH = os.path.dirname(os.path.abspath(__file__))
PICKLE_FILE = os.path.abspath(os.path.join(PATH, "..", "fixtures/test_pickle_file.txt"))


def pickle_save(self, obj, file_mode="ab"):
    """Save test object for further inspection and analysis"""
    with open(PICKLE_FILE, file_mode) as pf:
        pickle.dump(obj, pf)


def pickle_load(self, obj, file_mode="rb"):
    """load test object for further inspection and analysis"""
    with open(PICKLE_FILE, file_mode) as pf:
        return pickle.load(pf.read())
