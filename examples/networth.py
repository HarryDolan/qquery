#!/usr/bin/env python
"""Calculate net worth by year."""

import pdb
import qquery as qq
import sys
import math
import argparse

parser = argparse.ArgumentParser(description='Calculate net worth by year.')
parser.add_argument('--qdb', required=True)
parser.add_argument('--plot', action='store_true')
args = parser.parse_args()

qq.open(args.qdb)

theDate = '1992-12-31'
theDate = '2021-12-31'

cashBal = 0.00
balShares = {}

year = '99999'

def calcNW (cashBal, balShares, yearend):
    sValue = 0.00
    for sName in balShares.keys():
        price = qq.getPriceOnDate (sName, yearend)
        value = balShares[sName] * price
        if value > 0.0005:
            sValue += value
    netWorth = cashBal + sValue
    return netWorth
    

yr = []
nw = []
for t in qq.getTransactions():
    if t['date'] > theDate: break
    lastyear = year
    yearend = lastyear + '-12-31'
    year = t['date'][0:4]
    if year>lastyear:
        nw.append (calcNW (cashBal, balShares, yearend))
        yr.append(int(yearend[0:4]))

    cashBal += t['amount']
    sName = t['securityName']
    if t['categoryPath'] == 'Investments:Stock Split':
        if t['securityName'] in balShares.keys():
            t['securityShares'] = balShares[t['securityName']]
    if sName:
        if sName in balShares.keys():
            balShares[sName] += t['securityShares']
        else:
            balShares[sName] = t['securityShares']
        if math.fabs(balShares[sName]) < .0001:
            del balShares[sName]

nw.append (calcNW (cashBal, balShares, yearend))
yr.append(int(yearend[0:4]))

if args.plot:
    import matplotlib.pyplot as plt
    plt.bar (yr, nw)
    plt.show()
else:
    for y,n in zip(yr,nw):
        print ('{:4}-12-31 {:13,.2f}'.format(y,n))
        
