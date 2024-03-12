from scipy.optimize import minimize, NonlinearConstraint
import numpy as np
# np.set_printoptions(suppress=True)

"Plans: Figure out how the algorithm iterates to try to keep it in bounds,"
"Crime, Research value, ship upkeep?"
"Linearize ODE using Laplace, Polynomial using Log, linearization (?)"

# Create initial job, pop upkeep,output
# Modifier
MEP = 0 # MILITARIZED_ECONOMY_POLICY
CEP = 0 # CIVILIAN_ECONOMY_POLICY
DCLS = 1 # DECENT_CONDITIONS_LIVING_STANDARD

# Pop
PFI = 1 # POP_FOOD_IN
PAI = 1 # POP_AMENITY_IN

RCI = (1 * DCLS) # RULER_CONSUMER_IN
SCI = (.5 * DCLS) # SPECIALIST_CONSUMER_IN
WCI = (.25 * DCLS) # WORKER_CONSUMER_IN

PHI = 1 # POP_HOUSING_IN

RTO = (.5 * DCLS) # RULER_TRADE_OUT
STO = (.33 * DCLS) # SPECIALIST_TRADE_OUT
WTO = (.2 * DCLS) # WORKER_TRADE_OUT

RHV = 50 + (10 * DCLS) # RULER_HAPPINESS_VALUE
SHV = 50 + (5 * DCLS) # SPECIALIST_HAPPINESS_VALUE
WHV = 50 + (0) # WORKER_HAPPINESS_VALUE

RPP = 100 + (500 * DCLS) # RULER_POLITICAL_POWER
SPP = 100 + (250 * DCLS) # SPECIALIST_POLITICAL_POWER
WPP = 100 + (150 * DCLS) # WORKER_POLITICAL_POWER

# Job
MMO = 4 # MINER_MINERAL_OUT
FFO = 6 # FARMER_FOOD_OUT
TEO = 6 # TECHNICIAN_ENERGY_OUT
CTO = 4 # CLERK_TRADE_OUT
CAO = 2 # CLERK_AMENITIES_OUT

ECI = 1 # ENTERTAINER_CONSUMER_IN
EAO = 10 # ENTERTAINER_AMENITY_OUT
EUO = 1 # ENTERTAINER_UNITY_OUT
AMI = 6 # ARTISAN_MINERAL_IN
ACO = 6 * (1 - .25 * MEP + .25 * CEP) # ARTISAN_CONSUMER_OUT
MMI = 6 # METALLURGIST_MINERAL_IN
MAO = 3 * (1 + .25 * MEP - .25 * CEP) # METALLURGIST_ALLOY_OUT
BCI = 2 # BUREAUCRAT_CONSUMER_IN
BUO = 4 # BUREAUCRAT_UNITY_OUT
PAO = 3 # POLITICIAN_AMENITIES_OUT
PUO = 6 # POLITICIAN_UNITY_OUT

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
OBJ = 2 # OFFICE_BUREAUCRAT_JOBS
OEU = 2 # OFFICE_ENERGY_UPKEEP
PAPJ = 2 # PLANETARY_ADMINISTRATION_POLITITIAN_JOBS
PAAO = 5 # PLANETARY_ADMINISTRATION_AMENITIES_OUT
PAH = 5 # PLANETARY_ADMINISTRATION_HOUSING
PAEU = 5 # PLANETARY_ADMINISTRATION_ENERGY_UPKEEP

# Scenario
POPS = 30

# Create constraints
# Keep negative values as gain

# x = [FARMER, MINER, TECHNICIAN, CLERK,
#      ENTERTAINER, ARTISAN, METALLURGIST, BUREAUCRAT, POLITICIAN
#      FARM, MINE, GENERATOR, INDUSTRIAL, CITY,
#      THEATER, OFFICE, CAPITAL 1]
p = (0,np.inf)
one = (0, 1)
bounds = [p, p, p, p, 
          p, p, p, p, p,
          p, p, p, p, p,
          p, p, one]

def Goal(x):
    alloy = Alloy(x)
    unity = Unity(x)
    # c = [0, 0, -TEO, 0, 0, 0,
    #      FEU, MEU, GEU, TEU, IEU, CEU]
    # return alloy @ x
    return -alloy * 2 - unity

x0 = np.array([2, 4, 1, 1, 
               2, 2, 1, 1, 2,
               1, 2, 1, 2, 1,
               1, 1, 1])

def Alloy(x):
    # Alloy = METALLURGIST * MAO
    MAOA = MAO * (1 + Stability(x))
    alloy = np.array([0, 0, 0, 0,
                      0, 0, MAOA, 0, 0,
                      0, 0, 0, 0, 0, 
                      0, 0, 0])
    return alloy @ x

def Unity(x):
    # Unity = POLITICIAN * PUO
    PUOA = PUO * (1 + Stability(x))
    EUOA = EUO * (1 + Stability(x))
    BUOA = BUO * (1 + Stability(x))
    unity = np.array([0, 0, 0, 0,
                      EUOA, 0, 0, BUOA, PUOA,
                      0, 0, 0, 0, 0, 
                      0, 0, 0])
    return unity @ x

