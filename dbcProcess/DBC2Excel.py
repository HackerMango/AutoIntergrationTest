import copy
import math
import re
import os
import sqlite3


class NeedMsg:
    def __init__(self):
        self.can_Name = None
        self.msg_Name = None


class DataStruct:
    def __init__(self):
        self.TxNode = None
        self.ID_dec = None
        self.MsgName = None
        self.MsgDLC = None
        self.StartByte = None
        self.StartBit = None
        self.SignalName = None
        self.SignalSize = None
        self.factor = None
        self.offset = None
        self.min = None
        self.max = None
        self.DataType = None


def str2hex(string) -> list:
    for iterator_String in range(len(string)):
        string[iterator_String] = hex(int(string[iterator_String]))
    return string


db_Connect = sqlite3.connect(r'..\RearWheel.db')

db = db_Connect.cursor()
db.execute('SELECT MsgName from Msg_Table')
MsgTable_Select_Result = db.fetchall()

db.execute('SELECT Signalname from Signal_Table')
SigTable_Select_Result = db.fetchall()

MsgTableList_Result = []
SigTableList_Result = []

for select in MsgTable_Select_Result:
    MsgTableList_Result.append(select[0])

for select in SigTable_Select_Result:
    SigTableList_Result.append(select[0])

file_dbc = []
for root, dirs, files in os.walk('dbc_File'):
    for file in files:
        if os.path.splitext(file)[1] == '.dbc':
            file_dbc.append(file)

if os.path.exists("Excel_File"):
    print("")
else:
    os.makedirs("Excel_File")

MsgInfo = None

file = open('dbc_File\\' + 'test.txt', 'r', encoding='utf-8')

Need_Msg = []

while 1:
    lines = file.readlines(1)
    str0 = ''.join(lines)
    str1 = str0.replace('\n', '')
    Need_Msg.append(str1)
    if not lines:
        break
file.close()
Need_Msg.pop()
Txt_MsgInfo = []
temp_NeedMsg = NeedMsg()
for i in Need_Msg:
    temp_NeedMsg.can_Name = i.split(" ")[1]
    temp_NeedMsg.msg_Name = i.split(" ")[0]
    Txt_MsgInfo.append(copy.copy(temp_NeedMsg))

