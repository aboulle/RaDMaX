# RaDMaX
___
**_A graphical user inferface for the determination of strain and damage profiles in irradiated crystals from X-ray diffraction data_**
___

## Installation instructions
1. MS Windows
 * Download release file and run the *.exe file
2. Running from sources (Linux, Windows)
 * Download zip file and extract archive to your disk. In a shell, run the Radmax.py file with `python Radmax.py`.
 * Running from sources requires [python 2.7] (http://www.python.org), [Scipy](http://www.scipy.org), [Matplotlib](http://www.matplotlib.org) and [wxpython] (http://www.wxpython.org).
For the moment, the wxpython library is not compatible with Python 3 and above.
On most Linux systems the dependencies are available in the software repositories.
For debian based systems run (as root): `apt-get install python python-scipy python-matplolib python-wxgtk2.8`.
Windows installation files can be found on the corresponding websites.

## How to test the program
1. In the "File" menu select "Load Project"
2. Navigate to the "examples" folder
3. Navigate to the "YSZ" or "SiC-3C" folder
4. Load the *.ini file

* Any change in any of the upper panels has to be validated with the "Update" button to update the XRD curve.
* The strain and damage profiles can be modified by dragging the control points. The XRD curve is updated in real time.
* The strain and damage profile can be scaled up or down with the mouse wheel + pressing the "u" key. The XRD curve is update when the "u" key is released.
* Calculated XRD curves can be fitted to experimental data in the "Fitting window" tab.
* Conventional least-squares (recommended) or generalized simulated annealing algorithm can be used.
* The fitted curve, the strain and damage profiles are automatically saved (*.txt) in the folder selected above.
