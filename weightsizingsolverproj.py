import numpy as np
from atmosphere import *
from tsfc import *

#* Weight Regression Data
takeoff_weights = [
    154996, 836996, 342995, 584997, 57497, 256839, 112436, 892872, 286601,
    374786, 514000, 310852, 886258, 1410958, 76058, 585500, 171000, 322500,
    415000, 191800, 418878, 311734, 164000, 342100, 840000, 112436, 485017,
    585000, 840000, 886258, 310852, 311734, 191800, 322500, 418878, 551156,
    322500, 71650, 155000
]

empty_weights = [
    75561, 373999, 148118, 278003, 36343, 104168, 63934, 385809, 160497,
    216053, 275600, 173820, 399037, 628137, 42000, 282500, 126000, 98466,
    181610, 52090, 203928, 152119, 75560, 144492, 380000, 61249, 220462,
    282500, 380000, 399037, 173000, 152119, 77161, 98466, 203928, 251327,
    98392, 38581, 75562
]

aircraft_names = [
    "LM C130", "LM C5", "LM C141", "Boeing C17", "Grumman C2", "Airbus A400M",
    "Transall C160", "Antonov An124", "Antonov An70", "Ilyushin Il70", "A330 MRTT",
    "A400M-Atlas", "An-124 Ruslan", "An-225 Mriya", "An-72", "C-17 Globemaster III",
    "C-40A Clipper", "KC-135 Stratotanker", "KC-46 Pegasus", "KC-390", "IL-76",
    "Kawasaki C-2", "C-130J Hercules", "C-141 Starlifter", "C-5M Galaxy", "Transall C-160",
    "Xi'an Y-20", "C-17 Globemaster III", "C-5M Super Galaxy", "An-124 Ruslan",
    "A400M Atlas", "Kawasaki C-2", "Embraer KC-390", "C-135 Stratolifter", "Ilyushin Il-76",
    "Antonov An-22", "KC-135 Stratotanker", "C-27J Spartan", "C-130J Super Hercules"
]

#* Weight Regression:
takeoff_weights, empty_weights, aircraft_names = zip(*sorted(zip(takeoff_weights, empty_weights, aircraft_names)))
takeoff_weights, empty_weights, aircraft_names = (list(t) for t in zip(*sorted(zip(takeoff_weights, empty_weights, aircraft_names))))

empty_weights_log = np.log10(empty_weights)
takeoff_weights_log = np.log10(takeoff_weights)

# import matplotlib.pyplot as plt
# fig1, ax1 = plt.subplots()

# coef = np.polyfit(takeoff_weights_log, empty_weights_log, 1)
coef = np.polyfit(takeoff_weights, empty_weights, 1)
B, A = np.polyfit(empty_weights_log, takeoff_weights_log, 1)
# Hardcoding A and B since we eliminated some redundant data:
A = 0.377713761
B = 0.990277795
# m, b = np.polyfit()
poly1d_fn = np.poly1d(coef)


