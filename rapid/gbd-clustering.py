import pylab as pl
import geopandas
import sklearn
import sciris as sc
import hiptool as hp

toplot = [
#        'burdenmatrix',
        'burdenmap',
        ]

bod = sc.loadobj('gbd-data.dat')

which = {'dalys':0, 'deaths':1, 'prevalence':2}['dalys']

countries = bod.keys()
ncountries = len(countries)
burdencodes = hp.burdeninfo.dict.keys()
nburdens = len(burdencodes)
assert nburdens == len(bod[0][0].keys())

data = pl.zeros((ncountries,nburdens))

for c,country in enumerate(countries):
    for b,burdencode in enumerate(burdencodes):
        data[c,b] = bod[country][which][hp.burdeninfo.dict[burdencode]]

logdata = pl.log10(data+1)



# Plot all burdens
if 'burdenmatrix' in toplot:
    fig = pl.figure()
#    pl.subplot(2,1,1)
#    pl.imshow(data)
#    pl.colorbar()
#    pl.subplot(2,1,2)
    pl.imshow(logdata)
    pl.colorbar()


# Plot as map
if 'burdenmap' in toplot:
    world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
    world = world[(world.pop_est>0) & (world.name!="Antarctica")]
    world['bod'] = 0.0
    
    mapcountries = sc.dcp(countries)
    
    remapping = {
            'Bosnia and Herzegovina': 'Bosnia and Herz.',
            'Central African Republic': 'Central African Rep.',
            "Cote d'Ivoire": "Côte d'Ivoire",
            'Czech Republic': 'Czech Rep.',
            'Democratic Republic of the Congo': 'Dem. Rep. Congo',
            'Dominican Republic': 'Dominican Rep.',
            'Equatorial Guinea': 'Eq. Guinea',
            'Laos': 'Lao PDR',
            'North Korea': 'Dem. Rep. Korea',
            'Russian Federation':'Russia',
            'Solomon Islands': 'Solomon Is.',
            'South Korea': 'Korea',
            'South Sudan': 'S. Sudan',
            'The Bahamas': 'Bahamas', 
            'The Gambia': 'Gambia',
            }
    
    for key,val in remapping.items():
        mapcountries[mapcountries.index(key)] = val
    
    count = 0
    mismatchcount = 0
    matched = []
    unmatched = []
    for index, row in world.iterrows():
        if row['name'] in mapcountries:
            world.at[index, 'bod'] = logdata[c,-1]
            print(f'Match for {row["name"]}')
            matched.append(row['name'])
            count += 1
        else:
            unmatched.append(row['name'])
            mismatchcount += 1
    
    print(f'Matched {count} of {len(mapcountries)}')
    print('Mismatches 1:')
    print(sorted(list(set(mapcountries)-set(matched))))
    print('Mismatches 2:')
    print(sorted(list(set(unmatched))))
    
    fig = pl.figure(figsize=(40,18))
    ax = fig.add_axes([0.01, 0.01, 1.0, 1.0])
    world.plot(ax=ax, column='bod', edgecolor=(0.5,0.5,0.5));
    pl.show()


print('Done.')