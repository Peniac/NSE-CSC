""" 
General assumption 

1. A providing service will be treated as an already embedded network service, consolidated within a single rack. 

Environment 

1. Placement policy: consolidate the VNFs into the same server. If not possible, consolidate them into the same rack.  
"""


def placeProvidingServices(providing_services, datacenter):
	if len(providing_services) != len(datacenter._racks):
		raise ValueError("The number of providing services is not equal to the number of the datacenter racks.")

	# Node Mapping
	
	i = 0
	current_rack = "ToR"+str(i) 
	for service in providing_services:
		VNFs = list(service.nodes)
		# the servers of the current rack
		servers = [s for s in datacenter.allServers() if s.tor == current_rack]
		# remember which is the server that hosts the previous VNF of the chain
		server = servers[0]
		# the VNF index
		n = 0
		fits_n = True
		while n < len(VNFs) and fits_n:
			if server.canFitNode(service, VNFs[n]):
				server.putNode(service, VNFs[n])
				datacenter.VNF_to_server_mapping[VNFs[n]] = server
				n += 1
				fits_n = True
			else:
				for s in [s for s in servers if s!=server]:
					if s.canFitNode(service, VNFs[n]):
						s.putNode(service, VNFs[n])
						datacenter.VNF_to_server_mapping[VNFs[n]] = s
						n += 1
						fits_n = True	
						server = s
						break
					else:
						fits_n = False
						continue
		if not fits_n:
			return print("one VNF of the providing service does not fit into any of the servers")				
		else:
			i += 1
			current_rack = "ToR"+str(i)
		
		# Link Mapping

		# for every edge in the graph, find the corresponding servers that host the nodes of the edge, and apply its bandwidth on a path (set of links) that connects these servers 

		edges = list(service.edges)
		for edge in edges:
			bandwidth = service.edges[edge]['bandwidth']
			node1 = service.edges[edge]['source']
			node2 = service.edges[edge]['dest']
			server1 = datacenter.VNF_to_server_mapping[node1]
			server2 = datacenter.VNF_to_server_mapping[node2]
			# if the VNFs are placed within the same server, do not apply any bandwidth 
			if server1 != server2: 
				link_dict = datacenter.link_dict
				links = [link_dict[server1.id,server1.tor], link_dict[server2.id,server2.tor]]
				for link in links:
					# apply the bandwidth if the links have enough capacity
					if link.capacity - bandwidth >= 0:
						link.capacity -= bandwidth
					else:
						return print("links don't have enough capacity")
				