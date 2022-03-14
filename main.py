#### Importing useful packages
import numpy as np
import glob
import matplotlib.pyplot as plt
# import cv2
import random
import shutil
import os
import matplotlib.ticker
import yaml

#### Importing useful python scripts
from scripts.display import *
from scripts.defect import *
from scripts.simulation import *


### Set numpy random seed
np.random.seed(100)



#### If the file is run directly
if __name__ == '__main__':

	### Open the specified experiment yaml
	with open("experiments/defaultExp.yml", 'r') as stream:

		## Try to loadparse the yaml
		try:

			# Save it as experiment data
			expData = yaml.safe_load(stream)

		## Display an error
		except yaml.YAMLError as exc:
			
			# Print the exception
			print(exc)

	### Prepare a new experiment
	runNum = prepareExperiment()

	### If the experiment type specified was custom placed defects
	if expData['expType'] == "place":

		### Manually place defects
		dList = placeDefects(expData)

	### If the experiment type was a quench
	elif expData['expType'] == "quench":

		### Perform a quench
		dList = quench(expData)
	
	### Run the simulation of placed defects
	runSimulation(runNum, dList, expData)

	### Save the experiment video
	framesToVideo()