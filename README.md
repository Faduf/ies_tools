# ies_tools
Couple of small tools for rotating and combining IES photometric files.

# Setup

Required packages:
* Python 3.x
* scipy
* numpy

Install with pip or check out www.lfd.uci.edu/~gohlke/pythonlibs/


# Installation

Install from commandline:

Download the source:

```bash
git clone https://github.com/ollitapa/ies_tools.git
```

Install the scripts:

```bash
cd ies_tools
python setup.py install
```

# Usage

The package installs two scripts to the bin directory of the machine:

### rotateIES
```bash
This tool rotates IES file around z-axis for given degrees.

positional arguments:
  file               IES-file to rotate
  degrees            Rotate the ies-file degrees. The rotaation is clockwise
                     when looking at the direction of the light. 1 deg
                     accuracy only

optional arguments:
  -h, --help         show this help message and exit
  -o OUT, --out OUT  Out file
```

### combineIES

```bash
This tool combines two IES files to one. First file is upper, second lower
part.

positional arguments:
  upper                Upward light
  lower                Downward light

optional arguments:
  -h, --help           show this help message and exit
  -n, --no_flip_upper  Flip the upper file over
  -o OUT, --out OUT    Out file
  -s, --scale_upper    Scale the upper file to match the lower file based on
                       ovelapping area, phi=90deg
```