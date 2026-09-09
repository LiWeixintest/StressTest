from asyncio import all_tasks
# from TSMasterApi import *
from TSMasterApi.TSMasterAPI import *
from TSMasterApi.TSStruct import *
import time
import threading
import cantools

from libs.can.tsmaster.TSMasterApi import tsapp_set_vendor_detect_preferences


class TsmasterInterface:
    def __init__(self,device_type, device_index, chn_index = 0):
        self._sendMsgsList = []
        self._receiveMsgsList = []

    def msgToTransmitObj(self, can_id, can_data):
        pass

    #发送消息 
    # 消息ID can_id: 0x3B2 或者十进制 946; 
    # 消息内容 can_data: "44 00 00 12 E6 00 04 06"; 
    # 发送次数 msgCnt: -1为一直发送
    def sendMsg(self,can_id,can_data,msg_cnt = 1):
        can_id = convert16To10(can_id)
        msgObj = self.msgToTransmitObj(can_id,can_data)
        self._sendMsgsList.append({'msgObj':msgObj,'msgCnt':msg_cnt})

    def transmitMsg(self):
        while True:
            for msgHash in self._sendMsgsList:
                msgObj = msgHash['msgObj']
                msgCnt = msgHash['msgCnt']
                d = " ".join([str(ed) for ed in msgObj.frame.data])
                print(f"发送数据: ID: {msgObj.frame.can_id}, Data: {d}, 次数：{msgCnt}")
                cnt = 1 if msgCnt == -1 else msgCnt
                for i in range(cnt):
                    ret = self._zcan.Transmit(self._can_handle, msgObj, 1)
                    if ret != 1:
                        print("发送数据失败，结果: " + str(ret))
                    time.sleep(0.5)
            for msgHash in self._sendMsgsList:
                if msgHash['msgCnt'] > 0:
                    self._sendMsgsList.remove(msgHash)

    def receiveMsg(self):
        while True:
            rcv_num = self._zcan.GetReceiveNum(self._can_handle, 0)
            rcv_canfd_num = self._zcan.GetReceiveNum(self._can_handle, 0)
            if rcv_num:
                print("Receive CAN message number:%d" % rcv_num)
                rcv_msg, rcv_num = self._zcan.Receive(self._can_handle, rcv_num)
                for i in range(rcv_num):
                    if rcv_msg[i].frame.can_id == 866:
                        print("接收数据：[%d]:ts:%d, id:%d, dlc:%d, eff:%d, rtr:%d, data:%s" %(i, rcv_msg[i].timestamp,
                            rcv_msg[i].frame.can_id, rcv_msg[i].frame.can_dlc,
                            rcv_msg[i].frame.eff, rcv_msg[i].frame.rtr,
                            ''.join(str(rcv_msg[i].frame.data[j]) + ' ' for j in range(rcv_msg[i].frame.can_dlc))))
            elif rcv_canfd_num:
                print("Receive CANFD message number:%d" % rcv_canfd_num)
                rcv_canfd_msgs, rcv_canfd_num = self._zcan.ReceiveFD(self._can_handle, rcv_canfd_num, 1000)
                for i in range(rcv_canfd_num):
                    print("接收数据：[%d]:ts:%d, id:%d, len:%d, eff:%d, rtr:%d, esi:%d, brs: %d, data:%s" %(
                            i, rcv_canfd_msgs[i].timestamp, rcv_canfd_msgs[i].frame.can_id, rcv_canfd_msgs[i].frame.len,
                            rcv_canfd_msgs[i].frame.eff, rcv_canfd_msgs[i].frame.rtr, 
                            rcv_canfd_msgs[i].frame.esi, rcv_canfd_msgs[i].frame.brs,
                            ''.join(str(rcv_canfd_msgs[i].frame.data[j]) + ' ' for j in range(rcv_canfd_msgs[i].frame.len))))
            # else:
            #     break
            time.sleep(1)

    def closeDevice(self):
        self._zcan.CloseDevice(self._dev_handle)

#将16进制字符串转换为10进制.输入可能是"0x3B2","946",0x3B2,946
def convert16To10(value):
    if str(value).startswith("0x"):
        return int(value,16)
    else:
        return int(value)

