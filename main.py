import sys
import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'config', '.env'))

# 定义config（从.env读取）
config = {
    "LLM": {
        "provider": "alibaba_qwen",
        "model": os.getenv("MODEL"),  # 从 .env 读取
        "api_key": os.getenv("API_KEY"),
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "max_attempts": 10,
        "temperature": 0.7,
        "max_tokens": 1000,
        "timeout": 30
    },
    "output": {
        "results_dir": "results"
    }
}

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data_reader import get_patient_data, print_first_five_columns  # 导入新增函数
from agents_builder import build_multiagent_team
from team_runner import run_multiagent_team
from output_processor import process_and_save_output
from okg.knowledge_graph import fetch_pubmed_data, build_knowledge_graph, query_knowledge_graph  # 导入 okg 函数

def main():
    
    # 10578915
    imaging_id = input("请输入影像号: ")

    # 获取患者数据
    patient_data = get_patient_data(imaging_id)
    if patient_data is None:
        print(f"未找到影像号 {imaging_id} 的数据")
        return

    # 输出前五列数据
    print_first_five_columns(patient_data)

    # 新增：构建或查询知识图谱
    query_term = patient_data.get('disease', 'diabetes')  # 示例：从数据提取，或默认
    ids = fetch_pubmed_data(query_term, max_results=5)
    graph = build_knowledge_graph(ids)
    related_info = query_knowledge_graph(graph, query_term)  # 获取相关文章

    # 修复：将数据转换为字符串拼接
    enhanced_patient_data = str(patient_data) + f"\n相关医疗知识：{str(related_info)}"

    print(f"正在分析影像号 {imaging_id} ...")

    # 定义 agents_info
    agents_info = [
        {
            "name": "Doctor",
            "role": "一阶医生",
            "system_prompt": "你是一位经验丰富的医生，根据患者信息做出详细的判断和评估。请提供全面的分析。",
            "max_tokens": 300  # 添加每个代理的max_tokens
        },
        {
            "name": "Checker",
            "role": "检查者",
            "system_prompt": "你是一位检查者，负责检查医生的评估工作是否到位，包括内容完整性和格式是否正确。请指出任何不足。",
            "max_tokens": 250
        },
        {
            "name": "SecondOrderDoctor",
            "role": "二阶医生",
            "system_prompt": "你是一位二阶医生，基于一阶医生和检查者的内容，做出二次诊断确认。请验证并确认诊断结果。",
            "max_tokens": 300
        },
        {
            "name": "Summarizer",
            "role": "总结者",
            "system_prompt": "你是一位总结者，基于医生和检查者的输入，给出最简明的输出。保持简洁明了。",
            "max_tokens": 200
        }
    ]

    # 构建多代理团队
    team = build_multiagent_team(config, agents_info)

    # 运行团队推理
    reasoning_process, analysis_result = run_multiagent_team(enhanced_patient_data, team)

    # 处理并保存输出
    process_and_save_output(imaging_id, analysis_result, reasoning_process)

    print(f"分析完成，结果已保存到 results/{imaging_id}.csv")

if __name__ == "__main__":
    main()