def Stability(x, debug=False):
    # Approval = sum(HV * PP)/sum(PP)
    happiness = Happiness(x, debug)
    power = np.array([WPP, WPP, WPP, WPP,
                      SPP, SPP, SPP, SPP, RPP,
                      0, 0, 0, 0, 0,
                      0, 0, 0])
    approval = ((happiness*power)@x)/(power@x)
    approval = min(approval, 100)
    approval = max(approval, 0)
    # Stability
    stability = 50 + (approval-50) * (.6 ** (approval > 50))
    stability = min(stability, 100)
    stability = max(stability, 0)
    # stability = 50
    # if approval > 50:
    #     stability += (approval-50) * .6
    # if approval < 50:
    #     stability += (approval-50)
    # Stability modifier
    stability_mod = 0 + (stability-50)/100 * (.6 ** (stability > 50))
    
    if debug:
        print("stability: " + str(stability))
    return stability_mod

def Food(x):
    # Food: FARMER * FFO - (POPS) * PFI >= 0
    FFOA = FFO * (1 + Stability(x))
    food = [FFOA-PFI, -PFI, -PFI, -PFI,
            -PFI, -PFI, -PFI, -PFI, -PFI,
            0, 0, 0, 0, 0,
            0, 0, 0]
    return food @ x

constraints = []
constraints.append(NonlinearConstraint(Food, 0, np.inf))

def Happiness(x, debug=False):
    # Happiness = living standard + amenity_mod
    happiness = np.array([WHV, WHV, WHV, WHV,
                          SHV, SHV, SHV, SHV, RHV,
                          0, 0, 0, 0, 0,
                          0, 0, 0])
    amenities = Amenities(x)
    amenities_used = Amenities_used(x)
    amenities_mod = 0
    if amenities > 0:
        amenities_mod = min(20, 20*amenities/amenities_used)
    if amenities < 0:
        amenities_mod = max(-50, 200/3*amenities/amenities_used)
    happiness = happiness + amenities_mod
    if debug:
        print("amenities: " + str(amenities))
        print("amenities used: " + str(amenities_used))
        print("amenities mod: " + str(amenities_mod))
    return happiness

def Crime(x):
    # 
    happiness = Happiness(x)
    

def Amenities(x):
    # Amenties:  (ALL) * PAI - ENTERTAINER * EAO - CLERK * CAO <= 0
    amenities = [-PAI, -PAI, -PAI, CAO-PAI,
                 EAO-PAI, -PAI, -PAI, -PAI, PAO-PAI,
                 0, 0, 0, 0, 0,
                 0, 0, PAAO]
    return amenities @ x - 5

# constraints.append(NonlinearConstraint(Amenities, 0, np.inf))

def Amenities_used(x):
    # Amenties used:  (ALL) * PAI
    amenities_used = np.array([PAI, PAI, PAI, PAI,
                               PAI, PAI, PAI, PAI, PAI,
                               0, 0, 0, 0, 0,
                               0, 0, 0])
    return amenities_used @ x

def Consumer(x):
    # Consumer: ARTISAN * ACO - (WORKER) * WCI - (SPECIALIST) * SCI
    #           - ENTERTAINER * ECI >= 0
    ACOA = ACO * (1 + Stability(x))
    consumer = [-WCI, -WCI, -WCI, -WCI,
                -SCI-ECI, ACOA-SCI, -SCI, -SCI-BCI, -RCI,
                0, 0, 0, 0, 0,
                0, 0, 0]
    return consumer @ x

constraints.append(NonlinearConstraint(Consumer, 0, np.inf))

def Minerals(x):
    # Minerals: MINER * MMO - METALLURGIST * MMI - ARTISAN * AMI >= 0
    MMOA = MMO * (1 + Stability(x))
    minerals = [0, MMOA, 0, 0,
                0, -AMI, -MMI, 0, 0,
                0, 0, 0, 0, 0,
                0, 0, 0]
    return minerals @ x

constraints.append(NonlinearConstraint(Minerals, 0, np.inf))

def Energy(x):
    # Energy: TECHNICIANS * TEO + (WORKER) * WTO
    #         + (SPECIALIST) * STO - BUILDINGS * UPKEEP >= 0
    TEOA = TEO * (1 + Stability(x))
    CTOA = CTO * (1 + Stability(x))
    energy = [WTO, WTO, WTO+TEOA, WTO+CTOA,
              STO, STO, STO, STO, RTO,
              -FEU, -MEU, -GEU, -IEU, -CEU,
              -TEU, -OEU, -PAEU]
    return energy @ x

constraints.append(NonlinearConstraint(Energy, 0, np.inf))

def Pops(x):
    # Pops: ALL <= POPS
    pops = [1, 1, 1, 1,
            1, 1, 1, 1, 1,
            0, 0, 0, 0, 0,
            0, 0, 0]
    return pops @ x

constraints.append(NonlinearConstraint(Pops, 0, POPS))

