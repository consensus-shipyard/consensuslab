import scipy.special
import numpy as np 
import time,random
from math import floor,ceil
# import multiprocessing as mp
from scipy.stats import binom, poisson




def Bin(x,n,p):
	return binom.pmf(x, n, p)

def SSLE(l,alpha):
	return sum([Bin(i,l,alpha) for i in range(int(ceil(float(l)/2.)),l+1)])


def SSLE_pa(l,alpha):
	p0 = (1-np.exp(-alpha)-np.exp(alpha-1)+2*np.exp(-1))
	pa = (np.exp(alpha-1)-np.exp(-1))/(1-p0)
	return sum([Bin(i,l,pa) for i in range(int(ceil(l/2)),l+1)])
	#return [Bin(i,l,pa) for i in range(int(ceil(l/2)),l+1)]

def PLE(L,alpha): 
	p0 = (1-np.exp(-alpha)-np.exp(alpha-1)+2*np.exp(-1))
	pa = (np.exp(alpha-1)-np.exp(-1))
	paprime = pa/(1-p0)
	return sum([Bin(j,L,p0)*SSLE(L-j,paprime) for j in range(L+1)])

# def sum_nums(args):
# 	low = int(args[0])
# 	high = int(args[1])
# 	s = 0
   #      print low,high
   #  for i in range(low,high+1):
   #  	for j in range(i,height*na):
			# s += Poi((height-1)*nh,i,p)*Poi(height*na,j,p)
	# return s
	#return sum([Poi((height-1)*nh,i,p)*Poi(height*na,j,p) for i in range(low,high+1) for j in range(i,height*na)  ])


print(PLE(393,0.33)-pow(2,-30))