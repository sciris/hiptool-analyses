import pylab as pl
import geopandas
import sciris as sc
import hiptool as hp
from sklearn import cluster as sklc

pl.rc('font', size=16)

toplot = [
#        'burdenmatrix',
#        'burdenmap',
#        'clustermaps', # This is the one that's actually used
        ]

bod = sc.loadobj('gbd-data.dat')
country_data = sc.loadspreadsheet('country-data.xlsx')
savedir = '/home/cliffk/unsw/hiptool-analyses/rapid/talk_results'
which = {'dalys':0, 'deaths':1, 'prevalence':2}['dalys']
dosave = True
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
    
dpc = datapercapita # / datapercapita.max()
nd = normdata / normdata.max()

# Do clustering
clusters = [2,3,4,7,195]
clusterlabels = sc.odict()
clusterdalys = sc.odict()
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
    sorteddalys = pl.zeros(ncountries)
    for c in range(ncountries):
        sortedlabels[c] = reverseorder[labels[c]]/(nlabels-1)
        sorteddalys[c] = burdenbylabel[labels[c]]
    clusterlabels[str(cluster)] = sortedlabels
    clusterdalys[str(cluster)] = sorteddalys
    
    
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
         'Fr. S. Antarctic Lands': 'France', # Skip for 0 reference
         'N. Cyprus': 'Cyprus',
         'New Caledonia': 'France',
        })

    
def apply_data(world, input_data, minval, maxval):
    for index, row in world.iterrows():
        if row['name'] in remapping.keys():
            thiscountry = remapping[row['name']]
        else:
            thiscountry = row['name']
        c = mapcountries.index(thiscountry)
        world.at[index, 'plotvar'] = input_data[c]
        if minval is not None and row['name'] == 'Fr. S. Antarctic Lands': # Just for plotting to get the color bar right
            world.at[index, 'plotvar'] = minval
        if maxval is not None and row['name'] == 'N. Cyprus':
            world.at[index, 'plotvar'] = maxval
    return world


def plot_world(world):
    fig = pl.figure(figsize=(38,20))
    ax = fig.add_axes([0.01, 0.01, 1.0, 1.0])
    world.plot(ax=ax, column='plotvar', edgecolor=(0.5,0.5,0.5), cmap='parula', legend=True)
    fig.axes[0].set_position([0.04, 0.05, 0.9, 1.00]) # Fix map position
    fig.axes[1].set_position([0.95, 0.20, 0.9, 0.70]) # Fix colorbar position
    pl.xlabel('Longitude')
    pl.ylabel('Latitude')
    return fig


# Plot all burdens
if 'burdenmatrix' in toplot:
    fig = pl.figure()
    pl.imshow(logdata)
#    pl.imshow(pl.log10(normdata+1e-6))
    pl.colorbar()


# Plot as map
if 'burdenmap' in toplot:
    world = apply_data(world, datapercapita[:,-1], minval=0, maxval=1)
    fig = plot_world(world)
    pl.show()
    
if 'clustermaps' in toplot:
    for key,cdata in clusterdalys.items():
        world = apply_data(world, cdata, minval=0, maxval=1)
        fig = plot_world(world)
        pl.title(f'DALYs per person per year (number of clusters = {key})')
        if dosave:
            pl.savefig(f'{savedir}/rapid_clusterdalys-{key}.png', dpi=100)
    
    for key,cdata in clusterlabels.items():
        world = apply_data(world, cdata, minval=0, maxval=1)
        fig = plot_world(world)
        pl.title(f'Country cluster (number of clusters = {key})')
        if dosave:
            pl.savefig(f'{savedir}/rapid_clusterlabels-{key}.png', dpi=100)
    
    
    
    pl.show()

print('Done.')