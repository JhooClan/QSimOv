import math as m
import cmath as cm
import numpy as np
import random as rnd
# np.zeros((h,w), dtype=complex) Inicializa una matriz de numeros complejos con alto h y ancho w
# La suma de matrices se realiza con +. A + B
# La multiplicacion por un escalar se hace con *. n * A
# Para multiplicar las matrices A y B se usa np.dot(A,B)
# El producto Kronecker de A y B esta definido con np.kron(A,B)

class QRegistry:
    def __init__(self, qbits, **kwargs):    # QuBit list. Seed for the Pseudo Random Number Generation can be specified with seed = <seed> as an argument.
        if (type(qbits) != list or \
            not qbits or \
            #not all(type(qbit) == np.ndarray and \
            #        qbit.shape == (1,2) and \
            #        qbit.dtype == 'complex128' for qbit in qbits)):
            not all(type(qbit) == type(0) and \
                    (qbit == 0 or qbit == 1) for qbit in qbits)):
            raise ValueError('Impossible QuBit Registry')
        #qbs = qbits[:]
        qbs = [QOne() if i else QZero() for i in qbits]

        self.state = qbs[0]
        Normalize(self.state)
        del qbs[0]
        for qbit in qbs:
            Normalize(qbit)
            self.state = np.kron(self.state, qbit)
        Normalize(self.state)
        if (kwargs.get('seed', None) != None):
            rnd.seed(kwargs['seed'])

    def Measure(self, mask, remove = False): # List of numbers with the QuBits that should be measured, numerated as q0..qn. If you want to measure q2 and q4, the imput will be [2,4]. remove = True if you want to remove a QuBit from the registry after measuring
        if (type(mask) != list or \
            not all(type(num) == int for num in mask)):
            raise ValueError('Not valid mask')
        tq = m.log(self.state.size,  2)
        if (not all(num < tq and num > -1 for num in mask)):
            raise ValueError('Out of range')
        measure = []
        for qbit in mask:
            r = rnd.random()
            p = 0
            max = 2**(tq - (qbit + 1))
            cnt = 0
            rdy = True
            for i in range(0, self.state.size):
                if (cnt == max):
                    rdy = not rdy
                    cnt = 0
                if (rdy):
                    p += cm.polar(self.state[0,i])[0]**2
                cnt += 1
            if (r < p):
                me = 0
            else:
                me = 1
            measure.append(me)
            self.Collapse((tq - (qbit + 1)), me, remove)
        return measure

    def ApplyGate(self, *gates): # Applies a quantum gate to the registry.
        gate = gates[0]
        for i in range(1, len(gates)):
            gate = np.kron(gate, gates[i])
        self.state = np.dot(Bra(self.state), gate)
    
    def Collapse(self, qbit, measure, remove): # Collapses a qubit from the registry. qbit is the id of the qubit, numerated as q0..qn in the registry. measure is the value obtained when measuring it. remove indicates whether it should be removed from the registry.
        max = 2**qbit
        cnt = 0
        rdy = measure == 1
        mfd = []
        for i in range(0, self.state.size):
            if (cnt == max):
                rdy = not rdy
                cnt = 0
            if (rdy):
                self.state[0, i] = 0
                mfd.append(i)
            cnt += 1
        if (remove):
            for qbit in mfd[::-1]:
                self.state = np.delete(self.state, qbit, 1)
        Normalize(self.state)
    def DensityMatrix(self):
        return np.dot(Ket(self.state), Bra(self.state))
    def VNEntropy(self, **kwargs):
        base = kwargs.get('base', "e")
        #dm = self.DensityMatrix()
        #evalues, m = np.linalg.eig(dm)
        entropy = 0
        #for e in evalues:
        #    if e != 0:
        #        entropy += e * np.log(e)
        for amp in self.state[0]:
            p = cm.polar(amp)[0]**2
            if p > 0:
                if base == "e":
                    entropy += (p * np.log(p))
                elif type(base) == int or type(base) == float:
                    entropy += (p * m.log(p, base))
        return -entropy

def UnitaryMatrix(mat, decimals=10):
    mustbei = np.around(np.dot(mat, Dagger(mat)), decimals=decimals)
    return (mustbei == I(int(np.log2(mustbei.shape[0])))).all()

def Prob(q, x): # Devuelve la probabilidad de obtener x al medir el qbit q
    p = 0
    if (x < q.size):
        p = cm.polar(q[0,x])[0]**2
    return p

def Hadamard(n): # Devuelve una puerta Hadamard para n QuBits
    H = 1 / m.sqrt(2) * np.ones((2,2), dtype=complex)
    H[1,1] = -1 / m.sqrt(2)
    if n > 1:
        H = np.kron(H, Hadamard(n - 1))
    return H

