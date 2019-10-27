import sciris as sc

keys = ['Rheumatoid arthritis', 'Bacterial skin diseases', 'Congenital musculoskeletal and limb anomalies', 'Cataract']

bod = sc.loadobj('gbd-data.dat')

totals = sc.odict()

for key in keys:
    totals[key] = 0
    for country,val in bod.items():
        dalys = val[0]
        totals[key] += dalys[key]

print('Total DALYs:')
for key in keys:
    print(f'{key:50s}: {totals[key]:10.0f}')
    
    





