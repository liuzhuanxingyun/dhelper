import os
from openai import OpenAI
from typing import List, Dict, Any

class BaseAgent:
    def __init__(self, name: str, role: str, system_prompt: str, config: Dict[str, Any]):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.config = config
        self.memory = []  # 添加独立记忆列表
        # 创建OpenAI客户端
        self.client = OpenAI(
            api_key=self.config["LLM"]["api_key"],
            base_url=self.config["LLM"]["base_url"]
        )

    def think(self, input_data: str) -> str:
        try:
            # 构建上下文：系统提示 + 记忆 + 当前输入
            context = self.system_prompt
            if self.memory:
                context += "\n\n推理记忆:\n" + "\n".join([f"输入: {m['input']}\n输出: {m['output']}" for m in self.memory])
            context += f"\n\n当前输入: {input_data}"
            
            completion = self.client.chat.completions.create(
                model=self.config["LLM"]["model"],
                messages=[
                    {"role": "system", "content": context},  # 使用增强上下文
                    {"role": "user", "content": input_data}
                ],
                temperature=self.config["LLM"]["temperature"],
                max_tokens=self.config["max_tokens"],
                stream=False
            )
            output = completion.choices[0].message.content
            
            # 更新记忆（限制长度，避免过长）
            self.memory.append({"input": input_data, "output": output})
            if len(self.memory) > 5:  # 例如，保留最近5条
                self.memory.pop(0)
            
            return output
        except Exception as e:
            return f"Error: {str(e)}"

class ChiefAgent(BaseAgent):
    """
    Chief Agent: 负责接收原始输入，将其分解为几个主要的子任务，并为每个子任务指派一个Manager。
    """
    def decompose_task(self, initial_input: str) -> List[Dict[str, str]]:
        # 使用LLM将主任务分解为子任务描述列表
        # 为了简化，我们这里使用 think 方法，并要求它输出特定格式
        # 在实际应用中，可以增加更复杂的解析逻辑
        decomposition_prompt = f"根据以下用户请求，将其分解为多个独立的子任务，并为每个子任务定义一个目标。请以JSON格式的列表输出，每个对象包含'task_name'和'task_description'。例如：[{{\"task_name\": \"数据分析\", \"task_description\": \"分析患者的临床数据\"}}, ...]。\n\n用户请求：\n{initial_input}"
        raw_decomposition = self.think(decomposition_prompt)
        
        try:
            # 尝试解析LLM返回的JSON字符串
            import json
            # 清理输出，找到json部分
            start_index = raw_decomposition.find('[')
            end_index = raw_decomposition.rfind(']') + 1
            if start_index != -1 and end_index != -1:
                json_str = raw_decomposition[start_index:end_index]
                tasks = json.loads(json_str)
                if isinstance(tasks, list):
                    return tasks
            print(f"警告: Chief Agent未能解析任务分解的输出: {raw_decomposition}")
            return []
        except json.JSONDecodeError:
            print(f"警告: Chief Agent输出的JSON格式错误: {raw_decomposition}")
            return [] # 如果解析失败，返回空列表

class ManagerAgent(BaseAgent):
    """
    Manager Agent: 接收一个子任务，将其进一步分解为可执行的、更小的步骤，并指派给Worker。
    """
    def decompose_sub_task(self, sub_task_description: str) -> List[Dict[str, str]]:
        # 与Chief类似，将子任务分解为更小的步骤
        decomposition_prompt = f"根据以下子任务描述，将其分解为多个具体的、可执行的工作步骤。请以JSON格式的列表输出，每个对象包含'step_name'和'step_instruction'。例如：[{{\"step_name\": \"提取关键指标\", \"step_instruction\": \"从数据中提取血压、血糖值\"}}, ...]。\n\n子任务描述：\n{sub_task_description}"
        raw_decomposition = self.think(decomposition_prompt)
        
        try:
            import json
            start_index = raw_decomposition.find('[')
            end_index = raw_decomposition.rfind(']') + 1
            if start_index != -1 and end_index != -1:
                json_str = raw_decomposition[start_index:end_index]
                steps = json.loads(json_str)
                if isinstance(steps, list):
                    return steps
            print(f"警告: Manager Agent未能解析步骤分解的输出: {raw_decomposition}")
            return []
        except json.JSONDecodeError:
            print(f"警告: Manager Agent输出的JSON格式错误: {raw_decomposition}")
            return []

class WorkerAgent(BaseAgent):
    """
    Worker Agent: 负责执行具体的工作步骤。
    """
    def execute_step(self, step_instruction: str, context: str) -> str:
        # Worker直接执行指令
        prompt = f"请根据以下指令和上下文，完成任务并返回结果。\n\n上下文:\n{context}\n\n指令: {step_instruction}"
        return self.think(prompt)

def build_agent(config: Dict[str, Any], agent_info: Dict[str, Any]) -> BaseAgent:
    """
    根据信息创建一个Agent实例。
    """
    name = agent_info["name"]
    role = agent_info["role"]
    system_prompt = agent_info["system_prompt"]
    agent_type = agent_info.get("type", "Worker") # 默认为Worker

    agent_config = config.copy()
    agent_config["max_tokens"] = agent_info.get("max_tokens", 1000)

    agent_class_map = {
        "Chief": ChiefAgent,
        "Manager": ManagerAgent,
        "Worker": WorkerAgent,
        "Base": BaseAgent
    }
    
    agent_class = agent_class_map.get(agent_type, WorkerAgent)
    
    agent = agent_class(name, role, system_prompt, agent_config)
    print(f"Agent '{agent.name}' (类型: {agent_type}) 已创建。")
    return agent

def build_multiagent_team(config: Dict[str, Any], agents_info: List[Dict[str, Any]]) -> List[BaseAgent]:
    agents = []
    for info in agents_info:
        # 复用 build_agent 函数
        agent = build_agent(config, info)
        agents.append(agent)
    
    return agents