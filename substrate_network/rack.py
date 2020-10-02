import sys
sys.path.append('../')
from server import Server

class Rack(object):
 	
 	def __init__(self, rid):
 		self.rid = rid
 		self._servers = []

 	def accumulate(self, obj):
 		if type(obj) == Server:
 			self._servers.append(obj)
 		else:
 			raise TypeError(obj, "is not a Server object.")
