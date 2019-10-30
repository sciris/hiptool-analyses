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
modify_icer = False
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
                df['Unit cost', ind] = 2*unitcosts.mean() # 10000.0 # WARNING, completely arbitrary!
                df['ICER', ind] = 2*icers.mean() # 660000
    
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


country_data = sc.loadspreadsheet('country-data.xlsx')
interv_data = sc.loadspreadsheet('rapid_interventions.xlsx')

dalys = P.package().data['opt_dalys_averted']

sc.heading('DALYs figure')
category1 = interv_data['Category 1'].tolist()
category2 = interv_data['Category 2'].tolist()
interv_category = [c1+': '+c2 for c1,c2 in zip(category1, category2)]
categories = sorted(set(interv_category))
ncategories = len(categories)
nintervs = len(dalys)
nspends = 1
mapping = []
for i_c in interv_category:
    for c,cat in enumerate(categories):
        if i_c == cat:
            mapping.append(c)

dalydata = pl.zeros(ncategories)
for i in range(nintervs):
    c = mapping[i]
    dalydata[c] += dalys[i]
    print(f"{i} {categories[c]} {dalydata[c]} {interv_data['Short name'].tolist()[i]}")

fig = pl.figure(figsize=(10,8))
x = pl.arange(nspends)
axlist = []
previous = pl.zeros(nspends)

colors = [(0.5, 0.5, 0.0),
          (0.9, 0.5, 0.0),
          
          (0.6, 0.0, 0.6),
          (0.7, 0.1, 0.6),
          (0.8, 0.2, 0.6),
          (0.9, 0.3, 0.6),
          
          (0.0, 0.0, 0.3),
          (0.0, 0.1, 0.4),
          (0.0, 0.2, 0.5),
          (0.0, 0.3, 0.6),
          (0.0, 0.4, 0.7),
          (0.0, 0.5, 0.8),
          (0.0, 0.6, 0.9),
          
          (0.0, 0.5, 0.2),
          (0.0, 0.6, 0.3),
          (0.0, 0.7, 0.4),
          (0.0, 0.8, 0.5),
          (0.0, 0.9, 0.6),
        ]
colors = colors[::-1]

for c in range(len(categories)):
    current = dalydata[c]/1e6
    ax = pl.bar(x, current, bottom=previous, facecolor=colors[c])
    previous += current
    axlist.append(ax)
    
xticks = ['$%s' % val for val in [0.1, 0.3, 1, 3, 10, 30, 100, 300, '1k', '3k', '10k']]
pl.ylabel('DALYs averted (millions)')
titletext = 'DALYs averted annually by funding level and disease area'
pl.title(titletext)
pl.xticks(x, xticks)
pl.xlabel('EUHC expenditure per person per year')
pl.legend([ax[0] for ax in axlist][::-1], categories[::-1])

pl.show()