if __name__ == "__main__":
    # dbc = Dbcparser('D:\workspace\Ford\dbc\Y2024_FNV2_CMDB_v24.07_HS3.dbc')
    # msgH = dbc.decodeMsg(0x3B2,'44 00 00 12 E6 00 04 06')
    # print(f"Ignition_Status: {msgH['Ignition_Status']}")
    # msgData = dbc.encodeMsg(0x3B2,{"Ignition_Status":4})
    # print(msgData)
    print("tsmasterTest start...")

    # 初始化函数，调用TsMaster.dll 必须先调用初始化函数，否则其他函数无法使用
    print(initialize_lib_tsmaster("TSMaster".encode("utf8")))
    tsapp_set_vendor_detect_preferences(True,True,True,False,False,False,False)
    # 设置CAN通道
    print(tsapp_set_can_channel_count(2))
    # 设置LIN通道数 默认为0  但是还是建议调用函数来设置LIN通道为0
    tsapp_set_lin_channel_count(0)

    # 此处将TC1016的1通道绑定至软件1通道
    # tosun其他硬件只需修改第6个参数，找到对应型号即可
    # tsapp_set_mapping_verbose("TSMaster_demo".encode("utf8"), TLIBApplicationChannelType.APP_CAN,
    #                           CHANNEL_INDEX.CHN1,
    #                           "TC1016".encode("utf8"), TLIBBusToolDeviceType.TS_USB_DEVICE,
    #                           TLIB_TS_Device_Sub_Type.TC1016, 0, CHANNEL_INDEX.CHN1, True)
    # print(tsapp_set_mapping_verbose("TSMaster".encode("utf8"), TLIBApplicationChannelType(0),
    #                           0,
    #                           "PEAK".encode("utf8"), TLIBBusToolDeviceType(4),
    #                           -1, 0, 81, True))
    mapping = TLIBTSMapping()
    mapping.FAppName = b"TSMaster"  # 注意：字符串需要转换为bytes类型
    mapping.FAppChannelIndex = 0  # 应用通道索引
    mapping.FAppChannelType = TLIBApplicationChannelType(0)  # 通道类型设为CAN
    mapping.FHWDeviceType = TLIBBusToolDeviceType(4)  # 硬件设备类型设为PEAK USB
    mapping.FHWIndex = 0  # 硬件索引
    mapping.FHWChannelIndex = 81  # 硬件通道索引
    mapping.FHWDeviceSubType = -1  # 硬件子类型
    mapping.FHWDeviceName = b"PEAK"  # 硬件设备名称
    mapping.FMappingDisabled = True
    # print(tsapp_set_mapping(mapping))

    # mapping2 = TLIBTSMapping()
    # mapping2.FAppName = b"TSMaster"  # 注意：字符串需要转换为bytes类型
    # mapping2.FAppChannelIndex = 1  # 应用通道索引
    # mapping2.FAppChannelType = TLIBApplicationChannelType(0)  # 通道类型设为CAN
    # mapping2.FHWDeviceType = TLIBBusToolDeviceType(1)  # 硬件设备类型设为PEAK USB
    # mapping2.FHWIndex = 0  # 硬件索引
    # mapping2.FHWChannelIndex = 0  # 硬件通道索引
    # mapping2.FHWDeviceSubType = -1  # 硬件子类型
    # mapping2.FHWDeviceName = b"TS Virtual Device"  # 硬件设备名称
    # mapping2.FMappingDisabled = True
    # print(tsapp_set_mapping(mapping2))

    # 设置1通道波特率
    # print(tsapp_configure_baudrate_can(0, 500, False, False))

    connect_status = tsapp_connect()
    print("Connect status: "+str(connect_status))
    if 0 == connect_status:
        # 开启fifo功能才能使用receive接收函数
        tsfifo_enable_receive_fifo()
        print("Receive enable.")
    else:
        print("Connect error, exit.")
        exit(0)

    # 发送报文
    print("Send msg...")
    TCAN1 = TLIBCAN(FIdxChn=0, FIdentifier=0x3B2, FData=[0x40, 0x00, 0x00, 0x12, 0xE6, 0x00, 0x00, 0x02])
    # TCAN1 = TLIBCAN(FIdxChn=0, FProperties=1, FIdentifier=0x360, FData=[0x20, 0x00, 0x1C, 0x8A, 0x82, 0x80, 0xA0, 0x02])
    print(TCAN1)
    # 发送CAN报文 （单帧发送 周期发送）
    for i in range(5):
        print(tsapp_transmit_can_async(TCAN1))
        time.sleep(0.5)
    tsapp_add_cyclic_msg_can(TCAN1, 10)
    print("Send 360")
    TCAN2 = TLIBCAN(FIdxChn=0, FIdentifier=0x360, FData=[0x20, 0x00, 0x1D, 0x8A, 0x82, 0x80, 0xA0, 0x02])
    print(tsapp_transmit_can_async(TCAN2))
    for i in range(5):
        print(tsapp_transmit_can_async(TCAN1))
        time.sleep(0.5)

    # 接收报文
    print("Receive msg...")
    cansize = c_int32(1000)
    listcanmsg = (TLIBCAN * 1000)()
    r = tsfifo_receive_can_msgs(listcanmsg, cansize, 0, 1)
    print("Receive status:"+str(r))
    if r == 0:
        for i in range(cansize.value):
            # print("Canid:", listcanmsg[i].FIdentifier)
            if (listcanmsg[i].FIdentifier == 866): #866==0x362
                r_data = [f"{i:02x}" for i in listcanmsg[i].FData]
                print(r_data)
                print("Canid:", listcanmsg[i].FIdentifier,"Data:", listcanmsg[i].FData, "Time", listcanmsg[i].FTimeUs / 1000000)

    tsapp_disconnect()
    finalize_lib_tsmaster()



