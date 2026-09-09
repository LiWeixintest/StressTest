import xml.etree.ElementTree as ET
import os

def filter_testcases_by_strategy(xml_file_path, output_file_path=None):
    """
    根据测试策略筛选用例
    保留测试策略为"冒烟"的用例，删除测试策略为空的用例
    
    Args:
        xml_file_path: 输入XML文件路径
        output_file_path: 输出XML文件路径，如果不指定则覆盖原文件
    """
    # 解析XML文件
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    
    # 统计信息
    total_count = 0
    kept_count = 0
    removed_count = 0
    
    # 递归处理所有testsuite和testcase
    def process_element(element):
        nonlocal total_count, kept_count, removed_count
        
        # 处理testcase元素
        if element.tag == 'testcase':
            total_count += 1
            should_keep = False
            
            # 查找测试策略字段
            custom_fields = element.find('custom_fields')
            if custom_fields is not None:
                for custom_field in custom_fields.findall('custom_field'):
                    name_elem = custom_field.find('name')
                    if name_elem is not None:
                        name_text = name_elem.text if name_elem.text else ''
                        if '测试策略' in name_text:
                            value_elem = custom_field.find('value')
                            if value_elem is not None:
                                value_text = value_elem.text if value_elem.text else ''
                                if value_text.strip() == '冒烟' or value_text.strip() == '冒烟|最小集':
                                    should_keep = True
                                    kept_count += 1
                                    print(f"保留用例: {element.get('name', 'unknown')} (测试策略: {value_text})")
                                else:
                                    removed_count += 1
                                    print(f"删除用例: {element.get('name', 'unknown')} (测试策略: '{value_text}')")
                            break
            
            return should_keep
        
        # 递归处理子元素
        children_to_remove = []
        for child in element:
            if not process_element(child):
                children_to_remove.append(child)
        
        # 删除标记的子元素
        for child in children_to_remove:
            element.remove(child)
        
        return True  # 保留当前元素
    
    # 处理根元素下的所有子元素
    children_to_remove = []
    for child in root:
        if not process_element(child):
            children_to_remove.append(child)
    
    for child in children_to_remove:
        root.remove(child)
    
    # 输出统计信息
    print(f"\n总用例数: {total_count}")
    print(f"删除用例数: {removed_count}")
    print(f"保留用例数: {kept_count}")
    
    # 保存修改后的XML
    output_path = output_file_path if output_file_path else xml_file_path
    tree.write(output_path, encoding='utf-8', xml_declaration=True)
    print(f"已保存到: {output_path}")
    
    return tree

# 使用示例
if __name__ == "__main__":
    filter_testcases_by_strategy(r'C:\Users\Administrator\Downloads\Weather.testsuite-deep.xml', 'filtered_testcases.xml')