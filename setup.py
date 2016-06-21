from distutils.core import setup
from glob import glob
#from numpy import core
import matplotlib
import statsmodels.api
import sys
import py2exe

# Setup file for creating Windows EXE
# C:\Current Windows Directory>python setup.py py2exe

sys.path.append("C:\Users\shaythorne\Dropbox\GlobalEcology\PythonResources\Microsoft.VC90.CRT")

data_files = matplotlib.get_py2exe_datafiles()
data_files.append(("Microsoft.VC90.CRT", glob(r'C:\Users\shaythorne\Dropbox\GlobalEcology\PythonResources\Microsoft.VC90.CRT\*.*')))
setup(
    data_files=data_files,
    windows=['SARDM_v0_8.py'],
)