def QBit(a,b): # Devuelve un QuBit con a y b. q = a|0> + b|1>, con a y b complejos
    q = np.array([a,b], dtype=complex)
    q.shape = (1,2)
    Normalize(q)
    return q

def QZero(): # Devuelve un QuBit en el estado 0
    q = np.array([complex(1,0),complex(0,0)])
    q.shape = (1,2)
    return q

def QOne(): # Devuelve un QuBit en el estado 1
    q = np.array([complex(0,0),complex(1,0)])
    q.shape = (1,2)
    return q

def PauliX(): # Also known as NOT
    px = np.array([0,1,1,0], dtype=complex)
    px.shape = (2,2)
    return px

def PauliY():
    py = np.array([0,-1j,1j,0], dtype=complex)
    py.shape = (2,2)
    return py

def PauliZ():
    pz = np.array([1,0,0,-1], dtype=complex)
    pz.shape = (2,2)
    return pz

def V(): # V gate, usually seen in its controlled form C-V. Its hermitian also can be seen as V+.
#    v = np.array([1,0,0,1j], dtype=complex)
#    v.shape = (2,2)
#    return v
    v = np.array([1, -1j, -1j, 1], dtype=complex)
    v.shape = (2,2)
    return v * ((1 + 1j)/2)

def Bra(v): # Devuelve el QuBit pasado como parametro en forma de fila. <q|
    b = v[:]
    s = v.shape
    if s[0] != 1:
        b = np.transpose(b)
    return b

def Ket(v): # Devuelve el QuBit pasado como parametro en forma de columna. |q>
    k = v[:]
    s = v.shape
    if s[1] != 1:
        k = np.transpose(k)
    return k

def ApplyGate(state, gate): # Devuelve el resultado de aplicar una puerta logica sobre una serie de estados. El QuBit mas significativo a la izquierda de la lista.
    return np.dot(Bra(state), gate)

def Superposition(x, y): # Devuelve el estado compuesto por los dos QuBits.
    z = np.kron(x, y)
    Normalize(z)
    return z

def Normalize(state): # Funcion que asegura que se cumpla la propiedad que dice que |a|^2 + |b|^2 = 1 para cualquier QuBit. Si no se cumple, modifica el QuBit para que la cumpla si se puede.
    sqs = 0
    for i in range(0, state.size):
        sqs += cm.polar(state[0, i])[0]**2
    sqs = m.sqrt(sqs)
    if (sqs == 0):
        raise ValueError('Impossible QuBit')
    if (sqs != 1):
        for bs in state:
            bs /= sqs

def SWAP(): # SWAP gate for 2 qubits
    sw = np.zeros((4,4), dtype=complex)
    sw[0,0] = 1
    sw[1,2] = 1
    sw[2,1] = 1
    sw[3,3] = 1
    return sw

def SqrtSWAP(): # Square root of SWAP gate for 2 qubits
    sw = np.zeros((4,4), dtype=complex)
    sw[0,0] = 1
    sw[1,1] = 0.5 * (1+1j)
    sw[1,2] = 0.5 * (1-1j)
    sw[2,1] = 0.5 * (1-1j)
    sw[2,2] = 0.5 * (1+1j)
    sw[3,3] = 1
    return sw

'''
def SqrtNOT(): # Square root of NOT gate, also called V gate
    sn = np.array([1+1j, 1-1j, 1-1j, 1+1j], dtype=complex)
    sn.shape = (2,2)
    return sn * 0.5
'''

def ControlledU(gate): # Returns a controlled version of the given gate
    gdim = gate.shape[0]
    cu = np.eye(gdim*2, dtype=complex)
    cu[gdim:,gdim:] = gate
    return cu

def CNOT(): # Returns a CNOT gate for two QuBits, also called Feynman gate
    return ControlledU(PauliX())

def Toffoli(): # Returns a CCNOT gate for three QuBits. A, B, C -> P = A, Q = B, R = AB XOR C.
    ''' # This does the same as the line below. Circuit with the implementation of Toffoli gate using SWAP, CNOT, Controlled-V and Controlled-V+
    # Gates needed (without control SWAPs): 5
    gate = np.kron(I(1), ControlledU(V()))
    gate = np.dot(gate, np.kron(SWAP(), I(1)))
    gate = np.dot(gate, np.kron(I(1), ControlledU(V())))
    gate = np.dot(gate, np.kron(CNOT(), I(1)))
    gate = np.dot(gate, np.kron(I(1), ControlledU(Dagger(V()))))
    gate = np.dot(gate, np.kron(CNOT(), I(1)))
    gate = np.dot(gate, np.kron(SWAP(), I(1)))
    return gate
    '''
    return ControlledU(CNOT())

def Fredkin(): # Returns a CSWAP gate for three QuBits
    return ControlledU(SWAP())

