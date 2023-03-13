import math
import re
import os
import sqlite3


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

# sql = '''
#         INSERT
#         '''

target_DbcFile = "FAW_E001B_Backbone_PDCF_CANDBC_V0.8.dbc"

file_dbc = []
for root, dirs, files in os.walk('dbc_File'):
    for file in files:
        if os.path.splitext(file)[1] == '.dbc' and file == target_DbcFile:
            file_dbc.append(file)

if os.path.exists("Excel_File"):
    print("")
else:
    os.makedirs("Excel_File")

MsgInfo = None

for dbc_Name in file_dbc:
    file = open("dbc_File\\" + dbc_Name, 'r', encoding="gbk")

    CANInfo = re.match('^\\w+_\\w+_\\w+_(?P<CanName>\\w+)_\\w+', dbc_Name)
    CANName = CANInfo.group('CanName')

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

    file = open('dbc_File\\' + 'CDS_Chassis1.txt', 'r', encoding='utf-8')
    Need_Msg = []
    while 1:
        lines = file.readlines(1)
        str0 = ''.join(lines)
        str1 = str0.replace('\n', '')
        Need_Msg.append(str1)
        if not lines:
            break
    file.close()

    # filter out message what we need from dbc
    Msg_index = []
    for i in range(len(DBC_Data)):
        for j in range(len(Need_Msg)):
            if DBC_Data[i].MsgName == Need_Msg[j]:
                Msg_index.append(i)
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

    # str2hex(Excel_Data.ID_dec)
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
            db.execute('INSERT into Msg_Table (MsgName, CHeckMiss, CycleTime, CheckLCCS, MsgID, DLC) '
                       'VALUES (?,?,?,?,?,?)',
                       (Excel_Data[i].MsgName, flag, time, flag, int(Excel_Data[i].ID_dec, 16), Excel_Data[i].MsgDLC))

    for i in range(len(Excel_Data)):
        if Excel_Data[i].SignalName not in SigTableList_Result:
            db.execute('INSERT into Signal_Table (SgMsgName, StartByte, StartBit, SignalLength, '
                       'SignalName, DataType, SignalFactor, SignalOffset) '
                       'VALUES (?,?,?,?,?,?,?,?)',
                       (Excel_Data[i].MsgName, Excel_Data[i].StartByte,
                        Excel_Data[i].StartBit, Excel_Data[i].SignalSize,
                        Excel_Data[i].SignalName, Excel_Data[i].DataType, Excel_Data[i].factor, Excel_Data[i].offset))
    # write to Excel
    # xl = xlsxwriter.Workbook(r'Excel_File\\{0}_Msg.xlsx'.format(CANName))
    # sheet_1 = xl.add_worksheet('sheet1')
    # sheet_2 = xl.add_worksheet('sheet2')
    #
    # sheet_1.write_string(0, 0, 'ID')
    # sheet_1.write_string(0, 1, 'SendNode')
    # sheet_1.write_string(0, 2, 'AffectNode')
    # sheet_1.write_string(0, 3, 'MsgName')
    # sheet_1.write_string(0, 4, 'CheckMsgMiss')
    # sheet_1.write_string(0, 5, 'CycleTime')
    # sheet_1.write_string(0, 6, 'SendType')
    # sheet_1.write_string(0, 7, 'HasLCCS')
    # sheet_1.write_string(0, 8, 'CheckCSLC')
    #
    # sheet1_Count = 1
    # strLine = ''
    # for i in Unique_MsgName:
    #     sheet_1.write_string(sheet1_Count, 0, Excel_ID_dec[i])
    #     sheet_1.write_string(sheet1_Count, 1, Excel_TxNode[i])
    #     sheet_1.write_string(sheet1_Count, 2, '')
    #     strLine = Excel_MsgName[i]
    #     sheet_1.write_string(sheet1_Count, 3, strLine)
    #     for j in range(len(CycleTime_ID_dec)):
    #         if CycleTime_ID_dec[j] == Excel_ID_dec[i]:
    #             sheet_1.write_string(sheet1_Count, 5, CycleTime[j])
    #     for k in range(len(SendType_ID_dec)):
    #         if SendType_ID_dec[k] == Excel_ID_dec[i]:
    #             sheet_1.write_string(sheet1_Count, 6, SendType[k])
    #     for l in range(len(Excel_MsgName)):
    #         temp = Excel_MsgName[l]
    #         temp1 = Excel_SignalName[l]
    #         if Excel_MsgName[i] == Excel_MsgName[l]:
    #             if re.findall('livecounter', Excel_SignalName[l], re.IGNORECASE) or
    #             re.findall('checksum', Excel_SignalName[l], re.IGNORECASE):
    #                 sheet_1.write_string(sheet1_Count, 4, 'True')
    #                 sheet_1.write_string(sheet1_Count, 7, 'True')
    #                 sheet_1.write_string(sheet1_Count, 8, 'True')
    #                 break
    #             else:
    #                 sheet_1.write_string(sheet1_Count, 4, 'False')
    #                 sheet_1.write_string(sheet1_Count, 7, 'False')
    #                 sheet_1.write_string(sheet1_Count, 8, 'False')
    #
    #     sheet1_Count = sheet1_Count + 1
    #
    # sheet_2.write_string(0, 0, 'MsgName')
    # sheet_2.write_string(0, 1, 'CycleTime')
    # sheet_2.write_string(0, 2, 'StartByte')
    # sheet_2.write_string(0, 3, 'StartBit')
    # sheet_2.write_string(0, 4, 'SignalLength')
    # sheet_2.write_string(0, 5, 'SignalName')
    # sheet_2.write_string(0, 6, 'CheckInvalid')
    # sheet_2.write_string(0, 7, 'InvalidTime')
    # sheet_2.write_string(0, 8, 'InvalidValue')
    # sheet_2.write_string(0, 9, 'NeedByApp')
    # sheet_2.write_string(0, 10, 'DataType')
    # sheet_2.write_string(0, 11, 'factor')
    # sheet_2.write_string(0, 12, 'offset')
    # sheet_2.write_string(0, 13, 'RangeCheck')
    # sheet_2.write_string(0, 14, 'Min')
    # sheet_2.write_string(0, 15, 'Max')
    # sheet_2.write_string(0, 16, 'CheckFailedValue')
    #
    # sheet2_Count = 1
    # for i in range(len(Excel_MsgName)):
    #     # if re.findall('livecounter', Excel_SignalName[i], re.IGNORECASE) or
    #     re.findall('checksum', Excel_SignalName[i], re.IGNORECASE):
    #     if re.findall('checksum', Excel_SignalName[i], re.IGNORECASE):
    #         continue
    #     sheet_2.write_string(sheet2_Count, 0, Excel_MsgName[i])
    #     for j in range(len(CycleTime_ID_dec)):
    #         if Excel_ID_dec[i] == CycleTime_ID_dec[j]:
    #             sheet_2.write_string(sheet2_Count, 1, CycleTime[j])
    #     sheet_2.write_string(sheet2_Count, 2, str(Excel_StartByte[i]))
    #     sheet_2.write_string(sheet2_Count, 3, str((Excel_StartBit[i])))
    #     sheet_2.write_string(sheet2_Count, 4, str(Excel_SignalSize[i]))
    #     sheet_2.write_string(sheet2_Count, 5, Excel_SignalName[i])
    #     sheet_2.write_string(sheet2_Count, 6, '')
    #     sheet_2.write_string(sheet2_Count, 7, '')
    #     for k in range(len(InvalidValue_ID_dec)):
    #         if Excel_ID_dec[i] == InvalidValue_ID_dec[k]:
    #             sheet_2.write_string(sheet2_Count, 8, InvalidValue[k])
    #     sheet_2.write_string(sheet2_Count, 9, 'true')
    #     sheet_2.write_string(sheet2_Count, 10, Excel_DataType[i])
    #     sheet_2.write_string(sheet2_Count, 11, Excel_factor[i])
    #     sheet_2.write_string(sheet2_Count, 12, Excel_offset[i])
    #     sheet_2.write_string(sheet2_Count, 13, '')
    #     sheet_2.write_string(sheet2_Count, 14, Excel_min[i])
    #     sheet_2.write_string(sheet2_Count, 15, Excel_max[i])
    #     sheet_2.write_string(sheet2_Count, 16, '')
    #     sheet2_Count = sheet2_Count + 1
    # xl.close()

db_Connect.commit()
