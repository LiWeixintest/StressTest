from libs.can.zlg.zlgUds_structure import *
from libs.can.zlg.zlgUds import *
from libs.logger.logger import Logger
import threading

class zlgMain:
    def __init__(self):
        pass
    
    def start(self, deviceType, chn, abit, dbit, canType):
        zcanlib = ZCAN()
        self.g_zcanlib = zcanlib
        self.device_handle = zcanlib.OpenDevice(deviceType, 0, 0)  # 打开设备，参数：设备类型（CANFD200U），设备编号（存在多个设备时有效，从0开始），保留参数（0）
        if self.device_handle == INVALID_DEVICE_HANDLE:
            Logger.error("Open ZLG CANFD Device failed!")
            return False
        else:
            Logger.info("Open ZLG CANFD Device success!")
            Logger.info("device handle: " + str(self.device_handle))
        info = zcanlib.GetDeviceInf(self.device_handle)  # 打印设备信息
        Logger.info("Device Information:" + info.info_str())

        chn_handle = canfd_start(zcanlib, self.device_handle, chn, abit, dbit)  # 初始化CAN卡，获取通道句柄，并且开启队列发送模式
        self.g_chnhandle = chn_handle
        Logger.info(hex(chn_handle))
        return True
    
    def stop(self):
        self.g_zcanlib.CloseDevice(self.device_handle)

    def uds_start(self, idType, canType):
        zudslib = ZUDS()
        self.g_zudslib = zudslib

        # UDS初始化
        uds_handle = zudslib.Uds_Init(0)  # 初始化UDS，获取UDS句柄
        self.g_uds_handle = uds_handle
        Logger.info("uds_handle is %d" % uds_handle)

        chn_param = CHANNEL_PARAM()
        chn_param.channel_handle = self.g_chnhandle

        chn_param.Extend_Flag = idType  # 0-标准帧，1-扩展帧
        chn_param.CANFD_type = canType  # 0-CAN,1-CANFD
        chn_param.trans_version = 1  # 0-2004版本，1-2016版本

    def set_uds_param(lib, uds_handle, chn_param):
        param_15765 = ZUDS_ISO15765_PARAM()
        memset(byref(param_15765), 0, sizeof(param_15765))
        param_15765.version = chn_param.trans_version  #
        param_15765.max_data_len = 8 if chn_param.trans_version else 64
        param_15765.local_st_min = 0
        param_15765.block_size = 8
        param_15765.fill_byte = 0
        param_15765.frame_type = chn_param.Extend_Flag  # 0-标准帧，1-扩展帧
        param_15765.is_modify_ecu_st_min = 0  # 是否修改 ECU 的最小发送时间间隔参数
        param_15765.remote_st_min = 0
        param_15765.fc_timeout = 70  # 等待流控超时时间，单位ms
        param_15765.fill_mode = 1  # 数据长度填充模式，0-不填充，1-小于8字节填充到8，大于8字节就近填充，2-填充至最大字节
        lib.Uds_SetParam(uds_handle, 1, param_15765)  # 第二个参数为1对应15765结构体

        param_seesion = ZUDS_SESSION_PARAM()
        memset(byref(param_seesion), 0, sizeof(param_seesion))
        param_seesion.timeout = 2000
        param_seesion.enhanced_timeout = 5000
        lib.Uds_SetParam(uds_handle, 0, param_seesion)  # 第二个参数为0对应 应用层结构体

    def init_uds(self, requestId, responseId):
        self.g_req_id = requestId
        self.g_resp_id = responseId
    
    def send_uds(self, sid, data):
        response = ZUDS_RESPONSE()
        chn_param = CHANNEL_PARAM()
        chn_param.channel_handle = self.g_chn_handle
        chn_param.Extend_Flag = 0  # 0-标准帧，1-扩展帧
        chn_param.CANFD_type = 0  # 0-CAN,1-CANFD
        chn_param.trans_version = 1  # 0-2004版本，1-2016版本
        self.g_zudslib.Uds_SetTransmitHandler(self.g_uds_handle, byref(chn_param))  # 设置发送回调,将uds句柄与通道句柄绑定
        self.Set_param(self.g_zudslib, self.g_uds_handle, chn_param)
        request = ZUDS_REQUEST()
        memset(byref(request), 0, sizeof(request))
        request.src_addr = self.g_req_id 
        request.dst_addr = self.g_resp_id
        request.sid = sid
        request.param_len = len(data)  # len
        param_data = PARAM_DATA()  # 参数的list，成员数量需与request.param_len对应
        for i in range(request.param_len):
            param_data.data[i] = data[i]
        request.param = param_data.data
        self.g_zudslib.Uds_Request(self.g_uds_handle, request, response)
        memset(byref(param_data), 0, sizeof(param_data))
        if response.status == 0:
            if response.type == 0:
                print("NegativeResponse:%s SID: %s  NRC: %s" % (
                hex(response.response.negative.neg_code), hex(response.response.negative.sid),
                hex(response.response.negative.error_code)))
            if response.type == 1:
                print("PositiveResponse,RespId:%s,len:%d,data:%s" % (
                hex(response.response.positive.sid), response.response.positive.param_len, ''.join(
                    hex(response.response.positive.param[i]) + ' ' for i in range(response.response.positive.param_len))))
        if response.status == 1:
            print("响应超时")
        if response.status == 2:
            print("传输失败，请检查链路层，或请确认流控帧是否回复")
        if response.status == 3:
            print("取消请求")
        if response.status == 4:
            print("抑制响应")
        if response.status == 5:
            print("忙碌中")
        if response.status == 6:
            print("请求参数错误")
        return response
    
    def send_can(self, id, len, data):
        msg = ZCAN_Transmit_Data()
        msg.transmit_type = 0  # normal transmit
        msg.frame.eff = 0  # extern frame
        msg.frame.rtr = 0  # remote frame
        msg.frame.can_id = id
        msg.frame.can_dlc = len
        for j in range(msg.frame.can_dlc):
            msg.frame.data[j] = data[j]
        self.g_zcanlib.Transmit(self.g_chnhandle, msg, 1)

    def send_canfd(self, id, len, data):
        canfd_msgs = ZCAN_TransmitFD_Data()
        canfd_msgs.transmit_type = 0  # normal transmit
        canfd_msgs.frame.eff = 0  # extern frame
        canfd_msgs.frame.rtr = 0  # remote frame
        canfd_msgs.frame.brs = 1  # BRS
        canfd_msgs.frame.can_id = id
        canfd_msgs.frame.len = len
        for j in range(canfd_msgs.frame.len):
            canfd_msgs.frame.data[j] = data[j]
        self.g_zcanlib.TransmitFD(self.g_chnhandle, canfd_msgs, 1)

    def recv_can(self):
        recv_list = []
        rcv_num = self.g_zcanlib.GetReceiveNum(self.g_chnhandle, ZCAN_TYPE_CAN)
        rcv_canfd_num = self.g_zcanlib.GetReceiveNum(self.g_chnhandle, ZCAN_TYPE_CANFD)
        if rcv_num:
            rcv_msg, rcv_num = self.g_zcanlib.Receive(self.g_chnhandle, rcv_num, 1)
            for i in range(rcv_num):
                c_array = rcv_msg[i].frame.data
                pyList = [c_array[index] for index in range(len(c_array))]
                recv_dict = dict(recv_id=(rcv_msg[i].frame.can_id & 0x1fffffff), length=rcv_msg[i].frame.can_dlc, 
                                     data=pyList, extendFlag=rcv_msg[i].frame.eff)
                recv_list.append(recv_dict)
                # 如果收到响应ID
                # if rcv_msg[i].frame.can_id == self.g_resp_id:
                #     uds_frame = ZUDS_FRAME()
                #     memset(byref(uds_frame), 0, sizeof(uds_frame))
                #     uds_frame.id = rcv_msg[i].frame.can_id & 0x1fffffff # 传入真实ID
                #     uds_frame.extend = rcv_msg[i].frame.eff
                #     uds_frame.data_len = rcv_msg[i].frame.can_dlc
                #     for j in range(uds_frame.data_len):
                #         uds_frame.data[j] = rcv_msg[i].frame.data[j]
                #     self.g_zudslib.Uds_Onreceive(self.g_uds_handle, uds_frame)
        if rcv_canfd_num:
            rcv_canfd_msgs, rcv_canfd_num = self.g_zcanlib.ReceiveFD(self.g_chnhandle, rcv_canfd_num, 1)
            for i in range(rcv_canfd_num):
                c_array = rcv_msg[i].frame.data
                pyList = [c_array[index] for index in range(len(c_array))]
                recv_dict = dict(recv_id=(rcv_msg[i].frame.can_id & 0x1fffffff), length=rcv_msg[i].frame.can_dlc, 
                                 data=pyList, extendFlag=rcv_msg[i].frame.eff)
                recv_list.append(recv_dict)
                # 如果收到响应ID
                # if rcv_msg[i].frame.can_id == self.g_resp_id:
                #     uds_frame = ZUDS_FRAME()
                #     memset(byref(uds_frame), 0, sizeof(uds_frame))
                #     uds_frame.id = rcv_canfd_msgs[i].frame.can_id & 0x1fffffff # 传入真实ID
                #     uds_frame.extend = rcv_canfd_msgs[i].frame.eff
                #     uds_frame.data_len = rcv_canfd_msgs[i].frame.len
                #     for j in range(uds_frame.data_len):
                #         uds_frame.data[j] = rcv_canfd_msgs[i].frame.data[j]
                #     self.g_zudslib.Uds_Onreceive(self.g_uds_handle, uds_frame)
        return recv_list
