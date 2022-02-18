from datetime import datetime

#from id_map import *
"""
The relative order within the characters remains the same but order of string(in pair) gets reversed
Ex ==>> B7370000 -> 000037B7
"""

reverse_string_in_pair = lambda string: "".join(
    reversed([string[idx : idx + 2] for idx in range(0, len(string), 2)])
)

parse_sns_string = lambda string: json.loads(string["Records"][0]["Sns"]["Message"])


check_is_battery_latched = lambda string: convert_and_get_desired_value(string) == 1


hex_to_bin = lambda string: bin(int(string, 16))


def convert_and_get_temperature(string, roundabout=None):
    if not roundabout:
        roundabout = 0
    assert isinstance(roundabout, int), "`roundabout` value should be integer"
    temperature = int(string, 16) - roundabout
    return temperature


def convert_and_get_temperatures(string):
    temp = ""
    temperatures = []
    for idx, _str in enumerate(string):
        temp += _str
        if idx % 2:
            temperatures.append(convert_and_get_temperature(temp))
            temp = ""
    return temperatures


def convert_and_get_current_val(string):
    new_string = reverse_string_in_pair(string)
    if new_string[0:2] == "FF":
        current = (
            int(hex(int("100000000", 16) - int(new_string, 16)), 16) / 1000
        ) * 0.01
        current *= -1
    else:
        current = (int(new_string, 16) / 1000) * 0.01
    return current


def convert_and_get_desired_value(string, multiplier=None):
    string = reverse_string_in_pair(string)
    if not multiplier:
        multiplier = 1.0
    return int(string, 16) * multiplier


def convert_and_handle_negative_values(string, multiplier=None):
    new_string = reverse_string_in_pair(string)
    if new_string[0:2] == "FF":
        val = int("FFFF", 16) - int(new_string, 16)
        if multiplier:
            val *= multiplier
    else:
        val = convert_and_get_desired_value(string, multiplier=multiplier)
    return val


def handle_datetime(date, time):
    request_date = datetime.strptime(date, "%y%m%d")
    request_time = datetime.strptime(time, "%H%M%S")
    request_date = request_date.replace(
        hour=request_time.hour, minute=request_time.minute, second=request_time.second
    )
    return request_date

