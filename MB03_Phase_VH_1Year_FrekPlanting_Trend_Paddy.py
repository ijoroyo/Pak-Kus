# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 13:01:08 2020

@author: randy
"""
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

def FindPlantingHarvestTime(y_train):
	# # mencari nilai absolute FFT yang maximum nomornya
    MinUPadi = 6
    bandsinp = 31

    Y = y_train
    TH0=Y[0]; TP1=Y[1]; TH1=Y[2]; TP2=Y[3]; TH2=Y[4]; TP3=Y[5]; TH3=Y[6]; 
    
    TG1=0; TG2=0; TG3=0
    # Hitung waktu pertumbuhan TH0 sudah ngak ada, dipindah ke terakhir
    if(TH1==0)and(TP1>0): TH1=TH0+bandsinp
    if(TH2==0)and(TP2>0): TH2=TH0+bandsinp
    if(TH3==0)and(TP3>0): TH3=TH0+bandsinp
    if(TH1>TP1): TG1 = TH1-TP1; 
    if(TH2>TP2): TG2 = TH2-TP2; 
    if(TH3>TP3): TG3 = TH3-TP3;
    #print("Time Grouth:", TG1, TG2, TG3)

    FA=0    # Frekwensi tanam tidak hanya padi juga tanaman semusim lainnya
    if(TG1>0): FA=1
    if(TG2>0): FA=2
    if(TG3>0): FA=3

    TPPadi = np.zeros((3),dtype=np.uint16) 	# Time Planting
    THPadi = np.zeros((3),dtype=np.uint16) 	# Time Harvest
    FPPadi=0								# Frekweinsi Planting Padi
    
    if(TG1>MinUPadi-1): TPPadi[FPPadi]=TP1; THPadi[FPPadi]=TH1; FPPadi=FPPadi+1; 
    if(TG2>MinUPadi-1): TPPadi[FPPadi]=TP2; THPadi[FPPadi]=TH2; FPPadi=FPPadi+1;  
    if(TG3>MinUPadi-1): TPPadi[FPPadi]=TP3; THPadi[FPPadi]=TH3; FPPadi=FPPadi+1;  

    TPH = np.zeros((8),dtype=np.uint8)
    TPH[0]=FA;TPH[1]=FPPadi;TPH[2]=TPPadi[0];TPH[3]=THPadi[0];TPH[4]=TPPadi[1];TPH[5]=THPadi[1];TPH[6]=TPPadi[2]; TPH[7]=THPadi[2]
    return TPH

def main():
    #membuka data raster  menjadi array
    file_Input =sys.argv[1]
    file_output = os.path.splitext(file_Input)[0]+'_FrekPaddy.tif' 
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
    bandsout = 8
    proj_ref = ds2.GetProjectionRef()
    training_features = np.zeros((rows*cols,bands),dtype=np.uint16)
    res = np.zeros((rows*cols,bandsout),dtype=np.uint16)
    
    for band in range(bands):
        training_features[:,band]= (ds2.GetRasterBand(jbands-bands+band+1).ReadAsArray().astype(np.uint16)).flatten()
        
    ds2 = None
    for x in range(rows*cols):
        res[x,:] = FindPlantingHarvestTime(training_features[x,:])         
        
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
   
 