def Housing(x):
    # Housing: DISTRICT * GDH + CITY * CDH - POPS >= 0
    housing = [-1, -1, -1, -1, 
               -1, -1, -1, -1, -1,
               GDH, GDH, GDH, GDH, CDH,
               0, 0, PAH]
    return housing @ x

constraints.append(NonlinearConstraint(Housing, 0, np.inf))

def Farmers(x):
    # Jobs: BULDING * BUILDING_JOBS - JOBS >= 0
    farmers = [-1, 0, 0, 0,
               0, 0, 0, 0, 0,
               FFJ, 0, 0, 0, 0,
               0, 0, 0]
    return farmers @ x

constraints.append(NonlinearConstraint(Farmers, 0, np.inf))

def Miners(x):
    # Jobs: BULDING * BUILDING_JOBS - JOBS >= 0
    miners = [0, -1, 0, 0,
              0, 0, 0, 0, 0,
              0, MMJ, 0, 0, 0,
              0, 0, 0]
    return miners @ x

constraints.append(NonlinearConstraint(Miners, 0, np.inf))

def Technicians(x):
    # Jobs: BULDING * BUILDING_JOBS - JOBS >= 0
    technicians = [0, 0, -1, 0,
                   0, 0, 0, 0, 0,
                   0, 0, GTJ, 0, 0,
                   0, 0, 0]
    return technicians @ x

constraints.append(NonlinearConstraint(Technicians, 0, np.inf))

def Clerks(x):
    # Jobs: BULDING * BUILDING_JOBS - JOBS >= 0
    clerks = [0, 0, 0, -1,
              0, 0, 0, 0, 0,
              0, 0, 0, 0, CCJ,
              0, 0, 0]
    return clerks @ x

constraints.append(NonlinearConstraint(Clerks, 0, np.inf))

def Entertainers(x):
    # Jobs: BULDING * BUILDING_JOBS - JOBS >= 0
    entertainers = [0, 0, 0, 0,
                    -1, 0, 0, 0, 0,
                    0, 0, 0, 0, 0,
                    TEJ, 0, 0]
    return entertainers @ x

constraints.append(NonlinearConstraint(Entertainers, 0, np.inf))

def Artisans(x):
    # Jobs: BULDING * BUILDING_JOBS - JOBS >= 0
    artisans = [0, 0, 0, 0,
                0, -1, 0, 0, 0,
                0, 0, 0, IAJ, 0,
                0, 0, 0]
    return artisans @ x

constraints.append(NonlinearConstraint(Artisans, 0, np.inf))

def Metallurgists(x):
    # Jobs: BULDING * BUILDING_JOBS - JOBS >= 0
    metallurgists = [0, 0, 0, 0,
                     0, 0, -1, 0, 0,
                     0, 0, 0, IMJ, 0,
                     0, 0, 0]
    return metallurgists @ x

constraints.append(NonlinearConstraint(Metallurgists, 0, np.inf))

def Bureaucrats(x):
    # Jobs: BULDING * BUILDING_JOBS - JOBS >= 0
    bureaucrats = [0, 0, 0, 0, 
                   0, 0, 0, -1, 0,
                   0, 0, 0, 0, 0,
                   0, OBJ, 0]
    return bureaucrats @ x

constraints.append(NonlinearConstraint(Bureaucrats, 0, np.inf))

def Politicians(x):
    # Jobs: BULDING * BUILDING_JOBS - JOBS >= 0
    metallurgists = [0, 0, 0, 0,
                     0, 0, 0, 0, -1,
                     0, 0, 0, 0, 0,
                     0, 0, PAPJ]
    return metallurgists @ x

constraints.append(NonlinearConstraint(Politicians, 0, np.inf))

# Solve Problem

# solution = linprog(c, A_ub=A_ub, b_ub=b_ub)
# solution = linprog(c, A_ub=A_ub, b_ub=b_ub, integrality=1)
solution = minimize(Goal, x0, bounds=bounds, constraints=constraints, options={"maxiter":1000})
print(solution.message)
print(solution.success)
# [FARMER, MINER, TECHNICIAN, CLERK,
#      ENTERTAINER, ARTISAN, METALLURGIST, BUREAUCRAT, POLITICIAN
#      FARM, MINE, GENERATOR, INDUSTRIAL, CITY,
#      THEATER, OFFICE, CAPITAL 1]
print("FARMER, MINER, TECHNICIAN, CLERK")
print(solution.x[:4])
print("ENTERTAINER, ARTISAN, METALLURGIST, BUREAUCRAT, POLITICIAN")
print(solution.x[4:9])
print("FARM, MINE, GENERATOR, INDUSTRIAL, CITY")
print(solution.x[-8:-3])
print("THEATER, OFFICE, CAPITAL 1")
print(solution.x[-3:])
print("Stability mod: " + str(Stability(solution.x, debug=True)))
print(-solution.fun)
print("Alloy: " + str(Alloy(solution.x)))
print("Unity: " + str(Unity(solution.x)))
# print(solution)