import math

#* Importing GE-90 Engine Data
# import pandas as pd

# # Columns to import
# columns_to_import = ['Mach', 'Altitude', 'PowerCode', 'Thrust', 'RamDrag', 'FuelFlow', 'EINox']

# # Read the specific columns from the CSV file
# filtered_data = pd.read_csv('./Project/GE90-115B.csv', usecols=columns_to_import)
# # Calculate the new columns based on the existing data
# filtered_data['ThrustNet'] = filtered_data['Thrust'] - filtered_data['RamDrag']
# filtered_data['TSFC'] = filtered_data['FuelFlow'] / filtered_data['ThrustNet']

#* Equations
def Thrust_equation_lb(Mach, Altitude, PowerCode):
    return (
        87215.412352441 +
        -84921.888124016 * math.tanh(0.5 * (1.00327737594546 + 3.4830074889556 * Mach + 0.0000788536685090701 * Altitude + -0.0253712542393253 * PowerCode)) +
        51351.6587067938 * math.tanh(0.5 * (-1.34136513793766 + 4.65467006881983 * Mach + 0.0000837536010811189 * Altitude + 0.0536979463635514 * PowerCode)) +
        -41964.0917456052 * math.tanh(0.5 * (3.38865185570751 + -0.110411023322749 * Mach + -0.0000122224542081479 * Altitude + -0.0831214448525152 * PowerCode)) +
        79388.9240081843 * math.tanh(0.5 * (-2.72512328170832 + -0.595216931620992 * Mach + 0.000073996225991774 * Altitude + -0.0304283691011463 * PowerCode)) +
        50344.73691648 * math.tanh(0.5 * (3.75550001236709 + 0.781133978853655 * Mach + -0.000102705262228657 * Altitude + -0.0102351298493997 * PowerCode))
    )

def TSFC_lb_lb_hr(Mach, Altitude, PowerCode):
    return (
        -7.75605631152849 +
        0.200426942028317 * math.tanh(0.5 * (-5.28739087276884 + 3.94101853106119 * Mach + -0.0000027708831892946 * Altitude + 0.0811329984278542 * PowerCode)) +
        14.4730836959382 * math.tanh(0.5 * (-10.3324412033813 + -0.738635133470154 * Mach + 0.0000012768313501029 * Altitude + 0.558488545620705 * PowerCode)) +
        5.69093233463211 * math.tanh(0.5 * (15.4736132968188 + 1.21935939417574 * Mach + -0.0000015276328237609 * Altitude + -0.746365440892657 * PowerCode)) +
        0.621223200351436 * math.tanh(0.5 * (4.60996695909191 + 1.09370040973953 * Mach + -0.0000044813652256643 * Altitude + -0.222488243884856 * PowerCode))
    )

def Thrust_lapse(Mach, Altitude, PowerCode):
    return (
        (
            87215.412352441 +
            -84921.888124016 * math.tanh(0.5 * (1.00327737594546 + 3.4830074889556 * Mach + 0.0000788536685090701 * Altitude + -0.0253712542393253 * PowerCode)) +
            51351.6587067938 * math.tanh(0.5 * (-1.34136513793766 + 4.65467006881983 * Mach + 0.0000837536010811189 * Altitude + 0.0536979463635514 * PowerCode)) +
            -41964.0917456052 * math.tanh(0.5 * (3.38865185570751 + -0.110411023322749 * Mach + -0.0000122224542081479 * Altitude + -0.0831214448525152 * PowerCode)) +
            79388.9240081843 * math.tanh(0.5 * (-2.72512328170832 + -0.595216931620992 * Mach + 0.000073996225991774 * Altitude + -0.0304283691011463 * PowerCode)) +
            50344.73691648 * math.tanh(0.5 * (3.75550001236709 + 0.781133978853655 * Mach + -0.000102705262228657 * Altitude + -0.0102351298493997 * PowerCode))
        ) / 113284.384900881
    )