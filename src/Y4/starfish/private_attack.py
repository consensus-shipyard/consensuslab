import numpy as np
import math
import random
import matplotlib.pyplot as plt
from scipy.stats import poisson
from scipy.stats import binom

x = 27
y = 18
z = 3
beta = 1/3
ns = np.arange(0,105,5)

private_attack_d = True
private_attack_a = False

#### Discard old votes
p_ns_d = [1]

g_d = (1 - poisson.cdf(y-1,x))*(1 - poisson.cdf(0,z))
p_a = (1 - poisson.cdf(y-1,beta*x))*(1 - poisson.cdf(0,beta*z))
p_h = (1 - poisson.cdf(y-1,(1-beta)*x))*(1 - poisson.cdf(0,(1-beta)*z))
print("Chain growth:", g_d)
print("Honest chain growth:", p_h)
print("Adv chain growth:", p_a)


if private_attack_d:
	for n in ns[1:]:
		p_n = 0
		for i in range(math.ceil(3*n*p_h)):
			p_n += binom.pmf(i,n,p_a)*binom.cdf(i,n,p_h)
		p_ns_d.append(p_n)

	print(p_ns_d)


#### Accept old votes

p_ns_a = [1]

p = 1-poisson.cdf(0,z)
p_a = 1 - poisson.cdf(0,beta*z)
p_h = 1 - poisson.cdf(0,(1-beta)*z)
N2 = (1-p)/p
N1 = 1
for n in range(1,10):
	N1 += poisson.cdf(y-1,n*x)
g_d = 1/(N1+N2)
print("Chain growth:", g_d)

Nh2 = (1-p_h)/p_h
Nh1 = 1
for n in range(1,10):
	Nh1 += poisson.cdf(y-1,n*(1-beta)*x)
g_h = 1/(Nh1+Nh2)
print("Honest chain growth:", g_h)

Na2 = (1-p_a)/p_a
Na1 = 1
for n in range(1,10):
	Na1 += poisson.cdf(y-1,n*beta*x)
g_a = 1/(Na1+Na2)
print("Adv chain growth:", g_a)


if private_attack_a:
	num_runs = 10000000
	count = [0]*(len(ns)-1)

	for _ in range(num_runs):
		votes_a = np.random.poisson(beta*x, ns[-1])
		votes_h = np.random.poisson((1-beta)*x, ns[-1])
		len_a = len_h = 0
		num_a = num_h = 0
		for i in range(ns[-1]):
			## Grow the adv chain
			num_a += votes_a[i]
			if num_a >= y and random.uniform(0,1) < p_a:
				len_a += 1
				num_a = 0

			## Grow the honest chain
			num_h += votes_h[i]
			if num_h >= y and random.uniform(0,1) < p_h:
				len_h += 1
				num_h = 0

			## Compare chain lengths
			if i%5 == 4 and len_a >= len_h:
				count[i//5] += 1
	p_ns_a += [x/num_runs for x in count]
	print(p_ns_a)

# Result 1: private attack

# x = 13
# y = 11
# z = 1
# beta = 0.3
# ns = np.arange(0,105,5)

# 0.4730271750269285
# [1, 0.43453358969968486, 0.18985830370843224, 0.08340208912698058, 0.03683036650017975, 0.016347152658657996, 0.007291170860908282, 0.003267181118017998, 0.0014704963342361493, 0.0006645971978987748, 0.0003015389408095324, 0.000137310856054519, 6.273801333307294e-05, 2.8754914727453345e-05, 1.3217345269986095e-05, 6.091550810019136e-06, 2.814294234088913e-06, 1.303112246056796e-06, 6.046218982096922e-07, 2.810612380556123e-07, 1.308773569986462e-07]
# 0.5452647792908969
# [1, 0.2453202, 0.0935923, 0.0406422, 0.0185385, 0.0086661, 0.0041, 0.0019912, 0.0009368, 0.0004545, 0.0002221, 0.0001151, 5.34e-05, 2.52e-05, 1.26e-05, 6.5e-06, 3.2e-06, 1.3e-06, 6e-07, 4e-07, 1e-07]
		
			
# Result 2: adjust parameters

# x = 27
# y = 18
# z = 3
# beta = 1/3
# ns = np.arange(0,105,5)	 

# Chain growth: 0.9241867824982541
# Honest chain growth: 0.45944161230550146
# Adv chain growth: 0.0033626103520252764
# [1, 0.04946759166526039, 0.002765238549003624, 0.00016915024411091545, 1.098731980371078e-05, 7.417880811295828e-07, 5.135446347386528e-08, 3.616185401147366e-09, 2.5771929873259345e-10, 1.8531663168682444e-11, 1.3417257260118296e-12, 9.767496155677833e-14, 7.142241788786355e-15, 5.241944308128672e-16, 3.859298936388007e-17, 2.84897291630223e-18, 2.1080315453947448e-19, 1.562964199784934e-20, 1.16091552900204e-21, 8.63665695176566e-23, 6.43445220823262e-24]
# Chain growth: 0.9261098548751325
# Honest chain growth: 0.6151931773384326
# Adv chain growth: 0.3254110296041747



