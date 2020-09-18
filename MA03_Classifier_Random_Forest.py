import numpy as np
import pandas as pd
import sys, os, tqdm
from osgeo import gdal, ogr, osr
gdal.PushErrorHandler('CPLQuietErrorHandler')
gdal.UseExceptions()


import sys                
file_Image =sys.argv[1]
file_samples = os.path.splitext(file_Image)[0]+'_Samples.txt' 
file_output = os.path.splitext(file_Image)[0]+'_Class.Tif' 

print("Paddy Field Classification:")
print("Input Image      :", file_Image)
print("Input Samples    :", file_samples)
print("Output Classified:", file_output)

#======================================================
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
#======================================================

# NOTE: Make sure that the outcome column is labeled 'target' in the data file
data_samples = pd.read_csv(file_samples)
features = data_samples.drop(columns=['# id','class_id','xcoord','ycoord'])
training_features = features
training_labels = data_samples['class_id']

#membuka data raster  menjadi array
ds2 = gdal.Open(file_Image)
if ds2 is None:
    print ('Tidak bisa membaca %s' %file_Image)
    sys.exit(1)
gt = ds2.GetGeoTransform()
rows = ds2.RasterYSize
cols = ds2.RasterXSize
bands = ds2.RasterCount
print ("Number of Bands:", bands)
# proj_ref = ds2.GetProjectionRef()
testing_features = np.zeros((rows*cols,bands),dtype=np.uint16)  
for band in range(bands):
    testing_features[:,band]= (ds2.GetRasterBand(band+1).ReadAsArray().astype(np.uint16)).flatten()

ds2 = None

#============================================================ 
# Average CV score on the training set was: 0.9670068027210885
model = RandomForestClassifier(bootstrap=False, criterion="entropy", max_features=0.15000000000000002, min_samples_leaf=6, min_samples_split=3, n_estimators=100)
model.fit(training_features, training_labels)
results = model.predict(testing_features)

#============================================================

res_2d = results.reshape(rows,cols)

#menulisakan hasil dalam raster file_output format geotif 4 band float 32 bit
driver1 = gdal.GetDriverByName('GTiff')    
outRaster = driver1.Create(file_output, cols, rows, 1, gdal.GDT_UInt16)
outRaster.SetGeoTransform(gt)

outband = outRaster.GetRasterBand(1); outband.WriteArray(res_2d); outband.SetNoDataValue(0)

#Properly close the datasets to flush to disk
outband.FlushCache() 
outRaster.FlushCache()
