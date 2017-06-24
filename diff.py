from os import listdir
from os.path import isfile, join
mypath = '/dev/'
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

print onlyfiles

import string
import glob
devs = [string.replace(x, '/dev/', '') for x in glob.glob("/dev/*")]
print devs

