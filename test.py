import re
import xlrd


class TestCase:
    def __init__(self):
        self.TestFunction_Name = ""
        self.TestFunction_CaseName = []
        self.Case_Level = []
        self.Case_LevelFlag = []
        self.Case_TestStep = []
        self.Case_DesiredResult = []

    def clearData(self):
        self.TestFunction_Name = ""
        self.TestFunction_CaseName = []
        self.Case_Level = []
        self.Case_TestStep = []
        self.Case_DesiredResult = []


class MsgStruct:
    def __init__(self):
        self.msgName = ""
        self.Id = int(0)
        self.CycleTime = int(0)
        self.HasLCCK = ""


class SignalStruct:
    def __inti__(self):
        self.msgName = ""
        self.startByte = int(0)
        self.startBit = int(0)
        self.startLength = int(0)
        self.signalName = ""
        self.factor = 0
        self.offset = 0
        self.datatype = ""

# Vs Code Read File Path
# Execl_Book = xlrd.open_workbook("IntergrationTestCase\Data\Decy_Test.xlsx")

# Pycharm Read File Path
Execl_Book = xlrd.open_workbook("IntergrationTestCase\AutoIntergrationTest\Data\Decy_Test - 副本.xlsx")
Excel_Sheet = Execl_Book.sheets()
Test_Case_Data = []

for i in range(10):
    Test_Case_Data.append(Excel_Sheet[0].col_values(i)[13:])

Test_Array = []
for i in range(len(Test_Case_Data[0])):
    RearSteer_TestCase = TestCase()
    if Test_Case_Data[1][i] == "功能\nFunction":
        RearSteer_TestCase.TestFunction_Name = Test_Case_Data[0][i]
        i = i + 1
        while (1):
            Case_Level = []
            Case_TestStep = []
            Case_DesiredResult = []
            Case_LevelFlag = []
            if Test_Case_Data[1][i] == "用例":
                RearSteer_TestCase.TestFunction_CaseName.append(Test_Case_Data[0][i])
                i = i + 1
                while (1):
                    Case_Level.append(Test_Case_Data[3][i])
                    Case_TestStep.append(Test_Case_Data[4][i].split(sep="\n"))
                    Case_DesiredResult.append(Test_Case_Data[5][i].split(sep='\n'))
                    Case_LevelFlag.append(int(0))
                    i = i + 1
                    if Test_Case_Data[1][i] == "用例" or i >= len(Test_Case_Data[0]) - 1 or Test_Case_Data[1][
                        i] == "功能\nFunction":
                        RearSteer_TestCase.Case_Level.append(Case_Level)
                        RearSteer_TestCase.Case_TestStep.append(Case_TestStep)
                        RearSteer_TestCase.Case_DesiredResult.append(Case_DesiredResult)
                        RearSteer_TestCase.Case_LevelFlag.append(Case_LevelFlag)
                        break

            if Test_Case_Data[1][i] == "功能\nFunction" or i >= len(Test_Case_Data[0]) - 1:
                Test_Array.append(RearSteer_TestCase)
                break

# Execl_Book = xlrd.open_workbook("dbcProcess/Excel_File/ADAS_Msg.xlsx")
Execl_Book = xlrd.open_workbook("IntergrationTestCase\AutoIntergrationTest\dbcProcess\Excel_File\ADAS_Msg.xlsx")
Excel_Sheet = Execl_Book.sheets()



msgArray = []
signalArray = []

sheet1_Id = Excel_Sheet[0].col_values(0)[1:]
sheet1_MsgName = Excel_Sheet[0].col_values(3)[1:]
sheet1_CycleTime = Excel_Sheet[0].col_values(5)[1:]
sheet1_HasLCCK = Excel_Sheet[0].col_values(7)[1:]

sheet2_MsgName = Excel_Sheet[1].col_values(0)[1:]
sheet2_StartByte = Excel_Sheet[1].col_values(2)[1:]
sheet2_StartBit = Excel_Sheet[1].col_values(3)[1:]
sheet2_StartLength = Excel_Sheet[1].col_values(4)[1:]
sheet2_SignalName = Excel_Sheet[1].col_values(5)[1:]
sheet2_DataType = Excel_Sheet[1].col_values(10)[1:]
sheet2_Factor = Excel_Sheet[1].col_values(11)[1:]
sheet2_Offset = Excel_Sheet[1].col_values(12)[1:]

# # read Msg info to msgArray
# for i in range(len(Excel_Sheet[0].col_values(0))):
#     if i == 0:
#         continue
#     else:
#         msgStruct = MsgStruct()
#         msgStruct.msgName = Excel_Sheet[0].row_values(i)[3]
#         msgStruct.Id = Excel_Sheet[0].row_values(i)[0]
#         msgStruct.CycleTime = Excel_Sheet[0].row_values(i)[5]
#         msgStruct.HasLCCK = Excel_Sheet[0].row_values(i)[7]
#     msgArray.append(msgStruct)

# # read signal info to signalArray
# for i in range(len(Excel_Sheet[1].col_values(0))):
#     if i == 0:
#         continue
#     else:
#         signalStruct = SignalStruct()
#         signalStruct.msgName = Excel_Sheet[1].row_values(i)[0]
#         signalStruct.startByte = Excel_Sheet[1].row_values(i)[2]
#         signalStruct.startBit = Excel_Sheet[1].row_values(i)[3]
#         signalStruct.startLength = Excel_Sheet[1].row_values(i)[4]
#         signalStruct.signalName = Excel_Sheet[1].row_values(i)[5]
#         signalStruct.factor = Excel_Sheet[1].row_values(i)[11]
#         signalStruct.offset = Excel_Sheet[1].row_values(i)[12]
#         signalStruct.datatype = Excel_Sheet[1].row_values(i)[10]
#     signalArray.append(signalStruct)