def L_D_calc(cruise_L_D_guess,  A, B, payload_weight, cruise_alt_ft, cruise_range_nm, cruise_spd_mach, air_density_cruise_slugs, air_density_reserve_cruise_slugs, climb_initial_TSFC, climb_above10k_TSFC, cruise_TSFC, Wto_over_S, climb_rate_fpm):
    import numpy as np
    
    max_wingSpan = 262 # ft

    climb_L_D = 15
    # climb_rate_fpm = 1800 # ft/min
    climb_rate_fpm_initial = 1250
    climb_rate_fpm_final = 1750
    cruise_alt_ft = cruise_alt_ft
    cruise_velocity_kts = cruise_spd_mach*666.739
    cruise_L_D = cruise_L_D_guess #! need source for assumption

    segments = ["Start", "Taxi", "Takeoff", "Climb to 10kft", "Climb to 35kft", "Cruise", "Descent", "Reserve Cruise", "Reserve Loiter", "Land"]

    Endurance_climb_initial_hrs = (10000/climb_rate_fpm_initial)/60
    Endurance_climb_above10k_hrs = ((cruise_alt_ft - 10000)/climb_rate_fpm_final)/60
    Endurance_loiter_hrs = 0.5

    takeoff_weight_guess = 1400000

    crew_weight = 300*4
    payload_weight = payload_weight
    Mff_tfo = 0.005

    reserve_cruise_range_nm = 200
    reserve_cruise_velocity_kts = 250
    reserve_cruise_altitude_ft = 5000

    Mff_start = 0.99
    Mff_taxi = 0.995
    Mff_takeoff = 0.995
    Mff_climb_initial = np.e ** (-Endurance_climb_initial_hrs*climb_initial_TSFC/climb_L_D)
    Mff_climb_above10k = np.e ** (-Endurance_climb_above10k_hrs*climb_above10k_TSFC/climb_L_D)
    Mff_cruise = (np.e ** (-cruise_range_nm*cruise_TSFC/(cruise_velocity_kts*cruise_L_D)))
    Mff_descent = 0.99
    Mff_loiter = (np.e ** (Endurance_loiter_hrs*cruise_TSFC/(cruise_L_D))) ** -1
    Mff_reserve_cruise = (np.e ** (reserve_cruise_range_nm*cruise_TSFC/(reserve_cruise_velocity_kts*cruise_L_D))) ** -1
    Mff_land = 0.992
    fuel_fraction = [Mff_start, Mff_taxi, Mff_takeoff, Mff_climb_initial, Mff_climb_above10k, Mff_cruise, Mff_descent, Mff_reserve_cruise, Mff_loiter, Mff_land]
    Mff = np.prod(fuel_fraction)

    Mff_res = (1 - Mff_loiter * Mff_reserve_cruise)
    Mff_res = 0 #! Shoudln't this be nonzero (included in fuel_weight calc?)

    fuel_weight = (1 - Mff)*takeoff_weight_guess/(1 - Mff_res - Mff_tfo)

    #* Weight Converging

    empty_weight = takeoff_weight_guess - fuel_weight - payload_weight - crew_weight

    log10_empty_weight = (np.log10(takeoff_weight_guess) - A)/B
    empty_weight_allowable = 10 ** log10_empty_weight
    while abs(empty_weight - empty_weight_allowable) > 0.0001:
        if empty_weight > empty_weight_allowable:
            takeoff_weight_guess -= abs(empty_weight - empty_weight_allowable)/10
        else:
            takeoff_weight_guess += abs(empty_weight - empty_weight_allowable)/10
        empty_weight = takeoff_weight_guess - fuel_weight - payload_weight - crew_weight
        log10_empty_weight = (np.log10(takeoff_weight_guess) - A)/B
        empty_weight_allowable = 10 ** log10_empty_weight

    #* Fuel Fractions

    start_weights = [takeoff_weight_guess]
    fuel_used = []
    table_data = []
    for i in range(len(fuel_fraction)):
        start_weights.append(start_weights[i]*fuel_fraction[i])
        fuel_used.append(start_weights[i]*(1 - fuel_fraction[i]))
        
        if (segments[i] == "Cruise"):
            W_cruise = np.average([start_weights[i + 1], start_weights[i]])
            W_cruise_end = start_weights[i + 1]
        
        if (segments[i] == "Reserve Cruise"):
            W_reserve_cruise = np.average([start_weights[i + 1], start_weights[i]])
        
        if (segments[i] == "Land"):
            W_landing = start_weights[i]
        
        table_data.append({
            "Segment": i + 1,
            "Phase": segments[i],
            "FF": np.round(fuel_fraction[i], decimals=4),
            "Weight": np.round(start_weights[i]*fuel_fraction[i], decimals=2),
            "Fuel Used": np.round(start_weights[i]*(1 - fuel_fraction[i]), decimals=3)
        })
        
    ##* - Cruise Class I Drag Polar Estimation - ##
    takeoff_weight = empty_weight + fuel_weight + payload_weight + crew_weight
    
    c = .1628 # Roskam
    d = 0.7316 # Roskam
    cf = 0.0025 # Roskam
    e = 0.85

    S_wet = 10 ** (c + d*np.log10(takeoff_weight))

    S = takeoff_weight/(Wto_over_S)
    
    AR = (max_wingSpan ** 2)/S

    # Parasite Drag Estimation
    C_D_0 = cf*S_wet/S

    K = 1/(np.pi * AR * e)

    Cl = np.arange(-2, 2, 0.01)

    C_D = C_D_0 + K*(Cl ** 2)

    # Cruise L/D Estimation
    # Converting Cruise Velocity to ft/s
    cruise_velocity_fts = cruise_velocity_kts*1.68781

    # Calculating Cruise CL
    CL_cruise = W_cruise/(air_density_cruise_slugs*(cruise_velocity_fts ** 2)*(S/2))

    # Calculating Cruise CD
    CD_cruise = C_D_0 + K*(CL_cruise ** 2)

    # Calculating Cruise L/D
    L_D_cruise = CL_cruise / CD_cruise
    
    # TODO: ##* - Reserve Cruise Class I Drag Polar Estimation - ##
    reserve_cruise_velocity_fts = reserve_cruise_velocity_kts*1.68781
    
    CL_reserve_cruise = W_reserve_cruise/(air_density_reserve_cruise_slugs*(reserve_cruise_velocity_fts ** 2)*(S/2))
    
    CD_reserve_cruise = C_D_0 + K*(CL_reserve_cruise ** 2)
    
    L_D_reserve_cruise = CL_reserve_cruise / CD_reserve_cruise

    
    # Dictionary to hold all variables that get printed
    print_variables = {}
    
    print_variables['A'] = A
    print_variables['B'] = B
    print_variables['Mff_climb_initial'] = np.round(Mff_climb_initial, 4)
    print_variables['Mff_climb_above10k'] = np.round(Mff_climb_above10k, 4)
    print_variables['Mff_cruise'] = np.round(Mff_cruise, 4)
    print_variables['Mff'] = np.round(Mff, 4)
    print_variables['fuel_weight'] = np.round(fuel_weight, 4)
    print_variables['empty_weight'] = np.round(empty_weight, 2)
    print_variables['empty_weight_allowable'] = np.round(empty_weight_allowable, 2)
    print_variables['takeoff_weight'] = np.round(takeoff_weight, 2)
    print_variables['fuel_weight'] = np.round(fuel_weight, 2)
    print_variables['S_wet'] = np.round(S_wet, decimals=1)
    print_variables['S'] = np.round(S, decimals=1)
    print_variables['C_D_0'] = np.round(C_D_0, decimals=6)
    print_variables['K'] = np.round(K, decimals=3)
    print_variables['air_density_cruise_slugs'] = air_density_cruise_slugs
    print_variables['cruise_velocity_fts'] = np.round(cruise_velocity_fts, decimals=3)
    print_variables['W_cruise'] = np.round(W_cruise, decimals=3)
    print_variables['W_cruise_end'] = np.round(W_cruise_end, decimals=3)
    print_variables['W_landing'] = np.round(W_landing, decimals=3)
    print_variables['CL_cruise'] = np.round(CL_cruise, 4)
    print_variables['CD_cruise'] = np.round(CD_cruise, 5)
    print_variables['L_D_cruise'] = np.round(L_D_cruise, 4)
    print_variables['CL_reserve_cruise'] = np.round(CL_reserve_cruise, 4)
    print_variables['CD_reserve_cruise'] = np.round(CD_reserve_cruise, 5)
    print_variables['L_D_reserve_cruise'] = np.round(L_D_reserve_cruise, 4)
    print_variables['table_data'] = table_data
    print_variables['Cl'] = Cl
    print_variables['C_D'] = C_D
    print_variables['AR'] = AR
    
    return print_variables, {empty_weight, takeoff_weight}

