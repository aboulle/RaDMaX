# RaDMaX

**A graphical user inferface for the determination of strain and damage profiles in irradiated crystals from X-ray diffraction data**
___

## Installation instructions
Download zip file and extract it to your disk. In a shell, run the Radmax.py file with `python Radmax.py`.


Radmax requires [python 2.7] (http://www.python.org), [Scipy](http://www.scipy.org), [Matplotlib](http://www.matplotlib.org) and [wxpython] (http://www.wxpython.org).
For the moment, the wxpython library is not compatible with Python 3 and above. **RaDMaX won't work with Python 3.**


### MS Windows
1. For most users, especially on Windows and Mac, the easiest way to install scientific Python is to download **one** of these Python distributions, which includes most of the key packages:
 
 * [Anaconda](http://continuum.io/downloads): A free distribution for the SciPy stack. Supports Linux, Windows and Mac. [Download.](https://3230d63b5fc54e62148e-c95ac804525aac4b6dba79b00b39d1d3.ssl.cf1.rackcdn.com/Anaconda-2.3.0-Windows-x86.exe)
 * [Python(x,y)](http://python-xy.github.io/): A free distribution including the SciPy stack, based around the Spyder IDE. Windows only. [Download.](http://ftp.ntua.gr/pub/devel/pythonxy/Python(x,y)-2.7.10.0.exe)
 * [WinPython](http://winpython.github.io/): A free distribution including the SciPy stack. Windows only. [Download.] (http://sourceforge.net/projects/winpython/files/WinPython_2.7/2.7.9.5/WinPython-32bit-2.7.9.5.exe/download)


2. Download and install [WxPython] (http://downloads.sourceforge.net/wxpython/wxPython3.0-win32-3.0.2.0-py27.exe)


### GNU / Linux
On most Linux systems the dependencies are available in the software repositories. For debian based systems run (as root): `apt-get install python python-scipy python-matplolib python-wxgtk2.8`. 



## How to test the program
1. Navigate to the "examples/YSZ" or "examples/SiC-3C" folder
2. In a text editor open the *.ini file and modify lines 5-7: enter the path of the files on your system.
3. Launch Radmax.py
4. In the "File" menu select "Load Project"
5. Navigate to the "examples/YSZ" or "examples/SiC-3C" folder and load the *.ini file

* Any change in any of the upper panels has to be validated with the "Update" button to update the XRD curve.
* The strain and damage profiles can be modified by dragging the control points. The XRD curve is updated in real time.
* The strain and damage profile can be scaled up or down with the mouse wheel + pressing the "u" key. The XRD curve is update when the "u" key is released.
* Calculated XRD curves can be fitted to experimental data in the "Fitting window" tab.
* Conventional least-squares (recommended) or generalized simulated annealing algorithm can be used.
* The fitted curve, the strain and damage profiles are automatically saved (*.txt) in the folder selected above.
