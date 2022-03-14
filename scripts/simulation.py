#### Importing useful packages
import numpy as np
import glob
import matplotlib.pyplot as plt
import random
import os

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

	dList = []

	# dList.append(PlusDefect("defect1", np.array([2e-4, 0.0]), np.pi))

	# dList.append(MinusDefect("defect2", np.array([-2e-4, 0.0]), np.pi))


	dList.append(PlusDefect("defect1", np.array([2e-4, 0.0]), np.pi))

	dList.append(PlusDefect("defect2", np.array([-2e-4, 0.0]), np.pi))

	dList.append(MinusDefect("defect3", np.array([0.0, 2e-4]), np.pi))

	dList.append(MinusDefect("defect4", np.array([0.0, -2e-4]), np.pi))

	return dList



#### Function to perform a film quench
def quench(expData):

	dList = []

	numQuench = 200

	# Place roughly half positive defects
	for i in range(numQuench//2):

		pos = np.array([6e-4*(random.uniform(0, 1)-0.5), 435e-6*(random.uniform(0, 1)-0.5)])

		dList.append(PlusDefect("defect" + str(i+1), pos, np.pi))

	# Place roughly half positive defects
	for i in range(numQuench - numQuench//2):

		pos = np.array([6e-4*(random.uniform(0, 1)-0.5), 435e-6*(random.uniform(0, 1)-0.5)])

		dList.append(MinusDefect("defect" + str(numQuench//2 + i+1), pos, np.pi))

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



#### Function to run simulation
def runSimulation(runNum, dList, expData):

	### Number of iterations
	n = expData['n']

	### Experiment saverate
	saveRate = expData['saveRate']

	### Go through every iteration
	for i in range(n):

		## Every 100 iterations
		if i%100 == 0:

			# Display progress
			print(str(100*i/n)[:5] + '%')

		## Every savePer
		if i%saveRate == 0:

			# Save the board as an image
			saveBoard(runNum, i, dList, expData)

		## Update the board
		update(dList, expData)