def stark_parser(can_ids,vehicle_data):
    bmsData={}
    ControllerDATA={}

    if vehicle_data:
        for can_id, can_data in zip(can_ids, vehicle_data):
            can_data = can_data.rjust(16, "0")
            
            if can_id == "110": 
                try:
                    bmsData["balancingLimit"]= convert_and_get_desired_value(string=can_data[:4], multiplier=0.1)
                    
                    bmsData["prechargeActive"]= convert_and_get_desired_value(string=can_data[4:6])

                    bmsData["balancingActive"]= convert_and_get_desired_value(string=can_data[6:8])

                    bmsData["Pack_I_Master"] = convert_and_get_desired_value(string=can_data[8:],multiplier=0.01)

                except ValueError:
                    bmsData["balancingLimit"] = bmsData["prechargeActive"] = bmsData["balancingActive"] = bmsData["Pack_I_Master"] = 0

            elif can_id == "111":
                try:
                    bmsData["Pack_Q_SOC_Trimmed"] = convert_and_get_desired_value(
                        string=can_data[0:4], multiplier=0.01
                    )
                    bmsData["SOH"] = convert_and_get_desired_value(
                        string=can_data[4:8], multiplier=0.01
                    )
                    bmsData["BMSStatus"] = convert_and_get_desired_value(string=can_data[8:10])

                    bmsData["FullyChargeFlag"] = check_is_battery_latched(
                        string=can_data[10:12]
                    )
                    bmsData["Pack_V_Sum_of_Cells"] = convert_and_get_desired_value(
                        string=can_data[12:], multiplier=0.1
                    )
                except:
                    bmsData["Pack_Q_SOC_Terminal"] = bmsData["SOH"] = bmsData["BMSStatus"] = bmsData["FullyChargeFlag"] = bmsData["Pack_V_Sum_of_Cells"]=0
            elif can_id == "112":
                try:
                    bmsData["Aux_T"] = convert_and_get_temperatures(string=can_data[0:12])
                    
                    bmsData["BatteryCapacity"] = convert_and_get_desired_value(
                        string=can_data[12:], multiplier=0.1
                    )
                except:
                    bmsData["Aux_T"] = list()
                    bmsData["BatteryCapacity"] = 0
            elif (
                can_id == "113"
                or can_id == "114"
                or can_id == "115"
            ):
                try: 
                    if "CMU1_Cell_Vtgs" not in bmsData:
                        bmsData["CMU1_Cell_Vtgs"]=[]   
                    
                    bmsData["CMU1_Cell_Vtgs"].append(
                        convert_and_get_desired_value(can_data[0:4], multiplier=0.1)
                    )
                    bmsData["CMU1_Cell_Vtgs"].append(
                        convert_and_get_desired_value(can_data[4:8], multiplier=0.1)
                    )
                    bmsData["CMU1_Cell_Vtgs"].append(
                        convert_and_get_desired_value(can_data[8:12], multiplier=0.1)
                    )
                    bmsData["CMU1_Cell_Vtgs"].append(
                        convert_and_get_desired_value(can_data[12:], multiplier=0.1)
                    )
                except:
                    bmsData["CMU1_Cell_Vtgs"] = list()
            elif (
                can_id == "116"
                or can_id == "117"
                or can_id == "118"
            ):
                try:    
                    if "CMU2_Cell_Vtgs" not in bmsData:
                        bmsData["CMU2_Cell_Vtgs"]=[]  
                    bmsData["CMU2_Cell_Vtgs"].append(
                        convert_and_get_desired_value(can_data[0:4], multiplier=0.1)
                    )
                    bmsData["CMU2_Cell_Vtgs"].append(
                        convert_and_get_desired_value(can_data[4:8], multiplier=0.1)
                    )
                    bmsData["CMU2_Cell_Vtgs"].append(
                        convert_and_get_desired_value(can_data[8:12], multiplier=0.1)
                    )
                    bmsData["CMU2_Cell_Vtgs"].append(
                        convert_and_get_desired_value(can_data[12:], multiplier=0.1)
                    )
                except:
                    bmsData["CMU2_Cell_Vtgs"] = list()
            elif can_id == "11C":
                try:
                    bmsData["BatteryCapacity_Ah"] = convert_and_get_desired_value(can_data[0:4], multiplier=0.1)
                    bmsData["Pack_I_Master"] = convert_and_get_desired_value(can_data[4:8], multiplier=0.1)
                    bmsData["FW_major"] = convert_and_get_desired_value(can_data[8:10])
                    bmsData["FW_minor"] = convert_and_get_desired_value(can_data[10:12])
                    bmsData["BUILD_Date"] = convert_and_get_desired_value(can_data[12:14])
                    bmsData["hw_pcb"] = convert_and_get_desired_value(can_data[14:])
                except:
                    bmsData["BatteryCapacity_Ah"] = bmsData["Pack_I_Master"] = bmsData["FW_major"] = bmsData["FW_minor"] = bmsData["BUILD_Date"] = bmsData["hw_pcb"] = 0
            elif can_id == "12A":
                try:
                    bmsData["dynamic_in_limit"] = convert_and_get_desired_value(can_data[:4], multiplier=0.1)
                    bmsData["dynamic_out_limit"] = convert_and_get_desired_value(can_data[4:8], multiplier=0.1)
                except:
                    bmsData["dynamic_in_limit"] = bmsData["dynamic_out_limit"] = 0

            elif can_id == "705":
                try:
                    ControllerDATA["MotorTemp"] = convert_and_get_temperature(
                        string=can_data[0:2], roundabout=50
                    )
                    ControllerDATA["Controller_Temp"] = convert_and_get_temperature(
                        string=can_data[2:4], roundabout=50
                    )
                    ControllerDATA["SOC"] =  convert_and_get_desired_value(can_data[4:6])
                    ControllerDATA["Batt_Discharge_Current_Rate"] =  convert_and_get_desired_value(can_data[6:8])
                    ControllerDATA["Odometer"] = convert_and_get_desired_value(
                        string=can_data[8:], multiplier=0.1
                    )
                except:
                    ControllerDATA["MotorTemp"] = ControllerDATA["Controller_Temp"] = ControllerDATA["SOC"] = ControllerDATA["Batt_Discharge_Current_Rate"] = ControllerDATA["Odometer"] = 0
            elif can_id == "706":
                try:
                    ControllerDATA["Vehicle_Status"] = convert_and_get_desired_value(can_data[0:2])
                    ControllerDATA["AssistLevelGear"] = convert_and_get_desired_value(can_data[4:6])
                    ControllerDATA["AlarmFault"] = convert_and_get_desired_value(can_data[6:8])
                    ControllerDATA["SpeedLowHigh"] = convert_and_handle_negative_values(
                        string=can_data[8:12], multiplier=0.1
                    )
                    ControllerDATA["TripLowHigh"] = convert_and_get_desired_value(
                        string=can_data[12:], multiplier=0.1
                    )
                except:
                    ControllerDATA["Vehicle_Status"] = ControllerDATA["controller_mode"] =  ControllerDATA["AssistLevelGear"] = ControllerDATA["AlarmFault"] = ControllerDATA["SpeedLowHigh"] = ControllerDATA["TripLowHigh"] = 0 
            elif can_id == "708":
                try:
                    ControllerDATA["FaultStatus"] = [
                        convert_and_get_desired_value(can_data[0:2]),
                        convert_and_get_desired_value(can_data[2:4]),
                        convert_and_get_desired_value(can_data[4:6]),
                        convert_and_get_desired_value(can_data[6:8]),
                        convert_and_get_desired_value(can_data[8:10]),
                        convert_and_get_desired_value(can_data[10:12]),
                        convert_and_get_desired_value(can_data[12:14]),
                        convert_and_get_desired_value(can_data[14:16])
                        
                    ]
                except:
                    ControllerDATA["FaultStatus"] = list()
            elif can_id == "710":
                try:
                    ControllerDATA["ThrottleCommand"] = convert_and_get_desired_value(
                        string=can_data[0:2]
                    )
                    ControllerDATA["ThrottleMultiplier"] = convert_and_get_desired_value(
                        string=can_data[2:4]
                    )
                    ControllerDATA["MappedThrottle"] = convert_and_get_desired_value(
                        string=can_data[4:6]
                    )
                    ControllerDATA["ThrottlePotentiometer"] = convert_and_get_desired_value(
                        string=can_data[6:8], multiplier=0.1
                    )
                    ControllerDATA["BrakeCommand"] = convert_and_get_desired_value(
                        string=can_data[8:10], multiplier=1
                    )
                    ControllerDATA["MappedBrake"] = convert_and_get_desired_value(
                        string=can_data[10:12], multiplier=1
                    )
                    ControllerDATA["Potential2Row"] = convert_and_get_desired_value(
                        string=can_data[12:14], multiplier=0.1
                    )
                except:
                    ControllerDATA["ThrottleCommand"] =ControllerDATA["ThrottleMultiplier"] = ControllerDATA["MappedThrottle"] = ControllerDATA["ThrottlePotentiometer"] = ControllerDATA["BrakeCommand"] = ControllerDATA["MappedBrake"] = ControllerDATA["Potential2Row"] = 0
            elif can_id == "715":
                try:
                    ControllerDATA["BatteryCapacityVoltage"] = convert_and_get_desired_value(
                        string=can_data[8:10], multiplier=1
                    )
                    ControllerDATA["BatteryKeyswitchVoltage"] = convert_and_get_desired_value(
                        string=can_data[10:12], multiplier=1
                    )
                    ControllerDATA["MotorRPM"] = convert_and_handle_negative_values(
                        string=can_data[12:], multiplier=1
                    )
                except:
                    ControllerDATA["BatteryCapacityVoltage"] = ControllerDATA["BatteryKeyswitchVoltage"] = ControllerDATA["MotorRPM"] = 0
            elif can_id == "716":
                try:
                    ControllerDATA["ControllerMasterTimer"] = convert_and_get_desired_value(
                        string=can_data[2:10], multiplier=0.1
                    )
                    ControllerDATA["ControllerCurrentRMS"] = convert_and_get_desired_value(
                        string=can_data[12:14], multiplier=1
                    )
                    ControllerDATA["ControllerModulationDepth"] = convert_and_get_desired_value(
                        string=can_data[14:], multiplier=1
                    )
                    
                except:
                    ControllerDATA["ControllerMasterTimer"] = ControllerDATA["ControllerCurrentRMS"] = ControllerDATA["ControllerModulationDepth"] = 0
            elif can_id == "717":
                try:
                    ControllerDATA["ControllerFrequency"] = convert_and_get_desired_value(
                        string=can_data[0:4], multiplier=1
                    )
                    ControllerDATA["ControllerMainState"] = convert_and_get_desired_value(
                        string=can_data[4:6], multiplier=1
                    )
                except:
                    ControllerDATA["ControllerFrequency"] = ControllerDATA["ControllerMainState"] = 0
            elif can_id == "724":
                try:
                    ControllerDATA["MotorTorqueEstimated"] = convert_and_handle_negative_values(
                        string=can_data[0:4], multiplier=0.1
                    )
                    ControllerDATA["BatteryPowerConsumed"] = convert_and_get_desired_value(
                        string=can_data[4:6], multiplier=0.1
                    )
                    ControllerDATA["BatteryEnergyConsumed"] = convert_and_get_desired_value(
                        string=can_data[6:8], multiplier=0.1
                    )
                    ControllerDATA["VehiclePowerMode"] = convert_and_get_desired_value(
                        string=can_data[8:10]
                    )
                except:
                    ControllerDATA["MotorTorqueEstimated"] = ControllerDATA["BatteryPowerConsumed"] = ControllerDATA["BatteryEnergyConsumed"] = ControllerDATA["VehiclePowerMode"] = 0
            elif can_id == "725":
                try:
                    ControllerDATA["AccelerationRate"] = convert_and_get_desired_value(
                        string=can_data[0:2], multiplier=0.1
                    )
                    ControllerDATA["AccelerationReleaseRate"] = convert_and_get_desired_value(
                        string=can_data[2:4], multiplier=0.1
                    )
                    ControllerDATA["BrakeRate"] = convert_and_get_desired_value(
                        string=can_data[4:6], multiplier=0.1
                    )
                    ControllerDATA["DriveCurrentLimit"] = convert_and_get_desired_value(
                        string=can_data[6:8], multiplier=1
                    )
                    ControllerDATA["RegenCurrentLimit"] = convert_and_get_desired_value(
                        string=can_data[8:10], multiplier=1
                    )
                    ControllerDATA["BrakeCurrentLimit"] = convert_and_get_desired_value(
                        string=can_data[10:12], multiplier=1
                    )
                    ControllerDATA["RegenOff"] = 0 if can_data[12:14] == "FF" else 1
                    ControllerDATA["ControllerResetCANBaudRate"]=convert_and_get_desired_value(
                        string=can_data[14:], multiplier=1
                    )
                except:
                    ControllerDATA["AccelerationRate"] = ControllerDATA["AccelerationReleaseRate"] = ControllerDATA["BrakeRate"] = ControllerDATA["DriveCurrentLimit"] = ControllerDATA["RegenCurrentLimit"] = ControllerDATA["BrakeCurrentLimit"] =ControllerDATA["RegenOff"] = ControllerDATA["ControllerResetCANBaudRate"]=0
            elif can_id == "726":
                try:
                    ControllerDATA["ControllerSerialNumber"] = convert_and_get_desired_value( can_data[0:8] )
                    ControllerDATA["VCLVersion"] = convert_and_get_desired_value( can_data[8:10] )
                    ControllerDATA["VCLBuildNumber"] = convert_and_get_desired_value( can_data[10:12] )
                    ControllerDATA["OSVersion"] = convert_and_get_desired_value( can_data[12:14] )
                    ControllerDATA["OSBuildNumber"] = convert_and_get_desired_value( can_data[14:] )
                except:
                    ControllerDATA["ControllerSerialNumber"] = ControllerDATA["VCLVersion"] = ControllerDATA["VCLBuildNumber"] = ControllerDATA["OSVersion"] = ControllerDATA["OSBuildNumber"] = 0
        bmsData["Cell_V_Max_Val"] = max(bmsData["CMU1_Cell_Vtgs"]+bmsData["CMU2_Cell_Vtgs"])
        bmsData["Cell_V_Min_Val"] = min(list(filter(lambda x: x > 100, bmsData["CMU1_Cell_Vtgs"]))+list(filter(lambda x: x > 100, bmsData["CMU2_Cell_Vtgs"]))) if bmsData["Cell_V_Max_Val"] else 0          
    req_tuple=[]
    for key in bmsData.keys():
        req_tuple.append(bmsData[key])
    for key in ControllerDATA.keys():
        req_tuple.append(ControllerDATA[key])
    req_result = [bmsData["Cell_V_Min_Val"], bmsData["Cell_V_Max_Val"], bmsData["Pack_I_Master"], bmsData["Pack_Q_SOC_Trimmed"], bmsData["SOH"], bmsData["Pack_V_Sum_of_Cells"], bmsData["BMSStatus"], bmsData["Aux_T"], bmsData["BatteryCapacity"], bmsData["CMU1_Cell_Vtgs"][0], bmsData["CMU1_Cell_Vtgs"][1], bmsData["CMU1_Cell_Vtgs"][2], bmsData["CMU1_Cell_Vtgs"][3], bmsData["CMU1_Cell_Vtgs"][4], bmsData["CMU1_Cell_Vtgs"][5], bmsData["CMU1_Cell_Vtgs"][6], bmsData["CMU1_Cell_Vtgs"][7], bmsData["CMU1_Cell_Vtgs"][8], bmsData["CMU1_Cell_Vtgs"][9], bmsData["CMU1_Cell_Vtgs"][10], bmsData["CMU1_Cell_Vtgs"][11], 'bmsData["CMU1_Cell_Vtgs"][12]', 'bmsData["CMU1_Cell_Vtgs"][13]', 'bmsData["CMU1_Cell_Vtgs"][14]', 'bmsData["CMU1_Cell_Vtgs"][15]', 'bmsData["CMU1_Cell_Vtgs[16]"]', 'bmsData["CMU1_Cell_Vtgs[17]"]', bmsData["CMU2_Cell_Vtgs"][0], bmsData["CMU2_Cell_Vtgs"][1], bmsData["CMU2_Cell_Vtgs"][2], bmsData["CMU2_Cell_Vtgs"][3], bmsData["CMU2_Cell_Vtgs"][4], bmsData["CMU2_Cell_Vtgs"][5], bmsData["CMU2_Cell_Vtgs"][6], bmsData["CMU2_Cell_Vtgs"][7], bmsData["CMU2_Cell_Vtgs"][8], bmsData["CMU2_Cell_Vtgs"][9], bmsData["CMU2_Cell_Vtgs"][10], bmsData["CMU2_Cell_Vtgs"][11], 'bmsData["CMU2_Cell_Vtgs[12]"]', 'bmsData["CMU2_Cell_Vtgs[13]"]', 'bmsData["CMU2_Cell_Vtgs[14]"]', 'bmsData["CMU2_Cell_Vtgs[15]"]', 'bmsData["CMU2_Cell_Vtgs[16]"]', 'bmsData["CMU2_Cell_Vtgs[17]"]', ControllerDATA["MotorTemp"], ControllerDATA["Controller_Temp"], ControllerDATA["SOC"], ControllerDATA["Batt_Discharge_Current_Rate"], ControllerDATA["Odometer"], ControllerDATA["Vehicle_Status"], ControllerDATA["AssistLevelGear"], ControllerDATA["AlarmFault"], ControllerDATA["SpeedLowHigh"], ControllerDATA["TripLowHigh"], ControllerDATA["FaultStatus"], ControllerDATA["ThrottleCommand"], ControllerDATA["ThrottleMultiplier"], ControllerDATA["MappedThrottle"], ControllerDATA["BrakeCommand"], ControllerDATA["MappedBrake"], ControllerDATA["Potential2Row"], ControllerDATA["ThrottlePotentiometer"], ControllerDATA["BatteryCapacityVoltage"], ControllerDATA["BatteryKeyswitchVoltage"], ControllerDATA["MotorRPM"], ControllerDATA["ControllerMasterTimer"], ControllerDATA["ControllerCurrentRMS"], ControllerDATA["ControllerModulationDepth"], ControllerDATA["ControllerFrequency"], ControllerDATA["ControllerMainState"], ControllerDATA["MotorTorqueEstimated"], ControllerDATA["BatteryPowerConsumed"], ControllerDATA["BatteryEnergyConsumed"], ControllerDATA["AccelerationRate"], ControllerDATA["AccelerationReleaseRate"], ControllerDATA["BrakeRate"], ControllerDATA["DriveCurrentLimit"], ControllerDATA["RegenCurrentLimit"], ControllerDATA["BrakeCurrentLimit"], ControllerDATA["RegenOff"], ControllerDATA["ControllerResetCANBaudRate"], ControllerDATA["ControllerSerialNumber"], ControllerDATA["VCLVersion"], ControllerDATA["VCLBuildNumber"], ControllerDATA["OSVersion"], ControllerDATA["OSBuildNumber"], "dataType_controller", "Temperature Ambient", "Temperature C3 Box", "Temperature ON Board", "Datatype_ADC", bmsData["FullyChargeFlag"], ControllerDATA["VehiclePowerMode"], "vehicleState", "vehicle_parameter_ar_Status", bmsData["balancingLimit"], bmsData["prechargeActive"], bmsData["balancingActive"], bmsData["FW_major"], bmsData["FW_minor"], bmsData["BUILD_Date"], "brakeCount", 'bmsData["requested_current"]', 'bmsData["requested_voltage"]', "charger_param_requested_current", "charger_param_requested_voltage", "charger_param_output_current", "charger_param_output_voltage", "charger_param_status", "liq_temp", bmsData["dynamic_in_limit"], bmsData["dynamic_out_limit"], "HW", "SW", "dataType_Misc", "stringIndex"]
    return ",".join(map(str,req_result))
    #print(req_tuple)

            
