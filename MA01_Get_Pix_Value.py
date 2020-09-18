
import numpy as np
import pandas as pd

from osgeo import gdal, osr
gdal.PushErrorHandler('CPLQuietErrorHandler')
gdal.UseExceptions()
import sys, os, tqdm
from multiprocessing import Pool

def main():
    #membuka data raster  menjadi array
    file_Input =sys.argv[1]
    file_location =sys.argv[2]
    file_output = os.path.splitext(file_Input)[0]+'_Samples.txt' 
    print("Paddy Field Monitoring:")
    print("Input Image     :", file_Input)
    print("Input Location  :", file_location)
    print("Output Image    :", file_output)
    
    ds2 = gdal.Open(file_Input)
    if ds2 is None:
        print ('Tidak bisa membaca %s' %file_Input)
        sys.exit(1)
    ulx, xres, xskew, uly, yskew, yres  = ds2.GetGeoTransform()
    lrx = ulx + (ds2.RasterXSize * xres)
    lry = uly + (ds2.RasterYSize * yres)

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

    data_locations = pd.read_csv(file_location) #id, Class_ID, xcoord, ycoord, class_name, Note
    #print (data_locations)
    ndata = len(data_locations)
    print ("NData:", ndata);
    print ("ulx:", ulx, xres)
    print ("uly:", uly, yres)
    #data = data_locations.iloc[1,:]
    print ("Rows:",rows)
    print ("Cols:",cols)
        
    ds2 = None
    DNArray = np.zeros((ndata,bands+4),dtype=np.float64)
    n=0
    for i in range(ndata):
       id = data_locations.iloc[i,0]
       idcls = data_locations.iloc[i,1]
       lon = data_locations.iloc[i,2]
       lat = data_locations.iloc[i,3]
       clsnm = data_locations.iloc[i,4]
       x= (lon-ulx)/xres
       y= (lat-uly)/yres
       xx = int(x)
       yy = int(y)
       #print (lon, lat, clsnm, xx,yy)
       DNArray[i,0] = id
       DNArray[i,1] = idcls
       DNArray[i,2] = lon
       DNArray[i,3] = lat
       #DNArray[i,4] = clsnm
       xy=0
       if(xx>-1)and(xx<cols):
          if(yy>-1)and(yy<rows):
             xy = (yy*cols)+xx
             DNArray[n,4:] = training_features[xy,:]
             n=n+1
             #print (DNArray[i,:])			 
       #
    DNArrayFinal = np.zeros((n,bands+4),dtype=np.float64)
    DNArrayFinal[0:n,:] = DNArray[0:n,:]
       #
    headb=""
    for i in range(jbands):
       headb = headb+",band-"+str(i)
    head = "id,class_id,xcoord,ycoord"+headb
    np.savetxt(file_output,DNArrayFinal,fmt='%.4f',delimiter=',',header=head) #res[x,:] = Get_Pixel_Values(training_features[x,:],jbands)         

	#Properly close the datasets to flush to disk
    #outband.FlushCache() 
    #outRaster.FlushCache()
    
if __name__ == '__main__':
    main()
   
     
 