#### Importing useful packages
import numpy as np
import glob
import matplotlib.pyplot as plt
import cv2
import random
import shutil
import os
import matplotlib.ticker

class OOMFormatter(matplotlib.ticker.ScalarFormatter):
	def __init__(self, order=0, fformat='%1.1f', offset=True, mathText=True):
		self.oom = order
		self.fformat = fformat
		matplotlib.ticker.ScalarFormatter.__init__(self,useOffset=offset,useMathText=mathText)
	def _set_order_of_magnitude(self):
		self.orderOfMagnitude = self.oom
	def _set_format(self, vmin=None, vmax=None):
		self.format = self.fformat
		if self._useMathText:
			self.format = r'$\mathdefault{%s}$' % self.format


### Choose whether or not to show the board each save iteration
showBoard = False

### "Film" dimensions
# (1200, 870) um

### Number of iterations
n = 200000

### Save image every __ iterations
saveRate = 25

### Thickness of film
h = 7.5e-9 # (m)

### Frank Elastic Constant 3D
K_3D = 0.73e-11 # (N)

### Frank Elastic Constant 2D
K_2D = K_3D * h # (N) (Also more correct would be to multiply be sin^2(alpha) with alpha the tilt angle)

# Typical
# 3D K = (2 - 5) *10^-7 erg/cm

# Both K and eta can be the 3D version
# K_2D = K_3D * h 
# eta_2D = eta_3D * h

### Film viscosity 3D
eta_3D = 2.0e-6 # (N*s/m^2)

### Film viscosity 2D
eta_2D = eta_3D * h # (N*s/m)

### Boltzmann constant
k_B = 1.38e-27

### Defect core size
ra = 1e-6

### Temperature
T = 300

### Timestep
dt = 1e-5

### Max dist for annihilation
annihilationDist = 2e-6


### List to store defects in film
dList = []

### Set numpy random seed
np.random.seed(100)


#### Object for defect
class Defect():

	### Constructor for defect
	def __init__(self, name, strength, position, orientation):

		## Add attribute: name (str)
		self.name = name

		## Add attribute: strength (float)
		self.strength = strength

		## Add attribute: position (np.array([]): [3])
		self.position = position

		## Add attribute: velocity (np.array([]): [3])
		self.velocity = np.array([0.0, 0.0])

		## Add attribute: orientation (float)
		self.orientation = orientation

	### Display a single defect
	def showDefects(self):

		## Go through every defect and display the name
		for d in dList:

			# Print the defect name
			print(d.name)


	### Sqrt velocity
	def sqrtVelocity(self):

		## Temporary velocity vector
		velocity = np.array([0.0, 0.0])

		## Go through every defect
		for d in dList:

			# Must not be the same defect
			if d != self:

				# Find displacement vector from other defect to this defect
				dispVector = d.position - self.position

				# Find distance between the two defects
				dist = np.linalg.norm(dispVector)

				# Compute velocity component due to that defect and add to temporary velocity
				velocity = velocity - (K_2D/eta_2D)*(self.strength)*(d.strength)*dispVector/(dist**2)

		## Return computed Sqrt velocity
		return velocity


	### Yurke velocity
	def yurkeVelocity(self):

		## Temporary velocity vector
		velocity = np.array([0.0, 0.0])

		## Go through every defect
		for d in dList:

			# Must not be the same defect
			if d != self:

				# Find displacement vector from other defect to this defect
				dispVector = d.position - self.position

				# Find distance between the two defects
				dist = np.linalg.norm(dispVector)

				# Compute velocity component due to that defect and add to temporary velocity
				velocity = velocity - (K_2D/eta_2D)*(self.strength)*(d.strength)*dispVector/((dist**2)*np.log(dist/ra))

		## Return computed Sqrt velocity
		return velocity


	### Update the velocity of this defect
	def updateVelocity(self):

		## Update velocity of defect (sqrt)
		# self.velocity = self.sqrtVelocity()

		## Update velocity of defect (yurke)
		self.velocity = self.yurkeVelocity()


	### Brownian motion step
	def brownianStep(self):

		## Diffusion coefficient
		D = (k_B*T)/(6*np.pi*eta_3D*ra)

		## Mean value for Brownian step
		sigma = np.sqrt(4*D)

		## Mean
		mu = 0

		## Step in x-direction
		dx = np.random.normal(mu, sigma)

		## Step in y-direction
		dy = np.random.normal(mu, sigma)

		## Return step
		return np.array([dx, dy])


	### Brownian motion step (adaptive)
	def brownianStepAdaptive(self):

		## Mean
		mu = 0

		## Diffusion coefficient
		D = (k_B*T)/(6*np.pi*eta_3D*ra)

		## Mean value for Brownian step
		sigma = np.sqrt(4*D)

		## Step in x-direction
		dx = np.random.normal(mu, sigma)

		## Step in y-direction
		dy = np.random.normal(mu, sigma)

		## Return step
		return np.array([dx, dy])



	### Update the position of this defect
	def updatePosition(self):

		## Add velocity multiplied by timestep
		self.position = self.position + self.velocity*(dt) + self.brownianStep()



