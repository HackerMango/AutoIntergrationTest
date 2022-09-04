import re
import xlrd
import pandas as pd


class TestCase():
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


# Vs Code Read File Path
# Execl_Book = xlrd.open_workbook("IntergrationTestCase\Data\Decy_Test.xlsx")

# Pycharm Read File Path
Execl_Book = xlrd.open_workbook("Data/Decy_Test.xlsx")
Excel_Sheet = Execl_Book.sheets()
Test_Case_Data = []

for i in range(10):
    Test_Case_Data.append(Excel_Sheet[0].col_values(i)[13:])

Test_Array = []
RearSteer_TestCase_Array = []
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
                    if Test_Case_Data[1][i] == "用例" or i >= len(Test_Case_Data[0]) - 1:
                        RearSteer_TestCase.Case_Level.append(Case_Level)
                        RearSteer_TestCase.Case_TestStep.append(Case_TestStep)
                        RearSteer_TestCase.Case_DesiredResult.append(Case_DesiredResult)
                        RearSteer_TestCase.Case_LevelFlag.append(Case_LevelFlag)
                        break

            if Test_Case_Data[1][i] == "功能\nFunction" or i >= len(Test_Case_Data[0]) - 1:
                Test_Array.append(RearSteer_TestCase)
                break

SignalName = re.match('^(?P<signalname>\w+)=(?P<Value>\w+)', Test_Array[0].Case_TestStep[0][0])
print(SignalName.group("signalname"))
