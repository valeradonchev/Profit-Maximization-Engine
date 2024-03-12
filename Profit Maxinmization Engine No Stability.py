from scipy.optimize import minimize, NonlinearConstraint
import numpy as np
# np.set_printoptions(suppress=True)

"Plans: Stability, Ruler, rework code to be more readable?, ship upkeep?"
"Linearize ODE using Laplace, Polynomial using Log, linearization (?)"

# Create initial job, pop upkeep,output
# Modifier
MEP = 0 # MILITARIZED_ECONOMY_POLICY
CEP = 0 # CIVILIAN_ECONOMY_POLICY
DCLS = 1 # DECENT_CONDITIONS_LIVING_STANDARD

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
RHV = 50 + (10 * DCLS) # RULER_HAPPINESS_VALUE
SHV = 50 + (5 * DCLS) # SPECIALIST_HAPPINESS_VALUE
WHV = 50 + (0) # WORKER_HAPPINESS_VALUE
RPP = 1 + (7 * DCLS) # RULER_POLITICAL_POWER
SPP = 1 + (1 * DCLS) # SPECIALIST_POLITICAL_POWER
WPP = 1 + (0) # WORKER_POLITICAL_POWER

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
# Keep negative values as gain

# x = [FARMER, MINER, TECHNICIAN, CLERK, ENTERTAINER, ARTISAN, METALLURGIST,
#      FARM, MINE, GENERATOR, THEATER, INDUSTRIAL, CITY]
p = (0,np.inf)
bounds = [p, p, p, p, p, p, p,
          p, p, p, p, p, p]

def Goal(x):
    alloy = [0, 0, 0, 0, 0, 0, -MAO,
             0, 0, 0, 0, 0, 0]
    # c = [0, 0, -TEO, 0, 0, 0,
    #      FEU, MEU, GEU, TEU, IEU, CEU]
    return alloy @ x

x0 = [0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0]

def Stability(x):
    # Approval = sum(HV * PP)/sum(PP)
    happiness = np.array([WHV, WHV, WHV, WHV, SHV, SHV, SHV,
                          0, 0, 0, 0, 0 ,0])
    power = np.array([WPP, WPP, WPP, WPP, SPP, SPP, SPP,
                      0, 0, 0, 0, 0, 0])
    approval = sum((happiness*power)@x)/sum(power@x)
    approval = min(approval, 100)
    approval = max(approval, 0)
    # Stability
    stability = 50 + (approval-50) * .6 ** (approval > 50)
    # stability = 50
    # if approval > 50:
    #     stability += (approval-50) * .6
    # if approval < 50:
    #     stability += (approval-50)
    # Stability modifier
    stability_mod = 0 + (stability-50) * .6 ** (stability > 50)
    return stability_mod

def Food(x):
    # Food: (POPS) * PFI - FARMER * FFO <= 0
    food = [PFI-FFO, PFI, PFI, PFI, PFI, PFI, PFI,
            0, 0, 0, 0, 0 ,0]
    return food @ x

constraints = []
constraints.append(NonlinearConstraint(Food, -np.inf, 0))

def Amenities(x):
    # Amenties:  (ALL) * PAI - ENTERTAINER * EAO <= 0
    amenities = [PAI, PAI, PAI, PAI-CAO, PAI-EAO, PAI, PAI,
                 0, 0, 0, 0, 0, 0]
    return amenities @ x

constraints.append(NonlinearConstraint(Amenities, -np.inf, 0))

def Consumer(x):
    # Consumer: (WORKER) * WCI + (SPECIALIST) * SCI
    #           + ENTERTAINER * ECI - ARTISAN * ACO <= 0
    consumer = [WCI, WCI, WCI, WCI, SCI+ECI, SCI-ACO, SCI,
                0, 0, 0, 0, 0, 0]
    return consumer @ x

constraints.append(NonlinearConstraint(Consumer, -np.inf, 0))

