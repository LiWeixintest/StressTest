import os

def search_text_in_txt_files(folder_path, search_content):
    """
    在指定文件夹下的所有txt文件中查找指定内容
    
    参数:
        folder_path: 要搜索的文件夹路径
        search_content: 要查找的字符串内容
    
    返回:
        包含指定内容的文件名列表
    """
    found_files = []
    print(f"正在搜索文件夹: {folder_path} 中的txt文件，查找内容: '{search_content}'")
    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        print(f"文件夹路径不存在: {folder_path}")
        return found_files
    
    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        # 只处理 .txt 文件
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)
            
            # 尝试多种编码
            encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin-1']
            file_read = False
            
            for encoding in encodings:
                try:
                    # 以只读方式打开文件，尝试当前编码
                    with open(file_path, 'r', encoding=encoding, errors='strict') as file:
                        # 读取整个文件内容
                        content = file.read()
                        # 查找指定内容
                        if search_content in content:
                            found_files.append(filename)
                        file_read = True
                        break  # 成功读取，跳出编码循环
                except UnicodeDecodeError:
                    continue  # 编码不对，尝试下一个
                except Exception as e:
                    print(f"读取文件 {filename} 时出错 (编码 {encoding}): {e}")
                    file_read = True
                    break
            
            if not file_read:
                print(f"无法读取文件 {filename}，尝试了所有编码")
    
    return found_files

# 使用示例
if __name__ == "__main__":
    # 设置要搜索的文件夹路径
    #folder = input("请输入文件夹路径: ").strip()
    folder = r"E:\工作文档\福特\问题\logs\AndroidLog\logcat\logcat"
    # 设置要查找的内容
    #search_text = input("请输入要查找的内容: ").strip()
    search_text = "beginning of crash"#"onLocationChanged"
    # 执行搜索
    result = search_text_in_txt_files(folder, search_text)
    
    # 输出结果
    if result:
        print("\n找到包含指定内容的文件:")
        for file in result:
            print(f"  - {file}")
    else:
        print("\n未找到包含指定内容的文件")