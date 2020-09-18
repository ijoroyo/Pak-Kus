# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 13:01:08 2020

@author: randy
"""

from osgeo import gdal, osr
gdal.PushErrorHandler('CPLQuietErrorHandler')
gdal.UseExceptions()
import sys, os, tqdm
from multiprocessing import Pool
import tqdm

import numpy as np

  
def transformasi(y_train):
    # # Transformasi time series data menjadi FFT 
    freq = np.fft.fft(y_train)
    # # Hasil FFT hanya digunakan untuk FFT 1 sd FFT 9, FFT ke-10 dst dihilangkan (dijadikan 0)
    freq[4:]=0
    # # Transformasi Invers FFT     
    return np.fft.ifft(freq).real

def main():
    #membuka data raster  menjadi array
    file_Input =sys.argv[1]
    file_output = os.path.splitext(file_Input)[0]+'_FFT3.tif' 
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
    bands = 31 #ds2.RasterCount
    proj_ref = ds2.GetProjectionRef()
    training_features = np.zeros((rows*cols,bands),dtype=np.uint16)
    res = np.zeros((rows*cols,bands),dtype=np.uint16)
    
    for band in range(bands):
        training_features[:,band]= (ds2.GetRasterBand(jbands-bands+band+1).ReadAsArray().astype(np.uint16)).flatten()
        
    ds2 = None
    for x in range(rows*cols):
        res[x,:] = transformasi(training_features[x,:])         
        
    res_3d = np.zeros((bands,rows,cols),dtype=np.uint16)
    for i in range(bands):
        res_3d[i,:,:] = res[:,i].reshape(rows,cols)
        
    #menulisakan hasil dalam raster output format geotif 
    driver1 = gdal.GetDriverByName('GTiff')    
    outRaster = driver1.Create(file_output, cols, rows, bands, gdal.GDT_UInt16)
    outRaster.SetGeoTransform(gt)
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromWkt(proj_ref)
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    
    for band in range(bands):
        outband = outRaster.GetRasterBand(band+1); outband.WriteArray(res_3d[band,:,:]); outband.SetNoDataValue(0)
    #Properly close the datasets to flush to disk
    outband.FlushCache() 
    outRaster.FlushCache()
   
if __name__ == '__main__':
    main()
   
    