Wto_over_S = 160
cruise_L_D_guess = 12.20

#* Mission 2
# payload_weight = 295000
# cruise_range_nm = 5000

#* Mission 1
payload_weight = 430000
cruise_range_nm = 2500

#* Ferry
# payload_weight = 0
# cruise_range_nm = 8000

climb_rate_fpm = 1500
cruise_alt_ft = 37000
cruise_alt_meters = cruise_alt_ft*0.3048
cruise_spd_mach = 0.80
climb_initial_Mach = 250 * 0.00149984
climb_above10_Mach = 300 * 0.00149984
delta_temperature = 0

TSFC_tech_factor = 0.9

cruise_TSFC = TSFC_lb_lb_hr(Mach=0.8, Altitude=35000, PowerCode=50) * TSFC_tech_factor
climb_initial_TSFC = np.mean([TSFC_lb_lb_hr(Mach=climb_initial_Mach, Altitude=0, PowerCode=50), TSFC_lb_lb_hr(Mach=climb_initial_Mach, Altitude=10000, PowerCode=50)]) * TSFC_tech_factor
climb_above10k_TSFC = np.mean([TSFC_lb_lb_hr(Mach=climb_above10_Mach, Altitude=10000, PowerCode=50), TSFC_lb_lb_hr(Mach=climb_above10_Mach, Altitude=35000, PowerCode=50)]) * TSFC_tech_factor

# Calculating Atmospheric Conditions
result = calculate_atmosphere(cruise_alt_meters, delta_temperature)
air_density_cruise_slugs = result[3]["slugs/ft^3"]

reserve_cruise_alt_meters = 5000 * 0.3048
result = calculate_atmosphere(reserve_cruise_alt_meters, delta_temperature)
air_density_reserve_cruise_slugs = result[3]["slugs/ft^3"]

