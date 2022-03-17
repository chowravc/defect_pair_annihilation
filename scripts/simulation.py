#### Importing useful packages
import numpy as np
import glob
import matplotlib.pyplot as plt
import random
import os
import csv

#### Importing useful python scripts
from scripts.display import *
from scripts.defect import *


#### Check annihilation between two defects
def checkAnnihilation(d1, d2, expData):

	### First condition: They must be of equal and opposite sign
	if not ((d1.strength)*(d2.strength) < 0 and np.abs(d1.strength) == np.abs(d2.strength)):

		## Condition failed: cannot annihilate
		return False

	### Condition passed: they are of equal and opposite sign
	else:

		## Compute displacement vector between the two defects
		dispVector = d2.position - d1.position

		## Compute distance between the two defects
		dist = np.sum(dispVector**2)**0.5

		## If this distance is smaller than the prespecified annihilation distance
		if dist < expData['annihilationDist']:

			# They will annihilate
			return True

		## If it is not smaller than the prespecified annihilation distance
		else:

			# They will not annihilate
			return False



#### Run update sequence
def update(dList, expData):

	### For every existing defect
	for d in dList:

		## Update their positions
		d.updatePosition(dList, expData)

	### Temporary list to store names of defects that must be removed due to annihilation
	removed = []

	### For every existing defect
	for i, d1 in enumerate(dList):

		## Make sure it was not removed this update
		if d1.name not in removed:

			# For every other existing defect
			for j, d2 in enumerate(dList):

				# Make sure they aren't the same
				if d1.name != d2.name:

					# Check if they annihilate this cycle
					if checkAnnihilation(d1, d2, expData):

						# Add the names of both defects to list of defects to remove this update
						removed.append(d1.name)

						# Break out of this 
						break

	### Now go through every defect that was removed this update
	for dName in removed:

		## Go through every existing defect
		for index, d in enumerate(dList):

			# If it is in the list to remov
			if d.name == dName:

				## Remove the defect from the list of defects
				del dList[index]





#### Function to 'place' defects
def placeDefects(expData):

	### Create list to store existing defects
	dList = []

	# dList.append(PlusDefect("defect1", np.array([2e-4, 0.0]), np.pi))

	# dList.append(MinusDefect("defect2", np.array([-2e-4, 0.0]), np.pi))


	dList.append(PlusDefect("defect1", np.array([2e-4, 0.0]), np.pi))

	dList.append(PlusDefect("defect2", np.array([-2e-4, 0.0]), np.pi))

	dList.append(MinusDefect("defect3", np.array([0.0, 2e-4]), np.pi))

	dList.append(MinusDefect("defect4", np.array([0.0, -2e-4]), np.pi))

	### Return list of placed defects
	return dList



#### Function to perform a film quench
def quench(expData):

	### Create list to store existing defects
	dList = []

	### Number of defects to place at the quench
	numQuench = expData['quenchCount']

	### Dimensions of film
	filmDims = expData['filmDims']

	### Place roughly half positive defects
	for i in range(numQuench//2):

		## Choose a random (x, y) starting position
		pos = np.array([(1e-6*filmDims[0])*(random.uniform(0, 1)-0.5), (1e-6*filmDims[1])*(random.uniform(0, 1)-0.5)])

		## 'Place' positive defect at that position
		dList.append(PlusDefect("defect" + str(i+1), pos, np.pi))

	### Place roughly half positive defects
	for i in range(numQuench - numQuench//2):

		## Choose a random (x, y) starting position
		pos = np.array([(1e-6*filmDims[0])*(random.uniform(0, 1)-0.5), (1e-6*filmDims[1])*(random.uniform(0, 1)-0.5)])

		## 'Place' negative defect at that position
		dList.append(MinusDefect("defect" + str(numQuench//2 + i+1), pos, np.pi))

	### Return list of placed defects
	return dList



#### Prepare a new run/experiment
def prepareExperiment():

	### If the runs folder does not exist
	if len(glob.glob('runs/')) == 0:

		## Create the runs directory
		os.mkdir('runs/')

	### Obtain current run number by looking at existing runs
	runNum = len(glob.glob('runs/exp*/')) + 1

	### Create relevant directories
	os.mkdir('runs/exp' + str(runNum))
	os.mkdir('runs/exp' + str(runNum) + '/frames/')
	os.mkdir('runs/exp' + str(runNum) + '/data/')

	### Return the run number
	return runNum



#### Save the number of defects with time
def saveDefectNumber(i, dt, dList):

	### Find current time since start
	time = i*dt

	### Number of defects in film
	dNum = len(dList)

	### Obtain current run number by looking at existing runs
	runNum = len(glob.glob('runs/exp*/'))

	### Save to txt file
	with open('runs/exp' + str(runNum) + '/data/number.csv', 'a', newline='') as numberFile:

		## Create writer object
		writeNumberFile = csv.writer(numberFile)

		## If this is the first line
		if i == 0:

			# Append the headers to the csv file
			writeNumberFile.writerow(["time", "number"])
			writeNumberFile.writerow(["s", ""])

		## Append the data to the csv file
		writeNumberFile.writerow([time, dNum])




#### Function to run simulation
def runSimulation(runNum, dList, expData):

	### Number of iterations
	n = expData['n']

	### Timestep size
	dt = (expData['tn'] - expData['t0']) / n

	### Experiment saverate
	saveRate = expData['saveRate']

	### Go through every iteration
	for i in range(n):

		## Every 100 iterations
		if i%100 == 0:

			# Display progress
			print(str(100*i/n)[:5] + '%')

		## Save time and number of defects
		saveDefectNumber(i, dt, dList)

		## Every savePer
		if i%saveRate == 0:

			# Save the board as an image
			saveBoard(runNum, i, dList, expData)

		## Update the board
		update(dList, expData)