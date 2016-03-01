#
# Copyright 2016 VTT Technical Research Center of Finland
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import numpy as np
from scipy.interpolate import griddata
import argparse
from io import StringIO


def __symmetrise(th, arr):

    copySize = th.max() % 360
    thCopy = th
    arrSym = arr
    i = 1
    j = -1
    if copySize != 0:
        while thCopy.max() < 360:
            thCopy = np.concatenate((thCopy, th[::j] + copySize * i))
            arrSym = np.vstack((arrSym, arr))
            i += 1
            j *= -1

    return(thCopy, arrSym)


def __loadIES(fname):

    fid = open(fname)
    header = []

    while True:
        line = fid.readline()
        header.extend([line])
        if line.find('TILT') != -1:
            break

    data = fid.readline()

    # {# of lamps} {lumens per lamp} {candela multiplier}
    # {# of vertical angles}

    # {# of horizontal angles} {photometric type} {units type} {width}
    # {length} {height}
    lm = float(data.split(' ')[1])
    cdMulti = float(data.split(' ')[2])
    v_angle = float(data.split(' ')[3])
    h_angle = float(data.split(' ')[4])
    width = float(data.split(' ')[7])
    length = float(data.split(' ')[8])
    height = float(data.split(' ')[9])

    dataW = fid.readline()
    # 1 1 inputWatts

    arr = np.loadtxt(StringIO(fid.read().replace('\n', ' ')))
    fid.close()

    phi = arr[:v_angle]
    th = arr[v_angle:v_angle + h_angle]
    arr = arr[v_angle + h_angle:]
    arr = arr.reshape((h_angle, -1))

    return(header, lm, cdMulti, dataW, v_angle, h_angle, phi, th, arr,
           width, length, height)


def main():
    parser = argparse.ArgumentParser(
        description='This tool combines two IES files to one. \
                 First file is upper, second lower part.')

    parser.add_argument("upper", help="Upward light")
    parser.add_argument("lower", help="Downward light")
    parser.add_argument("-n", "--no_flip_upper",
                        help="Flip the upper file over",
                        action='store_true')
    parser.add_argument("-o", "--out", help="Out file")
    parser.add_argument("-s", "--scale_upper",
                        help="Scale the upper file to match the lower \
                        file based on ovelapping area, phi=90deg",
                        action='store_true')
    args = parser.parse_args()

    # Load datas
    (headerU, lmU, cdMultiU, dataWU, v_angleU, h_angleU, phiU, thU, arrU,
     width, length, height) = \
        __loadIES(args.upper)
    (headerD, lmD, cdMultiD, dataWD, v_angleD, h_angleD, phiD, thD, arrD,
     width, length, height) = \
        __loadIES(args.lower)

    # Symmetrise arrays if nescesary
    (thU, arrU) = __symmetrise(thU, arrU)
    (thD, arrD) = __symmetrise(thD, arrD)

    # Flip over upper part
    if not args.no_flip_upper:
        thU = 360 - thU
        phiU = 180 - phiU

    (phiD, thD) = np.meshgrid(phiD, thD)
    (phiU, thU) = np.meshgrid(phiU, thU)

    phiI = np.arange(0, 181, 1)
    thI = np.arange(0, 361, 1)

    ziDown = griddata((phiD.ravel(), thD.ravel()), arrD.ravel(),
                      (phiI[None, :], thI[:, None]),
                      method='nearest')
    ziUp = griddata((phiU.ravel(), thU.ravel()), arrU.ravel(),
                    (phiI[None, :], thI[:, None]),
                    method='nearest')
    # print(downArr)
    # print(upArr)
    # print(ziDown)
    # print(ziUp)
    truth = np.logical_and(ziDown != 0, ziUp != 0)

    # Overlapping area
    combArr = (ziDown + ziUp)

    # Scale the upper light to match the lower part
    # This is due to possibly a bit different placement of DUT
    if args.scale_upper:
        nn = len(ziDown[truth])
        sel = np.arange(0, nn)
        # Calculate scaling factor for each angle
        scalers = ziDown[truth][sel] / ziUp[truth][sel]
        x = np.average(scalers)
        std = np.std(scalers)
        print('Average scaling factor of upper light: %.1f' % x)
        print('Standard deviation in %d scaler points: %.3f' % (nn, std))
        combArr = (ziDown + ziUp * x)
        combArr[truth] = ((ziDown + ziUp * x) / 2)[truth]
        lmU = lmU * x
    else:
        # Overlapping area is averaged
        combArr[truth] = ((ziDown + ziUp) / 2)[truth]

    # print(combArr)

    foutN = 'Combined.ies'
    if args.out:
        foutN = args.out
    fout = open(foutN, 'w')
    fout.writelines(headerU)
    fout.write('1 %f %f %d %d 1 2 %f %f %f\n' % (lmD + lmU, cdMultiD,
                                                 len(phiI), len(thI),
                                                 width, length, height))

    fout.write(dataWU)
    j = 1
    for i in phiI:
        fout.write('%.1f ' % i)
        if(j % 20 == 0):
            fout.write('\n')
        j += 1
    fout.write('\n')
    j = 1
    for i in thI:
        fout.write('%.1f ' % i)
        if(j % 20 == 0):
            fout.write('\n')
        j += 1

    fout.write('\n')
    for r in range(combArr.shape[0]):
        row = combArr[r, :]
        j = 1
        for a in row:
            fout.write('%.5f ' % a)

            if(j % 12 == 0):
                fout.write('\n')
            j += 1
        fout.write('\n')
    fout.close()

if __name__ == '__main__':
    main()
