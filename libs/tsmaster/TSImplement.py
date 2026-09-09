# from libs.can.tsmaster.TSMasterApi.TSMasterAPI import *
from libs.can.tsmaster.TSMasterApi.TSAPI import *
from libs.logger import Logger

class TSImplement:
    connect_status = 1

    def __init__(self,config = None):
        Logger.info(set_libtsmaster_location(dllPath.encode("utf8")))
        Logger.info(initialize_lib_tsmaster("TSMaster".encode("utf8")))
        tsapp_set_vendor_detect_preferences(True, True, True, False, False, False, False)
        # 设置CAN通道
        Logger.info(tsapp_set_can_channel_count(2))
        # 设置LIN通道数 默认为0  但是还是建议调用函数来设置LIN通道为0
        tsapp_set_lin_channel_count(0)
        # 波特率
        # tsapp_configure_baudrate_can(0, 500, False, False)
        self.connect_status = tsapp_connect()
        Logger.info("tsapp_connect: "+str(self.connect_status))
        if 0 == self.connect_status:
            # 开启fifo功能才能使用receive接收函数
            tsfifo_enable_receive_fifo()
            Logger.info("Receive enable.")
        else:
            Logger.info("Connect error, exit.")
            # exit(0)

    def sendMsg(self,id:int,data:list[int]):
        '''
        发送can报文：id-报文id。例：sendMsg(0x3B2, [0x40, 0x00, 0x00, 0x12, 0xE6, 0x00, 0x00, 0x02])
        id: 整数，表示CAN报文id
        data: 整数列表，表示CAN报文数据
        '''
        TCAN1 = TLIBCAN(FIdxChn=0, FIdentifier=id, FData=data)
        r = tsapp_transmit_can_async(TCAN1)
        # Logger.debug("Send result: "+str(r)+ " Can: "+str(TCAN1))
        return r

    #接收消息,返回消息数组 [(866,"00 00 00 00 00 00 00 00"),(867,"00 00 00 00 00 00 00 00")]
    def receiveMsg(self):
        retMsg = []
        s = 1000
        cansize = c_int32(s)
        listcanmsg = (TLIBCAN * s)()
        r = tsfifo_receive_can_msgs(listcanmsg, cansize, 0, 1)
        # Logger.info("Receive status:" + str(r))
        if r == 0:
            retMsg = [(m.FIdentifier," ".join([f"{i:02x}" for i in m.FData])) for m in listcanmsg]

            # for i in range(s):
            #     # print("Canid:", listcanmsg[i].FIdentifier)
            #     if (listcanmsg[i].FIdentifier == 866):  # 866==0x362
            #         r_data = [f"{i:02x}" for i in listcanmsg[i].FData]
            #         print(r_data)
            #         print("Canid:", listcanmsg[i].FIdentifier, "Data:", listcanmsg[i].FData, "Time",
            #               listcanmsg[i].FTimeUs / 1000000)
        return retMsg

    def closeDevice(self):
        tsapp_disconnect()
        finalize_lib_tsmaster()

if __name__ == "__main__":
    pass