can_ids = ['20', '20', '20', '20', '20', '20', '705', '706', '708', '710', '715', '716', '717', '724', '726', '20', '20', '20', '20', '110', '111', '20', '112', '113', '114', '115', '116', '117', '118', '1806E5F4', '12A', '11C', '20', '258', '259', '20', '705', '706', '708', '710', '715', '716', '717', '724', '726', '20', '20', '20', '20', '20', '20', '705', '706', '708', '710', '715', '716', '717', '724', '726', '20', '20', '725', '20', '20', '110', '111', '112', '113', '114', '115', '116', '117', '118', '1806E5F4', '12A', '11C', '20', '20', '258', '259', '705', '706', '708', '710', '715', '716', '717', '724', '726', '20', '20', '20', '20', '20', '20', '20', '705', '706', '708', '710', '715', '716', '717', '724', '726', '20', '20', '20', '110', '111', '20', '112', '113', '114', '115', '116', '117', '118', '1806E5F4', '12A', '11C', '20', '20', '258', '259', '705', '706', '708', '710', '715', '716', '717', '724', '726', '20', '20', '20', '20', '20', '20', '705', '706', '708', '710', '715', '716', '717', '724', '726', '20', '20', '725', '20', '20', '110', '111', '112', '113', '114', '115', '116', '117', '118', '1806E5F4', '12A', '11C', '20', '20', '258', '259', '20', '705', '706', '708', '710', '715', '716', '717', '724', '726', '20', '20', '20', '20', '20', '20', '705', '706', '708', '710', '715', '716', '717', '724', '726', '20', '20', '20', '110', '111', '20', '112', '113', '114', '115', '116', '117', '118', '1806E5F4', '12A', '11C', '20', '20', '258', '259', '705', '706', '708', '710', '715', '716', '717', '724', '726', '20', '20', '20', '20', '20', '20', '705', '706', '708', '710', '715', '716', '717', '724', '726', '20', '725', '20', '20', '20', '110', '111', '112', '113', '114', '115', '116', '117', '118', '1806E5F4', '12A', '11C', '20', '20', '20', '705', '706', '708', '710', '715', '716', '717', '724', '726', '258', '259', '20', '20', '20', '20', '20', '20', '705', '706', '708', '710', '715', '716', '717', '724', '726', '20', '20', '20', '110', '111', '20', '112', '113', '114', '115', '116', '117', '118', '1806E5F4', '12A', '11C', '20', '20', '705', '706', '708', '710', '715', '716', '717', '724', '726', '20', '258', '259', '20', '20', '20', '20', '20', '20', '705', '706', '708', '710', '715', '716', '717', '724', '726', '725', '20', '20', '20', '110', '111', '112', '113', '114', '115', '116', '117', '118', '1806E5F4', '12A', '11C', '20', '20', '20', '705', '706', '708', '710', '715', '716', '717', '724', '726', '20', '258', '259', '20', '20', '20', '20', '20', '705', '706', '708', '710', '715', '716', '717', '724', '726', '20', '20', '20', '110', '111', '20', '112', '113', '114', '115', '116', '117', '118', '1806E5F4', '12A', '11C', '20', '20', '705', '706', '708', '710', '715', '716', '717', '724', '20', '726', '258', '259', '20', '20', '20', '20', '20', '20', '705', '706', '708', '710', '715', '716', '717', '724', '726', '725', '20', '20', '20', '110', '111', '112', '113', '114', '115', '116', '117', '118', '1806E5F4', '12A', '11C', '20', '20', '20', '705', '706', '708', '710', '715', '716', '717', '724', '726', '20', '258', '259', '20', '20', '20', '20', '20', '705', '706', '708', '710', '715', '716', '717', '724', '726', '20', '20', '20', '110', '111', '20', '112', '113', '114', '115', '116', '117', '118', '1806E5F4', '12A', '11C', '20', '20', '20', '705', '706', '708', '710', '715', '716', '717', '724', '726', '20', '258', '259', '20', '20', '20', '20', '20', '705', '706', '708', '710', '715', '716', '717', '724', '726', '725', '20', '20', '20', '110', '111', '112', '113', '114', '115', '116', '117', '118', '1806E5F4', '12A', '11C', '20', '20', '20', '705', '706', '708', '710', '715', '716', '717', '724', '726', '20', '20', '258', '259', '20', '20', '20', '20', '705', '706', '708', '710', '715', '20', '716', '717', '724', '726', '20', '20', '110', '111', '20', '112', '113', '114', '115', '116', '117', '118', '1806E5F4', '12A', '11C', '20', '20', '20', '705', '706', '708', '710', '715', '716', '717', '724', '726', '20', '20', '258', '259', '20', '20']

