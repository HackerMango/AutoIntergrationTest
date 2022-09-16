import re
import xlrd
import sqlite3

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


db_Connection = sqlite3.connect(r'RearWheel.db')
db_Cursor = db_Connection.cursor()
db_Cursor.execute('SELECT * from Msg_Table')
get_Data = db_Cursor.fetchall()
msg_Info = [list(x) for x in get_Data]

db_Cursor.execute('SELECT * from Signal_Table')
get_Data = db_Cursor.fetchall()
sig_Info = [list(x) for x in get_Data]

# Vs Code Read File Path
# Execl_Book = xlrd.open_workbook("IntergrationTestCase\Data\Decy_Test.xlsx")

# Pycharm Read File Path
Execl_Book = xlrd.open_workbook("Decy_Test - 副本.xlsx")
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



for fun in Test_Array:

    db_Cursor.execute('SELECT CaseName from Case_Table')
    case_Info = [i for x in db_Cursor.fetchall() for i in x]

    db_Cursor.execute('SELECT StepName from Step_Table')
    step_Info = [i for x in db_Cursor.fetchall() for i in x]

    for index in range(len(fun.TestFunction_CaseName)):
        if fun.TestFunction_CaseName[index] not in case_Info:
            db_Cursor.execute('INSERT into Case_Table (CaseName, Function_Name) VALUES (?, ?)', (fun.TestFunction_CaseName[index], fun.TestFunction_Name))

        for i in range(len(fun.Case_Level)):
            if (fun.TestFunction_CaseName[index] + '_{0}'.format(i)) not in step_Info:
                db_Cursor.execute('INSERT into Step_Table (StepName, CaseName, StepCheck) VALUES (?, ?, ?)', (fun.TestFunction_CaseName[index] + '_{0}'.format(i), fun.TestFunction_CaseName[index], 0))
            # db_Cursor.execute('INSERT into TestInfo_Table ()')
            for step in fun.Case_TestStep[index][i]:
                sent_Info = re.match('^(?P<signalname>\w+)=(?P<Value>\w+)', step)
                db_Cursor.execute('INSERT into TxInfo_Table (TxSignalName, TxSignalValue, StepName) VALUES (?, ?, ?)',
                                  (sent_Info.group('signalname'), sent_Info.group('Value'), fun.TestFunction_CaseName[index] + '_{0}'.format(i)))
            for result in fun.Case_TestStep[index][i]:
                recieve_Info = re.match('^(?P<signalname>\w+)=(?P<Value>\w+)', result)
                db_Cursor.execute('INSERT into RxInfo_Table (RxSignalName, RxSignalValue, StepName) VALUES (?, ?, ?)',
                                  (recieve_Info.group('signalname'), recieve_Info.group('Value'), fun.TestFunction_CaseName[index] + '_{0}'.format(i)))

db_Connection.commit()
print("asd")