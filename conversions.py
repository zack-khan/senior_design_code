# Speed of sound in air at sea level in feet/sec
speed_of_sound_ft_sec = 1125.33

# 1 knot = 1.68781 feet/sec
knot_to_ft_sec = 1.68781

def ft_sec_to_knots(ft_sec):
    return ft_sec / knot_to_ft_sec

def ft_sec_to_mach(ft_sec):
    return ft_sec / speed_of_sound_ft_sec

def knots_to_ft_sec(knots):
    return knots * knot_to_ft_sec

def knots_to_mach(knots):
    return ft_sec_to_mach(knots_to_ft_sec(knots))

def mach_to_ft_sec(mach):
    return mach * speed_of_sound_ft_sec

def mach_to_knots(mach):
    return ft_sec_to_knots(mach_to_ft_sec(mach))

# 1 meter = 3.28084 feet
meter_to_ft = 3.28084

def ft_to_meters(feet):
    return feet / meter_to_ft

def meters_to_ft(meters):
    return meters * meter_to_ft