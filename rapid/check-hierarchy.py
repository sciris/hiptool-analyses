import sciris as sc
import pylab as pl
import hiptool as hp

fn = 'gbd-data.dat'
bod = sc.loadobj(fn)

# DALYs match up, deaths almost do, prevalence does not
which = {'dalys':0, 'deaths':1, 'prevalence':2}['dalys']

afg = bod['Afghanistan'][which]

unsorted_codes = hp.causedict.values()
unsorted_names = hp.causedict.keys()
order = pl.argsort(unsorted_codes)
codes = [unsorted_codes[i] for i in order]
names = [unsorted_names[i] for i in order]
dalys = pl.array([afg[name] for name in names])
causeinds = range(len(order))

dd = sc.odict()
cd = sc.odict()
for c in causeinds:
    cd[codes[c]] = names[c]
    dd[codes[c]] = round(dalys[c])


h0 = dd['T']
h1 = sum(dd[['A','B','C']])

hierarchy = sc.odict()
for code in codes:
    hierarchy[code] = []
    for code2 in codes:
        relationship = hp.burdenhierarchy(code, code2)
        if relationship == 'child':
            hierarchy[code].append(code2)

problems = sc.odict()
for code in codes:
    total = dd[code]
    string = f'{code:10} Total: {total:8.0f}'
    if hierarchy[code]:
        children = sum(dd[hierarchy[code]])
        ratio = total/children
        string += f' Children: {children:8.0f} Ratio: {ratio:5.3f}'
        if not sc.approx(ratio, 1, 0.01):
            problems[code] = ratio
    print(string)

print('Done.')