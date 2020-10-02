"""
Definitions 

1. providing service: is a network service that exposes a subset of its VNFs to other services, i.e., consuming services (see definition in the 'consuming_service_generator' module), for functionality consumption. 
2. CSC engaged VNFs (w.r.t. the providing service): are (i) the VNF that "receives" the traffic from a consuming service, and (ii)the VNF that conveys this traffic back to the consuming service. The CSC engaged VNFs could be one (the same VNF receives, processes, and returns the traffic - CSC type 1) or two distinct VNFs. 

General assumptions

1. Every network service is modelled as a directed graph. Nodes represent VNFs, and edges represent virtual links. VNFs require CPU, and edges require bandwidth. 
2. We consider sequential services, e.g., 'A->B->C' is OK, whereas 'A->B,A->C,B->C' is NOT OK

Environment

1. CPU in [0.72, 1.44, 2.16, 2.88, 3.6GHz] (randomly) 
2. bandwidth in [10Mbps, 200Mbps] (randomly)
3. length (i.e., number of VNFs per service) in [3,8] (randomly)
4. Two CSC engaged VNFs are randomly sampled with replacement (this makes CSC types 1 feasible, but less frequent)
5. Duration = +infinity 
"""

# dependencies 
import networkx as nx 
import random 

def initializeNProvidingServices(N):
	''' 
	Function that generates N providing services, in the form of graphs, and returns them into a list
	'''

	if not type(N) is int or N<=0:
		raise ValueError("Only positive integers are allowed")
	# list to store the graphs 
	providingServices = [] 
	# list of candidate VNF CPU requirements 
	CPUs = [0.72, 1.44, 2.16, 2.88, 3.6] 
	CPUs = [round(cpu/7.2,2) for cpu in CPUs]
	for i in range(N): 
		# the length of the network service
		service_length = random.randint(3,8) 
		# list of CSC VNFs indices 
		CSC_engaged_VNFs = random.choices(range(service_length),k=2)
		# sort the indices of these VNFs, so that connections are established properly 
		CSC_engaged_VNFs.sort()
		# create empty directional graph
		G = nx.DiGraph(id=i, duration= float('inf'))  

		for j in range(service_length):
			# distinguish among CSC-engaged VNFs and the rest 
			if j not in CSC_engaged_VNFs:
				VNF_type = 'VNF'
			else:
				VNF_type = 'CSC_VNF'
			G.add_node("P{0}VNF{1}".format(i,j), type = VNF_type, cpu = random.choice(CPUs), serid = i, sertype = 'provider')

		nodes = list(G.nodes())
		# add edges between VNFs sequentially 
		for j in range(service_length-1):
			G.add_edge(nodes[j],nodes[j+1], source = nodes[j], dest= nodes[j+1], bandwidth = random.randrange(10,100))  

		# store the providing service 
		providingServices.append(G)  

	return providingServices
