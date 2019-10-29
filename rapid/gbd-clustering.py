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
country_data = sc.loadspreadsheet('country-data.xlsx')

which = {'dalys':0, 'deaths':1, 'prevalence':2}['dalys']

logeps = 1.0

countries = bod.keys()
ncountries = len(countries)
burdencodes = hp.burdeninfo.dict.keys()
nburdens = len(burdencodes)
assert nburdens == len(bod[0][0].keys())
#assert set(country_data['name']) == set(countries) # missing {'Palestine', 'Taiwan'}

data = pl.zeros((ncountries,nburdens))

for c,country in enumerate(countries):
    for b,burdencode in enumerate(burdencodes):
        data[c,b] = bod[country][which][hp.burdeninfo.dict[burdencode]]

logdata = pl.log10(data+logeps)

datapercapita = sc.dcp(data)
for c,country in enumerate(countries):
    try:
        row = country_data.findrow(key=country, col='name', asdict=True, die=True)
        datapercapita[c,:] /= row['population']
    except:
        print(f'Unmatched: {country}')
logdatapercapita = pl.log10(datapercapita+logeps)



# Plot all burdens
if 'burdenmatrix' in toplot:
    fig = pl.figure()
    pl.imshow(logdata)
    pl.colorbar()


# Plot as map
if 'burdenmap' in toplot:
    world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
    world = world[(world.pop_est>0) & (world.name!="Antarctica")]
    world['bod'] = 0.0
    
    mapcountries = sc.dcp(countries)

    remapping = sc.odict({
             'Bosnia and Herz.': 'Bosnia and Herzegovina',
             'Central African Rep.': 'Central African Republic',
             "Côte d'Ivoire": "Cote d'Ivoire",
             'Czech Rep.': 'Czech Republic',
             'Dem. Rep. Congo': 'Democratic Republic of the Congo',
             'Dominican Rep.': 'Dominican Republic',
             'Eq. Guinea': 'Equatorial Guinea',
             'Lao PDR': 'Laos',
             'Dem. Rep. Korea': 'North Korea',
             'Russia': 'Russian Federation',
             'Solomon Is.': 'Solomon Islands',
             'Korea': 'South Korea',
             'S. Sudan': 'South Sudan',
             'Bahamas': 'The Bahamas',
             'Gambia': 'The Gambia',
             'Kosovo': 'Serbia',
             'Somaliland': 'Somalia',
             'Falkland Is.': 'Argentina',
#             'Fr. S. Antarctic Lands': 'France',
             'N. Cyprus': 'Cyprus',
             'New Caledonia': 'France',
            })
    
    count = 0
    mismatchcount = 0
    matched = []
    unmatched = []
    for index, row in world.iterrows():
        if row['name'] in mapcountries+remapping.keys():
            if row['name'] in remapping.keys():
                thiscountry = remapping[row['name']]
            else:
                thiscountry = row['name']
            c = mapcountries.index(thiscountry)
            world.at[index, 'bod'] = logdatapercapita[c,-1]
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
    world.plot(ax=ax, column='bod', edgecolor=(0.5,0.5,0.5), cmap='parula');
    pl.show()

print('Done.')