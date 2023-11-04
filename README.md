# ILROPT
MINLP model implementation in Pyomo for "Joint optimization of location, inventory, and condition-based replacement decisions in service parts logistics" paper. Each file is using the same model but with different solvers.

As of now implementation done with commercial (Gurobi) and open-source (CBC and GLPK, IPOPT) solvers. As well as the implementation of decomposition solver tested MINDTPY that combines MIP and NLP solvers, pairwise (Gurobi-IPOPT, CBC-IPOPT and GLPK-IPOPT). 

Implementations were tested with randomly generated instances of 10 facilities (I), 5 customers (J), and 3 conditions (K). For larger instances, only change these I,J and K parameters. 
