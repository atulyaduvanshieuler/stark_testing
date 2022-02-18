import codecs

with codecs.open("CAN1_log_160222_Test_Vehicle.trc", "r", "UTF8") as inputFile:
    inputFile=inputFile.readlines()
can_ids=[]
can_ids_set=set()
counter=0
can_data=[]

#print(inputFile[14])
for line in inputFile[14:]:
    #print(line)
    req=[]
    req=[s for s in line.split(" ") if s!='']
    #print(req)
    can_ids.append(req[3])
    can_ids_set.add(req[3])
    can_data.append(req[5:-1])
#print(can_ids)
can_ids_set=list(can_ids_set)
can_ids_set.sort()
#print(can_data)
#print(can_ids_set)
new_can_ids_set=[]
for s in can_ids_set:
    if s[0]=="0":
        for i in range(len(s)):
            if s[i]!="0":
                new_can_ids_set.append(s[i:])
                break
    else:
        new_can_ids_set.append(s)
#print(new_can_ids_set)

cdata=[]
for c in can_data:
    cdata.append("".join(c))
#print(cdata)
new_can_ids=[]
for s in can_ids:
    if s[0]=="0":
        for i in range(len(s)):
            if s[i]!="0":
                new_can_ids.append(s[i:])
                break
    else:
        new_can_ids.append(s)
#print(new_can_ids)

neww=[]
neww=list(zip(new_can_ids, cdata))
#print(neww)


#110-118
#11A-11E
#705,706,708,710,715,716,717,724,726
#
#Not included 20,12a,259,725,1806E5F4
#728 not in can1 but in can2    


#with codecs.open("CAN2_LOG_160222_TestVehicle.trc", "r", "UTF8") as inputFile:
#    inputFile=inputFile.readlines()
#can2_ids=[]
#can2_ids_set=set()
#counter=0
#can2_data=[]
#
##print(inputFile[14])
#for line in inputFile[14:]:
#    #print(line)
#    req=[]
#    req=[s for s in line.split(" ") if s!='']
#    #print(req)
#    can2_ids.append(req[3])
#    can2_ids_set.add(req[3])
#    can2_data.append(req[5:-1])
##print(can2_ids)
#can2_ids_set=list(can2_ids_set)
#can2_ids_set.sort()
##print(can2_data)
##print(can2_ids_set)
#new_can2_ids_set=[]
#for s in can2_ids_set:
#    if s[0]=="0":
#        for i in range(len(s)):
#            if s[i]!="0":
#                new_can2_ids_set.append(s[i:])
#                break
#    else:
#        new_can2_ids_set.append(s)
#print(new_can2_ids_set)



