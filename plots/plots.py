import pickle 
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from pylab import *
import seaborn as sns
sns.set()
sns.set_style("whitegrid")
flatui = ['#009ADE','#FF1F5B']
sns.set_palette(flatui)

# black edges around all figures 
rc('axes', linewidth=1, edgecolor='black')


# Acceptance Rate
with open('C:/Users/angel/Desktop/open projects/3. NSE-CSC/code/results/data/acc_rate_NSE-CSC.pkl', 'rb') as f:
	y1 = pickle.load(f)
with open('C:/Users/angel/Desktop/open projects/3. NSE-CSC/code/results/data/acc_rate_baseline.pkl', 'rb') as f:
	y2 = pickle.load(f)
plt.figure(1)
plt.plot(list(y1.keys()), list(y1.values()),label ='NSE-CSC',linestyle='-',linewidth=3)
plt.plot(list(y2.keys()), list(y2.values()),label ='baseline',linestyle='--',linewidth=3)
plt.xlabel('number of requests',fontsize=16)
plt.ylabel('acceptance rate (%)',fontsize=16)
plt.legend(loc='lower left',prop={'size': 16}, edgecolor='black')
plt.xlim(left=0, right = len(list(y1.keys())))
plt.ylim(bottom=50, top=100.5)
plt.tight_layout()
plt.savefig('C:/Users/angel/Desktop/open projects/3. NSE-CSC/code/results/acceptance_rate.png')

# hops per edge  
with open('C:/Users/angel/Desktop/open projects/3. NSE-CSC/code/results/data/hops_NSE-CSC.pkl', 'rb') as f:
	hops1 = pickle.load(f)
with open('C:/Users/angel/Desktop/open projects/3. NSE-CSC/code/results/data/hops_baseline.pkl', 'rb') as f:
	hops2 = pickle.load(f)

plt.figure(2)
same_server_1 = 100 * sum([1 for x in hops1 if x==0]) / len(hops1)
same_rack_1 = 100 * sum([1 for x in hops1 if x==2]) / len(hops1)
different_rack_1 = 100 * sum([1 for x in hops1 if x==4]) /len(hops1)
same_server_2 = 100 * sum([1 for x in hops2 if x==0]) / len(hops2)
same_rack_2 = 100 * sum([1 for x in hops2 if x==2]) / len(hops2)
different_rack_2 = 100 * sum([1 for x in hops2 if x==4]) / len(hops2)
# set width of bar
barWidth = 0.25
# set height of bar
bars1 = [same_server_1, same_rack_1, different_rack_1]
bars2 = [same_server_2, same_rack_2, different_rack_2]
# Set position of bar on X axis
r1 = np.arange(len(bars1))
r2 = [x + barWidth for x in r1]
# Make the plot
plt.bar(r1, bars1, width=barWidth, edgecolor='black', label='NSE-CSC')
plt.bar(r2, bars2, width=barWidth, edgecolor='black', label='baseline', hatch='/')
# Add xticks on the middle of the group bars
#plt.xlabel('group', fontweight='bold')
plt.ylabel('adjacent VNF pairs (%)',fontsize=16)
plt.xticks([r + barWidth/2 for r in range(len(bars1))], ['same server', 'same rack', 'different racks'], fontsize=16)
# Create legend & Show graphic
plt.legend(loc='upper right',prop={'size': 16},edgecolor='black')
plt.ylim(top=100)
plt.tight_layout()
plt.savefig('C:/Users/angel/Desktop/open projects/3. NSE-CSC/code/results/hop_count.png')


# CPU utilization
with open('C:/Users/angel/Desktop/open projects/3. NSE-CSC/code/results/data/cpu_NSE-CSC.pkl', 'rb') as f:
	y1 = pickle.load(f)
with open('C:/Users/angel/Desktop/open projects/3. NSE-CSC/code/results/data/cpu_baseline.pkl', 'rb') as f:
	y2 = pickle.load(f)
plt.figure(3)
plt.plot(list(y1.keys()), list(y1.values()),label ='NSE-CSC',linestyle='-',linewidth=3)
plt.plot(list(y2.keys()), list(y2.values()),label ='baseline',linestyle='--',linewidth=3)
plt.xlabel('time intervals',fontsize=16)
plt.ylabel('CPU utilization (%)',fontsize=16)
plt.legend(loc='lower right',prop={'size': 16},edgecolor='black')
plt.xlim(left=0, right=600)
plt.ylim(bottom=0, top=100)
plt.tight_layout()
plt.savefig('C:/Users/angel/Desktop/open projects/3. NSE-CSC/code/results/cpu.png')

