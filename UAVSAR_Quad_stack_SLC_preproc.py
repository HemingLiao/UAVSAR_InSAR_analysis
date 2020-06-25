'''
    Multi-looking processing for multi-temporal full-polarimetric UAVSAR SAR data
'''

import os
import sys
import glob
import numpy as np
from scipy import ndimage
from scipy.special import comb
import matplotlib.pyplot as plt
import IO

def multilook_cpx(cpx_im,ML_Numi=(2,2)):
    '''
       multi-look processing of a complex SLC (matrix)
    '''
    sout = (cpx_im.shape[0] // ML_Num[0], cpx_im.shape[1] // ML_Num[1])
    im_real = cpx_im[0:sout[0]*ML_Num[0],0:sout[1]*ML_Num[1]].real
    im_imag = cpx_im[0:sout[0]*ML_Num[0],0:sout[1]*ML_Num[1]].imag
    im_real_ml = im_real.reshape([im_real.shape[0]//ML_Num[0], ML_Num[0], im_real.shape[1]//ML_Num[1], ML_Num[1]]).mean(3).mean(1)
    im_imag_ml = im_imag.reshape([im_imag.shape[0]//ML_Num[0], ML_Num[0], im_real.shape[1]//ML_Num[1], ML_Num[1]]).mean(3).mean(1)
    cpx_im_ml = im_real_ml + 1j*im_imag_ml
    return cpx_im_ml

def coherence_2SLCs(cpx_im1,cpx_im2,cc_wind=(5,5)):
    '''
       coherence of two co-registered complex images
    '''
    coherence = np.zeros(cpx_im1.shape)
    intf_cpx = cpx_im1*np.conj(cpx_im2)
    im1_intensity = np.square(np.abs(cpx_im1))
    im2_intensity = np.square(np.abs(cpx_im2))
    intf_cpx_ave = ndimage.uniform_filter(intf_cpx.real, size=cc_wind) + 1j * ndimage.uniform_filter(intf_cpx.imag, size=cc_wind)
    im1_intensity_ave = ndimage.uniform_filter(im1_intensity,size=cc_wind)
    im2_intensity_ave = ndimage.uniform_filter(im2_intensity,size=cc_wind)
    coherence = np.abs(intf_cpx_ave*cc_wind[0]*cc_wind[1])/np.sqrt((im1_intensity_ave*cc_wind[0]*cc_wind[1])*(im2_intensity_ave*cc_wind[0]*cc_wind[1]))
    return coherence


data = ['CValle_13300_07','grmesa_07805','Howlnd_16701','Laurnt_18801','Mondah_27080',
        'Rosamd_35012','SanAnd_05508','winnip_31606','NISARA_06800_01', 'SanAnd_05508_03',
        'SDelta_23518_02', 'winnip_31606_01','winnip_31606_01']

segment_list = [2, 2, 3, 4, 1, 1, 1, 1, 1, 1, 1, 1, 2]
cmlversion_list = ['1x1', '1x1', '1x1', '1x1', '1x1', '1x1','1x1','1x1','2x8','2x8','2x8','2x8', '2x8']

polarizations = ['HH','HV','VH','VV']

path0 = '/10TBstorage/Heming/coherence/'


for count,site in enumerate(data[12:],12):
    path1 = '/10TBstorage/Heming/UAVSAR_Heming/' + site + '/'
    temp = [file_name.split('/')[5][13:29] for file_name in glob.glob(os.path.join(path1,'*HH*.ann'))]
    dataset = sorted(temp)
    #print(dataset)
    
    acq_Num = len(dataset)      # Number of multiple temporal observations
    segment = segment_list[count]
    cmlversion = cmlversion_list[count]
    ML_Num = (2,3) # azimuth x range. 10m resolution in the multi-look product
    rg_ML = ML_Num[-1]*int(cmlversion[0])
    azi_ML = ML_Num[0]*int(cmlversion[-1])

    print('Start processing site: ' + site + ' segment: ' + str(segment))
    print('Multi-looking (azi x rg): ' + str(azi_ML) + 'x' + str(rg_ML) )
    # read/save each of the multi-temporal data for specific dataset: site
    for index in range(len(dataset)):
        imageName = dataset[index:index+1]
        print('Reading/save dataset:' + site + ',' + str(imageName).strip('[:]'))
        #breakpoint()
        stackPolSLC = IO.UAVSARReadQuadPolStack(imageName, pathuav=path1, segment=segment, cmlversion=cmlversion, polarizations = polarizations)      # complex data type
        stackml = np.zeros((stackPolSLC.shape[0]//ML_Num[0],stackPolSLC.shape[1]//ML_Num[1],stackPolSLC.shape[2])) +1j*np.zeros((stackPolSLC.shape[0]//ML_Num[0],stackPolSLC.shape[1]//ML_Num[1],stackPolSLC.shape[-1]))
        for pol in range(stackPolSLC.shape[-1]):
            stackml[:,:,pol] = multilook_cpx(stackPolSLC[:,:,pol],ML_Num)
        output_ML_SLC = path0 + 'results/npy_new_data/' + site.split('_')[0] + '_' + imageName[0].split('_')[-1] + '_seg' + str(segment) + '_rg'+ str(int(cmlversion[0])*ML_Num[-1]) +'_azi'+ str(int(cmlversion[-1])*ML_Num[0])+ '_ML_SLC'
        np.save(output_ML_SLC,stackml)
        del stackPolSLC
    print('\n')
 

########################################################################################################################
########################Generate all possible combinations##############################################################
########################################################################################################################
'''    phases = []
    coherences = []
    # phase
    for pp in range(len(polarizations)):
        print('Calculate/Save ' + site.split("_")[0] + polarizations[pp] + ' polarization ' + 'InSAR Phase')
        for kk in range(len(dataset)):
            for jj in range(kk+1,len(dataset)):
                print('dataset: ' + dataset[kk][-6:] + '-' + dataset[jj][-6:])
                phases = np.angle( stackml_list[kk][:,:,pp]*np.conj(stackml_list[jj][:,:,pp]) )
                # save the array
                output = path0 + '/results/npy/' + site.split("_")[0] + polarizations[pp] + '-' + dataset[kk][-6:] + '-' + dataset[jj][-6:] + '-ph'
                np.save(output,phases)

    # coherence
    for pp in range(len(polarizations)):
        print('Calculate/Save ' + site.split("_")[0] + polarizations[pp] + ' polarization ' + 'InSAR Coherence')
        for kk in range(acq_Num):
            for jj in range(kk+1,acq_Num):
                print('dataset: ' + dataset[kk][-6:] + '-' + dataset[jj][-6:])
                coherences = coherence_2SLCs(stackml_list[kk][:,:,pp],(stackml_list[jj][:,:,pp]))
                output = path0 + '/results/npy/' + site.split("_")[0] + polarizations[pp] + '-' + dataset[kk][-6:] + '-' + dataset[jj][-6:] + '-cc'
                np.save(output,coherences)
'''


'''
#############################################one figure for each plot##################################################
    # phase
    for pp in range(len(polarizations)):
        print('Calculate ' + polarizations[pp] + ' polarization ' + 'InSAR phase and coherence')
        for kk in range(len(dataset)):
            for jj in range(kk+1,len(dataset)):
                if (kk == 0) | (jj == kk+1):
                    print('Dataset: ' + site.split("_")[0] + ',' + dataset[kk][-6:] + '-' + dataset[jj][-6:])
                    phases = np.angle( stackml_list[kk][:,:,pp]*np.conj(stackml_list[jj][:,:,pp]) )
                    # save the array
                    output = path0 + '/results/npy/' + polarizations[pp] + '-' + dataset[kk][-6:] + '-' + dataset[jj][-6:] + '-ph'
                    np.save(output,phases)
                    # phase
                    fig,ax = plt.subplots(figsize=(phases.shape[1]/800,phases.shape[0]/800))
                    ax.imshow(phases,cmap='jet',vmin = -np.pi, vmax = np.pi)
                    ax.set_title(polarizations[pp] + '-' + dataset[kk][-6:] + '-' + dataset[jj][-6:], FontSize=10)
                    ax.set_xticks([])
                    ax.set_yticks([])
                    plt.subplots_adjust(left=0.01,right=0.99,bottom=0.01,top=0.94)
                    #fig.suptitle(site.split("_")[0],FontSize=25)
                    fig.savefig(os.path.join(path0,'results/') + site.split("_")[0] + '-' + polarizations[pp] + '-' + dataset[kk][-6:] + '-' + dataset[jj][-6:] + '-phase.pdf', dpi=300)
                    # coherence
                    coherences = coherence_2SLCs(stackml_list[kk][:,:,pp],(stackml_list[jj][:,:,pp]))
                    output = path0 + '/results/npy/' + polarizations[pp] + '-' + dataset[kk][-6:] + '-' + dataset[jj][-6:] + '-cc'
                    np.save(output,coherences)
                    fig,ax = plt.subplots(figsize=(coherences.shape[1]/800,coherences.shape[0]/800))
                    ax.imshow(coherences,cmap='gray',vmin = 0, vmax = 1)
                    ax.set_title(polarizations[pp] + '-' + dataset[kk][-6:] + '-' + dataset[jj][-6:], FontSize=10)
                    ax.set_xticks([])
                    ax.set_yticks([])
                    plt.subplots_adjust(left=0.01,right=0.99,bottom=0.01,top=0.94)
                    #fig.suptitle(site.split("_")[0],FontSize=25)
                    fig.savefig(os.path.join(path0,'results/') + site.split("_")[0] + '-' + polarizations[pp] + '-' + dataset[kk][-6:] + '-' + dataset[jj][-6:] + '-coherence.pdf', dpi=300)
                    plt.close('all')
                else:
                   print('skip ' + polarizations[pp] + '-' + dataset[kk][-6:] + '-' + dataset[jj][-6:])
'''



