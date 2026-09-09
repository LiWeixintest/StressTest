from libs.logger.logger import Logger
from adbutils import adb
from wir import *
import time


class MainTest(AndroidTest,PowerSupplyControl,CanMessage,TCULogCollector,ECGLogCollector):
   
    #国内fnv2
    def reopen_wifi_wifi_test(self,count=600):
        """已连接wifi状态下,开关wifi测试"""
        try:
            while True:
                if adb.device_list() == []:
                    time.sleep(1)
                else:
                    break
            self.open_wifi()
            time.sleep(0.5)
            self.connect_wifi()
            index = 0
            while index < count:
                index += 1
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------开关WIFI测试,测试次数{index}时间{date}------------------")
                self.close_wifi()
                time.sleep(1)
                self.open_wifi()
                time.sleep(15)
                wifi_status = self.get_wifi_status() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.online_music()  and self.account()# 是否可以访问网络
                #Logger.info(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                if wifi_status ==2 and network_card[1] ==3 and network_status == True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关wifi测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次开关wifi测试失败{Colors.RED}")      
        except Exception as e:
            Logger.error(f"开关wifi发送异常: {e}")
            self.screencap_display()

    def reopen_ccs_wifi_test(self,count=600):
        """已连接wifi状态下,开关ccs测试"""
        try:
            self.open_wifi()
            time.sleep(0.5)
            self.connect_wifi()
            index = 0
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------开关CCS测试,测试次数{index}时间{date}------------------")
                time.sleep(1)
                self.control_ccs()
                time.sleep(30)
                ccs_status=self.get_ccs_status()# 获取ccs状态
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.online_music()  and self.account()# 是否可以访问网络
                if wifi_status ==2 and network_card[1] ==3 and network_status == True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次开关ccs测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"开关ccs发送异常: {e}")
            self.screencap_display()
    
    def reopen_wifi_no_wifi_test(self,count=600):
        """未连接wifi状态下,开关wifi测试"""
        try:
            index = 0
            self.disconnect_wifi()
            self.close_wifi()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------开关WIFI测试,测试次数{index}时间{date}------------------")
                self.open_wifi()
                time.sleep(1)
                self.close_wifi()
                time.sleep(30)
                wifi_status = self.get_wifi_status() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.online_music()  and self.account()# 是否可以访问网络
                iqiyi_stus=self.iQiyi()
                if wifi_status ==0 and network_card[1] ==2 and network_status == True and iqiyi_stus == True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关wifi测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态:{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次开关wifi测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"开关wifi发送异常: {e}")
            self.screencap_display()

    def reopen_ccs_no_wifi_test(self,count=600):
        """未连接wifi状态下,开关ccs测试"""
        try:
            index = 0
            self.close_wifi()
            #self.disconnect_wifi()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------开关CCS测试,测试次数{index}时间{date}------------------")
                self.disconnect_wifi()
                time.sleep(1)
                self.control_ccs()
                time.sleep(30)
                ccs_status=self.get_ccs_status()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.online_music()  and self.account()# 是否可以访问网络
                iqiyi_stus=self.iQiyi()
                if wifi_status ==0 and network_card[1] ==2 and network_status == True and iqiyi_stus == True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态:{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次开关ccs测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"开关wifi发送异常: {e}")
            self.screencap_display()
    
    def reconnect_wifi_test(self,count=600):
        """重连wifi测试"""
        try:
            index = 0
            self.open_wifi()
            self.connect_wifi()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------重连WIFI测试,测试次数{index}时间{date}------------------")  
                self.disconnect_wifi()
                self.connect_wifi()
                time.sleep(30)
                wifi_status = self.get_wifi_status() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.online_music()  and self.account()# 是否可以访问网络
                if wifi_status ==2 and network_card[1] ==3 and network_status == True:
                    Logger.info(f"{Colors.GREEN}第{index}次重连wifi测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次重连wifi测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"重连wifi发送异常: {e}")
            self.screencap_display()

    def system_reset_wifi_test(self,count=600):
        """已连接wifi测试情况下系统重置"""
        try:
            index = 0
            self.open_wifi()
            self.connect_wifi()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------重置系统,测试次数{index}时间{date}------------------")
                self.system_reset()
                time.sleep(90)
                self.open_wifi()
                time.sleep(1)
                self.connect_wifi()
                time.sleep(1)
                ccs_status=self.get_ccs_status()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.online_music()  and self.account()# 是否可以访问网络
                if wifi_status == 2 and network_card[1] == 3 and network_status == True:
                    Logger.info(f"{Colors.GREEN}第{index}次重重置系统测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次重连重置系统测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"重连重置系统发送异常: {e}")
            self.screencap_display()
    
    def system_reset_no_wifi_test(self,count=600):
        """未连接wifi测试情况下系统重置"""
        try:
            index = 0
            self.close_wifi()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------重置系统,测试次数{index}时间{date}------------------")
                self.system_reset()
                time.sleep(90)
                time.sleep(1)
                ccs_status=self.get_ccs_status()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.online_music()  and self.account()# 是否可以访问网络
                iqiyi_stus=self.iQiyi()
                if wifi_status == 1 and network_card[1] == 2 and network_status == True and iqiyi_stus == True:
                    Logger.info(f"{Colors.GREEN}第{index}次重重置系统测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次重连重置系统测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"重连重置系统发送异常: {e}")
            self.screencap_display()

    def power_reset_wifi_test(self,count=600):
        """已连接wifi情况下电源重启测试"""
        try:
            index = 0
            self.open_wifi()
            self.connect_wifi()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------电源重启测试,测试次数{index}时间{date}------------------")
                self.stop_power()
                time.sleep(1)
                self.start_power()
                time.sleep(90)
                ccs_status=self.get_ccs_status()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.online_music()  and self.account()# 是否可以访问网络
                if wifi_status == 2 and network_card[1] == 3 and network_status == True:
                    Logger.info(f"{Colors.GREEN}第{index}次电源重启测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次电源重启测试测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"电源重启测试异常: {e}")
            self.screencap_display()
    
    def power_reset_no_wifi_test(self,count=600):
        """未连接wifi测试情况下电源重启测试"""
        try:
            index = 0
            self.close_wifi()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------电源重启测试次数{index}时间{date}------------------")
                self.stop_power()
                time.sleep(1)
                self.start_power()
                time.sleep(90)
                ccs_status=self.get_ccs_status()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.online_music()  and self.account()# 是否可以访问网络
                iqiyi_stus=self.iQiyi()
                if wifi_status == 1 and network_card[1] == 2 and network_status == True and iqiyi_stus==True:
                    Logger.info(f"{Colors.GREEN}第{index}次电源重启测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次电源重启测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"电源重启测试异常: {e}")
            self.screencap_display()

    def standby_wifi_test(self,count=600):
        """已连接wifi情况下standby模式测试"""
        try:
            index = 0
            self.open_wifi()
            self.connect_wifi()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------standby模式测试,测试次数{index}时间{date}------------------")
                set_power_status(2)
                time.sleep(3)
                set_power_status(1)
                time.sleep(90)
                ccs_status=self.get_ccs_status()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.online_music()  and self.account()# 是否可以访问网络
                if wifi_status == 2 and network_card[1] == 3 and network_status == True:
                    Logger.info(f"{Colors.GREEN}第{index}次standby模式测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次standby模式测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"standby模式测试异常: {e}")
            self.screencap_display()
    
    def standby_no_wifi_test(self,count=600):
        """未连接wifi情况下standby模式测试"""
        try:
            index = 0
            self.close_wifi()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------standby模式测试,测试次数{index}时间{date}------------------")
                set_power_status(2)
                time.sleep(3)
                set_power_status(1)
                time.sleep(90)
                ccs_status=self.get_ccs_status()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.online_music()  and self.account()# 是否可以访问网络
                iqiyi_stus=self.iQiyi()
                if wifi_status == 2 and network_card[1] == 3 and network_status == True and iqiyi_stus==True:
                    Logger.info(f"{Colors.GREEN}第{index}次standby模式测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次standby模式测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"standby模式测试异常: {e}")
            self.screencap_display()
    
    def ecg_reset_wifi_test(self,count=600):
        """已连接wifi情况下ECG测试"""
        try:
            index = 0
            self.open_wifi()
            self.connect_wifi()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------ECG测试,测试次数{index}时间{date}------------------")
                self.ecg_reset()
                time.sleep(90)
                ccs_status=self.get_ccs_status()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.online_music()  and self.account()# 是否可以访问网络
                if wifi_status == 2 and network_card[1] == 3 and network_status == True:
                    Logger.info(f"{Colors.GREEN}第{index}次ECG测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次ECG测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"ECG测试异常: {e}")
            self.screencap_display()
    
    def ecg_reset_no_wifi_test(self,count=600):
        """已连接wifi情况下ECG测试"""
        try:
            index = 0
            self.close_wifi()
            self.disconnect_wifi()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------ECG测试,测试次数{index}时间{date}------------------")
                self.ecg_reset()
                time.sleep(90)
                ccs_status=self.get_ccs_status()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.online_music()  and self.account()# 是否可以访问网络
                iqiyi_stus=self.iQiyi()
                if wifi_status == 1 and network_card[1] == 2 and network_status == True and iqiyi_stus==True:
                    Logger.info(f"{Colors.GREEN}第{index}次ECG测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次ECG测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"ECG测试异常: {e}")
            self.screencap_display()
    
    def tcu_reset_wifi_test(self,count=600):
        """已连接wifi情况下TCU测试"""
        try:
            index = 0
            self.open_wifi()
            self.connect_wifi()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------TCU测试,测试次数{index}时间{date}------------------")
                self.tcu_reset()
                time.sleep(90)
                ccs_status=self.get_ccs_status()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.online_music()  and self.account()# 是否可以访问网络
                if wifi_status == 2 and network_card[1] == 3 and network_status == True:
                    Logger.info(f"{Colors.GREEN}第{index}次TCU测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次TCU测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"TCU测试异常: {e}")
            self.screencap_display()

    def tcu_reset_no_wifi_test(self,count=600):
        """已连接wifi情况下TCU测试"""
        try:
            index = 0
            self.close_wifi()
            self.disconnect_wifi()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------TCU测试,测试次数{index}时间{date}------------------")
                self.tcu_reset()
                time.sleep(90)
                ccs_status=self.get_ccs_status()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.online_music()  and self.account()# 是否可以访问网络
                iqiyi_stus=self.iQiyi()
                if wifi_status == 1 and network_card[1] == 2 and network_status == True and iqiyi_stus==True:
                    Logger.info(f"{Colors.GREEN}第{index}次TCU测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次TCU测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"TCU测试异常: {e}")
            self.screencap_display()

    def ivi_reset_wifi_test(self,count=600):
        """已连接wifi情况下IVI测试"""
        try:
            index = 0
            self.open_wifi()
            self.connect_wifi()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------IVI测试,测试次数{index}时间{date}------------------")
                self.ivi_reset()
                time.sleep(90)
                ccs_status=self.get_ccs_status()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.online_music()  and self.account()# 是否可以访问网络
                if wifi_status == 2 and network_card[1] == 3 and network_status == True:
                    Logger.info(f"{Colors.GREEN}第{index}次IVI测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次IVI测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"IVI测试异常: {e}")
            self.screencap_display()

    def ivi_reset_no_wifi_test(self,count=600):
        """未连接wifi情况下IVI测试"""
        try:
            index = 0
            self.close_wifi()
            self.disconnect_wifi()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------IVI测试,测试次数{index}时间{date}------------------")
                self.ivi_reset()
                time.sleep(90)
                ccs_status=self.get_ccs_status()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.online_music()  and self.account()# 是否可以访问网络
                iqiyi_stus=self.iQiyi()
                if wifi_status == 1 and network_card[1] == 2 and network_status == True and iqiyi_stus==True:
                    Logger.info(f"{Colors.GREEN}第{index}次IVI测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次IVI测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"IVI测试异常: {e}")
            self.screencap_display()

    def str_wifi_test(self,count=600):
        """已连接wifi情况下STR休眠唤醒测试"""
        try:
            index = 0
            self.open_wifi()
            self.connect_wifi()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------STR休眠唤醒测试,测试次数{index}时间{date}------------------")
                set_power_status(2)
                time.sleep(3)
                set_power_status(0)
                time.sleep(70)
                set_power_status(1)
                time.sleep(90)
                ccs_status=self.get_ccs_status()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.online_music()  and self.account()# 是否可以访问网络
                iqiyi_stus=self.iQiyi()
                if wifi_status == 2 and network_card[1] == 2 and network_status == True and iqiyi_stus==True:
                    Logger.info(f"{Colors.GREEN}第{index}次STR休眠唤醒测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次STR休眠唤醒测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"STR休眠唤醒测试异常: {e}")
            self.screencap_display()
    
    def str_no_wifi_test(self,count=600):
        """未连接wifi情况下STR休眠唤醒测试"""
        try:
            index = 0
            self.close_wifi()
            self.disconnect_wifi()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------STR休眠唤醒测试,测试次数{index}时间{date}------------------")
                set_power_status(2)
                time.sleep(3)
                set_power_status(0)
                time.sleep(70)
                set_power_status(1)
                time.sleep(90)
                ccs_status=self.get_ccs_status()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.online_music()  and self.account()# 是否可以访问网络
                iqiyi_stus=self.iQiyi()
                if wifi_status == 1 and network_card[1] == 2 and network_status == True and iqiyi_stus==True:
                    Logger.info(f"{Colors.GREEN}第{index}次STR休眠唤醒测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次STR休眠唤醒测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"STR休眠唤醒测试异常: {e}")
            self.screencap_display()

    def sleep_wifi_test(self,count=600):
        """已连接wifi情况下深度休眠唤醒测试"""
        try:
            index = 0
            self.open_wifi()
            self.connect_wifi()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------深度休眠唤醒测试,测试次数{index}时间{date}------------------")
                set_power_status(2)
                time.sleep(5)
                set_power_status(0)
                time.sleep(150)
                set_power_status(1)
                time.sleep(90)
                ccs_status=self.get_ccs_status()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.online_music()  and self.account()# 是否可以访问网络
                iqiyi_stus=self.iQiyi()
                if wifi_status == 2 and network_card[1] == 2 and network_status == True and iqiyi_stus==True:
                    Logger.info(f"{Colors.GREEN}第{index}次深度休眠唤醒测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次深度休眠唤醒测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"深度休眠唤醒测试异常: {e}")
            self.screencap_display()
    
    def sleep_no_wifi_test(self,count=600):
        """未连接wifi情况下深度休眠唤醒测试"""
        try:
            index = 0
            self.close_wifi()
            self.disconnect_wifi()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------深度休眠唤醒测试,测试次数{index}时间{date}------------------")
                set_power_status(2)
                time.sleep(5)
                set_power_status(0)
                time.sleep(150)
                set_power_status(1)
                time.sleep(90)
                ccs_status=self.get_ccs_status()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.online_music()  and self.account()# 是否可以访问网络
                iqiyi_stus=self.iQiyi()
                if wifi_status == 1 and network_card[1] == 2 and network_status == True and iqiyi_stus==True:
                    Logger.info(f"{Colors.GREEN}第{index}次深度休眠唤醒测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次深度休眠唤醒测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"深度休眠唤醒测试异常: {e}")
            self.screencap_display()

    #国内fnv3
    def power_reset_no_wifi_test_fnv3(self,count=600):
        """未连接wifi测试情况下电源重启测试"""
        try:
            index = 0
            self.close_wifi()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------电源重启测试次数{index}时间{date}------------------")
                self.stop_power()
                time.sleep(1)
                self.start_power()
                time.sleep(90)
                time.sleep(1)
                wifi_status = self.get_wifi_status() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.online_music()  and self.account()# 是否可以访问网络
                iqiyi_stus=self.iQiyi()
                if wifi_status == 1 and network_card[1] == 2 and network_status == True and iqiyi_stus==True:
                    Logger.info(f"{Colors.GREEN}第{index}次电源重启测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次电源重启测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"电源重启测试异常: {e}")
            self.screencap_display()

    def system_reset_no_wifi_test_fnv3(self,count=600):
        """未连接wifi测试情况下系统重置"""
        try:
            index = 0
            self.close_wifi()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------重置系统,测试次数{index}时间{date}------------------")
                self.system_reset()
                time.sleep(90)
                time.sleep(1)
                wifi_status = self.get_wifi_status() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.online_music()  and self.account()# 是否可以访问网络
                iqiyi_stus=self.iQiyi()
                if wifi_status == 1 and network_card[1] == 2 and network_status == True and iqiyi_stus == True:
                    Logger.info(f"{Colors.GREEN}第{index}次重重置系统测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次重连重置系统测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"重连重置系统发送异常: {e}")
            self.screencap_display()

    def reopen_ccs_no_wifi_test_fnv3(self,count=600):
        """fnv3车型(707和625)未连接wifi状态下,开关ccs测试,查看vlan1和vlan2是否能正常上网"""
        try:
            index = 0
            #self.close_wifi()
            #self.disconnect_wifi()
            while index < count:
                index += 1
                while True:
                    if adb.device_list() == []:
                        time.sleep(1)
                    else:
                        break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------fnv3开关CCS测试,测试次数{index}时间{date}------------------")
                #self.disconnect_wifi()
                time.sleep(1)
                self.control_ccs()
                time.sleep(30)
                wifi_status = self.get_wifi_status() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.online_music()  and self.account()# 是否可以访问网络
                iqiyi_stus=self.iQiyi()
                if wifi_status ==0 and network_card[1] ==2 and network_status == True and iqiyi_stus == True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态:{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次开关ccs测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"fnv3开关CCS测试: {e}")
            self.screencap_display()

    def reopen_wifi_no_wifi_test_fnv3(self,count=600):
        """fnv3车型(707和625)未连接wifi状态下,开关wifi测试,查看vlan1和vlan2是否能正常上网"""
        try:
            index = 0
            self.close_wifi()
            #self.disconnect_wifi()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------fnv3开关WIFI测试,测试次数{index}时间{date}------------------")
                self.close_wifi()
                time.sleep(1)
                self.open_wifi()
                time.sleep(30)
                wifi_status = self.get_wifi_status() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.online_music()  and self.account()# 是否可以访问网络
                iqiyi_stus = self.iQiyi()
                if wifi_status ==0 and network_card[1] ==2 and network_status == True  and iqiyi_stus == True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关wifi测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态:{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次开关wifi测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"开关wifi发送异常: {e}")
            self.screencap_display()

    #海外
    def power_reset_wifi_test_ex(self,count=600):
        """已连接wifi情况下电源重启测试"""
        try:
            index = 0
            self.open_wifi_ex()
            self.connect_wifi_ex()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------重启测试,测试次数{index}时间{date}------------------")
                self.stop_power()
                time.sleep(1)
                self.start_power()
                time.sleep(90)
                ccs_status=self.get_ccs_status_ex()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status_ex() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.digital_owners_manual_ex()# 是否可以访问网络
                if wifi_status == 2 and network_card[1] == 3 and network_status == True:
                    Logger.info(f"{Colors.GREEN}第{index}次重启测试测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次重启测试测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"重启测试异常: {e}")
            self.screencap_display()
    
    def power_reset_no_wifi_test_ex(self,count=600):
        """未连接wifi测试情况下电源重启测试"""
        try:
            index = 0
            self.close_wifi_ex()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------电源重启测试次数{index}时间{date}------------------")
                self.stop_power()
                time.sleep(1)
                self.start_power()
                time.sleep(90)
                time.sleep(1)
                ccs_status=self.get_ccs_status_ex()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status_ex() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.digital_owners_manual_ex()# 是否可以访问网络
                if wifi_status == 0 and network_card[1] == 1 and network_status == True:
                    Logger.info(f"{Colors.GREEN}第{index}次电源重启测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次电源重启统测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"电源重启异常: {e}")
            self.screencap_display()

    def system_reset_wifi_test_ex(self,count=600):
        """已连接wifi测试情况下系统重置"""
        try:
            index = 0
            self.open_wifi_ex()
            self.connect_wifi_ex()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------重置系统,测试次数{index}时间{date}------------------")
                self.system_reset_ex()
                time.sleep(90)
                self.open_wifi_ex()
                time.sleep(1)
                self.connect_wifi_ex()
                time.sleep(1)
                ccs_status=self.get_ccs_status_ex()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status_ex() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.digital_owners_manual_ex()# 是否可以访问网络
                if wifi_status == 2 and network_card[1] == 2 and network_status == True:
                    Logger.info(f"{Colors.GREEN}第{index}次重重置系统测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次重连重置系统测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"重连重置系统发送异常: {e}")
            self.screencap_display()
    
    def system_reset_no_wifi_test_ex(self,count=600):
        """未连接wifi测试情况下系统重置"""
        try:
            index = 0
            self.close_wifi_ex()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------重置系统,测试次数{index}时间{date}------------------")
                self.system_reset_ex()
                time.sleep(90)
                time.sleep(1)
                ccs_status=self.get_ccs_status_ex()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status_ex() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.digital_owners_manual_ex()# 是否可以访问网络
                if wifi_status == 0 and network_card[1] == 1 and network_status == True:
                    Logger.info(f"{Colors.GREEN}第{index}次重重置系统测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次重连重置系统测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"重连重置系统发送异常: {e}")
            self.screencap_display()

    def reopen_wifi_wifi_test_ex(self,count=600):
        """已连接wifi状态下,开关wifi测试"""
        try:
            while True:
                if adb.device_list() == []:
                    time.sleep(1)
                else:
                    break
            self.open_wifi_ex()
            time.sleep(0.5)
            self.connect_wifi_ex()
            index = 0
            while index < count:
                index += 1
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------开关WIFI测试,测试次数{index}时间{date}------------------")
                self.close_wifi_ex()
                time.sleep(1)
                self.open_wifi_ex()
                time.sleep(15)
                wifi_status = self.get_wifi_status_ex() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.digital_owners_manual_ex()
                if wifi_status ==2 and network_card[1] ==2 and network_status == True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关wifi测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次开关wifi测试失败{Colors.RED}")      
        except Exception as e:
            Logger.error(f"开关wifi发送异常: {e}")
            self.screencap_display()
    
    def reopen_ccs_wifi_test_ex(self,count=600):
        """已连接wifi状态下,开关ccs测试"""
        try:
            self.open_wifi_ex()
            time.sleep(0.5)
            self.connect_wifi_ex()
            index = 0
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------开关CCS测试,测试次数{index}时间{date}------------------")
                time.sleep(1)
                self.control_ccs_ex()
                time.sleep(1)
                self.open_wifi_ex()
                time.sleep(30)
                ccs_status=self.get_ccs_status_ex()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status_ex() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.digital_owners_manual_ex()
                if wifi_status ==2 and network_card[1] ==2 and network_status == True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次开关ccs测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"开关ccs发送异常: {e}")
            self.screencap_display()

    def reopen_wifi_no_wifi_test_ex(self,count=600):
        """未连接wifi状态下,开关wifi测试"""
        try:
            index = 0
            self.close_wifi_ex()
            self.disconnect_wifi()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------开关WIFI测试,测试次数{index}时间{date}------------------")
                self.close_wifi_ex()
                time.sleep(1)
                self.open_wifi_ex()
                time.sleep(30)
                wifi_status = self.get_wifi_status_ex() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.digital_owners_manual_ex()
                if wifi_status ==1 and network_card[1] ==1 and network_status:
                    Logger.info(f"{Colors.GREEN}第{index}次开关wifi测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态:{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次开关wifi测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"开关wifi发送异常: {e}")
            self.screencap_display()
    
    def reopen_ccs_no_wifi_test_ex(self,count=600):
        """未连接wifi状态下,开关ccs测试"""
        try:
            index = 0
            self.close_wifi_ex()
            #self.disconnect_wifi()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------开关CCS测试,测试次数{index}时间{date}------------------")
                self.disconnect_wifi_ex()
                time.sleep(1)
                self.control_ccs_ex()
                time.sleep(30)
                ccs_status=self.get_ccs_status_ex()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status_ex() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.digital_owners_manual_ex()
                #iqiyi_stus=self.iQiyi()
                if wifi_status ==0 and network_card[1] ==1 and network_status == True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态:{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次开关ccs测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"开关wifi发送异常: {e}")
            self.screencap_display()
    
    def reconnect_wifi_test_ex(self,count=600):
        """重连wifi测试"""
        try:
            index = 0
            self.open_wifi_ex()
            self.connect_wifi_ex()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------重连WIFI测试,测试次数{index}时间{date}------------------")  
                self.disconnect_wifi_ex()
                self.connect_wifi_ex()
                time.sleep(30)
                wifi_status = self.get_wifi_status_ex() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.digital_owners_manual_ex()
                if wifi_status ==2 and network_card[1] ==2 and network_status == True:
                    Logger.info(f"{Colors.GREEN}第{index}次重连wifi测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次重连wifi测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"重连wifi发送异常: {e}")
            self.screencap_display()

    def standby_wifi_test_ex(self,count=600):
        """已连接wifi情况下电源重启测试"""
        try:
            index = 0
            self.open_wifi_ex()
            self.connect_wifi_ex()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------电源重启测试,测试次数{index}时间{date}------------------")
                set_power_status(2)
                time.sleep(3)
                set_power_status(1)
                time.sleep(90)
                ccs_status=self.get_ccs_status_ex()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status_ex() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.digital_owners_manual_ex()# 是否可以访问网络
                if wifi_status == 2 and network_card[1] == 2 and network_status == True:
                    Logger.info(f"{Colors.GREEN}第{index}次电源重启测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次电源重启测试测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"电源重启测试异常: {e}")
            self.screencap_display()
    
    def standby_no_wifi_test_ex(self,count=600):
        """已连接wifi情况下电源重启测试"""
        try:
            index = 0
            self.close_wifi_ex()
            self.disconnect_wifi_ex()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------电源重启测试,测试次数{index}时间{date}------------------")
                set_power_status(2)
                time.sleep(3)
                set_power_status(1)
                time.sleep(90)
                ccs_status=self.get_ccs_status_ex()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status_ex() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.digital_owners_manual_ex()# 是否可以访问网络
                if wifi_status == 0 and network_card[1] == 1 and network_status == True:
                    Logger.info(f"{Colors.GREEN}第{index}次电源重启测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次电源重启测试测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"电源重启测试异常: {e}")
            self.screencap_display()
   
    def ecg_reset_wifi_test_ex(self,count=600):
        """已连接wifi情况下ECG测试"""
        try:
            index = 0
            self.open_wifi_ex()
            self.connect_wifi_ex()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------ECG测试,测试次数{index}时间{date}------------------")
                self.ecg_reset()
                time.sleep(90)
                ccs_status=self.get_ccs_status_ex()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status_ex() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.digital_owners_manual_ex()# 是否可以访问网络
                if wifi_status == 2 and network_card[1] == 2 and network_status == True:
                    Logger.info(f"{Colors.GREEN}第{index}次ECG测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次ECG测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"ECG测试异常: {e}")
            self.screencap_display()

    def ecg_reset_no_wifi_test_ex(self,count=600):
        """未连接wifi情况下ECG测试"""
        try:
            index = 0
            self.close_wifi_ex()
            self.disconnect_wifi_ex()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------ECG测试,测试次数{index}时间{date}------------------")
                self.ecg_reset()
                time.sleep(90)
                ccs_status=self.get_ccs_status_ex()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status_ex() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.digital_owners_manual_ex()# 是否可以访问网络
                if wifi_status == 0 and network_card[1] == 1 and network_status == True:
                    Logger.info(f"{Colors.GREEN}第{index}次ECG测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次ECG测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"ECG测试异常: {e}")
            self.screencap_display()
     
    def tcu_reset_no_wifi_test_ex(self,count=600):
        """未连接wifi情况下TCU测试"""
        try:
            index = 0
            self.close_wifi_ex()
            self.disconnect_wifi_ex()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------TCU测试,测试次数{index}时间{date}------------------")
                self.tcu_reset()
                time.sleep(90)
                ccs_status=self.get_ccs_status_ex()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status_ex() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.digital_owners_manual_ex()# 是否可以访问网络
                if wifi_status == 0 and network_card[1] == 1 and network_status == True:
                    Logger.info(f"{Colors.GREEN}第{index}次TCU测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次TCU测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"TCU测试异常: {e}")
            self.screencap_display()
   
    def tcu_reset_wifi_test_ex(self,count=600):
        """已连接wifi情况下TCU测试"""
        try:
            index = 0
            self.open_wifi_ex()
            self.connect_wifi_ex()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------TCU测试,测试次数{index}时间{date}------------------")
                self.tcu_reset()
                time.sleep(90)
                ccs_status=self.get_ccs_status_ex()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status_ex() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.digital_owners_manual_ex()# 是否可以访问网络
                if wifi_status == 1 and network_card[1] == 2 and network_status == True:
                    Logger.info(f"{Colors.GREEN}第{index}次TCU测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次TCU测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"ECG测试异常: {e}")
            self.screencap_display()

    def ivi_reset_wifi_test_ex(self,count=600):
        """已连接wifi情况下IVI测试"""
        try:
            index = 0
            self.open_wifi_ex()
            self.connect_wifi_ex()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------IVI测试,测试次数{index}时间{date}------------------")
                self.ivi_reset()
                time.sleep(90)
                ccs_status=self.get_ccs_status_ex()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status_ex() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.digital_owners_manual_ex()# 是否可以访问网络
                if wifi_status == 1 and network_card[1] == 2 and network_status == True:
                    Logger.info(f"{Colors.GREEN}第{index}次IVI测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次IVI测试失败{Colors.RED}")             
        except Exception as e:
            Logger.error(f"IVI测试异常: {e}")
            self.screencap_display()

    def ivi_reset_no_wifi_test_ex(self,count=600):
        """未连接wifi情况下IVI测试"""
        try:
            index = 0
            self.close_wifi()
            self.disconnect_wifi()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------IVI测试,测试次数{index}时间{date}------------------")
                self.ivi_reset()
                time.sleep(90)
                ccs_status=self.get_ccs_status_ex()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status_ex() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.digital_owners_manual_ex()# 是否可以访问网络
                if wifi_status == 0 and network_card[1] == 1 and network_status == True:
                    Logger.info(f"{Colors.GREEN}第{index}次IVI测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次IVI测试失败{Colors.RED}")         
        except Exception as e:
            Logger.error(f"IVI测试异常: {e}")
            self.screencap_display()

    def str_wifi_test_ex(self,count=600):
        """已连接wifi情况下STR休眠唤醒测试"""
        try:
            index = 0
            self.open_wifi_ex()
            self.connect_wifi_ex()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------STR休眠唤醒测试,测试次数{index}时间{date}------------------")
                set_power_status(2)
                time.sleep(3)
                set_power_status(0)
                time.sleep(70)
                set_power_status(1)
                time.sleep(90)
                ccs_status=self.get_ccs_status_ex()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status_ex() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.digital_owners_manual_ex()# 是否可以访问网络
                if wifi_status == 2 and network_card[1] == 2 and network_status == True:
                    Logger.info(f"{Colors.GREEN}第{index}次STR休眠唤醒测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次STR休眠唤醒测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"STR休眠唤醒测试异常: {e}")
            self.screencap_display()
    
    def str_no_wifi_test_ex(self,count=600):
        """未连接wifi情况下STR休眠唤醒测试"""
        try:
            index = 0
            self.close_wifi_ex()
            self.disconnect_wifi_ex()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------STR休眠唤醒测试,测试次数{index}时间{date}------------------")
                set_power_status(2)
                time.sleep(3)
                set_power_status(0)
                time.sleep(70)
                set_power_status(1)
                time.sleep(90)
                ccs_status=self.get_ccs_status_ex()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status_ex() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.digital_owners_manual_ex()# 是否可以访问网络
                if wifi_status == 0 and network_card[1] == 1 and network_status == True:
                    Logger.info(f"{Colors.GREEN}第{index}次STR休眠唤醒测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次STR休眠唤醒测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"STR休眠唤醒测试异常: {e}")
            self.screencap_display()

    def sleep_wifi_test_ex(self,count=600):
        """已连接wifi情况下深度休眠唤醒测试"""
        try:
            index = 0
            self.open_wifi_ex()
            self.connect_wifi_ex()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------深度休眠唤醒测试,测试次数{index}时间{date}------------------")
                set_power_status(2)
                time.sleep(3)
                set_power_status(0)
                time.sleep(150)
                set_power_status(1)
                time.sleep(90)
                ccs_status=self.get_ccs_status_ex()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status_ex() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.digital_owners_manual_ex()# 是否可以访问网络
                if wifi_status == 2 and network_card[1] == 2 and network_status == True:
                    Logger.info(f"{Colors.GREEN}第{index}次深度休眠唤醒测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次深度休眠唤醒测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"深度休眠唤醒测试异常: {e}")
            self.screencap_display()
    
    def sleep_no_wifi_test_ex(self,count=600):
        """未连接wifi情况下深度休眠唤醒测试"""
        try:
            index = 0
            self.close_wifi_ex()
            self.disconnect_wifi_ex()
            while index < count:
                index += 1
                while True:
                        if adb.device_list() == []:
                            time.sleep(1)
                        else:
                            break
                adbdevices = adb.device()
                date=adbdevices.shell('date')
                Logger.info(f"------------------深度休眠唤醒测试,测试次数{index}时间{date}------------------")
                set_power_status(2)
                time.sleep(3)
                set_power_status(0)
                time.sleep(150)
                set_power_status(1)
                time.sleep(90)
                ccs_status=self.get_ccs_status_ex()
                if ccs_status==True:
                    Logger.info(f"{Colors.GREEN}第{index}次开关ccs加载成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"{Colors.RED}第{index}次开关ccs加载失败{Colors.RED}")
                wifi_status = self.get_wifi_status_ex() # 获取wifi状态
                network_card = self.get_network() # 获取网卡状态
                network_status= self.digital_owners_manual_ex()# 是否可以访问网络
                if wifi_status == 0 and network_card[1] == 1 and network_status == True:
                    Logger.info(f"{Colors.GREEN}第{index}次深度休眠唤醒测试成功{Colors.GREEN}")
                else:
                    self.screencap_display()
                    Logger.error(f"wifi状态：{wifi_status}, 网卡状态：{network_card}, 网络状态：{network_status}")
                    Logger.error(f"{Colors.RED}第{index}次深度休眠唤醒测试失败{Colors.RED}")          
        except Exception as e:
            Logger.error(f"深度休眠唤醒测试异常: {e}")
            self.screencap_display()
 
if __name__ == "__main__":
    pass
    main_test = MainTest()
    main_test.reopen_wifi_wifi_test(count=1)
    #main_test.reopen_wifi_wifi_test_ex()
    #main_test.reopen_ccs_wifi_test()
    #main_test.reopen_ccs_no_wifi_test_ex
    #main_test.reopen_wifi_no_wifi_test_ex()
    #main_test.reconnect_wifi_test_ex()


