'''
    This code visualizes the UAVSAR acquistions: use the acquisition dates for a timeline plot
    -- Heming Liao --
    -- hliao@alaska.edu --
'''

import glob
import os
import matplotlib.pyplot as plt
import datetime
from dateutil import relativedelta
import matplotlib.dates as mdates
import numpy as np

sites = ('NISARA_06800','SanAnd_05508','SDelta_23518','winnip_31606')

uavsar_dir = '/10TBstorage/Heming/UAVSAR_Heming/'

for site_name in sites:
    site_dir = glob.glob(uavsar_dir + site_name + '*')
    print('processing UAVSAR site: ' + site_dir[0].split('/')[-1])
    list_dir = os.listdir(site_dir[0])
    for item in list_dir:
        # whether there is a subdirectory(e.g segment1,segment2,...) under site_name
        if os.path.isdir(os.path.join(site_dir[0],item)):
            site_dir_new = os.path.join(site_dir[0], item)
            #print(site_dir_new)
            acq_date_list = [(file_name.split('_')[-4])  for file_name in glob.glob(os.path.join(site_dir_new, '*HH*.ann'))]
            acq_date_list_sort = sorted(acq_date_list)
            print('sorted acquisition dates: ')
            print(acq_date_list_sort)
            break
        if os.path.isfile(os.path.join(site_dir[0],item)):
            acq_date_list = [(file_name.split('_')[-4])  for file_name in glob.glob(os.path.join(site_dir[0], '*HH*.ann'))]
            acq_date_list_sort = sorted(acq_date_list)
            print('sorted acquisition dates: ')
            print(acq_date_list_sort)
            break

    # plot the time series acquisition dates on a plot
    dates_list = []
    for date in acq_date_list_sort:
        dates_list.append(datetime.datetime.strptime(date, '%y%m%d'))

    acq_Nums = len(dates_list)

    if acq_Nums>20:
        tile_value = [0.1, 0.25]
    else:
        tile_value = [0.1, 0.1]

    levels = np.tile(tile_value,
                     int(np.ceil(len(dates_list)/2)))[:len(dates_list)]

    # Create figure and plot a stem plot with the date
    fig, ax = plt.subplots(figsize=(14, 4), constrained_layout=True)
    #ax.set(title="UAVSAR acquisitions: " + site_name.split('_')[0],FontSize=12)
    fig.suptitle("UAVSAR acquisitions: " + site_name.split('_')[0],FontSize=12)

    markerline, stemline, baseline = ax.stem(dates_list, levels,
                                         linefmt="C1-", basefmt="k-")
    plt.setp(markerline, mec="r", mfc="w", zorder=1)

    # Shift the markers to the baseline by replacing the y-data by zeros.
    markerline.set_ydata(np.zeros(len(dates_list)))

    # annotate lines
    vert = np.array(['top', 'bottom'])[(levels > 0).astype(int)]
    for d, l, r, va in zip(dates_list, levels, acq_date_list_sort, vert):
        ax.annotate(r, xy=(d, l), xytext=(20, np.sign(l)*3),
                textcoords="offset points", va=va, ha="right",rotation=60)
    
    # format xaxis with 1 or 2 or 3 month intervals
    if acq_Nums>=40:  #the 60,30 value is a rough value, can be changed if necessary.
        interval_value = 3
    elif acq_Nums<40 and acq_Nums>=20:
        interval_value = 2
    elif acq_Nums<20:
        interval_value = 1
    ax.get_xaxis().set_major_locator(mdates.MonthLocator(interval=interval_value))
    ax.get_xaxis().set_major_formatter(mdates.DateFormatter("%Y/%m"))
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

    # remove y axis and spines
    ax.get_yaxis().set_visible(False)
    for spine in ["left", "top", "right"]:
        ax.spines[spine].set_visible(False)

    ax.margins(y=0.1)
    plt.ylim(-0.03,1.4*tile_value[-1])
    plt.show()
    outdir = '/10TBstorage/Heming/coherence/results/timeline_plots'
    outfig = os.path.join(outdir,site_name.split('_')[0] + '-acquisitions-timeline.pdf')
    plt.savefig(outfig,dpi=300)
    print('\n')