file = open(r"IntergrationTestCase\AutoIntergrationTest\wreiteFile\IntergrationData.cpp", 'r', encoding="gbk")
IntergrationData_Cpp_Data = []
while 1:
    line = file.readlines(1)
    if not line:
        break
    else:
        IntergrationData_Cpp_Data.append(''.join(line))
file.close()

need_Msg = []

file = open(r"IntergrationTestCase\AutoIntergrationTest\wreiteFile\IntergrationData.cpp", 'w', encoding="gbk")
# write to c or h file
for linenum in range(len(IntergrationData_Cpp_Data)):
    if IntergrationData_Cpp_Data[linenum] != "\nvoid MsgProcess::FillMsgData(){\n":
        file.write(IntergrationData_Cpp_Data[linenum])
    else:
        file.write(IntergrationData_Cpp_Data[linenum])
        for function in Test_Array:
            file.write("\ttestCase_Struct.test_Function_Name = \"{0}\";\n".format(function.TestFunction_Name))
            for cIndex in range(len(function.TestFunction_CaseName)):
                file.write("\ttestCase_Struct.test_Function_Name.push_back(\"{0}\");\n".format(function.TestFunction_CaseName[cIndex]))
                for x in range(len(function.Case_TestStep[cIndex])):
                    file.write("\ttestCase_Struct.case_LevelFlag.push_back(0);\n")
                    file.write("\ttestCase_Struct.case_Level.push_back(\"{0}\");\n".format(function.TestFunction_CaseName[cIndex][x]))
                    for j in range(len(function.Case_TestStep[cIndex][x])):
                        tx_Signal = re.match('^(?P<signalname>\w+)=(?P<Value>\w+)', function.Case_TestStep[cIndex][x][j])
                        if tx_Signal.group("signalname") in sheet2_SignalName:
                            file.write("\tsignalInfo.signal_Name = \"{0}\";\n".format(tx_Signal.group("signalname")))

                            temp_Index = sheet2_SignalName.index(tx_Signal.group("signalname"))
                            # get signal info
                            msgName = sheet2_MsgName[temp_Index]
                            file.write("\tsignalInfo.msg_Name = \"{0}\";\n".format(msgName))
                            file.write("\tmsgData.msg_Name = \"{0}\";\n".format(msgName))

                            startByte = sheet2_StartByte[temp_Index]
                            file.write("\tsignalInfo.signal_StartByte = {0};\n".format(startByte))

                            startBit = sheet2_StartBit[temp_Index]
                            file.write("\tsignalInfo.signal_StartBit = {0};\n".format(startBit))

                            signalLength = sheet2_StartLength[temp_Index]
                            file.write("\tsignalInfo.signal_Length = {0};\n".format(signalLength))

                            

                            # Msg_Info = sheet2_SignalName[temp_Index]
                            dataType = sheet2_DataType[temp_Index]
                            factor = sheet2_Factor[temp_Index]
                            file.write("\tsignalInfo.signal_Factor = {0};\n".format(factor))

                            offset = sheet2_Offset[temp_Index]
                            file.write("\tsignalInfo.signal_Offset = {0};\n".format(offset))

                            msgId = sheet1_Id[sheet1_MsgName.index(msgName)]
                            file.write("\tsignalInfo.id = {0};\n".format(msgId))
                            file.write("\tmsgData.id = {0};\n".format(msgId))

                            msgCycleTime = sheet1_CycleTime[sheet1_MsgName.index(msgName)]
                            file.write("\tmsgData.cycle_Time = {0};\n".format(msgCycleTime))

                            msgHasLCCS = sheet1_HasLCCK[sheet1_MsgName.index(msgName)]
                            # file.write("\tmsgData.")
                            
                            file.write("\ttestCase_Struct.case_TestStep.push_back(signalInfo);\n")
                            file.write("\ttestCase_Struct.Case_TestValue.push_back({0});\n".format(tx_Signal.group("Value")))
                            file.write("\n\n")
                        else:
                            print("No Such SignalName\n")

                for x1 in range(len(function.Case_DesiredResult[cIndex])):
                    for k in range(len(function.Case_DesiredResult[cIndex][x1])):
                        rx_Signal = re.match('^(?P<signalname>\w+)=(?P<Value>\w+)', function.Case_DesiredResult[cIndex][x][k])
                        if rx_Signal.group("signalname") in sheet2_SignalName:
                            temp_Index = sheet2_SignalName.index(rx_Signal.group("signalname"))
                            # get signal info
                            msgName = sheet2_MsgName[temp_Index]
                            startByte = sheet2_StartByte[temp_Index]
                            startBit = sheet2_StartBit[temp_Index]
                            signalLength = sheet2_StartLength[temp_Index]
                            # Msg_Info = sheet2_SignalName[temp_Index]
                            dataType = sheet2_DataType[temp_Index]
                            factor = sheet2_Factor[temp_Index]
                            offset = sheet2_Offset[temp_Index]
                            msgId = sheet1_Id[sheet1_MsgName.index(msgName)]
                            msgCycleTime = sheet1_CycleTime[sheet1_MsgName.index(msgName)]
                            msgHasLCCS = sheet1_HasLCCK[sheet1_MsgName.index(msgName)]
                        else:
                            print("No Such SignalName\n")


print("asdf")
# SignalName = re.match('^(?P<signalname>\w+)=(?P<Value>\w+)', Test_Array[0].Case_TestStep[0][0])
# print(SignalName.group("signalname"))
