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

def FindPlantingHarvestTime(y_train,jbands):
	# # mencari nilai absolute FFT yang maximum nomornya
    Y = y_train
    bandsinp = jbands

    YX = np.zeros((bandsinp+2),dtype=np.uint16)
    YX[1:bandsinp+1] =Y[0:bandsinp]
    YX[bandsinp+1]=Y[0]
    YX[0]=Y[bandsinp-1]
    Y = YX

    TP1 = 0
	# Data mulai nomor 1 sampai dengan 31 karena diganti dari YX
    for i in range(1,bandsinp+1):
        y_1=Y[i-1]; y0=Y[i]; y1=Y[i+1]
        if(y_1>y0) and (y0<y1):
            TP1 = i; break
    TP2 = 0
    for i in range(TP1+2,bandsinp+1):
        y_1=Y[i-1]; y0=Y[i]; y1=Y[i+1]
        if(y_1>y0) and (y0<y1):
            TP2 = i; break
    if(TP1==0): TP2=0
    TP3 = 0
    for i in range(TP2+2,bandsinp+1):
        y_1=Y[i-1]; y0=Y[i]; y1=Y[i+1]
        if(y_1>y0) and (y0<y1):
            TP3 = i; break
    if(TP2==0): TP3=0
    
    TH1 = 0
	# Data mulai nolomor 0 sampai dengan 30
    for i in range(1,bandsinp+1):
        y_1=Y[i-1]; y0=Y[i]; y1=Y[i+1]
        if(y_1<y0) and (y0>y1):
            TH1 = i; break
    TH2 = 0
    for i in range(TH1+2,bandsinp+1):
        y_1=Y[i-1]; y0=Y[i]; y1=Y[i+1]
        if(y_1<y0) and (y0>y1):
            TH2 = i; break
    if(TH1==0): TH2=0
    TH3 = 0
    for i in range(TH2+2,bandsinp+1):
        y_1=Y[i-1]; y0=Y[i]; y1=Y[i+1]
        if(y_1<y0) and (y0>y1):
            TH3 = i; break
    if(TH2==0): TH3=0
    
    TH0=0
    if(TH1<TP1): TH0=TH1; TH1=TH2; TH2=TH3; TH3=0
	
    TPH = np.zeros((7),dtype=np.uint8)
    TPH[0]=TH0;TPH[1]=TP1;TPH[2]=TH1;TPH[3]=TP2;TPH[4]=TH2;TPH[5]=TP3;TPH[6]=TH3; 
    return TPH

def main():
    #membuka data raster  menjadi array
    file_Input =sys.argv[1]
    file_output = os.path.splitext(file_Input)[0]+'_PlanHarvTime.tif' 
    print("Paddy Field Monitoring:")
    print("Input Image  :", file_Input)
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
    bandsout = 7
    proj_ref = ds2.GetProjectionRef()
    training_features = np.zeros((rows*cols,bands),dtype=np.uint16)
    res = np.zeros((rows*cols,bandsout),dtype=np.uint16)
    
    for band in range(bands):
        training_features[:,band]= (ds2.GetRasterBand(jbands-bands+band+1).ReadAsArray().astype(np.uint16)).flatten()
        
    ds2 = None
    for x in range(rows*cols):
        res[x,:] = FindPlantingHarvestTime(training_features[x,:],jbands)         
        
    res_3d = np.zeros((bandsout,rows,cols),dtype=np.uint16)
    for i in range(bandsout):
        res_3d[i,:,:] = res[:,i].reshape(rows,cols)
        
    #menulisakan hasil dalam raster file_output format geotif 
    driver1 = gdal.GetDriverByName('Gtiff')    
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
   
     
 
