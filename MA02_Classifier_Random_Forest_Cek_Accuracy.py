#import numpy as np
#from osgeo import gdal, ogr, osr
#gdal.PushErrorHandler('CPLQuietErrorHandler')
#gdal.UseExceptions()

 # Module sys has to be imported:
import sys                
file_samples =sys.argv[1]
print("Cek Accuracy for:", file_samples)
		
#======================================================
import pandas as pd
from sklearn.model_selection import train_test_split
# NOTE: Make sure that the outcome column is labeled 'class_id' in the data file
#file_samples ='Subang2018_S1_VH_RGB_Sample.txt'
data_samples = pd.read_csv(file_samples)
features = data_samples.drop(columns=['# id','class_id','xcoord','ycoord'])
labels = data_samples['class_id']
X_train, X_test, Y_train, Y_test = train_test_split(features, labels, train_size=0.7)

#============================================================ 
from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier(bootstrap=False, criterion="entropy", max_features=0.15000000000000002, min_samples_leaf=6, min_samples_split=3, n_estimators=100)
model.fit(X_train, Y_train)
print("Overall Acc Random Forest:", model.score(X_test, Y_test))

#============================================================ 
from sklearn.svm import SVC
model = SVC()
model.fit(X_train, Y_train)
print("Overall Acc SVC:",model.score(X_test, Y_test))
