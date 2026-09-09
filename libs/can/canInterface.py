from libs.can.zlg.zlgMain import *
from libs.can.test.TestCanDevice import *
from libs.can.controllCan.ControlCAN import *
from libs.logger.logger import Logger
import threading
from libs.can.dbc import DBC

class IgnCanInterface:
    def init_device(self, device_str, chn, abit, dbit, can_type):
        Logger.info('CanInter device init')
        Logger.info('Device info is: %s %s %s %s' % (device_str, chn, abit, dbit))
        if (chn == '0'):
            channelNum = 0
        elif (chn == '1'):
            channelNum = 1
        if (abit == '500k'):
            aBitRate = 500000
        elif (abit == '250k'):
            aBitRate = 250000
        if (dbit == '2M'):
            dBitRate = 2000000
        elif (dbit == '1M'):
            dBitRate = 1000000
        if can_type == 'CAN':
            canType = 0
        elif can_type == 'CANFD':
            canType = 1

        try:
            if device_str == 'ZLG USBCANFD_200U':
                self.device = zlgMain()
                ret = self.device.start(ZCAN_USBCANFD_200U, channelNum, aBitRate, dBitRate, canType)
                if ret == True:
                    Logger.info("ZLG CAN start success")
                else:
                    Logger.error("ZLG CAN start failed")
                    return False
            elif device_str == 'CANalyst-II':
                self.device = ControlCAN()
                ret = self.device.start(channelNum, aBitRate)
                if ret == True:
                    Logger.info("ControlCAN start success")
                else:
                    Logger.error("ControlCAN start failed")
                    return False
            elif device_str == 'TEST':
                self.device = TestDevice()
                self.device.start(0, channelNum, aBitRate, dBitRate)
        except:
            Logger.error("Init Device Failed!")
            return False
        self.init_flag = 1
        return True
    
    def stop_device(self):
        self.init_flag = 0

