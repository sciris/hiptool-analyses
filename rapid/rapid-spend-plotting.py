import pylab as pl
import sciris as sc

dosave = True
fig1 = True

sc.heading('Loading data...')
interv_data = sc.loadspreadsheet('rapid_interventions.xlsx')
spend_data = sc.loadspreadsheet('rapid_spending.xlsx')
D = sc.loadobj('results/rapid_spend_data.obj')
R = sc.loadobj('results/rapid_spend_results.obj')


#%% Fig. 1 -- DALYs
if fig1:
    sc.heading('Spending figure')
    interv_category = interv_data['Category 1'].tolist()
    categories = sorted(set(interv_category))
    ncategories = len(categories)
    nintervs = len(R[0]['alloc'])
    mapping = []
    for i_c in interv_category:
        for c,cat in enumerate(categories):
            if i_c == cat:
                mapping.append(c)
    
    allocdata = pl.zeros((2, ncategories))
    for country in R.keys(): # tODO: different regions
        opt_alloc = R[country]['alloc']
        orig_alloc = spend_data[country]
        for i in range(nintervs):
            c = mapping[i]
            allocdata[0,c] += orig_alloc[i]
            allocdata[1,c] += opt_alloc[i]
    
    fig = pl.figure()
    x = pl.arange(2)
    axlist = []
    previous = pl.zeros(2)
    for c in range(len(categories)):
        current = allocdata[:,c]/1e9
        ax = pl.bar(x, current, bottom=previous)
        previous += current
        axlist.append(ax)
    
    xticks = ['Current', 'Optimal']
    pl.ylabel('Spending (US$ billions)')
    pl.title('Spending annually by disease area across 39 countries')
    pl.xticks(x, xticks)
    pl.xlabel('EUHC expenditure')
    pl.legend([ax[0] for ax in axlist], categories)
    sc
    
    pl.show()
    
    if dosave:
        pl.savefig('results/rapid_spend_alloc.png', dpi=200)




print('Done.')