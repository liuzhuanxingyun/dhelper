import pandas as pd
import os

def get_patient_data(imaging_id, data_file=None):
    if data_file is None:
        # 自动定位到项目根目录下的 data 文件夹
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_file = os.path.join(base_dir, 'data', 'Thymus_data.csv')
    df = pd.read_csv(data_file, encoding='utf-8')  # 确保编码
    
    # 尝试转换为字符串匹配
    patient_row = df[df['影像号'].astype(str) == str(imaging_id)]
    
    if patient_row.empty:
        return None
    
    return patient_row.to_dict('records')[0]  # 返回行数据字典

# 新增函数：输出读取到的前五列数据（假设有患者数据）
def print_first_five_columns(patient_data):
    if patient_data is None:
        print("无患者数据可供显示")
        return
    
    # 获取前五列的键
    columns = list(patient_data.keys())[:5]  # 前五列：影像号, 是否有病理, 是否出组, 症状, 病理诊断
    print("前五列数据：")
    for col in columns:
        print(f"{col}: {patient_data[col]}")
