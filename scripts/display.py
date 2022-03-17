#### Importing useful packages
import matplotlib.pyplot as plt
import matplotlib.ticker
import glob
import cv2
import pandas as pd



#### Class to properly format matplotlib grids
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



#### Function to save the "board" as an image
def saveBoard(runNum, fNum, dList, expData):

	### Number of iterations
	n = expData['n']

	### Clear matplotlib plots
	plt.clf()

	### Generate subplots
	fig, ax = plt.subplots()

	### format order of magnitude of `ax.yaxis`
	order = -6
	ax.xaxis.set_major_formatter(OOMFormatter(order, '%1.1f'))
	ax.yaxis.set_major_formatter(OOMFormatter(order, '%1.1f'))

	### Get limits on the 'window'
	xLimValue = (expData['windowDims'][0]/2) * 1e-6
	yLimValue = (expData['windowDims'][1]/2) * 1e-6

	### Set limits to plot
	plt.xlim((-xLimValue, xLimValue))
	plt.ylim((-yLimValue, yLimValue))

	### Change x and y ticks
	plt.xticks([-6e-4, -4e-4, -2e-4, 0, 2e-4, 4e-4, 6e-4])
	plt.yticks([4e-4, -2e-4, 0, 2e-4, 4e-4])

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

	### Make x and y axis ticks equally spaced
	plt.gca().set_aspect('equal', adjustable='box')

	### Keep track of number of defects in the title
	plt.title("Number of defects: " + str(len(dList)))

	### If user wanted to show the board
	if expData['showBoard']:

		## Show the board
		plt.show()

	### Save each frame
	plt.savefig('runs/exp' + str(runNum) + '/frames/' + str(fNum).zfill(len(str(n))) + '.png', dpi=300)
	
	### Clear matplotlib plots
	plt.clf()

	### Close matplotlib plots
	plt.close()


#### Convert frames to video
def framesToVideo():

	### Access the number of the current run
	runNum = len(glob.glob('runs/exp*/'))

	### Path to directory containing frames
	framesDir = 'runs/exp' + str(runNum) + '/frames/'

	### Framerate of output video
	framerate = 25

	print('\nLoading frames: ' + framesDir)

	### Frames paths
	fPath = glob.glob(framesDir + '*')

	### If no frames found
	if len(fPath) == 0:

		print('\nNo Frames were found.')

	### If frames are found
	else:

		print('Found ' + str(len(fPath)) + ' frames.')

		## Output video name
		vPath = 'runs/exp' + str(runNum) + '/' + framesDir.split('/')[-3] + '.avi'

		## Reading first file for size
		im0 = cv2.imread(fPath[0])

		## Extracting video size
		height, width, layers = im0.shape
		size = (width, height)

		## Output video
		out = cv2.VideoWriter(vPath, cv2.VideoWriter_fourcc(*'DIVX'), framerate, size)

		## Starting video write
		for i, filename in enumerate(fPath):

			# Displaying progress
			if i%100 == 0:

				print(str(100*i/len(fPath))[0:4]+'%')

			# Reading current frame
			img = cv2.imread(filename)

			# Extracting shape
			h, w, l = img.shape

			# Checking if shape matches spec for video
			if h == height  and w == width and l == layers:

				# Write frame
				out.write(img)

			# If shape is different
			else:

				print('Incorrect shape for frame: ' + filename)
				break

		## Release the video
		out.release()

	print('\nDone.')



#### Creates a plot of number of defects as a function of time automatically
def numberPlotAuto(runNum=99999):

	### Check if default runNum was used
	if runNum == 99999:

		## Access the number of the current run
		runNum = len(glob.glob('runs/exp*/'))

	### Path to csv with number of defects as a function of time
	csvPath = 'runs/exp' + str(runNum) + '/data/number.csv'

	### Path to figure save location
	figPath = 'runs/exp' + str(runNum) + '/data/numberVsTime.png'

	### Load the csv as a pandas
	numberDataframe = pd.read_csv(csvPath, index_col=None)

	### Get the times
	times = pd.Series.to_numpy(numberDataframe['time'][1:]).astype(float)

	### Get the number
	number = pd.Series.to_numpy(numberDataframe['number'][1:]).astype(float)

	### Clear plots
	plt.clf()

	### Generate subplots
	fig = plt.figure(linewidth=1.5)
	ax = plt.gca()

	### Plot the number as function of time
	ax.scatter(times, number, c='blue', s=2, label='data')

	### Set axis scales to loglog
	ax.set_yscale('log')
	ax.set_xscale('log')

	### Move ticks inside
	ax.tick_params(direction='in', which='both', bottom=True, top=True, left=True, right=True)
	ax.tick_params(which='major', width=1.5, length=6)
	ax.tick_params(which='minor', width=1.2, length=3)

	### Add axis labels
	plt.xlabel('time (s)', fontsize=12)
	plt.ylabel('defect number', fontsize=12)

	### Add legend
	ax.legend()

	### Save figure
	plt.savefig(figPath, dpi=300)

	### Show plots
	# plt.show()

	### Clear plots
	plt.clf()

	### Close plots
	plt.close()