from scipy.optimize import linprog, minimize, NonlinearConstraint
import numpy as np
# np.set_printoptions(suppress=True)

"Plans: Stability, Ruler, rework code to be more readable?, ship upkeep?"
"Linearize ODE using Laplace, Polynomial using Log, linearization (?)"

# Create initial job, pop upkeep,output
# Modifier
MEP = 0 # MILITARIZED_ECONOMY_POLICY
CEP = 0 # CIVILIAN_ECONOMY_POLICY

# Pop
PFI = 1 # POP_FOOD_IN
PAI = 1 # POP_AMENITY_IN
RCI = 1 # RULER_CONSUMER_IN
SCI = .5 # SPECIALIST_CONSUMER_IN
WCI = .25 # WORKER_CONSUMER_IN
PHI = 1 # POP_HOUSING_IN
RTO = .5 # RULER_TRADE_OUT
STO = .33 # SPECIALIST_TRADE_OUT
WTO = .2 # WORKER_TRADE_OUT

# Job
MMO = 4 # MINER_MINERAL_OUT
FFO = 6 # FARMER_FOOD_OUT
TEO = 6 # TECHNICIAN_ENERGY_OUT
CTO = 4 # CLERK_TRADE_OUT
CAO = 2 # CLERK_AMENITIES_OUT
ECI = 1 # ENTERTAINER_CONSUMER_IN
EAO = 10 # ENTERTAINER_AMENITY_OUT
AMI = 6 # ARTISAN_MINERAL_IN
ACO = 6 * (1 - .25 * MEP + .25 * CEP) # ARTISAN_CONSUMER_OUT
MMI = 6 # METALLURGIST_MINERAL_IN
MAO = 3 * (1 + .25 * MEP - .25 * CEP) # METALLURGIST_ALLOY_OUT

# District
FFJ = 2 # FARM_FARMER_JOBS
FEU = 1 # FARM_ENERGY_UPKEEP
MMJ = 2 # MINE_MINER_JOBS
MEU = 1 # MINE_ENERGY_UPKEEP
GTJ = 2 # GENERATOR_TECHNICIAN_JOBS
GEU = 1 # GENERATOR_ENERGY_UPKEEP
IAJ = 1 # INDUSTRIAL_ARTISAN_JOBS
IMJ = 1 # INDUSTRIAL_METALLURGIST_JOBS
IEU = 2 # INDUSTRIAL_ENERGY_UPKEEP
GDH = 2 # GENERAL_DISTRICT_HOUSING
CCJ = 1 # CITY_CLERK_JOBS
CDH = 5 # CITY_DISTRICT_HOUSING
CEU = 2 # CITY_ENERGY_UPKEEP

# Building
TEJ = 2 # THEATER_ENTERTAINER_JOBS
TEU = 2 # THEATER_ENERGY_UPKEEP

# Scenario
POPS = 30

# Create constraints

# x = [FARMER, MINER, TECHNICIAN, CLERK, ENTERTAINER, ARTISAN, METALLURGIST,
#      FARM, MINE, GENERATOR, THEATER, INDUSTRIAL, CITY]
c = [0, 0, 0, 0, 0, 0, -MAO,
      0, 0, 0, 0, 0, 0]
# c = [0, 0, -TEO, 0, 0, 0,
#      FEU, MEU, GEU, TEU, IEU, CEU]
# Food: (POPS) * PFI - FARMER * FFO <= 0
Food = [PFI-FFO, PFI, PFI, PFI, PFI, PFI, PFI,
        0, 0, 0, 0, 0 ,0]
# Amenties:  (ALL) * PAI - ENTERTAINER * EAO <= 0
Amenities = [PAI, PAI, PAI, PAI-CAO, PAI-EAO, PAI, PAI,
             0, 0, 0, 0, 0, 0]
# Consumer Goods: (WORKER) * WCI + (SPECIALIST) * SCI
#                   + ENTERTAINER * ECI - ARTISAN * ACO <= 0
Consumer = [WCI, WCI, WCI, WCI, SCI+ECI, SCI-ACO, SCI,
            0, 0, 0, 0, 0, 0]
# Minerals: METALLURGIST * MMI + ARTISAN * AMI - MINER * MMO <= 0
Minerals = [0, -MMO, 0, 0, 0, AMI, MMI,
            0, 0, 0, 0, 0, 0]
# Energy: BUILDINGS * UPKEEP - TECHNICIANS * TEO - (WORKER) * WTO - (SPECIALIST) * STO <= 0
Energy = [-WTO, -WTO, -WTO-TEO, -WTO-CTO, -STO, -STO, -STO,
          FEU, MEU, GEU, TEU, IEU, CEU]
# Pops: ALL <= POPS
Pops = [1, 1, 1, 1, 1, 1, 1,
        0, 0, 0, 0, 0, 0]
# Jobs: JOBS - BULDING * JOBS <= 0
# Housing: POPS - DISTRICT * GDH - CITY * CDH <= 0
Housing = [1, 1, 1, 1, 1, 1, 1,
           -GDH, -GDH, -GDH, 0, -GDH, -CDH]
A_ub = np.array([Food,
                 Amenities,
                 Consumer,
                 Minerals,
                 Energy,
                 Pops,
                 [1, 0, 0, 0, 0, 0, 0,
                  -FFJ, 0, 0, 0, 0, 0],
                 [0, 1, 0, 0, 0, 0, 0,
                  0, -MMJ, 0, 0, 0, 0],
                 [0, 0, 1, 0, 0, 0, 0,
                  0, 0, -GTJ, 0, 0, 0],
                 [0, 0, 0, 1, 0, 0, 0,
                  0, 0, 0, 0, 0, -CCJ],
                 [0, 0, 0, 0, 1, 0, 0,
                  0, 0, 0, -TEJ, 0, 0],
                 [0, 0, 0, 0, 0, 1, 0,
                  0, 0, 0, 0, -IAJ, 0],
                 [0, 0, 0, 0, 0, 0, 1,
                  0, 0, 0, 0, -IMJ, 0],
                 Housing])
# b_ub = np.zeros(A_ub.shape[0])
b_ub = np.array([0, 0, 0, 0, 0, POPS, 0, 0, 0, 0, 0, 0, 0, 0])
# integrality = 1

# Solve Linear Problem

solution = linprog(c, A_ub=A_ub, b_ub=b_ub)
# solution = linprog(c, A_ub=A_ub, b_ub=b_ub, integrality=1)
# print(solution)
print(solution.x[:-6])
print(solution.x[-6:])
print(-solution.fun)