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


def __find_nearest_index(array, value):
    return (np.abs(array - value)).argmin()


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

    return(header, lm, cdMulti, dataW, v_angle,
           h_angle, phi, th, arr, width, length, height)


def main():
    parser = argparse.ArgumentParser(
        description='This tool rotates IES file\
         around z-axis for given degrees.')

    parser.add_argument("file", help="IES-file to rotate")
    parser.add_argument("degrees",
                        help="Rotate the ies-file degrees. The rotaation is\
                        clockwise when looking at the direction \
                        of the light. 1 deg accuracy only", type=float)
    parser.add_argument("-o", "--out", help="Out file")

    args = parser.parse_args()

    # Load datas
    (headerU, lmU, cdMultiU, dataWU, v_angleU,
     h_angleU, phiU, thU, arrU, width, length, height) = \
        __loadIES(args.file)

    # Symmetrise arrays if nescesary
    (thU, arrU) = __symmetrise(thU, arrU)

    # Flip over upper part
    # if not args.no_flip_upper:
    #    thU = 360 - thU
    #    phiU = 180 - phiU

    # Grid the data
    (phiU, thU) = np.meshgrid(phiU, thU)

    phiI = np.arange(0, 181, 1)
    thI = np.arange(0, 361, 1)

    zi = griddata((phiU.ravel(), thU.ravel()), arrU.ravel(),
                  (phiI[None, :], thI[:, None]),
                  method='nearest')

    # Multiply z array to direction of the rotation
    ziMultiplied = np.vstack((zi, zi))

    # Rotation is only int values.
    deg = np.ceil(args.degrees)
    print("Rotating %d degrees clockwise" % deg)

    idxRotStart = __find_nearest_index(thI, deg)
    idxRotEnd = idxRotStart + len(thI)

    # print(zi.shape)
    # print(ziMultiplied[idxRotStart:idxRotEnd, :].shape)

    zi = ziMultiplied[idxRotStart:idxRotEnd, :]

    # Write out rotated file
    foutN = 'Rotated.ies'
    if args.out:
        foutN = args.out
    fout = open(foutN, 'w')
    fout.writelines(headerU)
    fout.write('1 %f %f %d %d 1 2 %f %f %f\n' % (lmU, cdMultiU,
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
    for r in range(zi.shape[0]):
        row = zi[r, :]
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
