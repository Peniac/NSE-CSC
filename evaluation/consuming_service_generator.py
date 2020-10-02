''' 
Definitions

1. consuming service: is a network service that requires the consumption of additional VNF(s) that pertain to a different service, i.e., providing services. 
2. CSC engaged VNFs (w.r.t. the consuming service): are exactly two distinct VNFs. One VNF forwards the traffic to the receiver CSC engaged VNF of the providing service, whereas the other VNF receives the traffic, which is now processed by (a subset of) the providing service. 

General assumptions

1. Every network service is modelled as a directed graph. Nodes represent VNFs, and edges represent virtual links. VNFs require CPU, and edges require bandwidth. 
2. We consider sequential services, e.g., 'A->B->C' is OK, whereas 'A->B,A->C,B->C' is NOT OK

Environment

1. CPU in [0.72, 1.44, 2.16, 2.88, 3.6GHz] (randomly) 
2. bandwidth in [10Mbps, 200Mbps] (randomly)
3. length (i.e., number of VNFs per service) in [3,8] (randomly)
4. The two CSC engaged VNFs are randomly sampled (without replacement)
5. Duration in [3,10] time intervals
'''

# dependencies 
import networkx as nx 
import random 

def initializeConsumingService(providing_services, service_index, time):
	''' 
	Function that generates a consuming service, in the form of a graph. The consuming service pairs with a providing service, and the corresponding consuming service graph adds VNFs and edges for the CSC, also. 
	'''
	# the providing service that the consuming service will pair with
	providing_service = random.choice(providing_services)
	# list of possible VNF CPU requirements
	CPUs = [0.72, 1.44, 2.16, 2.88, 3.6]
	CPUs = [round(cpu/7.2,2) for cpu in CPUs]
	# the length of the network service
	service_length = random.randint(3,8)
	# list of CSC VNF indices 
	first_CSC_engaged_VNF = random.choice(range(service_length-1)) 
	CSC_engaged_VNFs = [first_CSC_engaged_VNF, first_CSC_engaged_VNF+1]
	# create empty directional graph 
	G = nx.DiGraph(id = service_index, type = 'consuming', provider_pair = providing_service.graph['id'], expires_in = time + random.randint(3,10))
	# populate the consuming service graph with VNF nodes
	for j in range(service_length):
		if j not in CSC_engaged_VNFs:
			VNF_type = 'VNF'
		else:
			VNF_type = 'C_CSC_VNF'
		G.add_node("C{0}VNF{1}".format(service_index,j), type = VNF_type, cpu = random.choice(CPUs), serid = service_index, sertype = 'consumer')
	
	nodes = list(G.nodes())
	# add edges between VNFs sequentially 
	for j in range(service_length-1):
		G.add_edge(nodes[j],nodes[j+1], source = nodes[j], dest= nodes[j+1], bandwidth = random.randrange(10,100), sertype = 'consuming') 

	# the corresponding CSC VNF indices of the providing service
	CSC_engaged_VNFs_provider = [n for n in providing_service.nodes if providing_service.nodes[n]['type'] == 'CSC_VNF']
	# add the CSC nodes of the providing service to the consuming service
	for j in CSC_engaged_VNFs_provider:
		G.add_node(j, type = 'P_CSC_VNF', sertype = 'provider')
	# add the 2 CSC-engaged edges 
	# from consuming to providing 
	G.add_edge(nodes[CSC_engaged_VNFs[0]], CSC_engaged_VNFs_provider[0], source = nodes[CSC_engaged_VNFs[0]], dest = CSC_engaged_VNFs_provider[0], bandwidth = random.randrange(10,100), sertype = 'providing')
	# from providing to consuming 
	if len(CSC_engaged_VNFs_provider) == 2:
		G.add_edge(CSC_engaged_VNFs_provider[1], nodes[CSC_engaged_VNFs[1]], source = CSC_engaged_VNFs_provider[1], dest = nodes[CSC_engaged_VNFs[1]], bandwidth = random.randrange(10,100), sertype = 'providing')
	else:
		G.add_edge(CSC_engaged_VNFs_provider[0], nodes[CSC_engaged_VNFs[1]], source = CSC_engaged_VNFs_provider[0], dest = nodes[CSC_engaged_VNFs[1]], bandwidth = random.randrange(10,100), sertype = 'providing')		

	return G


	