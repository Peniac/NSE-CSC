from rack import Rack
from switch import Switch 
from server import Server
from link import Link
from collections import defaultdict


#---------------------------------------------------------------------------------#
								# THREE LAYER FAT TREE #
#---------------------------------------------------------------------------------#

def generateThreeLayer(k):
	# initialize essential parameters 
	num_ports_per_switch = k	# number of ports per switch
	num_pod = k					# number of pods
	num_servers = int(k/2)			# number of hosts under a ToR switch 
	num_tor = int(k/2)				# number of ToR switches in a pod 
	num_agg = int(k/2)				# number of aggregation switches in a pod 
	num_core = int((k**2)/4)			# number of core switches 
	total_servers = int((k**3)/4)	# number of total servers 

	# initialize component generation 
	num_racks = num_pod * num_tor
	list_of_racks = []
	cpu_cores = 16
	for i in range(num_racks):
		rack = Rack(str(i))
		for j in range(num_servers):
			server = Server(i*(num_servers)+j,"server"+str(i)+"-"+str(j), cpu_cores)
			rack.accumulate(server)
		list_of_racks.append(rack)

	list_of_tors = []
	for i in range(num_tor * num_pod):
		tor = Switch("ToR"+str(i), "ToR", k)
		list_of_tors.append(tor)

	list_of_agg= []
	for i in range(num_agg * num_pod):
		agg = Switch("Agg"+ str(i), "Agg", k)
		list_of_agg.append(agg)

	list_of_core = []
	for i in range(num_core):
		core = Switch("Core"+str(i), "Core", k)
		list_of_core.append(core)

	list_of_links = []
	num_links = int(3 * (k**3) / 4)
	capacity = 1024 	# Mbits
	delay = 1			# ms
	for i in range(num_links):
		link = Link("link"+str(i), capacity, delay)
		list_of_links.append(link)

	return list_of_racks, list_of_tors, list_of_agg, list_of_core, list_of_links

link_dict = {}

def attachLinksThreeLayer(list_of_racks, list_of_tors, list_of_agg, list_of_core, list_of_links, k):
	temp_list_of_links = list(list_of_links)
	# each ToR is linked with their respective servers 
	tor_index = 0
	while tor_index < int((k**2)/2):
		podid = 0 # pod number
		i = 0 # rack counter
		for r in list_of_racks:
			if i % (int(k/2)) == 0 and i>0:
				podid += 1
			tor = list_of_tors[tor_index]
			for s in r._servers:
				link = temp_list_of_links[0]
				link.attach(s,tor)
				link_dict['end1',s.id]=link
				link_dict['end2',tor.id]=link
				# reference to the ToR each server is connected with 
				s.tor = tor.id
				s.pod = "pod"+str(podid)
				temp_list_of_links.remove(link)
			i += 1
			tor_index += 1
	# each ToR is linked with each Agg within a certain pod
	pod = 0
	start = 0
	end = int(k/2)
	while pod < k:
		tor_pod = list(list_of_tors[start:end])
		agg_pod = list(list_of_agg[start:end])
		for tor in tor_pod:
			for agg in agg_pod:
				link = temp_list_of_links[0]
				link.attach(tor,agg)
				link_dict['end1',tor.id]=link
				link_dict['end2',agg.id]=link
				temp_list_of_links.remove(link)
		pod += 1
		start = end
		end += int(k/2)

	# slice core switches into k/2 parts 
	# the i-th Agg within each pod should be linked with all core switches from i-th slice 
	slice_num = 0
	while slice_num < int(k/2):
		indices = [i for i in range(slice_num, int((k**2)/2), int(k/2))]
		temp_agg = []
		for i in indices:
			temp_agg.append(list_of_agg[i])
		core = list(list_of_core[int(k/2)*slice_num:int(k/2)*(slice_num+1)])

		for agg in temp_agg:
			for c in core:
				link = temp_list_of_links[0]
				link.attach(agg,c)
				link_dict['end1',agg.id]=link
				link_dict['end2',c.id]=link
				temp_list_of_links.remove(link)
		slice_num += 1

	return list_of_racks, list_of_tors, list_of_agg, list_of_core, list_of_links, link_dict



#---------------------------------------------------------------------------------#
								# TWO LAYER FAT TREE #
#---------------------------------------------------------------------------------#

def generateTwoLayer(num_of_servers, num_of_racks, num_of_core):

	list_of_racks = []
	cpu_cores = 1
	total_ram = 1.0
	total_storage = 1.0
	for i in range(num_of_racks):
		rack = Rack(str(i))
		for j in range(num_of_servers):
			server = Server(i*(num_of_servers)+j,"server"+str(i)+"-"+str(j), cpu_cores, total_ram, total_storage)
			server.tor = "ToR"+str(i)
			rack.accumulate(server)
		list_of_racks.append(rack)

	list_of_tors = []
	for i in range(num_of_racks):
		tor = Switch("ToR"+str(i), "ToR", num_of_servers+num_of_core)
		list_of_tors.append(tor)

	list_of_core = []
	for i in range(num_of_core):
		core = Switch("Core"+str(i), "Core", num_of_racks)
		list_of_core.append(core)

	list_of_links = []
	num_of_tor_links = int(num_of_servers*num_of_racks)
	capacity_tor = 1000 # Mbits
	num_of_other_links = int(num_of_racks*num_of_core)
	capacity_other = 10000 # Mbits
	delay = 90
	for i in range(num_of_tor_links):
		link = Link("link"+str(i), capacity_tor, delay)
		list_of_links.append(link)
	for i in range(num_of_other_links):
		link = Link("link"+str(num_of_tor_links+i), capacity_other, delay)
		list_of_links.append(link)

	return list_of_racks, list_of_tors, list_of_core, list_of_links


def attachLinksTwoLayer(list_of_racks, list_of_tors, list_of_core, list_of_links):

	temp_list_of_links = list(list_of_links)
	link_dict = {}
	servers = []
	index = 0
	for rack in list_of_racks:
		for s in rack._servers:
			servers.append(s)
			s.tor = list_of_tors[index].id
			link = temp_list_of_links[0]
			link.level = "Rack"
			link.attach(s,list_of_tors[index])
			link_dict[s.id,list_of_tors[index].id] = link
			temp_list_of_links.remove(link)
		index += 1

	for tor in list_of_tors:
		for core in list_of_core:
			link = temp_list_of_links[0]
			link.level = "OutOfRack"
			link.attach(tor,core)
			link_dict[tor.id, core.id] = link 
			temp_list_of_links.remove(link)

	return list_of_racks, list_of_tors, list_of_core, list_of_links, link_dict