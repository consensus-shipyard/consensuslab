import matplotlib.pyplot as plt
import numpy as np
import math

betas = np.arange(0.1, 0.5, 0.005)
m = 5

X1 = []
X2 = []
A = []

for beta in betas:
	A.append(beta*m)
	X = math.exp(-beta*m)*(1-beta)*m

	H1 = 0
	for i in range(30):
		H1 += (i//2+1)*math.exp(-(1-beta)*m)*((1-beta)*m)**i/math.factorial(i)
	

	Y = X + math.exp(-beta*m)*beta*m*H1

	X += (1-math.exp(-beta*m))*H1
	X1.append(X)

	H2 = 2*math.exp(-(1-beta)*m)
	# H2 = 0
	for i in range(1,30):
		H2 += (math.ceil(i/4)+1)*math.exp(-(1-beta)*m)*((1-beta)*m)**i/math.factorial(i)
	Y += (1-math.exp(-beta*m)-math.exp(-beta*m)*beta*m)*H2
	X2.append(Y)

fig, ax = plt.subplots()
ax.plot(betas,X2,label="Honest")
ax.plot(betas,A,label="Adv")
ax.legend()
plt.show()