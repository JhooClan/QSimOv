import numpy as np

class QGate(object):
	def __init__(self, name="UNNAMED"):
		self.m = 1
		self.mult = 1
		self.simple = True
		self.lines = []
		self.name = name
	
	def __getitem__(self, key):
		return self.m[key]
	
	def __setitem__(self, key, value):
		self.m[key] = value
	
	def __delitem__(self, key):
		del self.m[key]
	
	def __repr__(self):
		return self.m.__repr__()
	
	def __str__(self):
		return self.m.__str__()
	
	def __lt__(self, other):
		m = other
		if type(other) == QGate:
			m = other.m
		return self.m.__lt__(m)
	
	def __le_(self, other):
		m = other
		if type(other) == QGate:
			m = other.m
		return self.m.__le__(m)
	
	def __eq__(self, other):
		m = other
		if type(other) == QGate:
			m = other.m
		return self.m.__eq__(m)
	
	def __ne_(self, other):
		m = other
		if type(other) == QGate:
			m = other.m
		return self.m.__ne__(m)
	
	def __gt__(self, other):
		m = other
		if type(other) == QGate:
			m = other.m
		return self.m.__gt__(m)
	
	def __ge_(self, other):
		m = other
		if type(other) == QGate:
			m = other.m
		return self.m.__ge__(m)
	
	def __add__(self, other):
		m = other
		if type(other) == QGate:
			m = other.m
		sol = QGate()
		sol.addLine(self.m.__add__(m))
		return sol
	
	def __sub__(self, other):
		m = other
		if type(other) == QGate:
			m = other.m
		sol = QGate()
		sol.addLine(self.m.__sub__(m))
		return sol
	
	def __mod__(self, other):
		m = other
		if type(other) == QGate:
			m = other.m
		sol = QGate()
		sol.addLine(self.m.__mod__(m))
		return sol
	
	def __mul__(self, other):
		m = other
		if type(other) == QGate:
			m = other.m
		sol = QGate()
		sol.addLine(self.m.__mul__(m))
		return sol
	
	def __rmul__(self, other):
		m = other
		if type(other) == QGate:
			m = other.m
		sol = QGate()
		sol.addLine(self.m.__rmul__(m))
		return sol
	
	def __imul__(self, other):
		m = other
		if type(other) == QGate:
			m = other.m
		sol = QGate()
		sol.addLine(self.m.__rmul__(m))
		return sol
	
	def __matmul__(self, other):
		m = other
		if type(other) == QGate:
			m = other.m
		sol = QGate()
		sol.addLine(np.dot(self.m, m))
		return sol
	
	def __pow__(self, other):
		m = other
		if type(other) == QGate:
			m = other.m
		sol = QGate()
		sol.addLine(np.kron(self.m, m))
		return sol
	
	def addLine(self, *args):
		self.lines.append(list(args))
		if self.simple and (len(list(args)) > 1 or len(self.lines) > 1):
			self.simple = False
		aux = 1
		for gate in args:
			g = gate
			if type(gate) == QGate:
				g = gate.m
			aux = np.kron(aux, g)
		self.m = np.dot(self.m, aux)
	
	def setMult(self, mult):
		self.m *= mult/self.mult
		self.mult = mult
	
	def addMult(self, mult):
		self.m *= mult
		self.mult *= mult
	
	def setName(self, name):
		self.name = name

def getMatrix(gate):
	m = gate
	if type(gate) == QGate:
		m = gate.m
	return m

def UnitaryMatrix(mat, decimals=10):
	mustbei = np.around(np.dot(mat, Dagger(mat)), decimals=decimals)
	return (mustbei == I(int(np.log2(mustbei.shape[0])))).all()

def NormalizeGate(mat):
	det = np.linalg.det(mat)
	if det != 0:
		return mat/det
	else:
		return None

def Transpose(gate): # Returns the Transpose of the given matrix
	if type(gate) == QGate:
		t = QGate(gate.name + "T")
		t.addLine(np.matrix.transpose(gate.m))
	else:
		t = QGate("UT")
		t.addLine(np.matrix.transpose(gate))
	return t

def Dagger(gate): # Returns the Hermitian Conjugate or Conjugate Transpose of the given matrix
	if type(gate) == QGate:
		t = QGate(gate.name + "†")
		if gate.simple:
			t.addLine(Dagger(gate.m))
		else:
			lines = gate.lines[::-1]
			for line in lines:
				t.addLine(*[Dagger(g).m for g in line])
			t.setMult(gate.mult)
	else:
		t = QGate("U†")
		t.addLine(np.matrix.getH(gate))
	return t

def Invert(gate): # Returns the inverse of the given matrix
	if type(gate) == QGate:
		t = QGate(gate.name + "-¹")
		t.addLine(np.linalg.inv(gate.m))
	else:
		t = QGate("U-¹")
		t.addLine(np.linalg.inv(gate))
	return t