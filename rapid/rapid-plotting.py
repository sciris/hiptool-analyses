import pylab as pl
import sciris as sc

dosave = True
fig1 = 0
fig2 = 0
fig3 = 1

sc.heading('Loading data...')
country_data = sc.loadspreadsheet('country-data.xlsx')
interv_data = sc.loadspreadsheet('rapid_interventions.xlsx')
D = sc.loadobj('results/rapid_data.obj')
R = sc.loadobj('results/rapid_results.obj')


def dalys_fig(label='', region=None, income=None):
    sc.heading('DALYs figure')
    category1 = interv_data['Category 1'].tolist()
    category2 = interv_data['Category 2'].tolist()
    interv_category = [c1+': '+c2 for c1,c2 in zip(category1, category2)]
    categories = sorted(set(interv_category))
    ncategories = len(categories)
    nspends, nintervs = R[0]['dalys'].shape
    mapping = []
    for i_c in interv_category:
        for c,cat in enumerate(categories):
            if i_c == cat:
                mapping.append(c)
    
    dalydata = pl.zeros((nspends, ncategories))
    for co,country in enumerate(R.keys()):
        proceed = True
        if region and country_data['who_region',co] != region:
            proceed = False # Could use continue
        if income and country_data['income_group',co] != income:
            proceed = False # Could use continue
        if proceed:
            dalys = R[country]['dalys']
            for i in range(nintervs):
                c = mapping[i]
                dalydata[:,c] += dalys[:,i]
    
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
        current = dalydata[:,c]/1e6
        ax = pl.bar(x, current, bottom=previous, facecolor=colors[c])
        previous += current
        axlist.append(ax)
        
    xticks = ['$%s' % val for val in [0.1, 0.3, 1, 3, 10, 30, 100, 300, '1k', '3k', '10k']]
    pl.ylabel('DALYs averted (millions)')
    titletext = 'DALYs averted annually by funding level and disease area'
    if label: titletext += ': ' + label
    pl.title(titletext)
    pl.xticks(x, xticks)
    pl.xlabel('EUHC expenditure per person per year')
    pl.legend([ax[0] for ax in axlist][::-1], categories[::-1])
    
    pl.show()
    
    if dosave:
        connector = '' if not label else '-'
        pl.savefig(f'results/rapid_dalys-averted{connector}{label}.png', dpi=200)
    return fig



def alloc_fig(label='', region=None, income=None, byplatform=False, logscale=False):
    sc.heading('Allocation figure')
    if not byplatform:
        category1 = interv_data['Category 1'].tolist()
        category2 = interv_data['Category 2'].tolist()
        iter_category = [c1+': '+c2 for c1,c2 in zip(category1, category2)]
    else:
        iter_category = interv_data['Platform'].tolist()
    categories = sorted(set(iter_category))
    print(categories)
    if byplatform:
        order = [3,0,2,1,4]
        categories = [categories[o] for o in order]
    ncategories = len(categories)
    nspends, nintervs = R[0]['alloc'].shape
    mapping = []
    for i_c in iter_category:
        for c,cat in enumerate(categories):
            if i_c == cat:
                mapping.append(c)
    
    allocdata = pl.zeros((nspends, ncategories))
    for co,country in enumerate(R.keys()):
        proceed = True
        if region and country_data['who_region',co] != region:
            proceed = False # Could use continue
        if income and country_data['income_group',co] != income:
            proceed = False # Could use continue
        if proceed:
            alloc = R[country]['alloc']
            for i in range(nintervs):
                c = mapping[i]
                allocdata[:,c] += alloc[:,i]
    
    fig = pl.figure(figsize=(10,8))
    ax = fig.add_axes([0.08, 0.08, 0.65, 0.85])
    x = pl.arange(nspends)
    axlist = []
    previous = pl.zeros(nspends)
    
    if not byplatform:
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
    else:
        colors = [
              (0.9, 0.5, 0.0),
              (0.0, 0.5, 0.9),
              (0.0, 0.7, 0.4),
              (0.0, 0.8, 0.5),
              (0.0, 0.9, 0.6),
              ]
        colors = colors[::-1]
    
    for c in range(len(categories)):
        if not logscale:
            current = allocdata[:,c]/allocdata.sum(axis=1)*100
        else:
            current = allocdata[:,c]/1e9
        ax = pl.bar(x, current, bottom=previous, facecolor=colors[c])
        previous += current
        axlist.append(ax)
        
    xticks = ['$%s' % val for val in [0.1, 0.3, 1, 3, 10, 30, 100, 300, '1k', '3k', '10k']]
    if not logscale:
        pl.ylabel('Allocation (%)')
    else:
        pl.ylabel('Allocation (US$, billions)')
    if not byplatform:
        titletext = 'Spending annually by funding level'
    else:
        titletext = 'Spending annually by funding level'
    if label: titletext += ': ' + label
    pl.title(titletext)
    pl.xticks(x, xticks)
    pl.xlabel('EUHC expenditure per person per year')
    pl.legend([ax[0] for ax in axlist][::-1], categories[::-1], bbox_to_anchor=(1,0.8))
#    pl.gca().set_yscale('log')
    
    pl.show()
    
    if dosave:
        connector = '' if not label else '-'
        pl.savefig(f'results/rapid_alloc{connector}{label}.png', dpi=200)
    return fig



