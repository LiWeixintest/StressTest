from libs.logger.logger import Logger
from libs.can.zlg.zlgMain import *
from subprocess import PIPE, Popen
import uiautomator2 as u2
from adbutils import adb
from enum import Enum
import subprocess
import threading
import serial
import time
import re

powerStatus = 1 # 状态 0-停止 1-正常 2-Standby

class Colors:
    """字体颜色"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m' 

class Apps():
    """各个应用属性"""
    digital_owners_manual = "Digital Owner's Manual"#"Digital Owner's\nManual" #数字车主手册
    Settings_ex = "Settings" #设置
    qq_music = "QQ音乐" #QQ音乐
    Settings = "设置" #设置
    IQiyi = "爱奇艺" #爱奇艺

class CanDeviceType():
    """CAN设备属性"""
    ZLG_USBCANFD_200U = 0
    TSmaster = 1
    ZLG_USBCAN_2E_U = 2
    
class CanMessageType():
    """CAN消息类型"""
    CAN = 0
    CANFD = 1

class CanChannelNum():
    """CAN通道属性"""
    CAN1 = 0
    CAN2 = 1
    CAN3 = 2
    CAN4 = 3

class CanBitRate():
    """CAN波特率属性"""
    CAN_125K = 125000
    CAN_250K = 250000
    CAN_500K = 500000 #默认仲裁波特率
    CAN_1M = 1000000
    CANFD_500K = 500000 #默认仲裁波特率
    CANFD_1M = 1000000
    CANFD_2M = 2000000

class CanFDDataBitRate():
    """CAN数据波特率属性"""
    CANFD_500K = 500000
    CANFD_1M = 1000000
    CANFD_2M = 2000000 #默认数据波特率

class CarPwer():
    """车机电源模式"""
    Normal = 1 #车机正常模式
    Standby = 2 #Standby模式
    STR = 0 #STR休眠
    Sleep = 3 #深度休眠

class PowerSupplyType():
    """电源设备类型"""
    power_supply = 0 #可调电源
    relay = 1 #继电器

def send_can_start_device(
        device_type=ZCAN_USBCANFD_200U,
        channel_num=CanChannelNum.CAN1,
        bitrate=CanBitRate.CAN_500K,
        data_bitrate=CanFDDataBitRate.CANFD_2M,
        can_type=CanMessageType.CAN,
):
    device = zlgMain()
    device.start(device_type, channel_num, bitrate, data_bitrate, can_type)
    canfram_IGON = []
    canfram_IGOFF = []
    dlc = 0
    if can_type == 0:
        dlc = 8
        canfram_IGON = [0x44, 0x00, 0x00, 0x12, 0xE6, 0x00, 0x00, 0x02]
        canfram_IGOFF = [0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    elif can_type == 1:
        dlc = 16
        canfram_IGON = [0x44, 0x00, 0x00, 0x12, 0xE6, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        canfram_IGOFF = [0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    try:
        while True:
            global powerStatus #设置全局变量，用于控制电源状态
            if powerStatus == 1:
                if can_type == 1:
                    device.send_canfd(0x3b3, dlc, canfram_IGON)
                else:
                    device.send_can(0x3b3, dlc, canfram_IGON)
                #Logger.info(f"发送点火报文: {canfram_IGON}")
            elif powerStatus == 2:
                if can_type == 1:
                    device.send_canfd(0x3b3, dlc, canfram_IGOFF)
                else:
                    device.send_can(0x3b3, dlc, canfram_IGOFF)
                Logger.info(f"发送熄火报文: {canfram_IGOFF}")
            elif powerStatus == 0:
                Logger.info(f"停止发送CAN报文")
                continue
            elif powerStatus == 3:
                Logger.info(f"结束发送CAN报文")
                break
    except Exception as e:
        Logger.error(f"发送CAN报文异常: {e}")
    finally:
        # 无论怎么退出，都关闭CAN设备，释放句柄！！重要
        Logger.info("子线程退出,关闭CAN设备")
        device.stop()

# 提供接口给外部调用修改状态，不能外部直接赋值全局变量
def set_power_status(val:int):
    global powerStatus
    powerStatus = val

class PowerSupplyControl():
    """输出电源控制"""
    def com_init(self,port,baudrate=9600,devices=PowerSupplyType.power_supply):
        """
        初始化
        Args:
            port: 串口号,如'COM21'
            baudrate: 波特率,默认9600
            devices: 电源设备类型,默认可调电源
        """
        self.port = port
        self.baudrate = baudrate
        self.devices = devices
    
    def com_start(self,port,baudrate=9600):
        """连接串口"""
        self.ser = serial.Serial(port, baudrate)
        Logger.info(f"已连接串口: {port}, 波特率: {baudrate}")

    def com_stop(self):
        """断开连接"""
        self.ser.close()
        Logger.info(f"已断开串口: {self.port}")

    def start_power(self):
        """启动电源"""
        try:
            hex=""
            if self.devices == PowerSupplyType.power_supply:
                hex="00 10 00 04 00 01 02 00 01 6B 84"
                start=bytes.fromhex(hex)
                self.ser.write(start)
            elif self.devices == PowerSupplyType.relay:
                hex="00 01 FF" # 常闭闭合
                start=bytes.fromhex(hex)
                self.ser.write(start)
            else:
                command = "00 10 00 04 00 01 02 00 01 6B 84"
                start=bytes.fromhex(command)
                self.ser.write(start)
                command = "00 01 FF"
                start=bytes.fromhex(command)
                self.ser.write(start)
            
        except Exception as e:
            Logger.error(f"启动电源异常: {e}")

    def stop_power(self):
        """关闭电源"""
        try:
            hex=""
            if self.devices == PowerSupplyType.power_supply:
                hex="00 10 00 04 00 01 02 00 00 AA 44"
                stop=bytes.fromhex(hex)
                self.ser.write(stop)
            elif self.devices == PowerSupplyType.relay:
                hex="00 F1 FF" # 常闭断开
                stop=bytes.fromhex(hex)
                self.ser.write(stop)
            else:
                command = "00 10 00 04 00 01 02 00 00 AA 44"
                start=bytes.fromhex(command)
                self.ser.write(start)
                command = "00 F1 FF"
                start=bytes.fromhex(command)
                self.ser.write(start)
        except Exception as e:
            Logger.error(f"关闭电源异常: {e}")

class CanMessage():
    """模拟收发报文"""
    def can_init(self, 
                channel_num=CanChannelNum.CAN1,
                bitrate=CanBitRate.CAN_500K,
                data_bitrate=CanFDDataBitRate.CANFD_2M,
                bus_type=CanMessageType.CAN,
                device_type=CanDeviceType.ZLG_USBCANFD_200U
                ):
        """
        初始化CAN设备,并设置CAN通道、波特率、数据波特率和消息类型等参数
        Args:
            channel_num: CAN通道
            bitrate: 仲裁波特率
            data_bitrate: 数据波特率
            bus_type: 总线类型CAN、CANFD、LIN,默认为CAN
            device_type: 设备类型CANoe、ZLG_USBCANFD_200U(周立功)、TSmaster,默认为ZLG_USBCANFD_200U
        """
        if device_type == CanDeviceType.ZLG_USBCANFD_200U and bus_type == CanMessageType.CAN:
            self.dlc = 8 # CAN报文数据长度
            self.device = zlgMain()
            ret = self.device.start(ZCAN_USBCANFD_200U, channel_num, bitrate, data_bitrate, bus_type)
        elif device_type == CanDeviceType.ZLG_USBCANFD_200U and bus_type == CanMessageType.CANFD:
            self.dlc = 16 # CANFD报文数据长度
            self.device = zlgMain()
            ret = self.device.start(ZCAN_USBCANFD_200U, channel_num, bitrate, data_bitrate, bus_type)
        elif device_type == CanDeviceType.TSmaster  and bus_type == CanMessageType.CAN:
            pass
        elif device_type == CanDeviceType.TSmaster  and bus_type == CanMessageType.CANFD:
            pass
        self.canfram_IGON = [0x44, 0x00, 0x00, 0x12, 0xE6, 0x00, 0x00, 0x02]
        self.canfram_IGOFF = [0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        self.canfdfram_IGON = [0x44, 0x00, 0x00, 0x12, 0xE6, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        self.canfdfram_IGOFF = [0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
   
    def send_can(self, can_id, data, interval, count):
        """
        发送CAN报文
        Args:
            can_id: CAN ID
            data: 报文数据长度为8字节的列表,如[0x44, 0x00, 0x00, 0x12, 0xE6, 0x00, 0x00, 0x04]
            interval: 发送间隔，单位为秒
            count: 发送次数,如果count=0则一直发送
        """
        try:
            n = 0
            if count != 0:
                while n <= count:
                    time.sleep(interval)
                    self.device.send_can(can_id, self.dlc, data)
                    n += 1
            elif count == 0:
                while True:
                    time.sleep(interval)
                    self.device.send_can(can_id, self.dlc, data)
        except Exception as e:
            Logger.error(f"发送CAN消息时发生错误: {e}")

    def get_can_msg(self,can_id):
        """
        获取CAN报文
        Args:
            can_id: CAN ID
        Return: 
            CAN收到应报文的ID和值
        """
        try:
            count = 0
            while True:
                if count < 10:
                    can_msg = self.device.recv_can()
                    if can_msg != None and can_msg != []:
                        for msg in can_msg:
                            if msg["recv_id"] == can_id:
                                return msg["recv_id"], msg["data"]
                            else:
                                count += 1
                else:
                    Logger.error(f"未在CAN总线上收到ID为{can_id}的报文")
                    return None, None      
                time.sleep(0.1)
        except Exception as e:
            Logger.error(f"接收CAN消息时发生错误: {e}")
            return None, None
        
    def send_canfd(self, can_id, data, interval, count):
        """
        发送CANFD报文
        Args:
            can_id: CAN ID
            data: 报文数据长度为8字节的列表,如[0x44, 0x00, 0x00, 0x12, 0xE6, 0x00, 0x00, 0x04]
            interval: 发送间隔，单位为秒
            count: 发送次数
        """
        try:
            n = 0
            while n <= count:
                time.sleep(interval)
                self.device.send_canfd(can_id, self.dlc, data)
                n += 1
        except Exception as e:
            Logger.error(f"发送CAN消息时发生错误: {e}")

    def start_vehicle_fnv2(self):
        """
        CAN报文启动车机,fnv2车型
        """
        try:
            self.send_can(can_id=0x3b3,data=self.canfram_IGON,interval=1,count=0)
        except Exception as e:
            Logger.error(f"启动车机: {e}")
    
    def start_vehicle_fnv3(self):
        """
        CAN报文启动车机,fnv3车型
        """
        try:
            self.send_canfd(can_id=0x3b3,data=self.canfdfram_IGON,interval=1,count=0)
        except Exception as e:
            Logger.error(f"启动车机: {e}")
    
    def carpwer_change(self,carpwer=CarPwer.Normal):
        """
        切换电源模式
        Args:
            carpwer: 电源状态
        """
        try:
            global canflag
            status = 1
            while True:
                if status == 1:#启动车机，当adb检测到设备说明设备启动成功
                    self.send_can(can_id=0x3b2,data=self.canfram_IGON,interval=1,count=1)
                    if adb.device_list() == [] and carpwer == CarPwer.Normal and canflag == True:
                        time.sleep(1)
                    elif adb.device_list() != [] and carpwer == CarPwer.Normal and canflag == True:#若电源状态值为1保持当前状态
                        print("车辆已启动")
                        status = 1
                    elif adb.device_list() != [] and carpwer != CarPwer.Normal and canflag == True:
                        #若电源状态值不为1进入下一状态standby模式
                        status = 2
                    elif adb.device_list() != [] and carpwer == CarPwer.Normal and canflag == False:
                        #canflag等于False时停止发送
                        status = 4
                if status == 2:#启动成功后进入standby
                    self.send_can(can_id=0x3b2,data=self.canfram_IGOFF,interval=1,count=3)
                    if carpwer == CarPwer.Standby:#若电源状态值为2，成功进入Standby后启动车机
                        print("车机进入Standby模式")
                        status = 4
                    else:#反之进入下一状态STR模式
                        status = 0
                if status == 0:#等待进入STR当检测不到adb设备则成功进入STR
                    if adb.device_list() == []:
                        time.sleep(15)
                        if carpwer == CarPwer.STR:#成功进入STR后启动车机
                            print("车机进入STR")
                            status = 4
                        else:#反之进入下一状态深度模式
                            status = 3
                    else:
                        continue
                if status == 3:
                    time.sleep(90)
                    print("车机进入深度休眠")
                    status = 4 #成功进入深度休眠后启动车机
                if status == 4:
                    canflag = True
                    break
                #carpwer = CarPwer.Normal
                time.sleep(1)
        except Exception as e:
            Logger.error(f"启动车机: {e}")

    def start(self):
        """启动线程"""
        self.stop_flag = False
        self.thread = threading.Thread(target=self.carpwer_change,args=(CarPwer.Normal,))
        self.thread.start()
        print("线程已启动")

    def ecg_reset(self):
        """通过UDS的1101服务重启ECG,注意要使用周立功的通道1连接到HS1"""
        self.send_can(0x716, 8, [0x02,0x11,0x01,0x00,0x00,0x00,0x00,0x00])

    def tcu_reset(self):
        """通过UDS的1101服务重启TCU,注意要使用周立功的通道1连接到HS4"""
        self.send_can(0x754, 8, [0x02,0x11,0x01,0x00,0x00,0x00,0x00,0x00])

    def ivi_reset(self):
        """通过UDS的1101服务重启IVI,注意要使用周立功的通道0连接到HS3"""
        self.send_can(0x7d0, 8, [0x02,0x11,0x01,0x00,0x00,0x00,0x00,0x00])

    def function_reset(self):
        """通过UDS的1101服务重启TCU、ECG、IVI(功能寻址,暂不可用)"""
        self.send_can(0x7d8, 8, [0x02,0x11,0x01,0x00,0x00,0x00,0x00,0x00])   

class AndroidTest():
    "安卓相关操作,如进入应用、检查账号、在线音乐、连接wifi等。执行adb命令"

    def devices_init(self):
        """
        初始化，检查设备是否连接成功，若未连接成功则等待设备连接
        """
        try:
            """
            while True:
                if adb.device_list() == []:
                    Logger.info(f"{Colors.YELLOW}未检测到设备，正在等待设备连接...{Colors.RESET}")
                    time.sleep(1)
                else:
                    break
            """
            self.d = u2.connect()
            self.adbdevices = adb.device()
        except Exception as e:
            Logger.error(e)

    def enter_app(self,app_name=Apps.Settings):
        """
        进入应用
        Args:
            app_name:应用名称
        """
        try:
            if not hasattr(self, "d"):
                #检测未初始化设备，自动执行devices_init
                self.devices_init()
            if self.d.xpath('//*[@resource-id="com.android.systemui:id/home"]').exists:
                self.d.xpath('//*[@resource-id="com.android.systemui:id/home"]').click()
            elif self.d(resourceId="com.android.systemui:id/home_1").exists:
                self.d(resourceId="com.android.systemui:id/home_1").click()
            time.sleep(0.5)

            if self.d(resourceId="com.android.systemui:id/navi_all_apps").exists():
                self.d(resourceId="com.android.systemui:id/navi_all_apps").click()
            elif self.d(resourceId="com.android.systemui:id/all_apps").exists():
                self.d(resourceId="com.android.systemui:id/all_apps").click()
            elif self.d(resourceId="com.android.systemui:id/allapp").exists():
                self.d(resourceId="com.android.systemui:id/allapp").click()
            time.sleep(0.5)
            if not self.d(text=app_name).exists():
                self.d.xpath('//*[@resource-id="com.ford.sync.launcher:id/viewpager_all_menu"]').get().scroll_to(f'//*[@text="{app_name}"]')
            time.sleep(0.5)
            self.d(text=app_name).click()
        except Exception as e:
            Logger.error(e)

    def account(self):
        """
        检查账号二维码是否加载成功

        Return: 
            True:加载成功
            False:加载失败
        """
        try:
            if not hasattr(self, "d"):
                #检测未初始化设备，自动执行devices_init
                self.devices_init()
            if self.d(resourceId="com.android.systemui:id/qs_user_name").exists():
                self.d(resourceId="com.android.systemui:id/qs_user_name").click()
            elif self.d(resourceId="com.android.systemui:id/qs_user_head").exists():
                self.d(resourceId="com.android.systemui:id/qs_user_head").click()
            elif self.d(resourceId="com.android.systemui:id/tv_userName").exists():
                self.d(resourceId="com.android.systemui:id/tv_userName").click()
            elif self.d(resourceId="com.android.systemui:id/head_icon_background").exists():
                self.d(resourceId="com.android.systemui:id/head_icon_background").click()
            time.sleep(1)
            if self.d(resourceId="com.ford.sync.account:id/tv_refresh").exists():
                self.d(resourceId="com.ford.sync.account:id/tv_refresh").click()
            elif self.d(resourceId="com.ford.sync.account:id/layout_qr").exists():
                self.d(resourceId="com.ford.sync.account:id/layout_qr").click()
            time.sleep(3)
            if self.d(resourceId="com.ford.sync.account:id/iv_refresh").exists():
                self.d(resourceId="com.ford.sync.account:id/iv_refresh").click()
                time.sleep(1)
                if self.d(resourceId="com.ford.sync.account:id/iv_refresh").exists():
                    print(f"{Colors.RED}登录二维码加载失败{Colors.RESET}")
                    return False
            if self.d(resourceId="com.ford.sync.account:id/tv_qr_prompt_tlt").exists():
                self.d(resourceId="com.ford.sync.account:id/iv_refresh").click()
                time.sleep(1)
                if self.d(resourceId="com.ford.sync.account:id/iv_refresh").exists():
                    print(f"{Colors.RED}登录二维码加载失败{Colors.RESET}")
                    return False
            err_count=0
            status = self.d(resourceId="com.ford.sync.account:id/tv_refresh").exists()
            while status==True and err_count < 3:
                self.d(resourceId="com.ford.sync.account:id/tv_refresh").click()
                time.sleep(1)
                err_count=err_count+1
            if self.d(resourceId="com.ford.sync.account:id/tv_refresh").exists():
                self.d(resourceId="com.ford.sync.account:id/tv_refresh").click()
                time.sleep(1)
                if self.d(resourceId="com.ford.sync.account:id/tv_refresh").exists():
                    #print(f"{Colors.RED}登录二维码加载失败{Colors.RESET}")
                    return False
            else:
                #print(f"{Colors.GREEN}登录二维码加载成功{Colors.GREEN}")
                return True
        except Exception as e:
            Logger.error(f"加载登录二维码异常: {e}")
            return False

    def online_music(self):
        """
        检查在线音乐是否加载成功包括QQ音乐、喜马拉雅、新闻和云听
        
        Return: 
            True:加载成功
            False:加载失败
        """
        try:
            if not hasattr(self, "d"):
                #检测未初始化设备，自动执行devices_init
                self.devices_init()
            self.enter_app(Apps.qq_music)
            time.sleep(0.5)
            #切换QQ音乐
            if not self.d(text="QQ音乐").exists():
                if self.d(resourceId="com.baidu.car.radio:id/iv_logo").exists():
                    self.d(resourceId="com.baidu.car.radio:id/iv_logo").click()
                elif self.d(resourceId="com.baidu.car.radio:id/iv_arrow").exists():
                    self.d(resourceId="com.baidu.car.radio:id/iv_arrow").click()
                time.sleep(0.5)
                self.d(text="QQ音乐").click()
            time.sleep(0.5)
            if self.d(resourceId="com.baidu.car.radio:id/btn_retry_refresh").exists():
                self.d(resourceId="com.baidu.car.radio:id/btn_retry_refresh").click()
            if self.d(resourceId="com.baidu.car.radio:id/btn_empty_page").exists():
                self.d(resourceId="com.baidu.car.radio:id/btn_empty_page").click()
            time.sleep(3)
            if self.d(resourceId="com.baidu.car.radio:id/iv_empty_page").exists():
                self.d(resourceId="com.baidu.car.radio:id/iv_empty_page").click()
                time.sleep(2)
            no_tip = self.d(resourceId="com.edog.car:id/tv_network_no_tip").exists()
            iv_empty=self.d(resourceId="com.baidu.car.radio:id/iv_empty_page").exists()
            tv_empty=self.d(resourceId="com.baidu.car.radio:id/tv_empty_page").exists()
            btn_empty=self.d(resourceId="com.baidu.car.radio:id/btn_empty_page").exists()
            qq =False
            if no_tip ==True or iv_empty == True or tv_empty == True or btn_empty == True:
                qq = False
            else:
                qq = True
            #切换喜马拉雅
            time.sleep(0.5)
            if not self.d(text="喜马拉雅").exists():
                if self.d(resourceId="com.baidu.car.radio:id/iv_logo").exists():
                    self.d(resourceId="com.baidu.car.radio:id/iv_logo").click()
                elif self.d(resourceId="com.baidu.car.radio:id/iv_arrow").exists():
                    self.d(resourceId="com.baidu.car.radio:id/iv_arrow").click()
                time.sleep(0.5)
                self.d(text="喜马拉雅").click()
            if self.d(resourceId="com.baidu.car.radio:id/contentText",text="登录喜马拉雅账号并开通VIP即可畅听全部内容").exists():
                if self.d(resourceId="com.baidu.car.radio:id/rightButton").exists():
                    self.d(resourceId="com.baidu.car.radio:id/rightButton").click()
            if self.d(resourceId="com.baidu.car.radio:id/leftButton",text="登录").exists():
                if self.d(resourceId="com.baidu.car.radio:id/rightButton").exists():
                    self.d(resourceId="com.baidu.car.radio:id/rightButton").click()
            if self.d(resourceId="com.baidu.car.radio:id/rightButton",text="取消").exists():
                if self.d(resourceId="com.baidu.car.radio:id/rightButton").exists():
                    self.d(resourceId="com.baidu.car.radio:id/rightButton").click()
            if self.d(text="取消").exists() or self.d(text="登录").exists() or self.d(text="登录喜马拉雅账号并开通VIP即可畅听全部内容").exists():
                if self.d(resourceId="com.baidu.car.radio:id/rightButton").exists():
                    self.d(resourceId="com.baidu.car.radio:id/rightButton").click()
            if self.d.xpath('//android.widget.FrameLayout[1]').exists:
                if self.d(resourceId="com.baidu.car.radio:id/rightButton").exists():
                    self.d(resourceId="com.baidu.car.radio:id/rightButton").click()
            if self.d(resourceId="com.baidu.car.radio:id/scrollLinear").exists():
                if self.d(resourceId="com.baidu.car.radio:id/rightButton").exists():
                    self.d(resourceId="com.baidu.car.radio:id/rightButton").click()
            if self.d(resourceId="com.baidu.car.radio:id/btn_retry_refresh").exists():
                self.d(resourceId="com.baidu.car.radio:id/btn_retry_refresh").click()
            if self.d(resourceId="com.baidu.car.radio:id/btn_empty_page").exists():
                self.d(resourceId="com.baidu.car.radio:id/btn_empty_page").click()
            time.sleep(3)
            if self.d(resourceId="com.baidu.car.radio:id/iv_empty_page").exists():
                self.d(resourceId="com.baidu.car.radio:id/iv_empty_page").click()
                time.sleep(2)
            no_tip = self.d(resourceId="com.edog.car:id/tv_network_no_tip").exists()
            iv_empty=self.d(resourceId="com.baidu.car.radio:id/iv_empty_page").exists()
            tv_empty=self.d(resourceId="com.baidu.car.radio:id/tv_empty_page").exists()
            btn_empty=self.d(resourceId="com.baidu.car.radio:id/btn_empty_page").exists()
            xmly =False
            if no_tip ==True or iv_empty == True or tv_empty == True or btn_empty == True:
                xmly = False
            else:
                xmly = True
            #切换新闻
            if not self.d(text="新闻").exists():
                if self.d(resourceId="com.baidu.car.radio:id/iv_logo").exists():
                    self.d(resourceId="com.baidu.car.radio:id/iv_logo").click()
                elif self.d(resourceId="com.baidu.car.radio:id/iv_arrow").exists():
                    self.d(resourceId="com.baidu.car.radio:id/iv_arrow").click()
                time.sleep(0.5)
                self.d(text="新闻").click()
            if self.d(resourceId="com.baidu.car.radio:id/btn_retry_refresh").exists():
                self.d(resourceId="com.baidu.car.radio:id/btn_retry_refresh").click()
            if self.d(resourceId="com.baidu.car.radio:id/btn_empty_page").exists():
                self.d(resourceId="com.baidu.car.radio:id/btn_empty_page").click()
            time.sleep(3)
            if self.d(resourceId="com.baidu.car.radio:id/iv_empty_page").exists():
                self.d(resourceId="com.baidu.car.radio:id/iv_empty_page").click()
                time.sleep(2)
            no_tip = self.d(resourceId="com.edog.car:id/tv_network_no_tip").exists()
            iv_empty=self.d(resourceId="com.baidu.car.radio:id/iv_empty_page").exists()
            tv_empty=self.d(resourceId="com.baidu.car.radio:id/tv_empty_page").exists()
            btn_empty=self.d(resourceId="com.baidu.car.radio:id/btn_empty_page").exists()
            new =False
            if no_tip ==True or iv_empty == True or tv_empty == True or btn_empty == True:
                new = False
            else:
                new = True
            #切换云听
            if not self.d(text="云听").exists():
                if self.d(resourceId="com.baidu.car.radio:id/iv_logo").exists():
                    self.d(resourceId="com.baidu.car.radio:id/iv_logo").click()
                elif self.d(resourceId="com.baidu.car.radio:id/iv_arrow").exists():
                    self.d(resourceId="com.baidu.car.radio:id/iv_arrow").click()
                time.sleep(0.5)
                self.d(text="云听").click()
            if self.d(resourceId="com.edog.car:id/tvStart").exists():
                self.d(resourceId="com.edog.car:id/tvStart").click()
            if self.d(resourceId="com.edog.car:id/duration_12_month").exists():
                self.d(resourceId="com.edog.car:id/duration_12_month").click()
                time.sleep(1)
                self.d(resourceId="com.edog.car:id/tv_dialog_bottom_define").click()
            if self.d(resourceId="com.baidu.car.radio:id/btn_empty_page").exists():
                self.d(resourceId="com.baidu.car.radio:id/btn_empty_page").click()
            time.sleep(3)
            if self.d(resourceId="com.baidu.car.radio:id/btn_empty_page").exists():
                self.d(resourceId="com.baidu.car.radio:id/btn_empty_page").click()
                time.sleep(2)
            no_tip = self.d(resourceId="com.edog.car:id/tv_network_no_tip").exists()
            iv_empty=self.d(resourceId="com.baidu.car.radio:id/iv_empty_page").exists()
            tv_empty=self.d(resourceId="com.baidu.car.radio:id/tv_empty_page").exists()
            btn_empty=self.d(resourceId="com.baidu.car.radio:id/btn_empty_page").exists()
            yunting =False
            if no_tip ==True or iv_empty == True or tv_empty == True or btn_empty == True:
                yunting = False
            else:
                yunting = True
            qq_status = 0 # QQ音乐加载状态，加载失败返回0，加载成功返回二进制1,即1
            xmly_status = 0 # 喜马拉雅加载状态，加载失败返回0，加载成功返回二进制的10,即2
            new_status = 0 # 新闻加载状态，加载失败返回0，加载成功返回二进制的100,即4
            yunting_status = 0 # 云听加载状态，加载失败返回0，加载成功返回二进制的1000,即8
            if qq ==False: # QQ是否加载失败，加载失败返回0，加载成功返回1
                #Logger.error(f"{Colors.RED}QQ音乐和云听加载失败{Colors.RED}")
                qq_status = 0
            elif qq == True:
                #Logger.info(f"{Colors.GREEN}QQ音乐和云听加载成功{Colors.GREEN}")
                qq_status = 1
            if xmly ==False: # 喜马拉雅是否加载失败，加载失败返回0，加载成功返回2
                #Logger.error(f"{Colors.RED}喜马拉雅加载失败{Colors.RED}")
                xmly_status = 0
            elif xmly == True:
                #Logger.info(f"{Colors.GREEN}喜马拉雅加载成功{Colors.GREEN}")
                xmly_status = 2
            if new ==False: # 新闻是否加载失败，加载失败返回0，加载成功返回4
                #Logger.error(f"{Colors.RED}新闻加载失败{Colors.RED}")
                new_status = 0
            elif new == True:
                #Logger.info(f"{Colors.GREEN}新闻加载成功{Colors.GREEN}")
                new_status = 4
            if yunting ==False: # 云听是否加载失败，加载失败返回0，加载成功返回8
                #Logger.error(f"{Colors.RED}云听加载失败{Colors.RED}")
                yunting_status = 0
            elif yunting == True:
                #Logger.info(f"{Colors.GREEN}云听加载成功{Colors.GREEN}")
                yunting_status = 8
            status = qq_status + xmly_status + new_status + yunting_status # 计算总状态
            #print(f"QQ音乐加载状态: {qq_status}, 喜马拉雅加载状态: {xmly_status}, 新闻加载状态: {new_status}, 云听加载状态: {yunting_status}, 总状态: {status}")
            if status != 0 and status != None:
                #Logger.info(f"{Colors.GREEN}在线音乐加载成功{Colors.GREEN}")
                return True
            else:
                #Logger.error(f"{Colors.RED}在线音乐加载失败{Colors.RED}")
                return False
        except Exception as e:
            Logger.error(f"检查在线音乐加载状态异常: {e}")
            return False

    def open_wifi(self):
        """开启wifi"""
        try:
            if not hasattr(self, "d"):
                #检测未初始化设备，自动执行devices_init
                self.devices_init()
            self.enter_app()
            time.sleep(0.5)
            self.d.xpath('//*[@resource-id="com.adayo.settings:id/design_navigation_view"]').get().scroll_to('//*[@text="连接"]')
            #d(scrollable=True).scroll.to(text="连接")
            time.sleep(0.5)
            self.d(text="连接").click()
            time.sleep(0.5)
            self.d(text="WiFi").click()
            if not self.d(resourceId="com.adayo.settings:id/bt_switch").exists:
                self.smart_swipe_to_top()
            wifi=self.d(resourceId="com.adayo.settings:id/bt_switch").info["checked"] #获取wifi开关状态
            if wifi==False:
                self.d(resourceId="com.adayo.settings:id/bt_switch").click()
        except Exception as e:
            Logger.error(f"开启wifi异常: {e}")

    def close_wifi(self):
        """关闭wifi"""
        try:
            if not hasattr(self, "d"):
                #检测未初始化设备，自动执行devices_init
                self.devices_init()
            self.enter_app()
            time.sleep(0.5)
            self.d.xpath('//*[@resource-id="com.adayo.settings:id/design_navigation_view"]').get().scroll_to('//*[@text="连接"]')
            #self.d(scrollable=True).scroll.to(text="连接")
            time.sleep(0.5)
            self.d(text="连接").click()
            time.sleep(0.5)
            self.d(text="WiFi").click()
            if not self.d(resourceId="com.adayo.settings:id/bt_switch").exists:
                self.smart_swipe_to_top()
            wifi=self.d(resourceId="com.adayo.settings:id/bt_switch").info["checked"] #获取wifi开关状态
            if wifi==True:
                self.d(resourceId="com.adayo.settings:id/bt_switch").click()
        except Exception as e:
            Logger.error(f"关闭wifi异常: {e}")

    def iQiyi(self):
        """检查爱奇艺是否加载成功
        
        Return: 
            True:加载成功
            False:加载失败
        """
        try:
            if not hasattr(self, "d"):
                #检测未初始化设备，自动执行devices_init
                self.devices_init()
            self.enter_app(Apps.IQiyi)
            time.sleep(0.5)
            if self.d(resourceId="com.baidu.iov.dueros.videos:id/btn_empty_page").exists():
                self.d(resourceId="com.baidu.iov.dueros.videos:id/btn_empty_page").click()
                time.sleep(0.5)
                if self.d(resourceId="com.baidu.iov.faceos:id/un_sign_confirm").exists():
                    self.d(resourceId="com.baidu.iov.faceos:id/un_sign_confirm").click()
                time.sleep(0.5)
                if self.d(resourceId="com.baidu.iov.dueros.videos:id/leftButton").exists():
                    self.d(resourceId="com.baidu.iov.dueros.videos:id/leftButton").click()
                time.sleep(0.5)
                if self.d(resourceId="com.baidu.iov.dueros.videos:id/btn_left").exists():
                    self.d(resourceId="com.baidu.iov.dueros.videos:id/btn_left").click()
            if self.d(resourceId="com.baidu.iov.dueros.videos:id/leftButton").exists():
                self.d(resourceId="com.baidu.iov.dueros.videos:id/leftButton").click()
            if self.d(resourceId="com.baidu.iov.dueros.videos:id/btn_left").exists():
                self.d(resourceId="com.baidu.iov.dueros.videos:id/btn_left").click()
            time.sleep(3)
            count = 0
            iv=False
            tv=False
            btn=False
            while count < 3:
                time.sleep(1)
                iv=self.d(resourceId="com.baidu.iov.dueros.videos:id/iv_empty_page").exists()
                tv=self.d(resourceId="com.baidu.iov.dueros.videos:id/tv_empty_page").exists()
                btn=self.d(resourceId="com.baidu.iov.dueros.videos:id/btn_empty_page").exists()
                if iv or tv or btn:
                    self.d(resourceId="com.baidu.iov.dueros.videos:id/btn_empty_page").click()
                count += 1
            if iv or tv or btn:
                #print("爱奇艺加载失败")
                return False
            else:
                #print("爱奇艺加载成功")
                return True
        except Exception as e:
            Logger.error(f"加载爱奇艺异常: {e}")
            return False

    def digital_owners_manual_ex(self):
        """
        检查数字车主手册是否加载成功

        Return: 
            True:加载成功
            False:加载失败
        """
        try:
            if not hasattr(self, "d"):
                #检测未初始化设备，自动执行devices_init
                self.devices_init()
            command = f'adb shell dumpsys activity service com.android.car inject-vhal-event 0x11400400 0 0,520,0'#信号模拟发送P挡信号
            subp = Popen(command, stdout=PIPE, stderr=subprocess.STDOUT, shell=True)
            self.enter_app(Apps.digital_owners_manual)
            time.sleep(5)
            self.d(resourceId="com.ford.sync.electronicmanual:id/btn_view_manual").click()
            time.sleep(10)
            retry_count = 0
            while True:
                contentText=self.d(resourceId="com.ford.sync.electronicmanual:id/contentText").exists()
                Reload=self.d(resourceId="com.ford.sync.electronicmanual:id/leftButton", text="Reload").exists()
                if (contentText==True or Reload==True) and retry_count < 5:
                    time.sleep(5)
                    retry_count += 1
                else:
                    break
            if contentText==True or Reload==True:
                Logger.error(f"{Colors.RED}数字用户手册加载失败{Colors.RED}")
                return False
            
            else:
                Logger.info(f"{Colors.GREEN}数字用户手册加载成功{Colors.GREEN}")
                return True
        except Exception as e:
            Logger.error(f"检查数字车主手册加载状态异常: {e}")
            return False

    def connect_wifi_ex(self,name="智能软件内部"):
        """
        连接wifi

        Args:
            name: wifi名称
        """
        try:
            if not hasattr(self, "d"):
                #检测未初始化设备，自动执行devices_init
                self.devices_init()
            self.enter_app(Apps.Settings_ex)
            time.sleep(0.5)
            self.d.xpath('//*[@resource-id="com.adayo.settings:id/design_navigation_view"]').get().scroll_to('//*[@text="Connectivity"]')
            self.d(resourceId="com.adayo.settings:id/title", text="Connectivity").click()
            time.sleep(0.5)
            if self.d(description="WiFi").exists():
                self.d(description="WiFi").click()
            elif self.d(text="WiFi").exists():
                self.d(text="WiFi").click()
            elif self.d(text="Wi-Fi").exists():
                self.d(text="Wi-Fi").click()
            elif self.d.xpath('//*[@content-desc="Wi-Fi"]/android.widget.FrameLayout[1]').exists:
                self.d.xpath('//*[@content-desc="Wi-Fi"]/android.widget.FrameLayout[1]').click()
            if not self.d(resourceId="com.adayo.settings:id/wifi_switch_button").exists:
                self.smart_swipe_to_top_ex() #滑动到顶部
            time.sleep(0.5)
            self.d.xpath('//*[@resource-id="com.adayo.settings:id/wifi_setting_scroll"]').get().scroll_to(f'//*[@text="{name}"]')
            if not self.d(resourceId="com.adayo.settings:id/wifi_connected_show").exists():
                if  self.d(resourceId="com.adayo.settings:id/tv_main_title", text=f"{name}").exists:
                    self.d(resourceId="com.adayo.settings:id/tv_main_title", text=f"{name}").click()
                elif  self.d(resourceId="com.adayo.settings:id/tv_device_name", text=name).exists:
                    self.d(resourceId="com.adayo.settings:id/tv_device_name", text=name).click()
            elif self.d(resourceId="com.adayo.settings:id/tv_state").get_text() == "Not connected":
                if  self.d(resourceId="com.adayo.settings:id/tv_main_title", text=f"{name}").exists:
                    self.d(resourceId="com.adayo.settings:id/tv_main_title", text=f"{name}").click()
                elif  self.d(resourceId="com.adayo.settings:id/tv_device_name", text=name).exists:
                    self.d(resourceId="com.adayo.settings:id/tv_device_name", text=name).click()
            else:
                return True
            time.sleep(0.5)
            if self.d(resourceId="com.adayo.settings:id/editText").exists:
                self.d(resourceId="com.adayo.settings:id/editText").send_keys("zmrj6666")
                if not self.d(resourceId="com.baidu.car.input:id/iov_btn_enter").exists:
                    self.d(resourceId="com.adayo.settings:id/editText").click()
                time.sleep(0.5)
                if self.d(text="Listo").exists:
                    self.d(text="Listo").click()
                if self.d(text="Done").exists:
                    self.d(text="Done").click()
                elif self.d(resourceId="com.baidu.car.input:id/iov_btn_enter").exists:
                    self.d(resourceId="com.baidu.car.input:id/iov_btn_enter").click()
            n = 0
            while n < 10:
                time.sleep(1)
                self.d.xpath('//*[@resource-id="com.adayo.settings:id/wifi_setting_scroll"]').get().scroll_to('//*[@resource-id="com.adayo.settings:id/tv_state"]')
                if not self.d(resourceId="com.adayo.settings:id/tv_state").exists():
                    self.smart_swipe_to_top()
                    time.sleep(1)
                connected=self.d(resourceId="com.adayo.settings:id/wifi_connected_show").exists()#已连接成功图标是否存在
                state = self.d(resourceId="com.adayo.settings:id/tv_state").get_text()#连接状态获取"已连接"、"未连接"
                if connected==True or ("Not connected" not in state) :
                    #print("wifi连接成功")
                    return True
                elif connected != True and ("Not connected" in state):
                    n = n+1
            #print("wifi连接失败")
            return False

        except Exception as e:
            Logger.error(f"连接wifi异常: {e}")

    def disconnect_wifi_ex(self,name="智能软件内部"):
        """
        断开wifi

        Args:
            name: wifi名称
        """
        try:
            if not hasattr(self, "d"):
                #检测未初始化设备，自动执行devices_init
                self.devices_init()
            self.enter_app(Apps.Settings_ex)
            time.sleep(0.5)
            self.d.xpath('//*[@resource-id="com.adayo.settings:id/design_navigation_view"]').get().scroll_to('//*[@text="Connectivity"]')
            self.d(resourceId="com.adayo.settings:id/title", text="Connectivity").click()
            time.sleep(0.5)
            if self.d(description="WiFi").exists():
                self.d(description="WiFi").click()
            elif self.d(text="WiFi").exists():
                self.d(text="WiFi").click()
            elif self.d(text="Wi-Fi").exists():
                self.d(text="Wi-Fi").click()
            elif self.d.xpath('//*[@content-desc="Wi-Fi"]/android.widget.FrameLayout[1]').exists:
                self.d.xpath('//*[@content-desc="Wi-Fi"]/android.widget.FrameLayout[1]').click()
            if not self.d(resourceId="com.adayo.settings:id/wifi_switch_button").exists:
                self.smart_swipe_to_top() #滑动到顶部
            time.sleep(0.5)
            self.d.xpath('//*[@resource-id="com.adayo.settings:id/wifi_setting_scroll"]').get().scroll_to(f'//*[@text="{name}"]')
            if self.d(resourceId="com.adayo.settings:id/wifi_connected_show").exists():
                self.d(resourceId="com.adayo.settings:id/tv_device_name", text=name).click()
            time.sleep(3)
            connected=self.d(resourceId="com.adayo.settings:id/wifi_connected_show").exists()#已连接成功图标是否存在
            #state = self.d(resourceId="com.adayo.settings:id/tv_state").get_text()#连接状态获取"已连接"、"未连接"
            if connected==True:
                return True
        except Exception as e:
            Logger.error(f"断开wifi异常: {e}")

    def open_wifi_ex(self):
        """出口车型:开启wifi"""
        try:
            if not hasattr(self, "d"):
                #检测未初始化设备，自动执行devices_init
                self.devices_init()
            self.enter_app(Apps.Settings_ex)
            time.sleep(0.5)
            self.d.xpath('//*[@resource-id="com.adayo.settings:id/design_navigation_view"]').get().scroll_to('//*[@text="Connectivity"]')
            #d(scrollable=True).scroll.to(text="连接")
            time.sleep(0.5)
            self.d(text="Connectivity").click()
            time.sleep(0.5)
            if self.d(description="WiFi").exists():
                self.d(description="WiFi").click()
            elif self.d(text="WiFi").exists():
                self.d(text="WiFi").click()
            elif self.d(text="Wi-Fi").exists():
                self.d(text="Wi-Fi").click()
            elif self.d.xpath('//*[@content-desc="Wi-Fi"]/android.widget.FrameLayout[1]').exists:
                self.d.xpath('//*[@content-desc="Wi-Fi"]/android.widget.FrameLayout[1]').click()
            if not self.d(resourceId="com.adayo.settings:id/bt_switch").exists:
                self.smart_swipe_to_top_ex()
            wifi=self.d(resourceId="com.adayo.settings:id/bt_switch").info["checked"] #获取wifi开关状态
            if wifi==False:
                self.d(resourceId="com.adayo.settings:id/bt_switch").click()
        except Exception as e:
            Logger.error(f"开启wifi异常: {e}")

    def close_wifi_ex(self):
        "关闭wifi"
        try:
            if not hasattr(self, "d"):
                #检测未初始化设备，自动执行devices_init
                self.devices_init()
            self.enter_app(Apps.Settings_ex)
            time.sleep(0.5)
            self.d.xpath('//*[@resource-id="com.adayo.settings:id/design_navigation_view"]').get().scroll_to('//*[@text="Connectivity"]')
            #self.d(scrollable=True).scroll.to(text="连接")
            time.sleep(0.5)
            self.d(text="Connectivity").click()
            time.sleep(0.5)
            if self.d(description="WiFi").exists():
                self.d(description="WiFi").click()
            elif self.d(text="WiFi").exists():
                self.d(text="WiFi").click()
            elif self.d(text="Wi-Fi").exists():
                self.d(text="Wi-Fi").click()
            elif self.d.xpath('//*[@content-desc="Wi-Fi"]/android.widget.FrameLayout[1]').exists:
                self.d.xpath('//*[@content-desc="Wi-Fi"]/android.widget.FrameLayout[1]').click()
            if not self.d(resourceId="com.adayo.settings:id/bt_switch").exists:
                self.smart_swipe_to_top_ex()
            wifi=self.d(resourceId="com.adayo.settings:id/bt_switch").info["checked"] #获取wifi开关状态
            if wifi==True:
                self.d(resourceId="com.adayo.settings:id/bt_switch").click()
            time.sleep(2)
            if self.d(resourceId="com.adayo.settings:id/bt_switch").info["checked"]==False and self.get_network()==2:
                return True
            else:
                return False
        except Exception as e:
            Logger.error(f"关闭wifi异常: {e}")

    def control_ccs_ex(self):
        "开关CCS下的车辆连接功能按钮"
        try:
            if not hasattr(self, "d"):
                #检测未初始化设备，自动执行devices_init
                self.devices_init()
            self.enter_app(Apps.Settings_ex)
            time.sleep(0.5)
            self.d.xpath('//*[@resource-id="com.adayo.settings:id/design_navigation_view"]').get().scroll_to('//*[@text="Connectivity"]')    
            time.sleep(1)
            self.d.xpath('//*[@text="Connectivity"]').click()
            time.sleep(1)
            if not self.d.xpath('//*[@content-desc="Connected Vehicle Features"]/android.widget.FrameLayout[1]').exists:
                self.smart_swipe_to_top()
            self.d.xpath('//*[@content-desc="Connected Vehicle Features"]/android.widget.FrameLayout[1]').click()
            time.sleep(3)
            vehicle_connectivity='com.adayo.settings:id/bt_switch'
            if self.d(resourceId=vehicle_connectivity).info["checked"]:
                #如果开启则先关闭再开启
                self.d(resourceId=vehicle_connectivity).click()
                time.sleep(0.5)
                if self.d(resourceId="com.adayo.settings:id/leftButton", text="Continue").exists:
                    self.d(resourceId="com.adayo.settings:id/leftButton", text="Continue").click()
                elif self.d(resourceId="com.adayo.settings:id/leftButton").exists:
                    self.d(resourceId="com.adayo.settings:id/leftButton").click()
                elif self.d(text="Turn on Vehicle Connectivity?").exists:
                    self.d(resourceId="com.adayo.settings:id/leftButton", text="Continue").click()
                time.sleep(10)
                self.d(resourceId=vehicle_connectivity).click()
                time.sleep(1)
                if self.d(resourceId="com.adayo.settings:id/leftButton", text="Continue").exists:
                    self.d(resourceId="com.adayo.settings:id/leftButton", text="Continue").click()
                elif self.d(resourceId="com.adayo.settings:id/leftButton").exists:
                    self.d(resourceId="com.adayo.settings:id/leftButton").click()
                elif self.d(text="Turn on Vehicle Connectivity?").exists:
                    self.d(resourceId="com.adayo.settings:id/leftButton", text="Continue").click() 
                time.sleep(3)
            else:
                #如果关闭则开启
                self.d(resourceId=vehicle_connectivity).click()
                time.sleep(0.5)
                if self.d(resourceId="com.adayo.settings:id/leftButton", text="Continue").exists:
                    self.d(resourceId="com.adayo.settings:id/leftButton", text="Continue").click()
                elif self.d(resourceId="com.adayo.settings:id/leftButton").exists:
                    self.d(resourceId="com.adayo.settings:id/leftButton").click()
                elif self.d(text="Turn on Vehicle Connectivity?").exists:
                    self.d(resourceId="com.adayo.settings:id/leftButton", text="Continue").click()
            time.sleep(3)
        except Exception as e:
            Logger.error(f"开关CCS异常: {e}")

    def get_ccs_status_ex(self):
        """
        检测CCS是否加载成功

        Return:

            True:加载成功
            False:加载失败
        """
        try:
            if not hasattr(self, "d"):
                #检测未初始化设备，自动执行devices_init
                self.devices_init()
            self.enter_app(Apps.Settings_ex)
            time.sleep(0.5)
            self.d.xpath('//*[@resource-id="com.adayo.settings:id/design_navigation_view"]').get().scroll_to('//*[@text="Connectivity"]')    
            time.sleep(1)
            self.d.xpath('//*[@text="Connectivity"]').click()
            time.sleep(1)
            if not self.d.xpath('//*[@content-desc="Connected Vehicle Features"]/android.widget.FrameLayout[1]').exists():
                self.smart_swipe_to_top_ex()
            self.d.xpath('//*[@content-desc="Connected Vehicle Features"]/android.widget.FrameLayout[1]').click()
            time.sleep(30)
            if self.d.xpath('//*[@content-desc="Connected Vehicle Features"]/android.widget.FrameLayout[1]').exists():
                return True
            else:
                return False
        except Exception as e:
            Logger.error(f"检查CCS加载状态异常: {e}")
            return False

    def get_wifi_status_ex(self):
        """
        获取WiFi状态

        Return:

            0: WiFi已关闭
            1: WiFi已开启但未连接
            2: WiFi已连接
        """
        try:
            if not hasattr(self, "d"):
                #检测未初始化设备，自动执行devices_init
                self.devices_init()
            self.enter_app(Apps.Settings_ex)
            time.sleep(0.5)
            self.d.xpath('//*[@resource-id="com.adayo.settings:id/design_navigation_view"]').get().scroll_to('//*[@text="Connectivity"]')
            self.d(resourceId="com.adayo.settings:id/title", text="Connectivity").click()
            time.sleep(0.5)
            if self.d(description="WiFi").exists():
                self.d(description="WiFi").click()
            elif self.d(text="WiFi").exists():
                self.d(text="WiFi").click()
            elif self.d(text="Wi-Fi").exists():
                self.d(text="Wi-Fi").click()
            elif self.d.xpath('//*[@content-desc="Wi-Fi"]/android.widget.FrameLayout[1]').exists():
                self.d.xpath('//*[@content-desc="Wi-Fi"]/android.widget.FrameLayout[1]').click()
            self.smart_swipe_to_top()
            wifi=self.d(resourceId="com.adayo.settings:id/bt_switch").info["checked"] #获取wifi开关状态
            if wifi == True:
                #print("WiFi已开启")
                connected=self.d(resourceId="com.adayo.settings:id/wifi_connected_show").exists()#已连接成功图标是否存在
                #if not self.d(resourceId="com.adayo.settings:id/tv_state").exists():
                    #time.sleep(1)
                #state = self.d(resourceId="com.adayo.settings:id/tv_state").get_text()#连接状态获取"已连接"、"未连接"
                if connected==True:
                    #print("wifi连接成功")
                    return 2
                elif connected != True:
                    #print("未连接wifi")
                    return 1
            else:
                #print("WiFi已关闭")
                return 0
        except Exception as e:
            Logger.error(f"获取WiFi状态失败: {e}")

    def system_reset_ex(self):
        """系统复位"""
        try:
            if not hasattr(self, "d"):
                #检测未初始化设备，自动执行devices_init
                self.devices_init()
            self.enter_app(Apps.Settings_ex)
            time.sleep(0.5)
            self.d.xpath('//*[@resource-id="com.adayo.settings:id/design_navigation_view"]').get().scroll_to('//*[@text="System info"]')
            time.sleep(0.5)
            self.d(text="System info").click()
            time.sleep(0.5)
            self.d.xpath('//*[@content-desc="Update & reset"]/android.widget.FrameLayout[1]').click()
            time.sleep(0.5)
            if not self.d(text="Factory reset").exists():
                self.d.xpath('//*[@resource-id="com.adayo.settings:id/view_pager2"]/androidx.recyclerview.widget.RecyclerView[1]').get().scroll_to('//*[@text="Factory reset"]')
            self.d(text="Factory reset").click()
            time.sleep(0.5)
            self.d(resourceId="com.adayo.settings:id/leftButton").click()
            while True:
                if adb.device_list() == []:
                    print("系统正在重启中...")
                    time.sleep(1)
                else:
                    break
        except Exception as e:
            Logger.error(f"系统复位异常: {e}")

    def connect_wifi(self,name="智能软件内部"):
        """
        连接wifi

        Args:
            name: wifi名称
        """
        try:
            if not hasattr(self, "d"):
                #检测未初始化设备，自动执行devices_init
                self.devices_init()
            self.enter_app()
            time.sleep(0.5)
            self.d.xpath('//*[@resource-id="com.adayo.settings:id/design_navigation_view"]').get().scroll_to('//*[@text="连接"]')
            self.d(resourceId="com.adayo.settings:id/title", text="连接").click()
            time.sleep(0.5)
            self.d(description="WiFi").click()
            if not self.d(resourceId="com.adayo.settings:id/wifi_switch_button").exists():
                self.smart_swipe_to_top() #滑动到顶部
            time.sleep(0.5)
            self.d.xpath('//*[@resource-id="com.adayo.settings:id/wifi_setting_scroll"]').get().scroll_to(f'//*[@text="{name}"]')
            if not self.d(resourceId="com.adayo.settings:id/wifi_connected_show").exists():
                self.d(resourceId="com.adayo.settings:id/tv_device_name", text=name).click()
            elif self.d(resourceId="com.adayo.settings:id/tv_state").get_text() != "已连接":
                self.d(resourceId="com.adayo.settings:id/tv_device_name", text=name).click()
            else:
                return True
            time.sleep(0.5)
            if self.d(resourceId="com.adayo.settings:id/editText").exists():
                self.d(resourceId="com.adayo.settings:id/editText").send_keys("zmrj6666")
                if not self.d(resourceId="com.baidu.car.input:id/iov_btn_enter").exists():
                    self.d(resourceId="com.adayo.settings:id/editText").click()
                time.sleep(0.5)
                self.d(resourceId="com.baidu.car.input:id/iov_btn_enter").click()
            n = 0
            while n < 10:
                time.sleep(1)
                connected=self.d(resourceId="com.adayo.settings:id/wifi_connected_show").exists()#已连接成功图标是否存在
                if not self.d(resourceId="com.adayo.settings:id/tv_state").exists():
                    time.sleep(1)
                state = self.d(resourceId="com.adayo.settings:id/tv_state").get_text()#连接状态获取"已连接"、"未连接"
                if connected==True or ("已连接" in state) :
                    #print("wifi连接成功")
                    #return True
                    break
                elif connected != True and ("已连接" not in state):
                    n = n+1
            #print("wifi连接失败")
            return False

        except Exception as e:
            Logger.error(f"连接WiFi异常: {e}")

    def disconnect_wifi(self,name="智能软件内部"):
        """
        断开wifi连接

        Args:
            name: wifi名称
        """
        try:
            if not hasattr(self, "d"):
                #检测未初始化设备，自动执行devices_init
                self.devices_init()
            self.enter_app()
            time.sleep(0.5)
            self.d.xpath('//*[@resource-id="com.adayo.settings:id/design_navigation_view"]').get().scroll_to('//*[@text="连接"]')
            self.d(resourceId="com.adayo.settings:id/title", text="连接").click()
            time.sleep(0.5)
            self.d(description="WiFi").click()
            if not self.d(resourceId="com.adayo.settings:id/wifi_switch_button").exists():
                self.smart_swipe_to_top() #滑动到顶部
            time.sleep(0.5)
            self.d.xpath('//*[@resource-id="com.adayo.settings:id/wifi_setting_scroll"]').get().scroll_to(f'//*[@text="{name}"]')
            if self.d(resourceId="com.adayo.settings:id/wifi_connected_show").exists():
                self.d(resourceId="com.adayo.settings:id/tv_device_name", text=name).click()
            time.sleep(3)
            connected=self.d(resourceId="com.adayo.settings:id/wifi_connected_show").exists()#已连接成功图标是否存在
            #state = self.d(resourceId="com.adayo.settings:id/tv_state").get_text()#连接状态获取"已连接"、"未连接"
            if connected==True:
                return True
        except Exception as e:
            Logger.error(f"断开WiFi异常: {e}")

    def smart_swipe_to_top(self, scale=0.8, max_swipes=15):
        """
        使用百分比方式智能滑动到顶部
        Args:
            scale: 每次滑动的比例（0-1之间），越大滑动距离越长
            max_swipes: 最大滑动次数
        """
        try:
            if not hasattr(self, "d"):
                #检测未初始化设备，自动执行devices_init
                self.devices_init()
            prev_hierarchy = None
            same_count = 0
            for i in range(max_swipes):
                # 滑动前获取页面结构
                current_hierarchy = self.d.dump_hierarchy()
                
                # 检测是否到达顶部
                if prev_hierarchy == current_hierarchy:
                    same_count += 1
                    if same_count >= 2:  # 连续两次页面无变化，认为已到顶部
                        break
                else:
                    same_count = 0 
                # 执行向上滑动（滑动屏幕scale比例的距离）
                self.d.swipe_ext("down", scale=scale)
                time.sleep(0.3)
                prev_hierarchy = current_hierarchy
        except Exception as e:
            Logger.error(f"滑动过程中发生错误: {e}")

    def get_wifi_status(self):
        """
        获取WiFi状态
        Return:

            返回wifi状态
            0: WiFi已关闭
            1: WiFi已开启但未连接
            2: WiFi已连接
            3: 执行异常
        """
        try:
            if not hasattr(self, "d"):
                #检测未初始化设备，自动执行devices_init
                self.devices_init()
            self.enter_app()
            time.sleep(0.5)
            self.d.xpath('//*[@resource-id="com.adayo.settings:id/design_navigation_view"]').get().scroll_to('//*[@text="连接"]')
            self.d(resourceId="com.adayo.settings:id/title", text="连接").click()
            time.sleep(0.5)
            self.d(description="WiFi").click()
            self.smart_swipe_to_top()
            wifi=self.d(resourceId="com.adayo.settings:id/bt_switch").info["checked"] #获取wifi开关状态
            if wifi == True:
                #print("WiFi已开启")
                connected=self.d(resourceId="com.adayo.settings:id/wifi_connected_show").exists()#已连接成功图标是否存在
                if not self.d(resourceId="com.adayo.settings:id/tv_state").exists():
                    time.sleep(1)
                state = self.d(resourceId="com.adayo.settings:id/tv_state").get_text()#连接状态获取"已连接"、"未连接"
                if connected==True or ("已连接" in state) :
                    #print("wifi连接成功")
                    return 2
                elif connected != True and ("已连接" not in state):
                    #print("未连接wifi")
                    return 1
            else:
                #print("WiFi已关闭")
                return 0
        except Exception as e:
            Logger.error(f"获取WiFi状态失败: {e}")
            return 3
    
    def control_ccs(self):
        """开关CCS下的车辆连接功能按钮"""
        try:
            if not hasattr(self, "d"):
                #检测未初始化设备，自动执行devices_init
                self.devices_init()
            self.enter_app()
            time.sleep(0.5)
            self.d.xpath('//*[@resource-id="com.adayo.settings:id/design_navigation_view"]').get().scroll_to('//*[@text="连接"]')
            #d(scrollable=True).scroll.to(text="连接")
            time.sleep(0.5)
            self.d(text="连接").click()
            self.d(text="车辆互联").click()
            if not self.d(resourceId="com.adayo.settings:id/tv_item_content", text="车辆连接功能").exists():
                self.smart_swipe_to_top()
            time.sleep(3)
            if not self.d(resourceId="com.adayo.settings:id/bt_switch").info["checked"]:
                self.d(resourceId="com.adayo.settings:id/fl_switch_click").click()
                time.sleep(0.5)
                self.d(resourceId="com.adayo.settings:id/leftButton", text="继续").click()
                time.sleep(10)
            self.d(resourceId="com.adayo.settings:id/fl_switch_click").click()
            time.sleep(0.5)
            self.d(resourceId="com.adayo.settings:id/leftButton", text="继续").click()
            time.sleep(12)
            self.d(resourceId="com.adayo.settings:id/fl_switch_click").click()
            time.sleep(0.5)
            if self.d(resourceId="com.adayo.settings:id/leftButton", text="继续").exists:
                self.d(resourceId="com.adayo.settings:id/leftButton", text="继续").click()
        except Exception as e:
            Logger.error(f"开关CCS异常: {e}")

    def get_ccs_status(self):
        """检测CCS是否加载成功
        Return:

            True:加载成功
            False:加载失败
        """
        try:
            if not hasattr(self, "d"):
                #检测未初始化设备，自动执行devices_init
                self.devices_init()
            self.enter_app()
            time.sleep(1)
            self.d.xpath('//*[@resource-id="com.adayo.settings:id/design_navigation_view"]').get().scroll_to('//*[@text="连接"]')    
            time.sleep(1)
            self.d.xpath('//*[@text="连接"]').click()
            time.sleep(1)
            self.d.xpath('//*[@text="车辆互联"]').click()
            time.sleep(30)
            if self.d.xpath('//*[@text="车辆连接功能"]').exists:
                return True
            else:
                return False
        except Exception as e:
            Logger.error(f"{Colors.RED}检测CCS是否加载成功异常{Colors.RED}")
            return False

    def system_reset(self):
        "系统复位"
        try:
            if not hasattr(self, "d"):
                #检测未初始化设备，自动执行devices_init
                self.devices_init()
            self.enter_app()
            time.sleep(0.5)
            self.d.xpath('//*[@resource-id="com.adayo.settings:id/design_navigation_view"]').get().scroll_to('//*[@text="关于系统"]')
            #d(scrollable=True).scroll.to(text="关于系统")
            time.sleep(0.5)
            self.d(text="关于系统").click()
            time.sleep(0.5)
            self.d(text="更新与复位").click()
            time.sleep(0.5)
            #d(scrollable=True).scroll.to(text="系统复位")
            #scroll_view = d(resourceId="com.adayo.settings:id/fragment_container_zl")
            if not self.d(text="系统复位").exists():
                self.d.xpath('//*[@resource-id="com.adayo.settings:id/view_pager2"]/androidx.recyclerview.widget.RecyclerView[1]').get().scroll_to('//*[@text="系统复位"]')
                #d.swipe(50, 30 + 200, 30, 30, duration = 0.2) #
                #scroll_view.fling.vert.forward()
            self.d(text="系统复位").click()
            time.sleep(0.5)
            self.d(resourceId="com.adayo.settings:id/leftButton").click()
            while True:
                if adb.device_list() == []:
                    print("系统正在重启中...")
                    time.sleep(1)
                else:
                    break
        except Exception as e:
            if "kill process(ps): uiautomator" in e:
                self.adbdevices.shell('adb shell /data/local/tmp/atx-agent server -d --stop')
                self.adbdevices.shell('adb shell /data/local/tmp/atx-agent server -d')
            print(e)

    def get_network(self):
        """
        获取网卡信息，获取指定网络,若返回值等于3说明APN1/VPN2/WIFI网卡还在,
        若返回2说明APN1/VPN2网卡还在，若返回值小于2说明异常

        Return:
            result: 网卡列表
            result_rmnet: 网卡数量 
        """
        try:
            rmnet = self.adbdevices.shell("ifconfig | grep -i rmnet_data")
            pattern = r"rmnet_data\d{1,2} Link encap:"
            result= re.findall(pattern,rmnet)
            result_rmnet = len(result)
            if result == None:
                result = 0
                result_rmnet = 0
            """
            if result_rmnet == 0:
                Logger.error(f"{Colors.RED}APN1/VPN2/WIFI网卡异常，当前网卡数量：{result}{Colors.RED}")
            else:
                Logger.info(f"{Colors.GREEN}APN1/VPN2/WIFI网卡正常，当前网卡数量：{result}{Colors.GREEN}")
            """
            return result,result_rmnet
        except Exception as e:
            print(e)

    def reset_cm_services(self):
        """重启CM服务,重启后检查APN1/VPN2/WIFI网卡是否正常"""
        try:
            cmd=self.adbdevices.shell('ps -ef |grep -i connectivitymgr')
            pattern = r'^wir\s+(\d+)\s+\d+'
            match = re.search(pattern, cmd, re.MULTILINE)
            if match:
                Logger.info(f"进程启动成功ID: {match.group(1)}")
                time.sleep(1)
                self.adbdevices.shell(f'kill -6 {match.group(1)}')
            else:
                Logger.error("进程未启动")
            time.sleep(5)
            cmd=self.adbdevices.shell('ps -ef |grep -i connectivitymgr')
            pattern = r'^wir\s+(\d+)\s+\d+'
            match = re.search(pattern, cmd, re.MULTILINE)
            if match:
                Logger.info(f"进程重启成功ID: {match.group(1)}")
            else:
                Logger.error("进程重启失败")
        except Exception as e:
            print(e)

    def screencap_display(self):
        """截图"""
        try:
            now_time = datetime.datetime.now()
            file_name = now_time.strftime("%Y%m%d%H%M%S")
            command = f'adb exec-out screencap -p > ./screenshot_{file_name}.png'
            subp = Popen(command, stdout=PIPE, stderr=subprocess.STDOUT, shell=True)
            Logger.info(f"截图成功，文件名./screenshot_{file_name}.png")
        except Exception as e:
            Logger.error(f"截图失败: {e}")

    def smart_swipe_to_top_ex(self):
        """
        滑动到顶部
        Args:
            scale: 每次滑动的比例(0-1之间)，越大滑动距离越长
            max_swipes: 最大滑动次数
        """
        try:
            if not hasattr(self, "d"):
                #检测未初始化设备，自动执行devices_init
                self.devices_init()
            scroll_view = self.d.xpath('//*[@resource-id="com.adayo.settings:id/wifi_setting_scroll"]').get()
            # 先滚动到顶部
            while not self.d(resourceId="com.adayo.settings:id/wifi_switch_button").exists():
                scroll_view.scroll("down")
        except Exception as e:
            Logger.error(f"滑动过程中发生错误: {e}")
            
    def scroll_search(self,sliding, target):
        """
        滑动查找指定控件
        Args:
            sliding: 被滑动控件,例如'//*[@resource-id="com.adayo.settings:id/wifi_setting_scroll"]'
            target: 目标控件,例如'//*[@resource-id="com.adayo.settings:id/wifi_setting_scroll"]'
        """
        try:
            if not hasattr(self, "d"):
                #检测未初始化设备，自动执行devices_init
                self.devices_init()
            scroll_view = self.d.xpath(sliding).get()
            while not self.d.xpath(target).exists:
                scroll_view.scroll("down")
                time.sleep(0.5)
            while not self.d.xpath(target).exists:
                scroll_view.scroll("up")
                time.sleep(0.5)
        except Exception as e:
            Logger.error(f"滑动查找过程中发生错误: {e}")

    def get_device_info(self):
        """获取设备信息"""
        try:
            if not hasattr(self, "d"):
                #检测未初始化设备，自动执行devices_init
                self.devices_init()
            device_info = self.d.device_info
            Logger.info(f"设备信息:\n{device_info}")
            return device_info
        except Exception as e:
            Logger.error(f"获取设备信息失败: {e}")
            return {'serial': 'NA', 'sdk': 'NA', 'brand': 'NA', 'model': 'NA', 'arch': 'NA', 'version': "NA"}

class TCULogCollector:
    def __init__(self):
        self.process = None
        self.tcu_flag = False
        self.read_thread = None
        
    def start_collection(self):
        """启动日志采集"""
        if self.process is not None and self.process.poll() is None:
            Logger.info("TCU日志已在采集中")
            return
            
        HOST = '10.2.0.1'
        PORT = 10515
        device = '10.1.0.2'
        command = f'fdpclient -s {HOST} -p {PORT} -w tunnel {device} logcat'
        
        self.tcu_flag = True
        self.process = Popen(command, stdout=PIPE, stderr=subprocess.STDOUT,
                            shell=True, text=True, bufsize=1)
        
        # 启动读取线程
        self.read_thread = threading.Thread(target=self._read_logs, daemon=True)
        self.read_thread.start()
        Logger.info("TCU日志采集已启动")
    
    def _read_logs(self):
        """持续读取日志输出"""
        now_time = datetime.datetime.now()
        file_name = now_time.strftime("%Y%m%d%H%M%S")
        with open(f'TCU_{file_name}.txt', 'a', encoding='utf-8') as file:
            for line in iter(self.process.stdout.readline, ''):
                if not self.tcu_flag:
                    break
                if line:
                    file.write( line +'\n')
                    Logger.info(line.strip())
    
    def stop_collection(self):
        """停止日志采集"""
        self.tcu_flag = False
        
        if self.process and self.process.poll() is None:
            Logger.info("正在停止TCU日志采集...")
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            self.process = None
            Logger.info("TCU日志采集已停止")
        
        # 等待读取线程结束
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=1)

class ECGLogCollector:
    def __init__(self):
        self.process = None
        self.ecg_flag = False
        self.read_thread = None
        
    def start_collection(self):
        """启动日志采集"""
        if self.process is not None and self.process.poll() is None:
            Logger.info("ECG日志已在采集中")
            return
            
        HOST = '10.2.0.1'
        PORT = 10515
        command = f'fdpclient -s {HOST} -p {PORT} -w fnvlog'
        self.ecg_flag = True
        self.process = Popen(command, stdout=PIPE, stderr=subprocess.STDOUT,
                            shell=True, text=True, bufsize=1)
        
        # 启动读取线程
        self.read_thread = threading.Thread(target=self._read_logs, daemon=True)
        self.read_thread.start()
        Logger.info("ECG日志采集已启动")
    
    def _read_logs(self):
        """持续读取日志输出"""
        now_time = datetime.datetime.now()
        file_name = now_time.strftime("%Y%m%d%H%M%S")
        with open(f'ECG_{file_name}.txt', 'a', encoding='utf-8') as file:
            for line in iter(self.process.stdout.readline, ''):
                if not self.ecg_flag:
                    break
                if line:
                    file.write( line +'\n')
                    Logger.info(line.strip())
    
    def stop_collection(self):
        """停止日志采集"""
        self.ecg_flag = False
        
        if self.process and self.process.poll() is None:
            Logger.info("正在停止ECG日志采集...")
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            self.process = None
            Logger.info("ECG日志采集已停止")
        
        # 等待读取线程结束
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=1)

ecg_flag = True
tcu_flag = True
def ECG_logs():
    #通过radmoon获取ECG日志
    global ecg_flag
    HOST = '10.2.0.1'
    PORT = 10515
    command = f'fdpclient -s {HOST} -p {PORT} -w fnvlog'
    Logger.info("正在获取ECG日志...")
    while True:
        if ecg_flag == True:
            subp = Popen(command, stdout=PIPE, stderr=subprocess.STDOUT,
                        shell=True)
            outs = subp.stdout.readline()
            Logger.info(outs.decode('utf-8'))
        else:
            continue

def TCU_logs():
    #通过radmoon获取TCU日志
    global tcu_flag
    HOST = '10.2.0.1'
    PORT = 10515
    device = '10.1.0.2'
    command = f'fdpclient -s {HOST} -p {PORT} -w tunnel {device} logcat'
    Logger.info("正在获取TCU日志...")
    while True:
        if tcu_flag == True:
            subp = Popen(command, stdout=PIPE, stderr=subprocess.STDOUT,
                        shell=True)
            outs = subp.stdout.readline()
            Logger.info(outs.decode('utf-8'))
        else:
            continue

Logger()
"""
ecglogs = threading.Thread(target=ECG_logs)
ecglogs.start()
tculogs = threading.Thread(target=TCU_logs)
tculogs.start()
"""

if __name__ == "__main__":
    """
    can_type = CanMessageType.CANFD
    can_bitrate = CanBitRate.CAN_500K
    can_fd_bitrate = CanFDDataBitRate.CANFD_2M
    print(can_type,can_bitrate,can_fd_bitrate)
    send_can_start_device(ZCAN_USBCANFD_200U, CanChannelNum.CAN1, can_bitrate, can_fd_bitrate, can_type)
    
    # 使用示例
    tcu_collector = TCULogCollector()
    # 启动采集
    tcu_collector.start_collection()
    # ... 执行其他操作 ...
    # 停止采集
    tcu_collector.stop_collection()
    
    ecg_collector = ECGLogCollector()
    # 启动采集
    ecg_collector.start_collection()
    # ... 执行其他操作 ...
    time.sleep(10)  # 模拟其他操作的时间
    # 停止采集
    ecg_collector.stop_collection()
    """
    #cantest=CanMessage()
    #cantest.carpwer_change(CarPwer.Standby)
    #cantest.carpwer_change(CarPwer.STR)
    #cantest.carpwer_change(CarPwer.Sleep)
    androidtest = AndroidTest()
    androidtest.online_music()
    #androidtest.control_ccs()
    #androidtest.connect_wifi()
    #ECG = ECGLogCollector()
    #TCU = TCULogCollector()
    #ECG.start_collection()
    #TCU.start_collection()
    pass