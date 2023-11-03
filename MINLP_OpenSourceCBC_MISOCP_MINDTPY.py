from pyomo.environ import *
import pyomo.environ as pyo
import pyomo.kernel as pmo
import numpy as np
from scipy.stats import norm
from IPython.display import clear_output
import pandas

facilities= 10  # candidate facilities indexed by i
I=range(facilities)

customers = 5  # custmers, indexed by j
J=range(customers)
conditions = 3  # potential replacement conditions
K=range(conditions)
alfa=0.95 #confidence level

f = np.random.randint(1, 10, size=len(I))  # fixed facility operation cost for facility i (in $ per year)
h = np.random.uniform(0.2, 3.5, size=len(I))  # unit inventory holding cost for facility i (in $ per year)
tou = np.random.uniform(0.5, 1.5, size=len(I))  # replenishment for facility i (in years) (from an outside source to facility i

shape =(facilities,customers,conditions)  #dimensions of the array is defined as a tuple

d=np.random.randint(1,10,shape) #mean demand for customer j with replacement condition k when it served by facility i (in units per year)
sigma=np.random.random(shape) #standard deviation of demand for customer j with replacement condition k when it served by facility i (in units per year)
c=np.random.randint(100,200,shape) #cozt of allocating customer j with replacement condition k to facility i (in $ per year ) assumed to include downtime, shipping and replacement costs)
z=norm.ppf(alfa)

# Create a simple model
model = ConcreteModel()

model.x=Var(I,J,K,domain=pmo.Binary)  # 1 if facility i serves customer j with replacement condition k , 0 otherwise
model.y=Var(I,domain=pmo.Binary) # if facility i is open, 0 otherwise
model.s=Var(I,domain=pmo.NonNegativeIntegers) # stock level for facility i
model.v=Var(I,bounds=(1e-20,None),initialize=1e-20) # standard deviation in total lead time demand for facility i
model.t=Var(I,bounds=(1e-20,None),initialize=1e-20) # auxiliary variable to linearise quare root variable for MISOCP formulation
#bounds and initial value is needed for sqrt function execution over this variable.
#because it computes the first derivative

#objective function

#functional way of decleration of objectives no need for expressions and make it ready for abstract model
def facilityCost(model):
    return sum(model.y[i]*f[i] for i in I)

def inventoryHoldingCost(model):
    return sum(model.s[i]*h[i] for i in I)

def serviceCost(model):
    return sum(model.x[i,j,k]*c[i,j,k] for i in I for j in J for k in K)

model.facilityCost=facilityCost(model)
model.inventoryHoldingCost=inventoryHoldingCost(model)
model.serviceCost=serviceCost(model)
#just in this formulation, "expr" can be used instead of "rule". but abstract models need rule
model.mincost=Objective(rule=model.facilityCost+model.inventoryHoldingCost+model.serviceCost,sense=minimize)

model.constraint=pyo.Constraint(pyo.Any) #this is needed to write constraint labels as below

for j in J:
    model.constraint["constraint 1.b for customer",j]=sum(model.x[i,j,k] for i in I for k in K)==1

for i in I:
    for j in J:
        for k in K:
            model.constraint["constraint 1.c for facility", i,"customer ",j,"condition ",k]=model.x[i,j,k]<=model.y[i]

for i in I:
    model.constraint["constraint 1.d for facility ",i]=model.y[i]<=sum(model.x[i,j,k] for j in J for k in K)

for i in I:
    model.constraint["constraint 1.e for facility ",i]=sum((sigma[i,j,k]**2)*model.x[i,j,k]**2 for j in J for k in K)<=model.v[i]**2

for i in I:
    model.constraint["constraint 1.f for facility ",i]=model.s[i]-model.t[i]>=sum(tou[i]*d[i,j,k]*model.x[i,j,k] for j in J for k in K)

for i in I:
    model.constraint["lienarisation constraint greater than for ",i]=model.t[i]**2>=(z**2)*(tou[i]*model.v[i])
    model.constraint["linearisation constraint less than for ", i] = model.t[i] ** 2 <= (z ** 2) * (tou[i] * model.v[i])


#model.display() #turn this on to see the constraint names
# Solve the model using MindtPy
SolverFactory('mindtpy').solve(model, mip_solver='cbc', nlp_solver='ipopt', tee=True)



for i in I:
    if pyo.value(model.y[i])>0:
        print("y[",i,"]=",pyo.value(model.y[i]))

for i in I:
    if pyo.value(model.s[i]) > 0:
        print("s[", i, "]=", pyo.value(model.s[i]))

for i in I:
    if pyo.value(model.v[i]) > 0:
        print("v[", i, "]=", pyo.value(model.v[i]))

for i in I:
    for j in J:
        for k in K:
            if pyo.value(model.x[i,j,k]) > 0:
                print("x[", i,",",j,",",k,"]=", pyo.value(model.x[i,j,k]))