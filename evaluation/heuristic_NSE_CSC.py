'''
heuristic that embeds a consuming service, based on the notion of an embedding sequence

Arguments: 
	1. datacenter 
	2. service
	3. embedding sequence
'''
from collections import defaultdict 
import random

def NSE_CSC(datacenter, service, sequence):

	# virtual node mapping 

	# sort the racks once, according to their available tor-to-core link bandwidth
	ToR_switches = list([switch for switch in datacenter._switches if switch.level == "ToR"])
	Core_swithces = list([switch for switch in datacenter._switches if switch.level == "Core"])
	ToR_to_Core_links = defaultdict(list)
	for ToR in ToR_switches:
		for Core in Core_swithces:
			ToR_to_Core_links[ToR].append(datacenter.link_dict[ToR.id, Core.id].capacity)
		ToR_to_Core_links[ToR] = sum(ToR_to_Core_links[ToR])/len(ToR_to_Core_links[ToR])
	sorted(ToR_to_Core_links, key=lambda k: ToR_to_Core_links[k], reverse = True)
	tors = list(ToR_to_Core_links.keys())
	tors = [tor.id for tor in tors]

	for node in sequence.keys():
		placed = False

		# 'Place in the same server' attempt
		# find the server towards which the 'node' should be placed, according to the 'sequence'
		target_server = [s for s in datacenter.allServers() if sequence[node] in s._vnfs][0]
		if target_server.canFitNode(service, node):
			target_server.putNode(service, node)
			datacenter.VNF_to_server_mapping[node] = target_server
			placed = True
			continue

		# 'Place in the same rack' attempt
		if not placed:
			# find the servers of the rack of the 'target_server'
			target_servers = [s for s in datacenter.allServers() if s.tor == target_server.tor]
			target_servers.remove(target_server)
			isLeaf = True if node in sequence.values() else False
			# best fit (ascending order) if the node is leaf, else worst fit (descending order)
			target_servers.sort(key = lambda x: x.cpu, reverse = isLeaf)
			for s in target_servers:
				if s.canFitNode(service, node):
					s.putNode(service,node)
					datacenter.VNF_to_server_mapping[node] = s
					placed = True
					break
		
		# 'Place in another rack with the least amount of inter-rack traffic' attempt
		if not placed:
			# iterate through the sorted racks 
			for tor in tors:
				target_servers = [s for s in datacenter.allServers() if s.tor == tor]
				# best fit (ascending order) if the node is leaf, else worst fit (descending order)
				target_servers.sort(key = lambda x: x.cpu, reverse = isLeaf)
				for s in target_servers:
					if s.canFitNode(service, node):
						s.putNode(service,node)
						datacenter.VNF_to_server_mapping[node] = s
						placed = True
						break	
				if placed:
					break
		
		# the node can't be placed anywhere, stop the embedding procedure
		if not placed:
			break

	# if the last node attempted to be embedded is still not placed, cancel all placements related to this service
	if not placed:
		cancelPlacements(datacenter, service)
		return False
	
	# virtual link mapping 

	# for every edge in the graph, find the corresponding servers that host the nodes of the edge, and apply its bandwidth on a path (set of links) that connects these servers. The path is randomly selected. 
	placed = False
	edges = list(service.edges)
	for e in edges:
		bandwidth = service.edges[e]['bandwidth']
		node1 = service.edges[e]['source']
		node2 = service.edges[e]['dest']
		server1 = datacenter.VNF_to_server_mapping[node1]
		server2 = datacenter.VNF_to_server_mapping[node2]
		# if the nodes are placed within the same server, do not apply any bandwidth 
		if server1 == server2:
			pass
		# if the nodes are placed within the same rack, there is a unique path that connects them
		elif server1.tor == server2.tor: 
			link_dict = datacenter.link_dict
			links = [link_dict[server1.id,server1.tor], link_dict[server2.id,server2.tor]]
			if links[0].canFitEdge(service, e) and links[1].canFitEdge(service, e):
				links[0].putEdge(service, e)
				links[1].putEdge(service, e)
				datacenter.edge_to_links[e] = links
				placed = True
		# if the nodes are placed in servers of different racks 
		else:
			link_dict = datacenter.link_dict
			link1 = [link_dict[server1.id,server1.tor]][0]
			link4 = [link_dict[server2.id,server2.tor]][0]
			link2 = [link for link in datacenter._links if link.end1 == server1.tor]
			link2 = random.choice(link2)
			link3 = [link for link in datacenter._links if link.end1 == server2.tor and link.end2 == link2.end2][0]
			links = [link1,link2,link3,link4]
			# check if the edge can be placed in the selected path 
			if any(link.canFitEdge(service, e) == True for link in links):
				for link in links:
					link.putEdge(service, e)
				datacenter.edge_to_links[e] = links
				placed = True

	if not placed:
		cancelPlacements(datacenter, service)
		return False
	
	return True
					

def cancelPlacements(datacenter, service):
	'''
	removes the nodes and edges of the consuming service that have been embedded to the datacenter
	'''
	# remove the embedded nodes
	nodes = [n for n in service.nodes if service.nodes[n]['sertype'] == 'consumer']
	for n in nodes:
		if n in datacenter.VNF_to_server_mapping.keys():
			server = datacenter.VNF_to_server_mapping[n]
			server.removeNode(service, n)
			del datacenter.VNF_to_server_mapping[n]

	# remove the embedded edges 
	edges = list(service.edges)
	for e in edges:
		if e in datacenter.edge_to_links.keys():
			links = datacenter.edge_to_links[e]
			for link in links:
				link.removeEdge(service, e)
			del datacenter.edge_to_links[e]