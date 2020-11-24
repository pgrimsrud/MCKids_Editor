# MCKids_Editor

This is a level editor created to allow users to edit levels of the NES game M.C. Kids.

The editor is written in Python/Tk and requires the following:

* Python3
* PIL (the Python Imaging Library)
  * once you have python you can install this by doing 'pip install pillow'
  * note that you will need to add the paths to both python and pip to you system's PATH environment variable
* A C compiler (used for compression performance. The compression install step will complain if the compiler is missing
  * Windows: Install the 'Python development' workload as well as the 'Desktop development with C++' from Visual Studio 2019 Community (https://docs.microsoft.com/en-us/visualstudio/python/installing-python-support-in-visual-studio?view=vs-2019)
* Install the compression module included in this repo (python setup.py install)
* To launch the editor run 'python MCKids_Editor.py'
* A ROM of the game M.C. Kids for the NES is required (but not provided)