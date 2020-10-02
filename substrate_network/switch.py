class Switch():

	def __init__(self, swid, level, init_ports):
		self.id = swid
		self.cpu = 0
		self.ram = 0
		self.storage = 0
		self.level = level
		self.init_ports = init_ports
		self.avail_ports = init_ports

	def bindPort(self):
		if self.avail_ports > 0:
			self.avail_ports -= 1
		else:
			raise ValueError("Not enough ports to attach more links to the switch", self.id)