# inter-rack traffic 
with open('C:/Users/angel/Desktop/open projects/3. NSE-CSC/code/results/data/inter_rack_NSE-CSC.pkl', 'rb') as f:
	y1 = pickle.load(f)
with open('C:/Users/angel/Desktop/open projects/3. NSE-CSC/code/results/data/inter_rack_baseline.pkl', 'rb') as f:
	y2 = pickle.load(f)
plt.figure(4)
plt.plot(list(y1.keys()), list(y1.values()),label ='NSE-CSC',linestyle='-',linewidth=3)
plt.plot(list(y2.keys()), list(y2.values()),label ='baseline',linestyle='--',linewidth=3)
plt.xlabel('time intervals',fontsize=16)
plt.ylabel('inter-rack relative to total traffic (%)',fontsize=16)
plt.legend(loc='upper right',prop={'size': 16},edgecolor='black')
plt.xlim(left=0, right=600)
plt.ylim(bottom=0, top=100)
plt.tight_layout()
plt.savefig('C:/Users/angel/Desktop/open projects/3. NSE-CSC/code/results/inter_rack.png')


# hops per edge w.r.t. CSC-engaged and non CSC-engaged links  
with open('C:/Users/angel/Desktop/open projects/3. NSE-CSC/code/results/data/consuming_edges_hops_NSE-CSC.pkl', 'rb') as f:
	y1 = pickle.load(f)
with open('C:/Users/angel/Desktop/open projects/3. NSE-CSC/code/results/data/providing_edges_hops_NSE-CSC.pkl', 'rb') as f:
	y2 = pickle.load(f)
with open('C:/Users/angel/Desktop/open projects/3. NSE-CSC/code/results/data/consuming_edges_hops_baseline.pkl', 'rb') as f:
	y3 = pickle.load(f)
with open('C:/Users/angel/Desktop/open projects/3. NSE-CSC/code/results/data/providing_edges_hops_baseline.pkl', 'rb') as f:
	y4 = pickle.load(f)

y1 = np.asarray(y1)
y1 = np.sort(y1)
p1 = 1. * np.arange(len(y1)) / (len(y1) - 1)
y2 = np.asarray(y2)
y2 = np.sort(y2)
p2 = 1. * np.arange(len(y2)) / (len(y2) - 1)
y3 = np.asarray(y3)
y3 = np.sort(y3)
p3 = 1. * np.arange(len(y3)) / (len(y3) - 1)
y4 = np.asarray(y4)
y4 = np.sort(y4)
p4 = 1. * np.arange(len(y4)) / (len(y4) - 1)

plt.figure(5)
plt.ylabel('probability',fontsize=16)
plt.xlabel('hop count for non CSC adjacent VNFs', fontsize=16)
plt.plot(y1, p1, linewidth=3, label='NSE-CSC')
plt.plot(y3, p3, linewidth=3, linestyle='--',  label='baseline')
plt.legend(loc='upper left',prop={'size': 16},edgecolor='black')
plt.xlim(left=-0.03, right=4.03)
#plt.xticks([0,2,4],('0 (same server)', '2 (same rack)', '4 (different racks)'), rotation=15)
plt.xticks([0,2,4])
plt.ylim(bottom=0, top=1.00)
plt.tight_layout()
plt.savefig('C:/Users/angel/Desktop/open projects/3. NSE-CSC/code/results/hop_count_non-CSC.png')

plt.figure(6)
plt.ylabel('probability',fontsize=16)
plt.xlabel('hop count for CSC adjacent VNFs', fontsize=16)
plt.plot(y2, p2, linewidth=3, label='NSE-CSC')
plt.plot(y4, p4, linewidth=3, linestyle='--', label='baseline')
plt.legend(loc='upper left',prop={'size': 16},edgecolor='black')
plt.xlim(left=-0.03, right=4.03)
plt.xticks([0,2,4])
plt.ylim(bottom=0, top=1.00)
plt.tight_layout()
plt.savefig('C:/Users/angel/Desktop/open projects/3. NSE-CSC/code/results/hop_count_CSC.png')

