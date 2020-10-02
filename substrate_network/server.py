class Server(object):
	

	def __init__(self, num, serid, cpu, ram, storage):
		self.num = num
		self.id = serid 
		self.cpu = cpu
		self.initial_cpu = cpu
		self.tor = "None"
		self.pod = "None"
		self._vnfs = []

	def canFitNode(self, G, vnf):
		if (self.cpu - G.nodes[vnf]['cpu'] >= 0):
			return True 
		else:
			return False 

	def putNode(self, G, vnf):
		self.cpu -=  G.nodes[vnf]['cpu'] 
		self._vnfs.append(vnf)

	def removeNode(self, G, vnf):
		self.cpu = self.cpu +  G.nodes[vnf]['cpu']
		self._vnfs.remove(vnf)

