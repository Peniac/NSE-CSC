import sys 
sys.path.append('C://Users//angel//Desktop//open projects//3. NSE-CSC//code//substrate_network')

import numpy as np
import pickle 

from datacenter import DC
from providing_service_generator import initializeNProvidingServices
from providing_service_placement import placeProvidingServices
from consuming_service_generator import initializeConsumingService 
from embedding_sequence import embeddingLogic
from heuristic_NSE_CSC import NSE_CSC
from baseline_NSE import NSE


# dicts to store results 
total_accepted1 = 0
total_accepted2 = 0
acceptance_rate1 = {}
acceptance_rate2 = {}

cpu1 = {}
cpu2 = {}

total_flow1 = {}
inter_rack1 = {}
total_flow2 = {}
inter_rack2 = {}

if __name__ == "__main__":
	# define the substrate network topology 
	topology = "2-Layer Fat-Tree"

	# create the datacenters 
	datacenter1 = DC("id1", "City1", topology)
	datacenter2 = DC("id2", "City2", topology)

	# populate the datacenters with racks, servers and links
	# according to the specified topology
	datacenter1.populateDc(topology, 4, 20, 10, 5)
	datacenter2.populateDc(topology, 4, 20, 10, 5)

	# create and embed the providing services into each datacenter
	datacenters = [datacenter1, datacenter2]
	num_of_providing_services = len(datacenter1._racks)
	providing_services = initializeNProvidingServices(num_of_providing_services)
	for datacenter in datacenters:
		placeProvidingServices(providing_services, datacenter)

	# number of time intervals	
	max_time = 600
	# the number of arriving services per time interval follows a Poisson distribution, with an average of 20
	arriving_services = list(np.random.poisson(20, max_time + 1))  
	time = 0
	while time <= max_time:
		print(max_time - time)
		# find the expiring services at time 'time', if any, and remove them 
		expired_services1 = datacenter1.findExpiringServices(time)
		datacenter1.removeExpiredServices(expired_services1)
		expired_services2 = datacenter2.findExpiringServices(time)
		datacenter2.removeExpiredServices(expired_services2)
		# try to embed 'arriving_services[time]' consuming network services at time 'time' (sequentially)
		for i in range(arriving_services[time]):
			if time == 0:
				service_index = i
			else:
				service_index = sum(arriving_services[:time]) + i
			service = initializeConsumingService(providing_services, service_index, time)
			embedding_sequence = embeddingLogic(service)
			accepted1 = NSE_CSC(datacenter1, service, embedding_sequence)
			accepted2 = NSE(datacenter2, service)
			if accepted1:
				datacenter1.services[service] = service.graph['expires_in']
				total_accepted1 += 1
			if accepted2:
				datacenter2.services[service] = service.graph['expires_in']
				total_accepted2 += 1	
			# store the acceptance rates 
			acceptance_rate1[service_index] = 100 * total_accepted1 / (service_index+1)
			acceptance_rate2[service_index] = 100 * total_accepted2 / (service_index+1)
		
		# take a snapshot of the infrastructures, and count:
		# 1: the CPU utilization
		# 2: the number of hops per virtual edge
		# 3: the percentage of inter-rack flow w.r.t. the total flow
		# 4: the number of hops per service chain length 
		# 5: the number of hops per virtual edge w.r.t. CSC-engaged and non 
		# CSC-engaged links

		if time % 15 == 0 or time == 0:
			# 1: CPU utilization 
			cpu1[time] = 100 * sum([1-s.cpu for s in datacenter1.allServers()]) / 200.0
			cpu2[time] = 100 * sum([1-s.cpu for s in datacenter2.allServers()]) / 200.0

			# 2: number of hops per virtual edge
			hops1 = [len(datacenter1.edge_to_links[key]) for key in datacenter1.edge_to_links.keys()]
			hops2 = [len(datacenter2.edge_to_links[key]) for key in datacenter2.edge_to_links.keys()]

			# 3: inter-rack flow 
			total_flow1[time] = sum([l.init_capacity - l.capacity for l in datacenter1._links])
			inter_rack1[time] = 100 * sum([l.init_capacity - l.capacity for l in datacenter1._links if l.level == 'OutOfRack']) / total_flow1[time]
			total_flow2[time] = sum([l.init_capacity - l.capacity for l in datacenter2._links])
			inter_rack2[time] = 100 * sum([l.init_capacity - l.capacity for l in datacenter2._links if l.level == 'OutOfRack']) / total_flow2[time]

			# 5: the number of hops per virtual edge w.r.t. CSC-engaged and non 
			# CSC-engaged links
			consuming_edges_hops1 = [len(datacenter1.edge_to_links[key]) for key in datacenter1.edge_to_links.keys() if 'P' not in str(key)]
			providing_edges_hops1 = [len(datacenter1.edge_to_links[key]) for key in datacenter1.edge_to_links.keys() if 'P' in str(key)]
			consuming_edges_hops2 = [len(datacenter2.edge_to_links[key]) for key in datacenter2.edge_to_links.keys() if 'P' not in str(key)]
			providing_edges_hops2 = [len(datacenter2.edge_to_links[key]) for key in datacenter2.edge_to_links.keys() if 'P' in str(key)]

		time += 1
		