#%% Fig. 3 -- interventions
def common_interventions(region=None, income=None, byplatform=False, max_entries=10, entry=None, label=''):
    sc.heading('Top interventions figure')
    if not byplatform:
        category_list = interv_data['Category 1'].tolist()
    else:
        category_list = interv_data['Platform'].tolist()
    categories = sorted(set(category_list))
    if byplatform:
        order = [3,0,2,1,4]
        categories = [categories[o] for o in order]
    keycols = ['Short name', 'Category 1', 'Category 2', 'Platform', 'ICER']
    df = sc.dataframe(cols=keycols+['Percent'], nrows=len(interv_data))
    for key in keycols:
        df[key] = interv_data[key]
    df['Percent'] = 0.0
    df.sort('Short name')
    
    nspends, nintervs = R[0]['alloc'].shape
    all_counts = pl.zeros((nspends, nintervs))
    include_counts = sc.dcp(all_counts)
    for co,country in enumerate(R.keys()):
        proceed = True
        if region and country_data['who_region',co] != region:
            proceed = False # Could use continue
        if income and country_data['income_group',co] != income:
            proceed = False # Could use continue
        if proceed:
            alloc = R[country]['alloc']
            counts = pl.array(alloc>0, dtype=float)
            if entry is None:
                entries = range(nspends)
            else:
                entries = [entry]
            for i in entries:
                for j in range(nintervs):
                    all_counts[i,j] += 1
                    include_counts[i,j] += counts[i,j]
    
    for j in range(nintervs):
        include = include_counts[:,j].sum()
        total = all_counts[:,j].sum()
        df['Percent',j] = include / total
        
    # Ensure sorted!!
    data = sc.odict().make(keys=categories, vals=[])
    counts = sc.odict().make(keys=categories, vals=0)
    df.sort(col='Percent', reverse=True)
    for j in range(nintervs):
        if byplatform:
            this_category = df['Platform',j]
        else:
            this_category = df['Category 1',j]
        if counts[this_category] < max_entries:
            data[this_category].append(df[j].tolist())
            counts[this_category] += 1
        
    
        
    if dosave:
        df.export('results/rapid_top-interventions.xlsx')

    fig = pl.figure(figsize=(9,17))
    ax = fig.add_axes([0.5,0.1,0.45,0.85])
    count = 50
    ticklocs = []
    ticklabels = []
    if not byplatform:
        darkest = [pl.array([0.5, 0.1, 0.0]),
                   pl.array([0.0, 0.1, 0.5]),
                   pl.array([0.5, 0.0, 0.5]),
                   pl.array([0.1, 0.5, 0.0]),
                   ]
    else:
        darkest = [
              (0.5, 0.2, 0.0),
              (0.0, 0.2, 0.5),
              (0.0, 0.5, 0.0),
              (0.0, 0.5, 0.3),
              (0.0, 0.3, 0.5),
              ]
        darkest = darkest[::-1]
        
    
    position = df.cols.index('Percent')
    for k,key,vals in sc.odict(data).enumitems():
        count -= 2
        count2 = 0
        pl.text(-2, count, key, fontweight='bold', horizontalalignment='right', fontsize=6)
        maxval = len(vals)
        for row in vals:
            count -= 1
            count2 += 1
            thiscolor = darkest[k] + (count2/(maxval*2))*pl.array([1,1,1])
            ticklocs.append(count)
            ticklabels.append(row[0])
            percentage = float(row[position])*100 # WARNING, fragile!!
            pl.barh(count, percentage, facecolor=thiscolor, edgecolor='none')
    
    ax.set_yticks(ticklocs)
    ax.set_yticklabels(ticklabels, fontsize=4)
    ax.set_title(label)
    pl.xlim([0,100])
    pl.xlabel('Frequency of inclusion of intervention in EUHC package (%)')
    
    if dosave:
        connector = '' if not label else '-'
        pl.savefig(f'results/rapid_top-interventions{connector}{label}.png', dpi=200)
    return fig
        
    
    
#%% Fig. 1 -- DALYs
if fig1:
#    dalys_fig(label='Global')
#    dalys_fig(region='EUR', label='Europe')
    dalys_fig(region='AFR', label='Africa')
#    dalys_fig(income='Low income', label='Low-income')
#    dalys_fig(income='High income', label='High-income')

if fig2:
#    alloc_fig(label='Global')
    alloc_fig(label='platforms (Africa)', region='AFR', byplatform=True, logscale=True)
#    alloc_fig(region='EUR', label='Europe')
    alloc_fig(region='AFR', label='disease area (Africa)', logscale=True)
#    alloc_fig(income='Low income', label='Low-income')
#    alloc_fig(income='High income', label='High-income')

if fig3:
    common_interventions(region='AFR', income=None, byplatform=False, max_entries=100, entry=2, label='Africa (by disease area), USD1 pp')
    common_interventions(region='AFR', income=None, byplatform=True, max_entries=100, entry=2, label='Africa (by platform), USD1 pp')
    common_interventions(region='AFR', income=None, byplatform=False, max_entries=100, entry=4, label='Africa (by disease area), USD10 pp')
    common_interventions(region='AFR', income=None, byplatform=True, max_entries=100, entry=4, label='Africa (by platform), USD10 pp')
    common_interventions(region='AFR', income=None, byplatform=False, max_entries=100, entry=6, label='Africa (by disease area), USD100 pp')
    common_interventions(region='AFR', income=None, byplatform=True, max_entries=100, entry=6, label='Africa (by platform), USD100 pp')
    
    
    
    
    


print('Done.')