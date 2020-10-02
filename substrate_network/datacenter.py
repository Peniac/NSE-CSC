import sys 
sys.path.append('C://Users//angel//Desktop//open projects//NSE-CSC//code//substrate_network')

# dependencies 

from rack import Rack
from switch import Switch 
from server import Server
from link import Link
from generate_topology import  *
from collections import defaultdict
import copy

from scipy import stats 
import seaborn as sns
from matplotlib import pyplot as plt 

class DC(object):

	# the constructor
	def __init__(self, dcid, location, topology):
		# a datacenter is a collection of racks, switches and links
		# routes is a dictionary with key = (start_point, end_point) and value = list of links
		# db is a dictionary with key = service_id and value = list of server ids 
		# all_db is a dictionary with key = server_id and value = list of vnf names
		self.dcid = dcid
		self.location = location
		self.topology = topology
		self._racks = []
		self._switches = [] 
		self._links = []
		self.routes = {}
		self.link_dict = {}
		self.db = {}
		self.all_db = defaultdict(list)
		# service name: leaving time
		self.services = {}
		self.cpu = 0
		self.ram = 0 
		self.storage = 0
		self.revenue = 0 
		self.VNF_to_server_mapping = {}
		self.edge_to_links = defaultdict(list)

	# function used for appending to lists of objects that form the datacenter 
	def accumulate(self, obj):
		if type(obj) == Rack:
			self._racks.append(obj)
		elif type(obj) == Switch:
			self._switches.append(obj)
		elif type(obj) == Link:
			self._links.append(obj)
		else:
			raise TypeError(obj, "should be a Rack, a Switch or a Link.")

	# function used for populating a datacenter with network elements 
	def populateDc(self, topology, k, num_of_servers, num_of_racks, num_of_core):

		if topology == "3-Layer Fat-Tree":
			racks, tors, aggs, core, links =  generateThreeLayer(k)
			conf_racks, conf_tors, conf_aggs, conf_core, conf_links, link_dict = attachLinksThreeLayer(racks, tors, aggs, core, links, k)
			new_list = conf_racks + conf_tors + conf_aggs + conf_core + conf_links
			self.link_dict = dict(link_dict)
			for obj in new_list:
				self.accumulate(obj)

		if topology == "2-Layer Fat-Tree":
			racks, tors, core, links =  generateTwoLayer(num_of_servers, num_of_racks, num_of_core)
			conf_racks, conf_tors, conf_core, conf_links, link_dict = attachLinksTwoLayer(racks, tors, core, links)
			new_list = conf_racks + conf_tors + conf_core + conf_links
			self.link_dict = link_dict
			for obj in new_list:
				self.accumulate(obj)	

		else:
			raise ValueError("Please, insert a valid datacenter topology.")

	# function that returns all of the datacenter's servers
	def allServers(self):
		l_servers = []
		for r in self._racks:
			l_servers.append(r._servers)
		servers = [server for sublist in l_servers for server in sublist]

		return servers

	def findExpiringServices(self,time):
		expiring_services = []
		for k in self.services.keys():
			if self.services[k] == time:
				expiring_services.append(k)
		return expiring_services

	def removeExpiredServices(self, expired_services):
		for service in expired_services:
			nodes = [n for n in service.nodes if service.nodes[n]['sertype'] == 'consumer']
			for n in nodes:
				server = self.VNF_to_server_mapping[n]
				server.removeNode(service, n)
			for e in service.edges:
				links = self.edge_to_links[e]
				for link in links:
					link.removeEdge(service, e)





	