result, vars_of_interest = L_D_calc(cruise_L_D_guess,  A, B, payload_weight, cruise_alt_ft, cruise_range_nm, cruise_spd_mach, air_density_cruise_slugs, air_density_reserve_cruise_slugs, climb_initial_TSFC, climb_above10k_TSFC, cruise_TSFC, Wto_over_S, climb_rate_fpm)
L_D_cruise_calc = result['L_D_cruise']
L_D_difference = abs(cruise_L_D_guess - L_D_cruise_calc)

while L_D_difference >= 0.00005:
    if abs(cruise_L_D_guess - L_D_cruise_calc) > .001:
        if cruise_L_D_guess > L_D_cruise_calc:
            cruise_L_D_guess -= abs(cruise_L_D_guess - L_D_cruise_calc) / 2
        else:
            cruise_L_D_guess += abs(cruise_L_D_guess - L_D_cruise_calc) / 2
        # if cruise_L_D_guess > L_D_cruise_calc:
        #     cruise_L_D_guess -= 0.001
        # else:
        #     cruise_L_D_guess += 0.001
    else:
        if cruise_L_D_guess > L_D_cruise_calc:
            cruise_L_D_guess -= 0.00001
        else:
            cruise_L_D_guess += 0.00001
    
    
    
    result, vars_of_interest = L_D_calc(cruise_L_D_guess,  A, B, payload_weight, cruise_alt_ft, cruise_range_nm, cruise_spd_mach, air_density_cruise_slugs, air_density_reserve_cruise_slugs, climb_initial_TSFC, climb_above10k_TSFC, cruise_TSFC, Wto_over_S, climb_rate_fpm)
    L_D_cruise_calc = result['L_D_cruise']
    L_D_difference = abs(cruise_L_D_guess - L_D_cruise_calc)

print('')
print("{:<15} {:<15} {:<10} {:<10} {:<10}".format("Segment", "Phase", "FF", "Weight", "Fuel Used"))
print("=" * 60)
for row in result['table_data']:
    print("{:<15} {:<15} {:<10} {:<10} {:<10}".format(row["Segment"], row["Phase"], row["FF"], row["Weight"], row["Fuel Used"]))

print('')
print('-------------------------------------------------')
print("L_D_converged at:", np.round(L_D_cruise_calc, 5), np.round(cruise_L_D_guess, 5))
print('-------------------------------------------------')
print('')
print('----------- Wing Area Calculations ---------')
print("{:<15} {:<15} {:<10} {:<10}".format("Swet", "S", "CD_0", "K"))
print("=" * 47)
print("{:<15} {:<15} {:<10} {:<10}".format(np.round(result['S_wet'], decimals=1), np.round(result['S'], decimals=1), np.round(result['C_D_0'], decimals=4), np.round(result['K'], decimals=3)))

# Print statements
print('')
print(f"A: {result['A']}, B: {result['B']}")
print(f"Mff_climb_initial: {result['Mff_climb_initial']}")
print(f"Mff_climb_above10k: {result['Mff_climb_above10k']}")
print(f"Mff_cruise: {result['Mff_cruise']}")
print(f"Marginal fuel fraction: {result['Mff']}")
print(f"Fuel weight: {result['fuel_weight']}")
print('')
print("Converged Weight:\n---------------------")
print(f"Empty weight: {result['empty_weight']}")
print(f"Allowable empty weight: {result['empty_weight_allowable']}")
print(f"Takeoff Weight: {result['takeoff_weight']}")
print(f"Fuel weight: {result['fuel_weight']}")
print('')
print('Cruise L/D Calculations:\n---------------------')
print(f"Density (slug/ft3): {result['air_density_cruise_slugs']}")
print(f"Cruise Velocity (ft/s): {result['cruise_velocity_fts']}")
print(f"Cruise Weight (lbs): {result['W_cruise']}")
print(f"Cruise C_L: {result['CL_cruise']}")
print(f"Cruise C_D: {result['CD_cruise']}")
print(f"Cruise L/D: {result['L_D_cruise']}")
print('')
print('Reserve Cruise L/D Calculations:\n---------------------')
print(f"Reserve Cruise C_L: {result['CL_reserve_cruise']}")
print(f"Reserve Cruise C_D: {result['CD_reserve_cruise']}")
print(f"Reserve Cruise L/D: {result['L_D_reserve_cruise']}")
print('')
print(f"Aspect Ratio: {result['AR']}")