for dbc_Name in file_dbc:
    file = open("dbc_File\\" + dbc_Name, 'r', encoding="gbk")

    CANInfo = re.match('^FAW_(?P<CarClassName>\\w+)_(?P<CanName>\\w+)_(?P<ECUName>\\w+)_\\w+_\\w+', dbc_Name)
    CANName = (CANInfo.group('CanName'))
    CARName = CANInfo.group('CarClassName')

    # some val read from dbc
    DBC_Data = []
    testData = []

    # read dbc
    while 1:
        lines = file.readlines(1)
        str0 = ''.join(lines)
        str1 = str0.replace('\t', '')
        str2 = str1.replace('\n', '')
        if str2.startswith(' '):
            list_str = list(str2)
            list_str.pop(0)
            str3 = ''.join(list_str)
            testData.append(str3)
        else:
            testData.append(str2)
        if not lines:
            break
    file.close()

    # split the line to val
    N_Lines = len(testData)
    for i in range(N_Lines):
        temp_DataStruct = DataStruct()
        strLine = testData[i]
        if strLine.startswith('BO_ '):
            MsgInfo = re.search('^BO_ (?P<ID_dec>\\w+) (?P<MsgName>\\w+) *: (?P<DLC>\\w+) (?P<TxNode>\\w+)', strLine)
        elif strLine.startswith('SG_ '):
            SignalInfo = re.search(
                '^SG_ (?P<SignalName>\\w+) : (?P<startBit>\\d+)\\|(?P<signalSize>\\d+)@(?P<is_little_endian>\\d+)'
                '(?P<is_signed>[+|-]) \\((?P<factor>[\\d.+-eE]+),(?P<offset>[\\d.+-eE]+)\\) '
                '\\[(?P<min>[\\d.+-eE]+)\\|(?P<max>[\\d.+-eE]+)] \"(?P<unit>.*)\" (?P<RxNodeList>.*)',
                strLine)
            if SignalInfo.group('is_little_endian') == '1' and SignalInfo.group('is_signed') == '+':
                temp_DataStruct.TxNode = MsgInfo.group('TxNode')
                temp_DataStruct.ID_dec = MsgInfo.group('ID_dec')
                temp_DataStruct.MsgName = MsgInfo.group('MsgName')
                temp_DataStruct.MsgDLC = MsgInfo.group('DLC')
                temp_DataStruct.StartByte = math.floor(int(SignalInfo.group('startBit')) / 8)
                temp_DataStruct.StartBit = int(SignalInfo.group('startBit')) % 8
                temp_DataStruct.SignalName = SignalInfo.group('SignalName')
                temp_DataStruct.SignalSize = SignalInfo.group('signalSize')
                temp_DataStruct.factor = SignalInfo.group('factor')
                temp_DataStruct.offset = SignalInfo.group('offset')
                temp_DataStruct.min = SignalInfo.group('min')
                temp_DataStruct.max = SignalInfo.group('max')
                DBC_Data.append(temp_DataStruct)
        else:
            continue

    # filter out message what we need from dbc
    Msg_index = []
    i = 0
    while i < len(DBC_Data):
        if i != 0 and len(Msg_index) > 0:
            if Msg_index[-1] != i - 1:
                while DBC_Data[i].MsgName == DBC_Data[i - 1].MsgName:
                    i = i + 1
                    if i >= len(DBC_Data):
                        break
        elif i != 0 and len(Msg_index) == 0:
            while DBC_Data[i].MsgName == DBC_Data[i - 1].MsgName:
                i = i + 1
                if i >= len(DBC_Data):
                    break
        for j in range(len(Txt_MsgInfo)):
            if i >= len(DBC_Data):
                break
            if DBC_Data[i].MsgName == Txt_MsgInfo[j].msg_Name and CANName == Txt_MsgInfo[j].can_Name:
                Msg_index.append(i)
        if i >= len(DBC_Data):
            break
        i = i + 1
        # if Record_MsgName[i] == 'SVB1_1':
        #     Msg_index.append(i)
        # if Record_MsgName[i] == 'ABS_1':
        #     Msg_index.append(i)
        # if Record_MsgName[i] == 'ABS_2':
        #     Msg_index.append(i)
        # if Record_MsgName[i] == 'HCU_2_12':
        #     Msg_index.append(i)
        # if Record_MsgName[i] == 'HCU_2_4':
        #     Msg_index.append(i)
        # if Record_MsgName[i] == 'HCU_2_2':
        #     Msg_index.append(i)
        # if Record_MsgName[i] == 'HCU_2_7':
        #     Msg_index.append(i)
        # if Record_MsgName[i] == 'ESC_3_1':
        #     Msg_index.append(i)

    # update msg send`s type, cycle times and signal`s invalid value
    CycleTime = []
    CycleTime_ID_dec = []
    SendType = []
    SendType_ID_dec = []
    InvalidValue = []
    InvalidValue_ID_dec = []
    InvalidValue_SignalName = []

    for i in range(len(testData)):
        strLine = testData[i]
        if strLine.startswith('BA_ '):
            BAInfo = re.match('^BA_ +\"(?P<BA_Type>[A-Za-z\\d]+)+\" +(.+)', strLine)
            if BAInfo.group('BA_Type') == 'GenMsgCycleTime':
                CycleTimeInfo = re.match('^BA_ \"GenMsgCycleTime\" BO_ (?P<ID_dec>\\w+) (?P<CycleTime>.+);', strLine)
                CycleTime.append(CycleTimeInfo.group('CycleTime'))
                CycleTime_ID_dec.append(CycleTimeInfo.group('ID_dec'))
            if BAInfo.group('BA_Type') == 'GenMsgSendType':
                SendTypeInfo = re.match('^BA_ \"GenMsgSendType\" BO_ (?P<ID_dec>\\w+) (?P<SendType>.+);', strLine)
                SendType.append(SendTypeInfo.group('SendType'))
                SendType_ID_dec.append(SendTypeInfo.group('ID_dec'))
            if BAInfo.group('BA_Type') == 'GenSigInvalidValue':
                InvalidValueInfo = re.match(
                    '^BA_ \"GenSigInvalidValue\" SG_ (?P<ID_dec>\\w+) (?P<SignalName>\\w+) (?P<InvalidValue>.+);',
                    strLine)
                InvalidValue.append(InvalidValueInfo.group('InvalidValue'))
                InvalidValue_ID_dec.append(InvalidValueInfo.group('ID_dec'))
                InvalidValue_SignalName.append(InvalidValueInfo.group('SignalName'))
        else:
            continue

    # define the message which will be writing to excel
    Excel_Data = []

    # filter out message
    for i in range(len(Msg_index)):
        Excel_Data.append(DBC_Data[Msg_index[i]])

    for i in range(len(SendType)):
        if SendType[i] == '5':
            SendType[i] = 'Cyclic + Change'
        if SendType[i] == '0':
            SendType[i] = 'Cyclic'
        if SendType[i] == '2':
            SendType = 'BAF'
        if SendType[i] == '8':
            SendType[i] = 'DualCycle'
        if SendType[i] == '10':
            SendType[i] = 'None'
        if SendType[i] == '9':
            SendType[i] = 'OnChange'
        if SendType[i] == '1':
            SendType[i] = 'Spontaneous'

    for index in range(len(Excel_Data)):
        Excel_Data[index].ID_dec = hex(int(Excel_Data[index].ID_dec))
    str2hex(InvalidValue_ID_dec)
    str2hex(SendType_ID_dec)
    str2hex(CycleTime_ID_dec)
    str2hex(InvalidValue)

    for i in range(len(Excel_Data)):
        if Excel_Data[i].factor == '1':
            if float(Excel_Data[i].min) < 0:
                if int(Excel_Data[i].SignalSize) <= 8:
                    Excel_Data[i].DataType = 'int8_T'
                elif int(Excel_Data[i].SignalSize) <= 16:
                    Excel_Data[i].DataType = 'int16_T'
                elif int(Excel_Data[i].SignalSize) <= 32:
                    Excel_Data[i].DataType = 'int32_T'
                elif int(Excel_Data[i].SignalSize) <= 64:
                    Excel_Data[i].DataType = 'int64_T'
                else:
                    print('No this DataType')
            else:
                if int(Excel_Data[i].SignalSize) <= 8:
                    Excel_Data[i].DataType = 'uint8_T'
                elif int(Excel_Data[i].SignalSize) <= 16:
                    Excel_Data[i].DataType = 'uint16_T'
                elif int(Excel_Data[i].SignalSize) <= 32:
                    Excel_Data[i].DataType = 'uint32_T'
                elif int(Excel_Data[i].SignalSize) <= 64:
                    Excel_Data[i].DataType = 'uint64_T'
                else:
                    print('No this DataType')
        else:
            Excel_Data[i].DataType = 'real32_T'

    Unique_MsgName = []
    temp = ''
    for i in range(len(Excel_Data)):
        if temp != Excel_Data[i].MsgName:
            Unique_MsgName.append(i)
            temp = Excel_Data[i].MsgName

    for i in Unique_MsgName:
        flag = 1
        for msgName_It in range(len(Excel_Data)):
            temp = Excel_Data[msgName_It].MsgName
            temp1 = Excel_Data[msgName_It].SignalName
            if Excel_Data[i].MsgName == Excel_Data[msgName_It].MsgName:
                if re.findall('livecounter', Excel_Data[msgName_It].SignalName, re.IGNORECASE) or \
                        re.findall('checksum', Excel_Data[msgName_It].SignalName, re.IGNORECASE):
                    flag = 1
                    break
                else:
                    flag = 0
        time = 0
        for j in range(len(CycleTime_ID_dec)):
            if CycleTime_ID_dec[j] == Excel_Data[i].ID_dec:
                time = CycleTime[j]

        if Excel_Data[i].MsgName not in MsgTableList_Result:
            db.execute('INSERT into Msg_Table (MsgName, CHeckMiss, CycleTime, CheckLCCS, MsgID, DLC, CANName) '
                       'VALUES (?,?,?,?,?,?,?)',
                       (Excel_Data[i].MsgName, flag, time, flag, int(Excel_Data[i].ID_dec, 16),
                        Excel_Data[i].MsgDLC, CANName))
    db_Connect.commit()

    for i in range(len(Excel_Data)):
        if Excel_Data[i].SignalName not in SigTableList_Result:
            db.execute("SELECT Msg_TableID from Msg_Table where MsgName == '%s'" % Excel_Data[i].MsgName)
            MsgTable_ID = db.fetchall()
            db.execute('INSERT into Signal_Table (Msg_TableID, StartByte, StartBit, SignalLength, '
                       'SignalName, DataType, SignalFactor, SignalOffset) '
                       'VALUES (?,?,?,?,?,?,?,?)',
                       (MsgTable_ID[0][0], Excel_Data[i].StartByte,
                        Excel_Data[i].StartBit, Excel_Data[i].SignalSize,
                        Excel_Data[i].SignalName, Excel_Data[i].DataType, Excel_Data[i].factor, Excel_Data[i].offset))
db_Connect.commit()
