import numpy as np
import math
import random
import matplotlib.pyplot as plt
from scipy.stats import poisson
from scipy.stats import binom

x = 13
y = 11
z = 1
beta = 0.3
ns = np.arange(0,105,5)


#### Discard old votes
p_ns_d = [0]

g_d = (1 - poisson.cdf(y-1,x))*(1 - poisson.cdf(0,z))
p_a = (1 - poisson.cdf(y-1,beta*x))*(1 - poisson.cdf(0,beta*z))
p_h = (1 - poisson.cdf(y-1,(1-beta)*x))*(1 - poisson.cdf(0,(1-beta)*z))
print(g_d)

for n in ns[1:]:
	p_n = 0
	for i in range(math.ceil(3*n*p_h)):
		p_n += binom.pmf(i,n,p_a)*binom.cdf(i,n,p_h)
	p_ns_d.append(p_n)

print(p_ns_d)


#### Accept old votes

p_ns_a = [0]

p = 1-poisson.cdf(0,z)
p_a = 1 - poisson.cdf(0,beta*z)
p_h = 1 - poisson.cdf(0,(1-beta)*z)
N2 = (1-p)/p
N1 = 1
for n in range(1,10):
	N1 += poisson.cdf(y-1,n*x)
g_a = 1/(N1+N2)
print(g_a)



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

# Result:
# 0.4730271750269285
# [0, 0.43453358969968486, 0.18985830370843224, 0.08340208912698058, 0.03683036650017975, 0.016347152658657996, 0.007291170860908282, 0.003267181118017998, 0.0014704963342361493, 0.0006645971978987748, 0.0003015389408095324, 0.000137310856054519, 6.273801333307294e-05, 2.8754914727453345e-05, 1.3217345269986095e-05, 6.091550810019136e-06, 2.814294234088913e-06, 1.303112246056796e-06, 6.046218982096922e-07, 2.810612380556123e-07, 1.308773569986462e-07]
# 0.5452647792908969
# [0, 0.2453202, 0.0935923, 0.0406422, 0.0185385, 0.0086661, 0.0041, 0.0019912, 0.0009368, 0.0004545, 0.0002221, 0.0001151, 5.34e-05, 2.52e-05, 1.26e-05, 6.5e-06, 3.2e-06, 1.3e-06, 6e-07, 4e-07, 1e-07]
		
			
	 




