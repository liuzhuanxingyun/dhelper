from typing import List, Dict, Any, Tuple
from agents_builder import BaseAgent, ChiefAgent, ManagerAgent, WorkerAgent, build_agent

def run_hierarchical_team(
    initial_input: str,
    chief_agent: ChiefAgent,
    manager_prototype_info: Dict[str, Any],
    worker_prototype_info: Dict[str, Any],
    config: Dict[str, Any]
) -> Tuple[List[str], str]:
    """
    运行三层架构的智能体团队。
    1. Chief Agent 分解任务。
    2. 为每个子任务创建一个 Manager Agent。
    3. 每个 Manager Agent 分解其子任务为具体步骤。
    4. 为每个步骤创建一个 Worker Agent 来执行。
    5. 结果逐层返回，最终由 Chief Agent 汇总。
    """
    reasoning_process = []
    separator = "----------------------------------------------------------------------------------------------------\n----------------------------------------------------------------------------------------------------"  # 大量分隔符用于划分每个Agent的输出，两行
    print("--- Chief Agent 开始工作 ---")
    
    # 1. Chief分解任务
    reasoning_process.append(separator)  # 添加分隔符
    sub_tasks = chief_agent.decompose_task(initial_input)
    chief_output = f"主任务已分解为 {len(sub_tasks)} 个子任务: {[task['task_name'] for task in sub_tasks]}"
    print(f"Chief: {chief_output}")
    reasoning_process.append(f"Chief: {chief_output}")

    if not sub_tasks:
        final_summary = "Chief未能成功分解任务，流程终止。"
        reasoning_process.append(final_summary)
        return reasoning_process, final_summary

    # 2. 为每个子任务创建Manager并执行
    manager_outputs = []
    for i, task in enumerate(sub_tasks):
        reasoning_process.append(separator)  # 添加分隔符
        print(f"\nManager {i+1}: 处理子任务 '{task['task_name']}'")
        
        # 创建Manager Agent
        manager_info = manager_prototype_info.copy()
        manager_info["name"] = f"Manager_{task['task_name'].replace(' ', '_')}"
        manager_agent = build_agent(config, manager_info)
        
        # 3. Manager分解子任务
        steps = manager_agent.decompose_sub_task(f"原始数据和问题:\n{initial_input}\n\n子任务目标: {task['task_description']}")
        manager_output = f"子任务 '{task['task_name']}' 已分解为 {len(steps)} 个步骤: {[step['step_name'] for step in steps]}"
        print(f"  {manager_agent.name}: {manager_output}")
        reasoning_process.append(f"{manager_agent.name}: {manager_output}")

        if not steps:
            manager_outputs.append(f"子任务 '{task['task_name']}' 的结果: Manager未能分解步骤。")
            continue

        # 4. 为每个步骤创建Worker并执行
        worker_outputs = []
        step_context = initial_input # 初始上下文是原始输入
        for j, step in enumerate(steps):
            reasoning_process.append(separator)  # 添加分隔符
            print(f"    Worker {j+1}: 执行步骤 '{step['step_name']}'")
            
            # 创建Worker Agent
            worker_info = worker_prototype_info.copy()
            worker_info["name"] = f"Worker_{task['task_name'].replace(' ', '_')}_{step['step_name'].replace(' ', '_')}"
            worker_agent = build_agent(config, worker_info)
            
            # Worker执行步骤
            worker_result = worker_agent.execute_step(step['step_instruction'], step_context)
            print(f"      输出: {worker_result[:100]}...")  # 打印部分结果
            reasoning_process.append(f"      {worker_agent.name}: {worker_result}")
            worker_outputs.append(worker_result)
            
            # 更新上下文，为下一个worker提供信息
            step_context += f"\n\n步骤 '{step['step_name']}' 的已完成结果:\n{worker_result}"

            reasoning_process.append(separator)  # 在Workers之间添加分隔符

        # Manager汇总Worker的结果
        reasoning_process.append(separator)  # 添加分隔符
        manager_summary_prompt = f"你已完成子任务 '{task['task_name']}'。请根据以下所有工作步骤的结果，对该子任务进行总结。\n\n上下文:\n{step_context}"
        manager_final_output = manager_agent.think(manager_summary_prompt)
        print(f"  {manager_agent.name} 总结: {manager_final_output[:100]}...")
        reasoning_process.append(f"{manager_agent.name} 总结: {manager_final_output}")
        manager_outputs.append(f"子任务 '{task['task_name']}' 的总结:\n{manager_final_output}")

    # 5. Chief汇总所有Manager的结果
    reasoning_process.append(separator)  # 添加分隔符
    print("\nChief: 开始最终汇总")
    all_manager_summaries = "\n\n".join(manager_outputs)
    final_summary_prompt = f"所有子任务已完成。请根据以下各子任务的总结，结合原始请求，生成最终的、完整的报告。\n\n原始请求:\n{initial_input}\n\n各子任务总结:\n{all_manager_summaries}"
    final_result = chief_agent.think(final_summary_prompt)
    
    print(f"最终结果: {final_result[:200]}...")  # 打印部分最终结果
    reasoning_process.append(f"Chief 最终总结: {final_result}")
    
    return reasoning_process, final_result

def run_multiagent_team(patient_data: Dict[str, Any], team: List[BaseAgent]):
    # 此函数保留，以防需要运行旧的扁平化团队结构
    # 但在新的三层架构中，我们将使用 run_hierarchical_team
    print("警告: run_multiagent_team 已被调用，但推荐使用 run_hierarchical_team。")
    # ... (原有代码可以保留或移除)
    return ["旧流程已停用"], "请更新到 run_hierarchical_team"