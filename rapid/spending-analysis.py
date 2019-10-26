import pylab as pl
import sciris as sc
import hiptool as hp

sc.heading('Initializing...')
sc.tic()

dosave = True
missing_data = ['remove', 'assumption'][1] # Choose how to handle missing data

# Load input files
D = sc.odict() # Data
R = sc.odict() # Results
bod_data = sc.loadobj('gbd-data.dat')
country_data = sc.loadspreadsheet('country-data.xlsx')
spend_data = sc.loadspreadsheet('rapid_spending.xlsx')
baseline_factor = country_data.findrow('Zambia', asdict=True)['icer_multiplier'] # Zambia was used for this

# Get country list
countries = sc.dcp(spend_data.cols)
countries.remove('Short name')

# Create default
P = hp.Project()
P.loadburden(filename='rapid_BoD.xlsx')
P.loadinterventions(filename='rapid_interventions.xlsx')
ninterventions = P.intervsets[0].data.nrows

# Load data
sc.heading('Loading data...')
for c,country in enumerate(countries):
    print(f'  Working on {country}...')
    D[country] = sc.dcp(P)
    
    # Replace with actual burden data
    for k,key in enumerate(['DALYs', 'Deaths', 'Prevalence']):
        D[country].burden().data[key] = bod_data[country][k][:]
    
    # Adjust interventions
    for key in ['Unit cost', 'ICER']:
        this_factor = country_data['icer_multiplier'][c]
        
        df = D[country].interv().data
        missing_inds = sc.findinds(df[key]<0)
        if len(missing_inds):
            if missing_data == 'remove':
                df.rmrows(missing_inds)
            elif missing_data == 'assumption':
                for ind in missing_inds:
                    df['Unit cost', ind] = 1.0 # WARNING, completely arbitrary!
                    df['ICER', ind] = 66 
        
        D[country].interv().data[key] *= this_factor/baseline_factor


# Analysis
sc.heading('Analyzing...')
def optimize(D, country_data, country, c):
    print(f'  Working on {country} ({c+1}/{len(country_data)})...')
    D[country].makepackage(verbose=False)
    meta = country_data.findrow(country, asdict=True)
    
    spend = spend_data[country].sum()
    D[country].package().optimize(budget=spend)
    df = D[country].package().data
    alloc = sc.dcp(df['opt_spend'][:])
    dalys = sc.dcp(df['opt_dalys_averted'][:])
    result = sc.odict({'meta':meta, 'alloc':pl.array(alloc), 'dalys':pl.array(dalys), 'package':D[country].package()})
    return result

results = sc.parallelize(optimize, iterkwargs={'c':list(range(len(countries))), 'country':countries}, kwargs={'D':D, 'country_data':country_data})
for r,result in enumerate(results):
    R[countries[r]] = result



# Saving
if dosave:
    sc.heading('Saving...')
    sc.saveobj('results/rapid_spend_data.obj', D)
    sc.saveobj('results/rapid_spend_results.obj', R)


sc.toc()
print('Done.')