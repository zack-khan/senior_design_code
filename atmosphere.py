import math

def convert_temperature(temperature):
    return {
        'Celsius': temperature - 273.15,
        'Kelvin': temperature,
        'Fahrenheit': (temperature - 273.15) * 9/5 + 32,
        'Rankine': temperature * 9/5
    }

def convert_speed_of_sound(speed):
    return {
        'ft/s': speed * 3.28084,
        'knots': speed * 1.94384,
        'mph': speed * 2.23694,
        'm/s': speed
    }

def convert_pressure(pressure):
    return {
        'Pascals': pressure,
        'atmospheres': pressure / 101325.0,
        'inHg': pressure * 0.0002953,
        'psi': pressure * 0.00014503773779
    }

def convert_density(density):
    return {
        'slugs/ft^3': density * 0.00194032,
        'kg/m^3': density
    }

def calculate_atmosphere(altitude, delta_temperature):
    air_mol_weight = 28.9644
    density_sl = 1.225
    pressure_sl = 101325
    temperature_sl = 288.15
    gamma = 1.4
    gravity = 9.80665
    r_gas = 8.31432
    r = 287.053

    altitudes = [0, 11000, 20000, 32000, 47000, 51000, 71000, 84852]
    pressures_rel = [1, 2.23361105092158e-1, 5.403295010784876e-2, 8.566678359291667e-3, 1.0945601337771144e-3, 6.606353132858367e-4, 3.904683373343926e-5, 3.6850095235747942e-6]
    temperatures = [288.15, 216.65, 216.65, 228.65, 270.65, 270.65, 214.65, 186.946]
    temp_grads = [-6.5, 0, 1, 2.8, 0, -2.8, -2, 0]
    gmr = gravity * air_mol_weight / r_gas

    if altitude < -5000 or altitude > 86000:
        return "Error: Altitude must be between -5000 and 86000 meters."

    if delta_temperature is None:
        delta_temperature = 0

    i = 0
    if altitude > 0:
        while altitude > altitudes[i + 1]:
            i += 1

    base_temp = temperatures[i]
    temp_grad = temp_grads[i] / 1000
    pressure_rel_base = pressures_rel[i]
    delta_altitude = altitude - altitudes[i]
    temperature = base_temp + temp_grad * delta_altitude

    if abs(temp_grad) < 1e-10:
        pressure_relative = pressure_rel_base * math.exp(-gmr * delta_altitude / 1000 / base_temp)
    else:
        pressure_relative = pressure_rel_base * math.pow(base_temp / temperature, gmr / temp_grad / 1000)

    temperature += delta_temperature
    speed_of_sound = math.sqrt(gamma * r * temperature)
    pressure = pressure_relative * pressure_sl
    density = density_sl * pressure_relative * temperature_sl / temperature
    viscosities = 1.512041288 * math.pow(temperature, 1.5) / (temperature + 120) / 1000000.0
    
    temperature_units = convert_temperature(temperature)
    speed_units = convert_speed_of_sound(speed_of_sound)
    pressure_units = convert_pressure(pressure)
    density_units = convert_density(density)

    return temperature_units, speed_units, pressure_units, density_units, viscosities

# Example usage
# altitude_meters = 1000 # in meters
# delta_temperature = 10  # temperature offset in Kelvin
# result = calculate_atmosphere(altitude_meters, delta_temperature)
# print("Temperature:", result[0], "K")
# print("Speed of Sound:", result[1], "m/s")
# print("Pressure:", result[2], "Pa")
# print("Density:", result[3], "kg/m3")
# print("Viscosities:", result[4], "Pa.s")

# print(f"Temperature: {result[0]}")
# print(f"Speed of Sound: {result[1]}")
# print(f"Pressure: {result[2]}")
# print(f"Density: {result[3]}")


# def Atmosphere(alt):
#     """ Compute temperature, density, and pressure in standard atmosphere.
#     Correct to 86 km.  Only approximate thereafter.
#     Input:
# 	alt	geometric altitude, km.
#     Return: (sigma, delta, theta)
# 	sigma	density/sea-level standard density
# 	delta	pressure/sea-level standard pressure
# 	theta	temperature/sea-level std. temperature
#     """

#     REARTH = 6369.0		# radius of the Earth (km)
#     GMR = 34.163195
#     NTAB = 8			# length of tables

#     htab = [ 0.0,  11.0, 20.0, 32.0, 47.0, 51.0, 71.0, 84.852 ]
#     ttab = [ 288.15, 216.65, 216.65, 228.65, 270.65, 270.65, 214.65, 186.946 ]
#     ptab = [ 1.0, 2.2336110E-1, 5.4032950E-2, 8.5666784E-3, 1.0945601E-3, 6.6063531E-4, 3.9046834E-5, 3.68501E-6 ]
#     gtab = [ -6.5, 0.0, 1.0, 2.8, 0, -2.8, -2.0, 0.0 ]

#     h = alt*REARTH/(alt+REARTH)	# geometric to geopotential altitude

#     i=0; j=len(htab)
#     while (j > i+1):
#         k = (i+j)/2
#         if h < htab[k]:
#             j = k
#         else:
#             i = k
#     tgrad = gtab[i]		# temp. gradient of local layer
#     tbase = ttab[i]		# base  temp. of local layer
#     deltah=h-htab[i]		# height above local base
#     tlocal=tbase+tgrad*deltah	# local temperature
#     theta = tlocal/ttab[0]	# temperature ratio

#     if 0.0 == tgrad:
#         delta=ptab[i]*math.exp(-GMR*deltah/tbase)
#     else:
#         delta=ptab[i]*math.pow(tbase/tlocal, GMR/tgrad)
    
#     sigma = delta/theta
#     return ( sigma, delta, theta )

# print(Atmosphere(2))