#### Object for +1 defect
class PlusDefect(Defect):

	### Constructor for +1 defect
	def __init__(self, name, position, orientation):

		## Create object from parent
		super().__init__(name, 1.0, position, orientation)



#### Object for -1 defect
class MinusDefect(Defect):

	### Constructor for -1 defect
	def __init__(self, name, position, orientation):

		## Create object from parent
		super().__init__(name, -1.0, position, orientation)



#### Check annihilation between two defects
def checkAnnihilation(d1, d2):

	### First condition: They must be of equal and opposite sign
	if not ((d1.strength)*(d2.strength) < 0 and np.abs(d1.strength) == np.abs(d2.strength)):

		## Condition failed: cannot annihilate
		return False

	### Condition passed: they are of equal and opposite sign
	else:

		## Compute displacement vector between the two defects
		dispVector = d2.position - d1.position

		## Compute distance between the two defects
		dist = np.linalg.norm(dispVector)

		## If this distance is smaller than the prespecified annihilation distance
		if dist < annihilationDist:

			# They will annihilate
			return True

		## If it is not smaller than the prespecified annihilation distance
		else:

			# They will not annihilate
			return False



#### Run update sequence
def update():

	### For every existing defect
	for d in dList:

		## Update their velocities
		d.updateVelocity()

	### For every existing defect
	for d in dList:

		## Update their positions
		d.updatePosition()

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
					if checkAnnihilation(d1, d2):

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



#### Function to save the "board" as an image
def saveBoard(runNum, fNum):

	### Clear matplotlib plots
	plt.clf()

	### Generate subplots
	fig, ax = plt.subplots()

	# format order of magnitude of `ax.yaxis`
	order = -6
	ax.xaxis.set_major_formatter(OOMFormatter(order, '%1.1f'))
	ax.yaxis.set_major_formatter(OOMFormatter(order, '%1.1f'))

	### Set limits to plot
	plt.xlim((-6e-4, 6e-4))
	plt.ylim((-435e-6, 435e-6))

	### Add labels to axes
	plt.xlabel("x-position (m)")
	plt.xlabel("y-position (m)")

	### Add gridlines to the plot
	plt.grid()

	### Go through existing defects
	for d in dList:

		## Obtain their current position
		r = d.position

		## Find the x-value
		xPos = r[0]

		## Find the y-value
		yPos = r[1]

		## Line of data to store
		outLine = str(d.strength) + ' ' + str(xPos) + ' ' + str(yPos) + ' ' + str(d.orientation) + '\n'

		## Name of output txt file
		txtFileName = 'runs/exp' + str(runNum) + '/data/' + d.name + '.txt'

		## Open txt
		with open(txtFileName, 'a') as txtFile:

			# Write line in append mode
			txtFile.write(outLine)

		## If this is positive defect
		if d.strength > 0:

			# Plot red defect
			ax.scatter(xPos, yPos, color="red", s=2)

		## If this is a negative defect
		else:

			# Plot blue defect
			ax.scatter(xPos, yPos, color="blue", s=2)

	### Keep track of number of defects in the title
	plt.title("Number of defects: " + str(len(dList)))

	### If user wanted to show the board
	if showBoard:

		## Show the board
		plt.show()

	### Save each frame
	plt.savefig('runs/exp' + str(runNum) + '/frames/' + str(fNum).zfill(len(str(n))) + '.png', dpi=300)



#### Function to run simulation
def runSimulation(runNum):

	for i in range(n):

		if i%100 == 0:

			print(str(100*i/n)[:5] + '%')

		if i%saveRate == 0:

			saveBoard(runNum, i)

		update()



#### Function to 'place' defects
def placeDefects():

	# dList.append(PlusDefect("defect1", np.array([2e-4, 0.0]), np.pi))

	# dList.append(MinusDefect("defect2", np.array([-2e-4, 0.0]), np.pi))


	dList.append(PlusDefect("defect1", np.array([2e-4, 0.0]), np.pi))

	dList.append(PlusDefect("defect2", np.array([-2e-4, 0.0]), np.pi))

	dList.append(MinusDefect("defect3", np.array([0.0, 2e-4]), np.pi))

	dList.append(MinusDefect("defect4", np.array([0.0, -2e-4]), np.pi))



#### Function to perform a film quench
def quench():

	numQuench = 200

	# Place roughly half positive defects
	for i in range(numQuench//2):

		pos = np.array([6e-4*(random.uniform(0, 1)-0.5), 435e-6*(random.uniform(0, 1)-0.5)])

		dList.append(PlusDefect("defect" + str(i+1), pos, np.pi))

	# Place roughly half positive defects
	for i in range(numQuench - numQuench//2):

		pos = np.array([6e-4*(random.uniform(0, 1)-0.5), 435e-6*(random.uniform(0, 1)-0.5)])

		dList.append(MinusDefect("defect" + str(numQuench//2 + i+1), pos, np.pi))



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

if __name__ == '__main__':

	### Prepare a new experiment
	runNum = prepareExperiment()

	# print(sigma)

	### Manually place defects
	placeDefects()

	### Or alternatively, perform a quench
	# quench()

	### Run the simulation of placed defects
	runSimulation(runNum)