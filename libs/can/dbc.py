from cantools import database
from libs.logger.logger import Logger

class DBC():
    """
    解析dbc文件,获取信号和报文内容,将信号的物理值转成原始值
    """
    def __init__(self,path) -> None:
        """
        加载DBC文件
        
        :parame path: dbc文件路径
        """
        try:
            self.db = database.load_file(path)
            Logger.info(f"The {path} load success.")
        except Exception as e:
            Logger.error(e)
            raise
    
    def get_message_info(self,message:int)->dict:
        """
        通过报文id获取指定报文的name、dlc
        
        :parame message: 报文ID,为十六进制数

        :return frame_dict: 以字典形式返回报文的id、报文名称message、dlc
        """
        try:
            frame_dict = {"id":message,"message":"","dlc":"", "signals":""}
            frame_info = self.db.get_message_by_frame_id(message)
            frame_dict["message"]=frame_info.name #获取报文名称
            frame_dict["dlc"]=frame_info.length #获取报文DLC
            frame_dict["signals"] = frame_info.signals #获取报文中的所有信号
            # Logger.info(f"The {message} message info {frame_dict}.")
            return frame_dict
        except Exception as e:
            Logger.error('CAN Id Not Exist: ' + str(e))
            raise
    
    def get_signal_info(self,message:int,signal:str)->dict:
        """
        通过报文id获取指定报文的name、dlc
        
        :parame message: 报文ID,为十六进制数

        :parame signal: 信号名
        
        :return signal_dict: 以字典形式返回信号的name信号名、start开始位、length长度、
        scale变换比例、offset偏移量,报文的id、报文名称message、dlc
        """
        try:
            signal_dict = {
                            "id":hex(message),
                            "message":"",
                            "dlc":"",
                            "name":signal,
                            "start":"",
                            "length":"",
                            "scale":"",
                            "offset":""
                            }
            # 获取报文ID相关信息
            frame_info = self.db.get_message_by_frame_id(message)
            signal_dict["message"]=frame_info.name #获取报文名称
            signal_dict["dlc"]=frame_info.length #获取报文DLC
            # 获取信号信息
            signal_info = frame_info.get_signal_by_name(signal)
            signal_dict["start"]=signal_info.start #获取信号开始位
            signal_dict["length"]=signal_info.length #获取信号长度
            signal_dict["scale"]=signal_info.scale #获取变换比例
            signal_dict["offset"]=signal_info.offset #获取偏移量
            # Logger.info(f"The {signal} signal information under the {message} message is {signal_dict}.")
            return signal_dict
        except Exception as e:
            Logger.error(e)
            raise

    def physical_to_raw(self,signal_info ,physical:float) -> int:
        """
        将对应信号的物理值转成原始值,公式为: 原始值 = (物理值 - 偏移量) / 缩放因子,其中缩放因子也叫变换比例
        
        :parame message: 报文ID,为十六进制数

        :parame signal: 信号名称

        :parame physical: 物理值

        :return value: 返回原始值,为十进制数
        """
        try:
            value = int((physical-signal_info["offset"])/signal_info["scale"])
            # Logger.info(f"The physical value of the {signal_info["name"]} signal under the {signal_info["message"]} message is {value}.")
            return value
        except Exception as e:
            Logger.error(e)
            raise

    def raw_to_physical(self, signal_info, raw:int) -> float:
        try:
            value = raw * signal_info["scale"] + signal_info["offset"]
            # Logger.info(f"The physical value of the {signal_info["name"]} signal under the {signal_info["message"]} message is {value}.")
            return value
        except Exception as e:
            Logger.error(e)
            raise

    # TODO 仅适用于Motorola格式（大端）
    # TODO 采取另一种方案，for i in len循环，一位一位处理
    def set_message_frame(self, can_data, start, len, dlc, signal_raw: int) -> list:
        start_byte = start // 8
        h_bit = start % 8
        if len <= h_bit + 1:
            byte_cnt = 1
            tmp_l_bit = h_bit + 1 - len
        else:
            # 一个字节放不下，会占用其他字节
            # 计算总共几个字节
            remainBits = len - (h_bit + 1)
            byte_cnt = (remainBits - 1) // 8 + 1
            byte_cnt += 1 # 加上最初的一个字节
            tmp_l_bit = 0
        tmp_h_bit = h_bit
        tmp_byte_index = start_byte
        tmp_len = len
        tmp_raw = signal_raw
        for _ in range(byte_cnt):
            # 清0原数据
            mask = (1 << (tmp_h_bit+ 1)) - (1 << tmp_l_bit)
            can_data[tmp_byte_index] = can_data[tmp_byte_index] & ~mask
            # 提取目标值，取出目标值在当前字节h和l之间的部分
            currByte = tmp_raw >> (tmp_len - (tmp_h_bit - tmp_l_bit + 1))
            # 设置新数据
            can_data[tmp_byte_index] = (can_data[tmp_byte_index] | (currByte << tmp_l_bit)) & 0xff
            tmp_byte_index += 1
            tmp_len -= (tmp_h_bit - tmp_l_bit + 1)
            tmp_h_bit = 7
            if tmp_len >= 8:
                tmp_l_bit = 0
            else:
                tmp_l_bit = 7 - tmp_len + 1
        return can_data
    
    # TODO 仅适用于Motorola格式（大端）
    def get_message_frame(self, candata, start, len, dlc): 
        value = 0
        start_byte = start // 8
        h_bit = start % 8
        if len <= h_bit + 1:
            byte_cnt = 1
            tmp_l_bit = h_bit + 1 - len
        else:
            # 一个字节放不下，会占用其他字节
            # 计算总共几个字节
            remainBits = len - (h_bit + 1)
            byte_cnt = (remainBits - 1) // 8 + 1
            byte_cnt += 1 # 加上最初的一个字节
            tmp_l_bit = 0
        tmp_h_bit = h_bit
        tmp_byte_index = start_byte
        tmp_len = len
        for _ in range(byte_cnt):
            cur_byte_value = (candata[tmp_byte_index] & ((1 << (tmp_h_bit + 1)) - 1)) >> tmp_l_bit
            tmp_len = tmp_len - (tmp_h_bit - tmp_l_bit + 1) # 剩下的位=总位数-已经处理的位数
            value |= (cur_byte_value << tmp_len)

            tmp_byte_index += 1
            tmp_h_bit = 7
            if tmp_len > 8:
                tmp_l_bit = 0
            else:
                tmp_l_bit = 8 - tmp_len
        return value

    # 设置信号的值，实际值，可能是小数
    def set_signal_value(self, message_id: int, byte_data: list, signal_name: str, signal_value: float):
        # 获取信号的信息：message，dlc，name，start，length，scale，offset
        signal_info = self.get_signal_info(message_id, signal_name)
        # 根据scale和offset计算信号的原始值
        signal_raw_value = self.physical_to_raw(signal_info, signal_value)
        message_frame = self.set_message_frame(byte_data, signal_info['start'], signal_info['length'], signal_info['dlc'], signal_raw_value)
        # 返回带有信号值的报文
        return message_frame
    
    def set_signal_value_by_raw(self, message_id: int, byte_data: list, signal_name: str, signal_value: int):
        # 获取信号的信息：message，dlc，name，start，length，scale，offset
        signal_info = self.get_signal_info(message_id, signal_name)
        message_frame = self.set_message_frame(byte_data, signal_info['start'], signal_info['length'], signal_info['dlc'], signal_value)
        # 返回带有信号值的报文
        return message_frame
    
    # 获取信号的值，实际值，可能是小数
    def get_signal_value(self, message_id: int, byte_data : list, signal_name: str) -> float:
        # 获取信号的信息
        signal_info = self.get_signal_info(message_id, signal_name)
        # 获取信号的原始值
        signal_raw_value = self.get_message_frame(byte_data, signal_info['start'], signal_info['length'], signal_info['dlc'])
        signal_value = self.raw_to_physical(signal_info, signal_raw_value)
        return signal_value

    def get_signal_value_by_raw(self, message_id: int, byte_data : list, signal_name: str) -> float:
        # 获取信号的信息
        signal_info = self.get_signal_info(message_id, signal_name)
        # 获取信号的原始值
        signal_raw_value = self.get_message_frame(byte_data, signal_info['start'], signal_info['length'], signal_info['dlc'])
        return signal_raw_value