def I(n): # Returns Identity Matrix of specified size
    IM = np.array([[1,0],[0,1]], dtype=complex)
    if n > 1:
        IM = np.kron(IM, I(n - 1))
    return IM

def Transpose(gate): # Returns the Transpose of the given matrix
    return np.matrix.transpose(gate)

def Dagger(gate): # Returns the Hermitian Conjugate or Conjugate Transpose of the given matrix
    return np.matrix.getH(gate)

def Invert(gate): # Returns the inverse of the given matrix
    return np.linalg.inv(gate)

def getSC(number):
    return len(str(number).replace('.', ''))

def setSC(number, sc):
    res = 0
    num = str(number).split('.')
    i = len(num[0])
    d = 0
    if i >= sc:
        diff = i - sc
        res = int(num[0][0:sc]+"0"*diff)
    elif len(num) == 2:
        d = len(num[1])
        tsc = min(sc - i, d)
        diff = 0
        if sc - i > d:
            diff = sc - i - d
        res = float(num[0] + '.' + num[1][0:tsc]+"0"*diff)
        if d > tsc and num[1][tsc] >= '5':
            res += 10**-tsc
    return res

def toComp(angle, sc=None): # Returns a complex number with module 1 and the specified phase. Improved precision with k*pi/2, with k integer
    while angle >= 2*np.pi:
        angle -= 2*np.pi
    if sc == None:
        sc = getSC(angle)
    res = np.around(m.cos(angle), decimals=sc-1) + np.around(m.sin(angle), decimals=sc-1)*1j
    aux = 2 * angle
    if aux == 0:
        res = 1+0j
    elif aux == 1*np.pi:
        res = 1j
    elif aux == 2*np.pi:
        res = -1+0j
    elif aux == 3*np.pi:
        res = -1j
    return res

def PhaseShift(angle): # Phase shift (R) gate, rotates qubit with specified angle (in radians)
    ps = np.array([1, 0, 0, toComp(angle)], dtype=complex)
    ps.shape = (2,2)
    return ps

def Peres(): # A, B, C -> P = A, Q = A XOR B, R = AB XOR C. Peres gate.
    ''' # Implementation of Peres gate with smaller gates.
    # Gates needed (without control SWAPs): 4
    gate = np.kron(SWAP(), I(1))
    gate = np.dot(gate, np.kron(I(1), ControlledU(V())))
    gate = np.dot(gate, np.kron(SWAP(), I(1)))
    gate = np.dot(gate, np.kron(I(1), ControlledU(V())))
    gate = np.dot(gate, np.kron(CNOT(), I(1)))
    gate = np.dot(gate, np.kron(I(1), ControlledU(Dagger(V()))))
    return gate
    '''
    return np.dot(Toffoli(), np.kron(CNOT(), I(1)))

def R(): # A, B, C -> P = A XOR B, Q = A, R = AB XOR ¬C. R gate.
    ''' Old implementation using Peres gate.
    gate = np.kron(I(2), PauliX())
    gate = np.dot(gate, Peres())
    gate = np.dot(gate, np.kron(SWAP(), I(1)))
    '''
    # Optimized implementation with smaller gates
    # Gates needed (without control SWAPs): 6
    gate = np.kron(SWAP(), PauliX())
    gate = np.dot(gate, np.kron(I(1), ControlledU(V())))
    gate = np.dot(gate, np.kron(SWAP(), I(1)))
    gate = np.dot(gate, np.kron(I(1), ControlledU(V())))
    gate = np.dot(gate, np.kron(CNOT(), I(1)))
    gate = np.dot(gate, np.kron(I(1), ControlledU(Dagger(V()))))
    gate = np.dot(gate, np.kron(SWAP(), I(1)))
    return gate

def TR(): # A, B, C -> P = A, Q = A XOR B, R = A¬B XOR C. TR gate.
    # Implementation of TR gate with smaller gates.
    # Gates needed (without control SWAPs): 6
    gate = np.kron(I(1), np.kron(PauliX(), I(1)))
    gate = np.dot(gate, np.kron(SWAP(), I(1)))
    gate = np.dot(gate, np.kron(I(1), ControlledU(V())))
    gate = np.dot(gate, np.kron(SWAP(), I(1)))
    gate = np.dot(gate, np.kron(I(1), ControlledU(V())))
    gate = np.dot(gate, np.kron(CNOT(), I(1)))
    gate = np.dot(gate, np.kron(I(1), ControlledU(Dagger(V()))))
    gate = np.dot(gate, np.kron(I(1), np.kron(PauliX(), I(1))))
    return gate

