import pylab as pl
import geopandas
import sciris as sc
import hiptool as hp
from sklearn import cluster as sklc

toplot = [
#        'burdenmatrix',
        'burdenmap',
        'clustermaps',
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

burdeneps = 1.0
totalburden = data[:,-1]
totalpercapita = datapercapita[:,-1]
normdata = sc.dcp(data)
for c,country in enumerate(countries):
    normdata[c,:] /= totalburden[c]

order = pl.argsort(totalpercapita)
for i,o in enumerate(order):
    print(f'{i+1:3}. {countries[o]:15}: {totalpercapita[o]: 6.3f}')
    
dpc = datapercapita / datapercapita.max()
nd = normdata / normdata.max()

# Do clustering
clusters = [2,3,4,7,20,190]
clusterdata = sc.odict()
for cluster in clusters:
    kmeans = sklc.KMeans(n_clusters=cluster, random_state=0).fit(dpc)
    labels = kmeans.labels_
    nlabels = max(labels)+1
    burdenbylabel = pl.zeros(nlabels)
    popbylabel = pl.zeros(nlabels)
    for c in range(ncountries):
        burdenbylabel[labels[c]] += totalburden[c]
        row = country_data.findrow(key=countries[c], col='name', asdict=True, die=True)
        popbylabel[labels[c]] += row['population']
    for l in range(nlabels):
        burdenbylabel[l] /= popbylabel[l]
    print(popbylabel)
    print(burdenbylabel)
    labelorder = pl.argsort(burdenbylabel)
    reverseorder = pl.argsort(labelorder)
    print(cluster)
    print(labelorder)
    sortedlabels = pl.zeros(ncountries)
    for c in range(ncountries):
        sortedlabels[c] = reverseorder[labels[c]]
        sortedlabels[c] = burdenbylabel[labels[c]]
    clusterdata[str(cluster)] = sortedlabels
    
    
# Set up map data
world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
world = world[(world.pop_est>0) & (world.name!="Antarctica")]
world['plotvar'] = 0.0

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
#         'Fr. S. Antarctic Lands': 'France', # Skip for 0 reference
#         'N. Cyprus': 'Cyprus',
         'New Caledonia': 'France',
        })

def apply_data(world, input_data):
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
            world.at[index, 'plotvar'] = input_data[c]
            
            matched.append(row['name'])
            count += 1
        else:
            print(row['name'])
            if thiscountry == 'Fr. S. Antarctic Lands':
                world.at[index, 'plotvar'] = 0.99
            if thiscountry == 'N. Cyprus':
                world.at[index, 'plotvar'] = 0.01
            unmatched.append(row['name'])
            mismatchcount += 1
    
#    print(f'Matched {count} of {len(mapcountries)}')
#    print('Mismatches 1:')
#    print(sorted(list(set(mapcountries)-set(matched))))
#    print('Mismatches 2:')
#    print(sorted(list(set(unmatched))))
    
    return world



# Plot all burdens
if 'burdenmatrix' in toplot:
    fig = pl.figure()
    pl.imshow(logdata)
#    pl.imshow(pl.log10(normdata+1e-6))
    pl.colorbar()


# Plot as map
if 'burdenmap' in toplot:
    world = apply_data(world, datapercapita[:,-1])
    fig = pl.figure(figsize=(40,18))
    ax = fig.add_axes([0.01, 0.01, 1.0, 1.0])
    world.plot(ax=ax, column='plotvar', edgecolor=(0.5,0.5,0.5), cmap='parula', legend=True);
    pl.show()
    
if 'clustermaps' in toplot:
    for key,cdata in clusterdata.items():
        world = apply_data(world, cdata)
        fig = pl.figure(figsize=(40,18))
        ax = fig.add_axes([0.01, 0.01, 1.0, 1.0])
        world.plot(ax=ax, column='plotvar', edgecolor=(0.5,0.5,0.5), cmap='parula', legend=True);
        pl.title(f'Clusters = {key}')
    pl.show()

print('Done.')