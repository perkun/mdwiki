import hashlib
import os
import shutil


def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)
#         print("mkdir: ", path)


def rmdir(path):
    if os.path.exists(path):
        shutil.rmtree(path)



def hash_filename(filename):
    ext = os.path.splitext(filename)[-1]  # dot included
    return hashlib.sha1(filename.encode()).hexdigest() + ext


def change_file_ext(filename, new_ext):
    return os.path.splitext(filename)[0] + '.' + new_ext