# save the acceptance rate dicts 
with open('C:/Users/angel/Desktop/open projects/3. NSE-CSC/code/results/data/acc_rate_NSE-CSC.pkl', 'wb') as f:
	pickle.dump(acceptance_rate1, f)
with open('C:/Users/angel/Desktop/open projects/3. NSE-CSC/code/results/data/acc_rate_baseline.pkl', 'wb') as f:
	pickle.dump(acceptance_rate2, f)

# save the number of hops per virtual edge lists 
with open('C:/Users/angel/Desktop/open projects/3. NSE-CSC/code/results/data/hops_NSE-CSC.pkl', 'wb') as f:
	pickle.dump(hops1, f)
with open('C:/Users/angel/Desktop/open projects/3. NSE-CSC/code/results/data/hops_baseline.pkl', 'wb') as f:
	pickle.dump(hops2, f)

# save the CPU utilization dicts 
with open('C:/Users/angel/Desktop/open projects/3. NSE-CSC/code/results/data/cpu_NSE-CSC.pkl', 'wb') as f:
	pickle.dump(cpu1, f)
with open('C:/Users/angel/Desktop/open projects/3. NSE-CSC/code/results/data/cpu_baseline.pkl', 'wb') as f:
	pickle.dump(cpu2, f)

# save the inter-rack percentages dicts 
with open('C:/Users/angel/Desktop/open projects/3. NSE-CSC/code/results/data/inter_rack_NSE-CSC.pkl', 'wb') as f:
	pickle.dump(inter_rack1, f)
with open('C:/Users/angel/Desktop/open projects/3. NSE-CSC/code/results/data/inter_rack_baseline.pkl', 'wb') as f:
	pickle.dump(inter_rack2, f)

# save the number of hops per virtual edge lists 
with open('C:/Users/angel/Desktop/open projects/3. NSE-CSC/code/results/data/consuming_edges_hops_NSE-CSC.pkl', 'wb') as f:
	pickle.dump(consuming_edges_hops1, f)
with open('C:/Users/angel/Desktop/open projects/3. NSE-CSC/code/results/data/providing_edges_hops_NSE-CSC.pkl', 'wb') as f:
	pickle.dump(providing_edges_hops1, f)
with open('C:/Users/angel/Desktop/open projects/3. NSE-CSC/code/results/data/consuming_edges_hops_baseline.pkl', 'wb') as f:
	pickle.dump(consuming_edges_hops2, f)
with open('C:/Users/angel/Desktop/open projects/3. NSE-CSC/code/results/data/providing_edges_hops_baseline.pkl', 'wb') as f:
	pickle.dump(providing_edges_hops2, f)

print('Finished !!!')


