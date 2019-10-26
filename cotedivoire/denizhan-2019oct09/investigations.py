import hiptool as hp

burdenfile  = 'civ_burdenset_ck.xlsx'
intervfile  = 'civ_interventions_ck.xlsx'
do_optimize = False # Whether or not to run the optimization
do_plot     = False # Whether or not to plot

P = hp.Project()
P.loadburden(burdenfile)
P.loadinterventions(intervfile)
P.makepackage()

if do_optimize:
    P.package().optimize()

if do_plot:
    fig1 = P.package().plot_spending(which='current')
    fig2 = P.package().plot_spending(which='optimized')
    fig3 = P.package().plot_dalys(which='current')
    fig4 = P.package().plot_dalys(which='optimized')
    fig5 = P.package().plot_cascade()