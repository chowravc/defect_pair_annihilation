#### Importing useful packages
import numpy as np


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

		## Add attribute: orientation (float)
		self.orientation = orientation


	### Display a single defect
	def showDefects(self, dList):

		## Go through every defect and display the name
		for d in dList:

			# Print the defect name
			print(d.name)


	### Sqrt velocity
	def sqrtVelocity(self, x, y, dList, expData):

		## Frank Elastic Constant 2D
		K_2D = expData['K_3D'] * expData['h'] # (N) (Also more correct would be to multiply be sin^2(alpha) with alpha the tilt angle)

		## Film viscosity 2D
		eta_2D = expData['eta_3D'] * expData['h'] # (N*s/m)

		## Temporary velocity vector
		velocity = np.array([0.0, 0.0])

		## Go through every defect
		for d in dList:

			# Must not be the same defect
			if d != self:

				# Find displacement vector from other defect to this defect
				dispVector = d.position - np.array([x, y])

				# Find squared distance between the two defects
				distSq = np.sum(dispVector**2)

				# Compute velocity component due to that defect and add to temporary velocity
				velocity = velocity - (K_2D/eta_2D)*(self.strength)*(d.strength)*dispVector/(distSq)

		## Return computed Sqrt velocity
		return velocity


	### Yurke velocity
	def yurkeVelocity(self, x, y, dList, expData):
		
		## Frank Elastic Constant 2D
		K_2D = expData['K_3D'] * expData['h'] # (N) (Also more correct would be to multiply be sin^2(alpha) with alpha the tilt angle)

		## Film viscosity 2D
		eta_2D = expData['eta_3D'] * expData['h'] # (N*s/m)
		ra = expData['ra']

		## Temporary velocity vector
		velocity = np.array([0.0, 0.0])

		## Go through every defect
		for d in dList:

			# Must not be the same defect
			if d != self:

				# Find displacement vector from other defect to this defect
				dispVector = d.position - np.array([x, y])

				# Find distance between the two defects
				dist = np.linalg.norm(dispVector)

				# Compute velocity component due to that defect and add to temporary velocity
				velocity = velocity - (K_2D/eta_2D)*(self.strength)*(d.strength)*dispVector/((dist**2)*np.log(dist/ra))

		## Return computed Sqrt velocity
		return velocity


	### Return a velocity step
	def velocityStep(self, f, dList, expData):

		## Timestep
		dt = (expData['tn'] - expData['t0']) / expData['n']

		## Get current position of the defect
		x0 = self.position[0]
		y0 = self.position[1]

		## Find first order RK4
		a, b = f(x0, y0, dList, expData)
		k1x, k1y = dt*a, dt*b

		## Find second order RK4
		a, b = f(x0 + k1x/2, y0 + k1x/2, dList, expData)
		k2x, k2y = dt*a, dt*b

		## Find third order RK4
		a, b = f(x0 + k2x/2, y0 + k2y/2, dList, expData)
		k3x, k3y = dt*a, dt*b

		## Find fourth order RK4
		a, b = f(x0 + k3x, y0 + k3y, dList, expData)
		k4x, k4y = dt*a, dt*b 
		
		## Add up all RK4 terms for x and y
		kx = (k1x + 2*k2x + 2*k3x + k4x)/6
		ky = (k1y + 2*k2y + 2*k3y + k4y)/6
		
		## Create a velocity step vector
		k = np.array([kx, ky])

		## Return the velocity step
		return k



	### Brownian motion step
	def brownianStep(self, expData):

		k_B = expData['k_B']

		T = expData['T']

		eta_3D = expData['eta_3D']

		ra = expData['ra']

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



	### Update the position of this defect
	def updatePosition(self, dList, expData):

		## If the user specified sqrt velocity
		if expData['velocityType'] == "sqrt":

			# Add velocity multiplied by timestep
			self.position = self.position + self.velocityStep(self.sqrtVelocity, dList, expData) + self.brownianStep(expData)

		## If the user specified Yurke velocity
		if expData['velocityType'] == "yurke":

			# Add velocity multiplied by timestep
			self.position = self.position + self.velocityStep(self.yurkeVelocity, dList, expData) + self.brownianStep(expData)



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