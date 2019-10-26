import sciris as sc
import pylab as pl
import hiptool as hp

fn = 'gbd-data.dat'
bod = sc.loadobj(fn)

# DALYs match up, deaths almost do, prevalence does not
which = {'dalys':0, 'deaths':1, 'prevalence':2}['dalys']

afg = bod['Afghanistan'][which]

codes = hp.burdeninfo.dict.keys()
names = hp.burdeninfo.dict.values()
dalys = pl.array([afg[name] for name in names])

dd = sc.odict()
for c,code in enumerate(codes):
    dd[code] = round(dalys[c])

problems = sc.odict()
for code in codes:
    total = dd[code]
    string = f'{code:10} Total: {total:8.0f}'
    if hp.burdeninfo.children[code]:
        children = sum(dd[hp.burdeninfo.children[code]])
        ratio = total/children
        string += f' Children: {children:8.0f} Ratio: {ratio:5.3f}'
        if not sc.approx(ratio, 1, 0.01):
            problems[code] = ratio
    print(string)

print('Done.')