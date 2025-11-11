from typing import List, Dict, Any, Tuple
from agents_builder import Agent

def run_multiagent_team(patient_data: Dict[str, Any], team: List[Agent]):
    """
    运行多智能体团队推理。
    首先输入 patient_data，然后按顺序让四个智能体分析：
    1. Doctor: 分析 patient_data
    2. Checker: 检查 Doctor 的输出
    3. SecondOrderDoctor: 基于 Doctor 和 Checker 的输出进行二次确认
    4. Summarizer: 总结所有输出
    返回推理过程列表和最终分析结果。
    """
    reasoning_process = []
    
    # Doctor 分析 patient_data
    doctor_output = team[0].think(str(patient_data))
    print(f"Doctor 输出: {doctor_output}")
    reasoning_process.append(doctor_output)
    
    # Checker 检查 Doctor 的输出
    checker_output = team[1].think(doctor_output)
    print(f"Checker 输出: {checker_output}")
    reasoning_process.append(checker_output)
    
    # SecondOrderDoctor 基于 Doctor 和 Checker 的输出
    combined_input = f"Doctor 输出: {doctor_output}\nChecker 输出: {checker_output}"
    second_doctor_output = team[2].think(combined_input)
    print(f"SecondOrderDoctor 输出: {second_doctor_output}")
    reasoning_process.append(second_doctor_output)
    
    # Summarizer 总结所有
    all_outputs = f"Doctor 输出: {doctor_output}\nChecker 输出: {checker_output}\nSecondOrderDoctor 输出: {second_doctor_output}"
    summarizer_output = team[3].think(all_outputs)
    print(f"Summarizer 输出: {summarizer_output}")
    reasoning_process.append(summarizer_output)
    
    # 最终结果为 Summarizer 的输出
    analysis_result = summarizer_output
    
    return reasoning_process, analysis_result