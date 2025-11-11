import os
import pandas as pd

def process_and_save_output(imaging_id, analysis_result, reasoning_process, doctor_suggestion=None, results_dir='results/'):
    # 自动定位到项目根目录
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    results_path = os.path.join(base_dir, results_dir)
    os.makedirs(results_path, exist_ok=True)
    file_path = os.path.join(results_path, f'{imaging_id}.csv')

    # 准备数据：影像号、推理流程、结果、医生建议
    data = {
        '影像号': imaging_id,
        '推理流程': reasoning_process,
        '分析结果': analysis_result,
        '医生建议': doctor_suggestion or '无'
    }

    # 如果文件存在，追加；否则创建
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        new_row = pd.DataFrame([data])
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        df = pd.DataFrame([data])

    df.to_csv(file_path, index=False)