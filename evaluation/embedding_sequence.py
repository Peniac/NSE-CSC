'''
Root selection
Root: The root is the CSC-engaged VNF of the consuming service with the least CPU demands

Adding children of a node i 
AddChildren(i): determine the set of neighboring nodes of i (N_i), pertaining to the consuming service only, and are not in the tree yet. 
	If |N_i| > 1:
		for every j,k in N_i (where, without loss of generality, (i,j) and (j,k) in E_C), j is placed as left sibling of k, if d^{ij} > d^{ik}
	If |N_i| = 1:
		the unique j in N_i is placed as the only child of i 
	If |N_i| = 0:
		i is a leaf 
'''

import numpy as np

def embeddingLogic(service):
	'''
	Returns a dictionary with the heuristic embedding logic 
	(key: node, value (list): (order, the node towards which the key will be placed)).
	The 'order' is determined by a pre-order traversal of a tree logic, and each node is placed towards its parent (except from the root, which is placed towards the CSC-engaged VNF of the providing service).
	'''
	# create the dictionary
	sequence = {}
	# the nodes of the (expanded) consuming service
	all_nodes = list(service.nodes)
	# the nodes of the consuming service only
	nodes1 = [n for n in all_nodes if service.nodes[n]['sertype'] == 'consumer']
	# the CSC nodes as pertaining to the consuming service only (i.e., in V*_C)
	CSC_VNFs = [(n,service.nodes[n]['cpu']) for n in nodes1 if service.nodes[n]['type'] == 'C_CSC_VNF']
	# the consuming CSC_VNF that has the minimum CPU resource requirements 
	root = [i for (i,j) in CSC_VNFs if j == min([j for (i,j) in CSC_VNFs])][0]
	# find the neighbors of the root 
	root_neighbors = findNeighbors(service, root, sequence)
	# the root will be placed towards an already embedded node
	towards = [node for node in root_neighbors if service.nodes[node]['sertype'] == 'provider'][0]
	# update the dictionary 
	sequence[root] = towards
	# continue with the remaining nodes 
	all_nodes.remove(root)
	sequence = populateSequence(service, all_nodes, root, sequence)
	return sequence



def findNeighbors(service, node, sequence):
	'''
	Although there is a built-in networkx function for that, I implement a custom function to get the neighbors of a node that are not in the sequence yet.
	'''
	neighbors = []
	remaining_nodes = [n for n in service.nodes if n not in sequence.keys() and n not in sequence.values()]
	for n in remaining_nodes:
		if (n,node) in service.edges or (node,n) in service.edges:
			neighbors.append(n)
	return neighbors


def populateSequence(service, all_nodes, previous_node, sequence):
	# while there are still nodes not in the sequence
	while all_nodes:
		# find the neighbors of the previous node that are not in the sequence
		neighbors = findNeighbors(service, previous_node, sequence)
		# if there are no neighbors, the node is a leaf
		if not neighbors:
			return sequence
		# sort the neighbors according to edge bandwidth requirements
		edges = list(service.in_edges(previous_node)) + list(service.out_edges(previous_node))
		edges.sort(key = lambda x: service.edges[x]['bandwidth'], reverse = True)
		for edge in edges:
			# get the nodes of the edge
			target_nodes = [service.edges[edge]['source'], service.edges[edge]['dest']]
			# only bother with nodes that are not in the sequence yet
			node = [n for n in target_nodes if n not in sequence.keys() and n not in sequence.values()]
			if node:
				node = node[0]
			else:
				continue
			# if the node is in the consuming service
			if node in all_nodes and service.nodes[node]['sertype'] == 'consumer':
				sequence[node] = previous_node
				all_nodes.remove(node)
				temp_previous_node = node
				# recursively call the function, where all_nodes is substituted by the neighbors (not in the sequence) of the current node
				sequence = populateSequence(service, findNeighbors(service, temp_previous_node, sequence), temp_previous_node, sequence)
			if service.nodes[node]['sertype'] == 'provider':
				all_nodes.remove(node)
	return sequence
			

