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

from data_reader import get_patient_data, print_first_five_columns
from agents_builder import build_agent
from team_runner import run_hierarchical_team
from output_processor import process_and_save_output
from okg.knowledge_graph import fetch_pubmed_data, build_knowledge_graph, query_knowledge_graph

def main():
    
    # 10578915
    imaging_id = input("请输入影像号: ")

    # 获取患者数据
    patient_data = get_patient_data(imaging_id)
    if patient_data is None:
        print(f"未找到影像号 {imaging_id} 的数据")
        return

    # 输入问题
    question = input("请输入问题（默认为'分析病人数据并生成诊断报告'）: ").strip()
    if not question:
        question = "分析这个病人的各项数据，给出诊断报告"

    # 输出前五列数据
    print_first_five_columns(patient_data)

    # 构建或查询知识图谱
    query_term = patient_data.get('disease', 'Thymus')
    ids = fetch_pubmed_data(query_term, max_results=5)
    graph = build_knowledge_graph(ids)
    related_info = query_knowledge_graph(graph, query_term)
    
    # 组合最终输入
    initial_input = f"【原始数据】:\n{str(patient_data)}\n\n【相关医疗知识】:\n{str(related_info)}\n\n【问题】:\n{question}"

    print(f"正在分析影像号 {imaging_id} ...")

    # 定义三层架构 Agent 的原型信息
    # 这些信息将用于动态创建 Agent
    chief_agent_info = {
        "name": "Chief_Agent",
        "role": "总指挥",
        "type": "Chief",
        "system_prompt": "你是一个顶级的医疗项目主管(Chief)。你的任务是理解用户关于患者数据的复杂请求，将其分解为几个逻辑清晰、相互独立的子任务，并为每个子任务设定明确的目标。你的输出必须是结构化的JSON。请确保输出不超过 1000 个 token。",
        "max_tokens": 1000
    }

    manager_prototype_info = {
        # name 将被动态生成
        "role": "项目经理",
        "type": "Manager",
        "system_prompt": "你是一个医疗分析团队的项目经理(Manager)。你的任务是接收一个子任务目标，并将其分解为一系列具体的、可按顺序执行的工作步骤。你的输出必须是结构化的JSON。请确保输出不超过 500 个 token。",
        "max_tokens": 500
    }

    worker_prototype_info = {
        # name 将被动态生成
        "role": "分析员",
        "type": "Worker",
        "system_prompt": "你是一位专业的医疗数据分析员(Worker)。你的任务是精确地执行给定的指令，并根据提供的上下文信息，生成清晰、准确的结果。请直接回答，不要添加无关内容。请确保输出不超过 500 个 token。",
        "max_tokens": 500
    }

    # 1. 创建 Chief Agent
    chief_agent = build_agent(config, chief_agent_info)

    # 2. 运行分层团队
    reasoning_process, analysis_result = run_hierarchical_team(
        initial_input=initial_input,
        chief_agent=chief_agent,
        manager_prototype_info=manager_prototype_info,
        worker_prototype_info=worker_prototype_info,
        config=config
    )

    # 3. 处理并保存输出
    # 将列表形式的推理过程转换为字符串
    reasoning_str = "\n\n".join(reasoning_process)
    process_and_save_output(imaging_id, analysis_result, reasoning_str)

    print(f"\n分析完成，结果已保存到 results/{imaging_id}.csv")

if __name__ == "__main__":
    main()
