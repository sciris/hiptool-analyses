"""
This script demonstrates example usage of HIPtool.

Usage:

python3 -i example.py

Version: 2019oct26
"""

import pylab as pl
import sciris as sc
import hiptool as hp

dosave = False # Whether or not to save an example data file
doplot = True # Whether or not to plot

country = 'Zambia'
spend = 100 # Per person spending
missing_data = ['remove', 'assumption'][1] # Choose how to handle missing data

P = hp.Project()
P.loadburden(filename='rapid_BoD.xlsx')
P.loadinterventions(filename='rapid_interventions.xlsx')

# Modify MEC values
modify_icer = True
modify_mec = False
if modify_mec:
    sigma = 1.0
    for r in range(P.intervsets[0].data.nrows):
        row = P.intervsets[0].data['parsedbc',r]
        for i,val in enumerate(row):
            mec = val[1]
    #        newmec = min(1.0, 0.5*mec)
            newmec = pl.median([0, (1+sigma*pl.randn())*mec, 1])
            val[1] = newmec
if modify_icer:
    sigma = 0.5
    rands = 1 + sigma*pl.randn(P.intervsets[0].data.nrows)
    rands = pl.maximum(rands, 0.1)
    P.intervsets[0].data['ICER'] *= rands

bod_data = sc.loadobj('gbd-data.dat')
country_data = sc.loadspreadsheet('country-data.xlsx')
baseline_factor = country_data.findrow('Zambia', asdict=True)['icer_multiplier'] # Zambia was used for this

# Replace with actual burden data
for k,key in enumerate(['DALYs', 'Deaths', 'Prevalence']):
    for b,burden in enumerate(P.burden().data['Cause'].tolist()):
        P.burden().data[key, b] = bod_data[country][k][burden]

# Adjust interventions
c = country_data['name'].tolist().index(country)
for key in ['Unit cost', 'ICER']:
    this_factor = country_data['icer_multiplier'][c]
    
    df = P.interv().data
    missing_inds = sc.findinds(df[key]<0)
    if len(missing_inds):
        unitcosts = df['Unit cost'][:]
        icers = df['ICER'][:]
        valid = sc.findinds(df[key]>0)
        unitcosts = unitcosts[valid]
        icers = icers[valid]
        if missing_data == 'remove':
            df.rmrows(missing_inds)
        elif missing_data == 'assumption':
            for ind in missing_inds:
                df['Unit cost', ind] = unitcosts.mean() # 10000.0 # WARNING, completely arbitrary!
                df['ICER', ind] = icers.mean() # 660000
    
    P.interv().data[key] *= this_factor/baseline_factor


P.makepackage()
meta = country_data.findrow(country, asdict=True)

# Optimize
P.package().optimize(budget=spend*meta['population'], verbose=True)

df = P.package().data
df.sort(col='shortname')


# Ploting
if doplot:
#    P.burden().plot()
#    fig1 = P.package().plot_spending(which='current')
    fig2 = P.package().plot_spending(which='optimized')
#    fig3 = P.package().plot_dalys(which='current')
    fig4 = P.package().plot_dalys(which='optimized')
    fig5 = P.package().plot_cascade(cutoff=100e3)
    pl.show()
    
print('Done')

#from PyQt5 import QtWidgets, QtCore
#import sys
#MyApp = QtWidgets.QApplication(sys.argv)
#V = MyApp.desktop().screenGeometry()
#h = V.height()
#w = V.width()
#print("The screen resolution (width X height) is the following:")
#print(str(w) + "X" + str(h))
#print('and')
#print(QtCore.Qt.AA_EnableHighDpiScaling)
#print(QtCore.Qt.AA_UseHighDpiPixmaps)
#print('done')