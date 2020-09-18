# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 13:01:08 2020

@author: randy
"""

import numpy as np
from osgeo import gdal, osr
gdal.PushErrorHandler('CPLQuietErrorHandler')
gdal.UseExceptions()
import sys, os, tqdm
from multiprocessing import Pool

import numpy as np

def Phase_Paddy_eachDays(y_train):

	# # mencari nilai absolute FFT yang maximum nomornya
    bandsinp = 40
    Y = y_train
    TP1=Y[2]; TH1=Y[3]; TP2=Y[4]; TH2=Y[5]; TP3=Y[6]; TH3=Y[7]; 
    # nomor mulai 1 sd 31
    TG1=0; TG2=0; TG3=0
    if(TH1>TP1): TG1 = TH1-TP1; 
    if(TH2>TP2): TG2 = TH2-TP2; 
    if(TH3>TP3): TG3 = TH3-TP3;

    Phase = np.zeros((bandsinp),dtype=np.uint8)
    if(TH1>40): TH1=40
    if(TP1<TH1):
         for i in range(TP1-1,TH1):
             DNPhase = i+2-TP1
             PhasePaddy = ((DNPhase * 4)/(TG1+1)) +0.5
             Phase[i]=PhasePaddy
    if(TH2>40): TH2=40
    if(TP2<TH2):
         for i in range(TP2-1,TH2):
             DNPhase = i+2-TP2
             PhasePaddy = ((DNPhase * 4)/(TG2+1)) +0.5
             Phase[i]=PhasePaddy
    if(TH3>40): TH3=40
    if(TP3<TH3):
         for i in range(TP3-1,TH3):
             DNPhase = i+2-TP3
             PhasePaddy = ((DNPhase * 4)/(TG3+1)) +0.5
             Phase[i]=PhasePaddy
    for i in range(0,9):
        Phase[i] = Phase[i+31] + Phase[i]
    
    res = Phase[0:31]
    return res

def main():
    #membuka data raster  menjadi array
    file_Input =sys.argv[1]
    file_output = sys.argv[2] 
    print("Paddy Field Monitoring:")
    print("Input_Image:",file_Input)
    print("Output Image :", file_output)
    
    ds2 = gdal.Open(file_Input)
    if ds2 is None:
        print ('Tidak bisa membaca %s' %file_Input)
        sys.exit(1)
    gt = ds2.GetGeoTransform()
    rows = ds2.RasterYSize
    cols = ds2.RasterXSize
    jbands = ds2.RasterCount
	# bands_index = np.arange(jbands) + 1
    bands = jbands #ds2.RasterCount
    bandsout = 31
    proj_ref = ds2.GetProjectionRef()
    training_features = np.zeros((rows*cols,bands),dtype=np.uint16)
    res = np.zeros((rows*cols,bandsout),dtype=np.uint16)
    
    for band in range(bands):
        training_features[:,band]= (ds2.GetRasterBand(jbands-bands+band+1).ReadAsArray().astype(np.uint16)).flatten()
        
    ds2 = None
    for x in range(rows*cols):
        res[x,:] = Phase_Paddy_eachDays(training_features[x,:])         
        
    res_3d = np.zeros((bandsout,rows,cols),dtype=np.uint16)
    for i in range(bandsout):
        res_3d[i,:,:] = res[:,i].reshape(rows,cols)
        
    #menulisakan hasil dalam raster file_output format geotif 
    driver1 = gdal.GetDriverByName('GTiff')    
    outRaster = driver1.Create(file_output, cols, rows, bandsout, gdal.GDT_UInt16)
    outRaster.SetGeoTransform(gt)
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromWkt(proj_ref)
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    
    for band in range(bandsout):
        outband = outRaster.GetRasterBand(band+1); outband.WriteArray(res_3d[band,:,:]); outband.SetNoDataValue(0)
    
	#Properly close the datasets to flush to disk
    outband.FlushCache() 
    outRaster.FlushCache()
    
if __name__ == '__main__':
    main()
   
 
