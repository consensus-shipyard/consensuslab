import matplotlib.pyplot as plt
import numpy as np
import math


m = 13 #expected blocks/votes
l = 15 #votes per proposing certificate
betas = np.arange(0.0, 0.5, 0.005)

P = []
PA = []


for beta in betas:
	H_mean = m*(1-beta)
	A_mean = m*beta

	p = 1
	for i in range(l):
		p -= math.exp(-m)*(m**i)/math.factorial(i)
	P.append(p/2)


	pa = 1
	for a in range(l):
		temp = 0
		for h in range(l-a):
			temp += math.exp(-H_mean)*(H_mean**h)/math.factorial(h)
		for h in range(l-a,5*l):
			temp += (math.exp(-H_mean)*(H_mean**h)/math.factorial(h))*(math.comb(l-1,a)/math.comb(h+a,a))
		pa -= math.exp(-A_mean)*(A_mean**a)/math.factorial(a)*temp
	PA.append(pa)

fig, ax = plt.subplots()
ax.plot(betas,PA,label="p_a")
ax.plot(betas,P,label="p/2")
ax.legend()
plt.show()