def Minerals(x):
    # Minerals: METALLURGIST * MMI + ARTISAN * AMI - MINER * MMO <= 0
    minerals = [0, -MMO, 0, 0, 0, AMI, MMI,
                0, 0, 0, 0, 0, 0]
    return minerals @ x

constraints.append(NonlinearConstraint(Minerals, -np.inf, 0))

def Energy(x):
    # Energy: BUILDINGS * UPKEEP - TECHNICIANS * TEO
    #         - (WORKER) * WTO - (SPECIALIST) * STO <= 0
    energy = [-WTO, -WTO, -WTO-TEO, -WTO-CTO, -STO, -STO, -STO,
              FEU, MEU, GEU, TEU, IEU, CEU]
    return energy @ x

constraints.append(NonlinearConstraint(Energy, -np.inf, 0))

def Pops(x):
    # Pops: ALL <= POPS
    pops = [1, 1, 1, 1, 1, 1, 1,
            0, 0, 0, 0, 0, 0]
    return pops @ x

constraints.append(NonlinearConstraint(Pops, 0, POPS))

def Housing(x):
    # Housing: POPS - DISTRICT * GDH - CITY * CDH <= 0
    housing = [1, 1, 1, 1, 1, 1, 1,
               -GDH, -GDH, -GDH, 0, -GDH, -CDH]
    return housing @ x

constraints.append(NonlinearConstraint(Housing, -np.inf, 0))

def Farmers(x):
    # Jobs: JOBS - BULDING * BUILDING_JOBS <= 0
    farmers = [1, 0, 0, 0, 0, 0, 0,
               -FFJ, 0, 0, 0, 0, 0]
    return farmers @ x

constraints.append(NonlinearConstraint(Farmers, -np.inf, 0))

def Miners(x):
    # Jobs: JOBS - BULDING * BUILDING_JOBS <= 0
    miners = [0, 1, 0, 0, 0, 0, 0,
              0, -MMJ, 0, 0, 0, 0]
    return miners @ x

constraints.append(NonlinearConstraint(Miners, -np.inf, 0))

def Technicians(x):
    # Jobs: JOBS - BULDING * BUILDING_JOBS <= 0
    technicians = [0, 0, 1, 0, 0, 0, 0,
                   0, 0, -GTJ, 0, 0, 0]
    return technicians @ x

constraints.append(NonlinearConstraint(Technicians, -np.inf, 0))

def Clerks(x):
    # Jobs: JOBS - BULDING * BUILDING_JOBS <= 0
    clerks = [0, 0, 0, 1, 0, 0, 0,
              0, 0, 0, 0, 0, -CCJ]
    return clerks @ x

constraints.append(NonlinearConstraint(Clerks, -np.inf, 0))

def Entertainers(x):
    # Jobs: JOBS - BULDING * BUILDING_JOBS <= 0
    entertainers = [0, 0, 0, 0, 1, 0, 0,
              0, 0, 0, -TEJ, 0, 0]
    return entertainers @ x

constraints.append(NonlinearConstraint(Entertainers, -np.inf, 0))

def Artisans(x):
    # Jobs: JOBS - BULDING * BUILDING_JOBS <= 0
    artisans = [0, 0, 0, 0, 0, 1, 0,
              0, 0, 0, 0, -IAJ, 0]
    return artisans @ x

constraints.append(NonlinearConstraint(Artisans, -np.inf, 0))

def Metallurgists(x):
    # Jobs: JOBS - BULDING * BUILDING_JOBS <= 0
    metallurgists = [0, 0, 0, 0, 0, 0, 1,
                     0, 0, 0, 0, -IMJ, 0]
    return metallurgists @ x

constraints.append(NonlinearConstraint(Metallurgists, -np.inf, 0))

# Solve Problem

# solution = linprog(c, A_ub=A_ub, b_ub=b_ub)
# solution = linprog(c, A_ub=A_ub, b_ub=b_ub, integrality=1)
solution = minimize(Goal, x0, bounds=bounds, constraints=constraints)
# print(solution)
print(solution.x[:-6])
print(solution.x[-6:])
print(-solution.fun)