vehicle_data = ['8000A00348010600', '8000A00348010600', '8000A00348010600', '8000A00348010600', '8000A00348010500', '8000A00348010600', '4A590000F80C0000', '0420000000004C01', '0000000100000000', '000000071313D900', '0000000051510000', '00EE734F00000200', '00000A0000000000', '0000000001000000', '02870100010E2500', '8000A00348010600', '8000A00348010600', '8000A00348010600', '8000A00348010600', 'B49E000000000000', '0922102703002C03', '8000A00348010600', '161715151414E205', '5000549E579E599E', '5A9E5A9E569E569E', '599E559E00000000', 'B19EB29EB09EB39E', 'B29EB29EB39EB29E', '0000B49E00000000', '0348010600000000', 'C603C40900000000', 'C006C00602053242', '8000A00348010600', '0000000000000000', '0000000000000000', '8000A00348010600', '4A590000F80C0000', '0420000000004C01', '0000000100000000', '000000071313D900', '0000000051510000', '00F3734F00000300', '00000A0000000000', '0000000001000000', '02870100010E2500', '8000A00348010600', '8000A00348010600', '8000A00348010600', '8000A00348010600', '8000A00348010600', '8000A00348010600', '4A590000F80C0000', '0420000000004C01', '0000000100000000', '000000071313D900', '0000000051510000', '00F8734F00000200', '00000A0000000000', '0000000001000000', '02870100010E2500', '8000A00348010600', '8000A00348010500', '0000006464000F02', '8000A00348010600', '8000A00348010600', 'B49E0000AC15FFFF', '0922102703002C03', '161715151414E205', '5000549E599E5A9E', '5B9E5A9E569E569E', '599E559E00000000', 'B29EB19EB19EB19E', 'B29EB39EB39EB39E', '0000B49E00000100', '0348010600000000', 'C603C40900000000', 'C006C00602053242', '8000A00348010600', '8000A00348010600', '0000000000000000', '0000000000000000', '4A590000F80C0000', '0420000000004C01', '0000000100000000', '000000071313D900', '0000000051510000', '00FD734F00000200', '00000A0000000000', '0000000001000000', '02870100010E2500', '8000A00348010600', '8000A00348010600', '8000A00348010600', '8000A00348010600', '8000A00348010600', '8000A00348010600', '8000A00348010600', '4A590000F80C0000', '0420000000004C01', '0000000100000000', '000000071313D900', '0000000051510000', '0001744F00000200', 'FFFF0A0000000300', '0000000001000000', '02870100010E2500', '8000A00348010600', '8000A00348010600', '8000A00348010600', 'B49E0000AC15FFFF', '0922102703002C03', '8000A00348010600', '161715151414E205', '5000549E589E599E', '5A9E5B9E549E569E', '599E549E00000000', 'B19EB19EAF9EB19E', 'B09EB19EB29EB19E', '0000B39E00000000', '0348010600000000', 'C603C40900000000', 'C006C00602053242', '8000A00348010500', '8000A00348010600', '0000000000000000', '0000000000000000', '4A590000F80C0000', '0420000000004C01', '0000000100000000', '000000071313D900', '0000000051510000', '0006744F00000300', '00000A0000000300', '0000000001000000', '02870100010E2500', '8000A00348010600', '8000A00348010600', '8000A00348010600', '8000A00348010500', '8000A00348010600', '8000A00348010600', '4A590000F80C0000', '0420000000004C01', '0000000100000000', '000000071313D900', '0000000051510000', '000B744F00000300', '00000A000000F8FF', '0000000001000000', '02870100010E2500', '8000A00348010600', '8000A00348010600', '0000006464000F02', '8000A00348010600', '8000A00348010600', 'B59E0000AC15FFFF', '0922102703002C03', '161715151414E205', '5100539E589E599E', '5A9E5B9E559E559E', '5A9E559E00000000', 'B29EB19EB09EB29E', 'B19EB29EB39EB39E', '0000B49E00000000', '0348010600000000', 'C603C40900000000', 'C006C00602053242', '8000A00348010600', '8000A00348010600', '0000000000000000', '0000000000000000', '8000A00348010600', '4A590000F80C0000', '0420000000004C01', '0000000100000000', '000000071313D900', '0000000051510000', '0010744F00000300', 'FFFF0A000000F8FF', '0000000001000000', '02870100010E2500', '8000A00348010600', '8000A00348010600', '8000A00348010600', '8000A00348010600', '8000A00348010600', '8000A00348010600', '4A590000F80C0000', '0420000000004C01', '0000000100000000', '000000071313D900', '0000000051510000', '0015744F00000300', '00000A0000000300', '0000000001000000', '02870100010E2500', '8000A00348010600', '8000A00348010600', '8000A00348010600', 'B49E0000AC15FFFF', '0922102703002C03', '8000A00348010600', '161715151414E205', '5000539E589E5A9E', '5B9E5C9E569E569E', '599E559E00000000', 'B19EB29EB09EB19E', 'B19EB19EB39EB29E', '0000B49E00000000', '0348010600000000', 'C603C40900000000', 'C006C00602053242', '8000A00348010600', '8000A00348010600', '0000000000000000', '0000000000000000', '4A590000F80C0000', '0420000000004C01', '0000000100000000', '000000071313D900', '0000000051510000', '0019744F00000300', '00000A0000000100', '0000000001000000', '02870100010E2500', '8000A00348010600', '8000A00348010600', '8000A00348010600', '8000A00348010500', '8000A00348010600', '8000A00348010600', '4A590000F80C0000', '0420000000004C01', '0000000100000000', '000000071313D900', '0000000051510000', '001E744F00000200', 'FFFF0A000000F8FF', '0000000001000000', '02870100010E2500', '8000A00348010600', '0000006464000F02', '8000A00348010600', '8000A00348010600', '8000A00348010600', 'B49E0000AC15FFFF', '0922102703002C03', '161715151414E205', '5000539E589E5A9E', '5A9E5B9E569E569E', '599E559E00000000', 'B19EB19EAF9EB29E', 'B29EB29EB49EB29E', '0000B49E00000000', '0348010600000000', 'C603C40900000000', 'C006C00602053242', '8000A00348010600', '8000A00348010600', '8000A00348010600', '4A590000F80C0000', '0420000000004C01', '0000000100000000', '000000071313D900', '0000000051510000', '0023744F00000200', '00000A0000000300', '0000000001000000', '02870100010E2500', '0000000000000000', '0000000000000000', '8000A00348010600', '8000A00348010600', '8000A00348010600', '8000A00348010600', '8000A00348010600', '8000A00348010600', '4A590000F80C0000', '0420000000004C01', '0000000100000000', '000000071313D900', '0000000051510000', '0028744F00000300', '00000A0000000100', '0000000001000000', '02870100010E2500', '8000A00348010600', '8000A00348010600', '8000A00348010600', 'B49E0000AC15FFFF', '0922102703002C03', '8000A00348010600', '161715151414E205', '5000549E599E5A9E', '5C9E5A9E559E569E', '5A9E549E00000000', 'B19EB09EB19EB19E', 'B09EB29EB49EB49E', '0000B49E00000000', '0348010600000000', 'C603C40900000000', 'C006C00602053242', '8000A00348010600', '8000A00348010600', '4A590000F80C0000', '0420000000004C01', '0000000100000000', '000000071313D900', '0000000051510000', '002D744F00000300', '00000A0000000100', '0000000001000000', '02870100010E2500', '8000A00348010600', '0000000000000000', '0000000000000000', '8000A00348010600', '8000A00348010600', '8000A00348010600', '8000A00348010600', '8000A00348010600', '8000A00348010600', '4A590000F80C0000', '0420000000004C01', '0000000100000000', '000000071313D900', '0000000051510000', '0032744F00000200', '00000A0000000100', '0000000001000000', '02870100010E2500', '0000006464000F02', '8000A00348010600', '8000A00348010600', '8000A00348010600', 'B49E0000AC15FFFF', '0922102703002C03', '161715151414E205', '5000529E589E599E', '5A9E5A9E559E559E', '589E549E00000000', 'B19EB09EB09EB19E', 'B19EB19EB39EB39E', '0000B49E00000000', '0348010600000000', 'C603C40900000000', 'C006C00602053242', '8000A00348010600', '8000A00348010600', '8000A00348010600', '4A590000F80C0000', '0420000000004C01', '0000000100000000', '000000071313D900', '0000000051510000', '0036744F00000300', '00000A0000000100', '0000000001000000', '02870100010E2500', '8000A00348010600', '0000000000000000', '0000000000000000', '8000A00348010600', '8000A00348010600', '8000A00348010600', '8000A00348010600', '8000A00348010600', '4A590000F80C0000', '0420000000004C01', '0000000100000000', '000000071313D900', '0000000051510000', '003B744F00000200', 'FFFF0A000000FAFF', '0000000001000000', '02870100010E2500', '8000A00348010600', '8000A00348010600', '8000A00348010600', 'B39E0000AC15FFFF', '0922102703002C03', '8000A00348010600', '161715151414E205', '4F00519E579E599E', '5A9E5B9E559E559E', '5A9E559E00000000', 'B19EB09EAF9EB19E', 'B19EB29EB39EB39E', '0000B49E00000000', '0348010600000000', 'C603C40900000000', 'C006C00602053242', '8000A00348010600', '8000A00348010600', '4A590000F80C0000', '0420000000004C01', '0000000100000000', '000000071313D900', '0000000051510000', '0040744F00000300', '00000A000000FBFF', '0000000001000000', '8000A00348010600', '02870100010E2500', '0000000000000000', '0000000000000000', '8000A00348010600', '8000A00348010600', '8000A00348010600', '8000A00348010600', '8000A00348010600', '8000A00348010500', '4A590000F80C0000', '0420000000004C01', '0000000100000000', '000000071313D900', '0000000051510000', '0045744F00000200', 'FFFF0A000000FAFF', '0000000001000000', '02870100010E2500', '0000006464000F02', '8000A00348010600', '8000A00348010600', '8000A00348010600', 'B49E0000AC15FFFF', '0922102703002C03', '161715151414E205', '5000539E5A9E5A9E', '5B9E5B9E559E569E', '599E549E00000000', 'B29EB29EB09EB19E', 'B29EB29EB39EB39E', '0000B49E00000000', '0348010600000000', 'C603C40900000000', 'C006C00602053242', '8000A00348010600', '8000A00348010600', '8000A00348010600', '4A590000F80C0000', '0420000000004C01', '0000000100000000', '000000071313D900', '0000000051510000', '004A744F00000200', '00000A0000000100', '0000000001000000', '02870100010E2500', '8000A00348010600', '0000000000000000', '0000000000000000', '8000A00348010600', '8000A00348010600', '8000A00348010600', '8000A00348010500', '8000A00348010600', '4A590000F80C0000', '0420000000004C01', '0000000100000000', '000000071313D900', '0000000051510000', '004E744F00000300', 'FFFF0A0000000100', '0000000001000000', '02870100010E2500', '8000A00348010600', '8000A00348010600', '8000A00348010600', 'B59E0000AC15FFFF', '0922102703002C03', '8000A00348010500', '161715151414E205', '5100529E589E5A9E', '5A9E599E559E559E', '599E549E00000000', 'B19EB09EAF9EB09E', 'B09EB29EB39EB39E', '0000B59E00000000', '0348010500000000', 'C603C40900000000', 'C006C00602053242', '8000A00348010600', '8000A00348010600', '8000A00348010600', '4A590000F80C0000', '0420000000004C01', '0000000100000000', '000000071313D900', '0000000051510000', '0053744F00000300', '00000A000000FBFF', '0000000001000000', '02870100010E2500', '8000A00348010600', '0000000000000000', '0000000000000000', '8000A00348010600', '8000A00348010600', '8000A00348010600', '8000A00348010600', '8000A00348010600', '4A590000F80C0000', '0420000000004C01', '0000000100000000', '000000071313D900', '0000000051510000', '0058744F00000200', '00000A0000000300', '0000000001000000', '02870100010E2500', '0000006464000F02', '8000A00348010600', '8000A00348010600', '8000A00348010600', 'B49E0000AC15FFFF', '0922102703002C03', '161715151414E205', '5000539E579E5B9E', '5B9E5C9E579E559E', '599E539E00000000', 'B19EB19EB19EB29E', 'B29EB29EB29EB29E', '0000B39E00000000', '0348010600000000', 'C603C40900000000', 'C006C00602053242', '8000A00348010600', '8000A00348010500', '8000A00348010600', '4A590000F80C0000', '0420000000004C01', '0000000100000000', '000000071313D900', '0000000051510000', '005D744F00000300', '00000A0000000400', '0000000001000000', '02870100010E2500', '8000A00348010600', '8000A00348010600', '0000000000000000', '0000000000000000', '8000A00348010600', '8000A00348010600', '8000A00348010600', '8000A00348010600', '4A590000F80C0000', '0420000000004C01', '0000000100000000', '000000071313D900', '0000000051510000', '8000A00348010600', '0062744F00000300', '00000A0000000400', '0000000001000000', '02870100010E2500', '8000A00348010600', '8000A00348010600', 'B39E0000AC15FFFF', '0922102703002C03', '8000A00348010600', '161715151414E205', '4F00529E599E599E', '5B9E5B9E559E549E', '589E539E00000000', 'B09EB19EAF9EB19E', 'B19EB29EB29EB39E', '0000B49E00000000', '0348010600000000', 'C603C40900000000', 'C006C00602053242', '8000A00348010600', '8000A00348010500', '8000A00348010500', '4A590000F80C0000', '0420000000004C01', '0000000100000000', '000000071313D900', '0000000051510000', '0066744F00000200', 'FFFF0A000000F9FF', '0000000001000000', '02870100010E2500', '8000A00348010600', '8000A00348010500', '0000000000000000', '0000000000000000', '8000A00348010600', '8000A00348010600']

print(stark_parser(can_ids, vehicle_data))