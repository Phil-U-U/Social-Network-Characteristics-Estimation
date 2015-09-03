"""
Estimate Motif (of Size Three) Concentration by Pair-wise Subgraph Random Walk ( PSRW ) 
Author: Phil Hengjun Cui
Date: 08/24/15
Reference: Efficiently Estimating Motif Statistics of Large Networks. ACM Transactions on Knowledge Discovery from Data, Vol. 9, No. 2, Article 8, Publication date: September 2014.
"""

import sys
import os
import time
import random
import matplotlib.pyplot as plt  
import json
import igraph 


os.chdir('/Users/cui/Dropbox/Data Mining-Sampling on Graphs/Data/SamplingMotifs')
#os.chdir('/home/phil/Dropbox/Data Mining-Sampling on Graphs/Data/SamplingMotifs')
filename = "YouTube.txt"   # accurate clustering coefficient is 0.0021
graph =	igraph.Graph.Read_Edgelist( filename )
graph.to_undirected()
print "Read Graph Done!"
N_nodes = graph.vcount()



def StepLabel( SampleBudget ):
	label_steps = [] 
	N_blocks = 4   # 4

	for idx_block in xrange( N_blocks ):  
		initial_steps = 10**2
		final_steps = 10*initial_steps + initial_steps

		fold = 10**idx_block
		initial_steps *=  fold
		final_steps   *=  fold

		for steps in xrange( initial_steps if idx_block == 0 else initial_steps*2, final_steps, initial_steps ):
			label_steps.append( steps )

	if SampleBudget != label_steps[-1]:
		print("Error: SampleBudget and number of blocks are not consistent!")
		quit()

	return label_steps


def SamplingMotifs( SampleBudget, label_collectData ):
	
	results_concentration = []
	generatorSampleBudget = xrange( 1, SampleBudget+1 )
	

	num_concentration = 0       # numerator   of concentration
	den_concentration = 0       # denominator of concentration
	cnt_TargetMotif   = 0

	#  Select initial motif
	FoundInitialMotif = False
	while FoundInitialMotif == False:
		node_1 = random.randint( 1, N_nodes )
		neighbors_node_1 = graph.neighbors( node_1 )
		if len( neighbors_node_1 ) > 1:
			node_2 = neighbors_node_1[ random.randint( 0, len( neighbors_node_1 )-1 ) ]
			FoundInitialMotif = True
	
	motif_current = [ node_1, node_2 ]


	for idx_SB in generatorSampleBudget:

		neighbors_node1 = graph.neighbors( motif_current[0] )
		neighbors_node2 = graph.neighbors( motif_current[1] )

		n_Neighbors_node1 = len( neighbors_node1 )
		n_Neighbors_node2 = len( neighbors_node2 )
		n_Neighbors = n_Neighbors_node1 + n_Neighbors_node2

		FoundMotif = False

		while FoundMotif == False:
			# random.randint Return a random integer N such that a <= N <= b
			# Totally n_Neighbors balls, 2 of which are black balls, and the others are white ones.
			idx_NextMotif = random.randint( 0, n_Neighbors-1 ) 
			if   idx_NextMotif < n_Neighbors_node1:
				node_selected = neighbors_node1[ idx_NextMotif ]
				CheckMotif    = node_selected in graph.neighbors( motif_current[1] )
				motif_next    = [ motif_current[0], node_selected ]
			elif idx_NextMotif >= n_Neighbors_node1:
				node_selected = neighbors_node2[ idx_NextMotif - n_Neighbors_node1 ]
				CheckMotif    = node_selected in graph.neighbors( motif_current[0] )
				motif_next    = [ motif_current[1], node_selected ]
			else:
				print "Index Error: idx_NextMotif"

			if node_selected == motif_current[0] or node_selected == motif_current[1]:
				FoundMotif = False
			else:
				FoundMotif = True

		if CheckMotif == True:
			cnt_TargetMotif   += 1
			num_concentration += 1.0/6
			den_concentration += 1.0/6
		else:
			den_concentration += 1.0/2

		motif_current = motif_next

		if idx_SB in set(label_collectData):
			concentration = float( num_concentration )/den_concentration
			results_concentration.append( concentration )
			print "Current Step = %d" % idx_SB
			print "Concentration = %f" % concentration
	
	return results_concentration

#Plot Estimation vs Steps
def PlotFrame( label_collectData, results_concentration, frame ):
	# Initialize Plotting Settings
	x_axis = label_collectData
	y_axis = results_concentration
	

	# Save data
	os.chdir('/Users/cui/Dropbox/Create/SamplingMotifs/PSRW/Results_PSRW')
	f = open('Concentration_'+filename[:-4]+ '_PSRW_Frame_' + str(frame) + '.txt', 'w+')
	data = {'x_axis': x_axis, 'y_axis': y_axis }
	json.dump( data, f )
	f.close()

if "__main__" == __name__:
	frames = 100
	SampleBudget = 10**6     # 10**6

	label_collectData = StepLabel( SampleBudget )

	for frame in xrange( frames ):
		results_concentration = SamplingMotifs( SampleBudget, label_collectData )
		PlotFrame( label_collectData, results_concentration, frame )