class CanInterface:
    wakeUpCan = dict(send_id=0x3b2, length=8, data=[0x44, 0x00, 0x00, 0x10, 0xe6, 0x00, 0x00, 0x02], cycle=100, time=-1, cyc_timer = 0)
    init_flag = 0
    def __init__(self):
        Logger.info("CanInterface init")
        self.ignDevice = None
        self.device = None
        self.canSendList = []
        self.canRecvList = []
        self.init_flag = 0
        self.ignStopFlag = False # 停止IGN信号标志位

    '''
    初始化设备
    根据device_str调用不同设备的初始化函数
    '''
    def init_device(self, device_str, chn, abit, dbit, can_type):
        Logger.info('CanInter device init')
        Logger.info('Device info is: %s %s %s %s' % (device_str, chn, abit, dbit))
        if (chn == '0'):
            channelNum = 0
        elif (chn == '1'):
            channelNum = 1
        if (abit == '500k'):
            aBitRate = 500000
        elif (abit == '250k'):
            aBitRate = 250000
        if (dbit == '2M'):
            dBitRate = 2000000
        elif (dbit == '1M'):
            dBitRate = 1000000
        if can_type == 'CAN':
            canType = 0
        elif can_type == 'CANFD':
            canType = 1

        try:
            if device_str == 'ZLG USBCANFD_200U':
                self.device = zlgMain()
                ret = self.device.start(ZCAN_USBCANFD_200U, channelNum, aBitRate, dBitRate, canType)
                if ret == True:
                    Logger.info("ZLG CAN start success")
                else:
                    Logger.error("ZLG CAN start failed")
                    return False
            elif device_str == 'CANalyst-II':
                self.device = ControlCAN()
                ret = self.device.start(channelNum, aBitRate)
                if ret == True:
                    Logger.info("ControlCAN start success")
                else:
                    Logger.error("ControlCAN start failed")
                    return False
            elif device_str == 'TEST':
                self.device = TestDevice()
                self.device.start(0, channelNum, aBitRate, dBitRate)
        except:
            Logger.error("Init Device Failed!")
            return False
        self.init_flag = 1
        read_thread_ = threading.Thread(None, target=self.send_recv_thread, args=())
        read_thread_.start()
        # 打开设备，重置模式和IGN信号
        self.normalMode()
        self.setIgnition(4)
        return True
    
    def init_ign_device(self, d: IgnCanInterface):
        self.ignDevice = d

    def init_dbc(self, mainDbc: DBC):
        self.dbc = mainDbc

    def stop_device(self):
        self.init_flag = 0
        Logger.info("Stop CAN Device")
        self.device.stop()

    def stop_ign_device(self):
        self.ignDevice = None

    def sendCanRaw(self, id: str, data: str, cyc: str, time: str):
        '''
        初始化can报文：id-报文id，cyc-周期，time-发送次数
        '''
        dataList = [] # 将CAN数据字符串,如0000000000000000转换为列表
        for i in range(0, len(data), 2):
            hex_pair = data[i:i + 2]
            # 将截取的十六进制字符串转换为十进制整数
            decimal_num = int(hex_pair, 16)
            dataList.append(decimal_num)
        send_dict = dict(send_id=int(id), length=8, data=dataList, cycle=int(cyc), time=int(time), cyc_timer = int(cyc))
        self.canSendList.append(send_dict)

    '''
    初始化can报文：id-报文id，cyc-周期，time-发送次数
    '''
    def start_can(self, id, cyc, time):
        send_dict = dict(send_id=id, length=8, data=[0,0,0,0,0,0,0,0], cycle=cyc, time=time, cyc_timer = int(cyc))
        self.canSendList.append(send_dict)

    def stopIgnition(self):
        Logger.info("Stop Ignition")
        self.ignStopFlag = True

    def transportMode(self):
        Logger.info("Transport Mode")
        self.ignStopFlag = False
        self.wakeUpCan["data"][6] = self.wakeUpCan["data"][6] & ~0x0C
        self.wakeUpCan["data"][6] = self.wakeUpCan["data"][6] | (3 << 2)

    def normalMode(self):
        Logger.info("Normal Mode")
        self.ignStopFlag = False
        self.wakeUpCan["data"][6] = self.wakeUpCan["data"][6] & ~0x0C
        self.wakeUpCan["data"][6] = self.wakeUpCan["data"][6] | (0 << 2)

    def setIgnition(self, sig: int):
        '''
        设置IgnitionStatus
        '''
        self.ignStopFlag = False
        if (sig > 15) or (sig < 0):
            return
        self.wakeUpCan["data"][0] = self.wakeUpCan["data"][0] & 0x0F
        self.wakeUpCan["data"][0] = self.wakeUpCan["data"][0] | (sig << 4)

    def send_recv_thread(self):
        threadCyc = 5 # 线程循环周期 ms
        while True:
            # 关闭Qt窗口，停止线程
            if self.init_flag == 0:
                return
            time.sleep(threadCyc/1000)
            # 发送唤醒报文
            if self.ignStopFlag != True:
                self.wakeUpCan["cyc_timer"] += threadCyc
            if self.wakeUpCan["cyc_timer"] >= self.wakeUpCan["cycle"]:
                self.wakeUpCan["cyc_timer"] = 0
                if self.ignDevice == None:
                    self.wakeUpCan["send_id"] = 0x3b2
                    self.device.send_can(self.wakeUpCan["send_id"], self.wakeUpCan["length"], self.wakeUpCan["data"])
                else:
                    self.wakeUpCan["send_id"] = 0x3b3
                    # self.device.send_can(self.wakeUpCan["send_id"], self.wakeUpCan["length"], self.wakeUpCan["data"])
                    self.ignDevice.device.send_can(self.wakeUpCan["send_id"], self.wakeUpCan["length"], self.wakeUpCan["data"])
            # 发送can报文
            for canSend in self.canSendList:
                if canSend["cycle"] == 0:
                    # 该报文只发送一次
                    self.device.send_can(canSend["send_id"], canSend["length"], canSend["data"])
                    Logger.info("Send Can: " + str(canSend["send_id"]) + " " + str(canSend["data"]))
                    self.canSendList.remove(canSend)
                else:
                    # 该报文需要循环发送
                    canSend["cyc_timer"] += threadCyc
                    if canSend["cyc_timer"] >= canSend["cycle"]:
                        canSend["cyc_timer"] = 0
                        Logger.info("Send Can: " + str(canSend["send_id"]) + " " + str(canSend["data"]))
                        self.device.send_can(canSend["send_id"], canSend["length"], canSend["data"])
                        if canSend["time"] > 0:
                            canSend["time"] -= 1
                        if canSend["time"] == 0:
                            self.canSendList.remove(canSend)
            # 接收can报文
            if self.canRecvList == []:
                continue
            # 遍历需要接收的报文，增加超时计时器的值
            for canRecvCheck in self.canRecvList:
                canRecvCheck['timeoutTimer'] += threadCyc
            # 遍历device接收到的报文
            for deviceRecvList in self.device.recv_can():
                # 查找是否有需要接收的报文
                for canRecvCheck in self.canRecvList:
                    # 如果已经收到期望报文，跳过
                    if canRecvCheck['checkResult'] == 1:
                        continue
                    # 判断超时，如果超时，跳过
                    if canRecvCheck['timeoutTimer'] >= canRecvCheck['timeout']:
                        continue
                    # 未超时且收到期望报文，判断报文值
                    if deviceRecvList["recv_id"] == canRecvCheck["recv_id"]:
                        # TODO 判断报文长度
                        # if deviceRecvList["length"] != canRecvCheck["length"]:
                        #     break
                        Logger.info(f"CAN Recv: {deviceRecvList['recv_id']} Data: {deviceRecvList['data']}")
                        for i in range(0, len(deviceRecvList["data"])):
                            # 一字节一字节判断
                            if (deviceRecvList["data"][i] & canRecvCheck["mask"][i]) != canRecvCheck["exp"][i]:
                                # 出现不匹配，跳出
                                canRecvCheck['checkResult'] = 0
                                break
                            else:
                                canRecvCheck['checkResult'] = 1
                        if canRecvCheck['checkResult'] == 1:
                            Logger.info(f"CAN Recv: {canRecvCheck['recv_id']} Success")
            time.sleep(threadCyc/1000)

    def recvCanRaw(self, id: str, timeout: str, data: str, mask: str):
        '''
        注册需要接收的can报文
        id-报文id
        timeout-超时时间
        data-期望报文
        mask-期望报文掩码
        '''
        Logger.info(f'CAN Recv Register: {id} Timeout: {timeout} Expect: {data} Mask: {mask}')
        dataList = []
        for i in range(0, len(data), 2):
            hex_pair = data[i:i + 2]
            decimal_num = int(hex_pair, 16)
            dataList.append(decimal_num)
        maskList = []
        for i in range(0, len(mask), 2):
            hex_pair = mask[i:i + 2]
            decimal_num = int(hex_pair, 16)
            maskList.append(decimal_num)
        recvDict = dict(recv_id=int(id), exp=dataList, mask=maskList, timeout=int(timeout), timeoutTimer = 0, checkResult=0)
        self.canRecvList.append(recvDict)

    '''
    检查是否所有需要接收的can报文都已经接收到期望的值
    只要有一个报文没有接收到期望的值，就返回False
    '''
    def recvCanCheck(self):
        timeoutCheckFlag = False
        if len(self.canRecvList) == 0:
            Logger.info('CAN Recv Check List Is Empty')
            return True
        while True:
            for canRecv in self.canRecvList:
                if canRecv["checkResult"] == 0:
                    if canRecv['timeoutTimer'] < canRecv['timeout']:
                        # 没有收到期望值，但没有超时，继续while循环
                        timeoutCheckFlag = True
                        continue
                    # 没有收到期望值，且已经超时，返回False
                    Logger.error(f"CAN Recv {canRecv['recv_id']} Error")
                    return False
            # 所有需要接收的can报文都已经接收到期望的值，返回True
            if timeoutCheckFlag== True:
                timeoutCheckFlag = False
            else:
                return True

    def can_clear(self):
        self.canSendList = []
        self.canRecvList = []
        self.device.recv_can()
