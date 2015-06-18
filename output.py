#!/usr/bin/env python
# -*- coding: utf-8 -*-

from xlutils.copy import copy
from xlrd import open_workbook
from xlwt import easyxf, Workbook
import os
import cPickle


def write(ret, rho, tau):
    print ret[0][0]
    w_sheet = wb.add_sheet(ret[0][0]) # the sheet to write to within the writable copy
    for i, r in enumerate(ret):
        for j, c in enumerate(r):
            w_sheet.write(i, j, c)


def getret(irho, itau):
    rho = -1., -2., -3., -0.5
    tau = 0.1, 0.2, 0.3, 0.4, 0.5, 0.01
    rho, tau = rho[irho], tau[itau]
    title = ['rho=%1.1f, tau=%1.2f' % (rho, tau), 'Lambda', 'L1/L0', 'Y', 'Y1/Y0', '(Y1-Y0)*2/(Y1+Y0)', 'P', 'P1/P0']
    ret = [title]

    for i in range(30):
        fi = 'result/result1_%d_%d_%d.pkl' % (irho, itau, i)
        pkl = cPickle.load(open(fi, 'rb'))

        Y0, Y1 = pkl['Y0'], pkl['Y1']
        L0, L1 = pkl['lam0'], pkl['lam1']
        P0, P1 = pkl['P0'], pkl['P1']
        if i == 0:
            dL, dY, dY2, dP = None, None, None, None
            ret.append([i, L0, dL, Y0, dY, dY2, P0, dP])

        dL = L1 / L0
        dY = Y1 / Y0
        dY2 = (Y1-Y0)*2/(Y1+Y0)
        dP = P1/P0
        ret.append([i+1, L1, dL, Y1, dY, dY2, P1, dP])

    return ret, rho, tau


if __name__ == '__main__':
    file_path = 'FinalResult.20150527.xls'
    #rb = open_workbook(file_path, formatting_info=True)
    #wb = copy(rb) # a writable copy (I can't read values out of this, only write to it)
    wb = Workbook(encoding='utf8')

    for itau in range(6):
        ret, rho, tau = getret(3, itau)
        write(ret, rho, tau)

    wb.save(file_path)