def URG(): # A, B, C -> P = (A+B) XOR C, Q = B, R = AB XOR C.
    # Implementation of URG gate with smaller gates.
    # Gates needed (without control SWAPs): 8
    gate = np.kron(I(1), ControlledU(V()))
    gate = np.dot(gate, np.kron(SWAP(), I(1)))
    gate = np.dot(gate, np.kron(I(1), ControlledU(V())))
    gate = np.dot(gate, np.kron(CNOT(), I(1)))
    gate = np.dot(gate, np.kron(I(1), ControlledU(Dagger(V()))))
    gate = np.dot(gate, np.kron(CNOT(), I(1)))
    gate = np.dot(gate, np.kron(I(1), SWAP()))
    gate = np.dot(gate, np.kron(CNOT(), I(1)))
    gate = np.dot(gate, np.kron(I(1), CNOT()))
    gate = np.dot(gate, np.kron(CNOT(), I(1)))
    gate = np.dot(gate, np.kron(I(1), SWAP()))
    gate = np.dot(gate, np.kron(SWAP(), I(1)))
    return gate

def BJN(): # A, B, C -> P = A, Q = B, R = (A+B) XOR C. BJN gate.
    # Implementation of TR gate with smaller gates.
    # Gates needed (without control SWAPs): 5
    gate = np.kron(SWAP(), I(1))
    gate = np.dot(gate, np.kron(I(1), ControlledU(V())))
    gate = np.dot(gate, np.kron(SWAP(), I(1)))
    gate = np.dot(gate, np.kron(I(1), ControlledU(V())))
    gate = np.dot(gate, np.kron(CNOT(), I(1)))
    gate = np.dot(gate, np.kron(I(1), ControlledU(V())))
    gate = np.dot(gate, np.kron(CNOT(), I(1)))
    return gate

def hopfCoords(qbit):
    alpha = qbit[0][0]
    beta = qbit[0][1]
    theta = np.arccos(alpha) * 2
    print (theta)
    s = np.sin(theta/2)
    if (s != 0):
        phi = np.log(beta/np.sin(theta/2)) / 1j
    else:
        phi = 0j
    return (theta, phi)

def getTruthTable(gate, ancilla=None, garbage=0): # Prints the truth table of the given gate.
    # You can set the ancilla bits to not include them in the table, with the list of values they must have.
    # For example, if you have two 0s and one 1 as ancilla bits, ancilla[0,0,1]. It always takes the last bits as the ancilla ones!
    # The garbage=n removes the last n bits from the truth table, considering them garbage.
    # For example, if you have 6 outputs and the last 4 outputs are garbage, only the value of the first two would be printed.
    # Always removes the last n bits!
    num = int(np.log2(gate.shape[0]))
    for i in range(0, gate.shape[0]):
        nbin = [int(x) for x in bin(i)[2:]]
        qinit = [0 for j in range(num - len(nbin))]
        qinit += nbin
        if ancilla == None or qinit[-len(ancilla):] == ancilla:
            qr = QRegistry(qinit)
            qr.ApplyGate(gate)
            mes = qr.Measure([j for j in range(num-garbage)])
            if ancilla != None:
                ini = qinit[:-len(ancilla)]
            else:
                ini = qinit
            print(str(ini) + " -> " + str(mes))

def QEq(q1, q2):
    return np.array_equal(q1,q2) and str(q1) == str(q2)

def HalfSubstractor(): # A, B, 0 -> P = A-B, Q = Borrow, R = B = Garbage
    hs = np.kron(SWAP(), I(1))
    hs = np.dot(hs, TR())
    hs = np.dot(hs, np.kron(SWAP(), I(1)))
    hs = np.dot(hs, np.kron(I(1), SWAP()))
    return hs

def Substractor(): # A, B, Bin, 0, 0, 0 -> P = A-B, Q = Borrow, R = B1 = Garbage, S = B1B2 = Garbage, T = Bin = Garbage, U = B = Garbage
    # Can be used as a comparator. Q will be 0 if A>=B, 1 otherwise.
    fs = np.kron(I(2), np.kron(SWAP(), I(2)))
    fs = np.dot(fs, np.kron(HalfSubstractor(), I(3)))
    fs = np.dot(fs, np.kron(I(2), np.kron(SWAP(), I(2))))
    fs = np.dot(fs, np.kron(I(1), np.kron(SWAP(), np.kron(SWAP(), I(1)))))
    fs = np.dot(fs, np.kron(I(2), np.kron(SWAP(), SWAP())))
    fs = np.dot(fs, np.kron(HalfSubstractor(), I(3)))
    fs = np.dot(fs, np.kron(I(2), np.kron(SWAP(), I(2))))
    fs = np.dot(fs, np.kron(I(3), np.kron(SWAP(), I(1))))
    fs = np.dot(fs, np.kron(I(1), np.kron(URG(), I(2))))
    return fs
