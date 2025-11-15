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

def build_multiagent_team(config: Dict[str, Any], agents_info: List[Dict[str, Any]]) -> List[BaseAgent]:
    agents = []
    for info in agents_info:
        name = info["name"]
        role = info["role"]
        system_prompt = info["system_prompt"]
        
        # 创建代理专用config，添加max_tokens
        agent_config = config.copy()
        agent_config["max_tokens"] = info["max_tokens"]  # 添加每个代理的max_tokens
        
        # 动态创建子类（继承BaseAgent）
        class_name = name + "Agent"
        def __init__(self, config):
            BaseAgent.__init__(self, name, role, system_prompt, config)
        
        cls = type(class_name, (BaseAgent,), {'__init__': __init__})
        
        # 创建实例
        agent = cls(agent_config)  # 传递agent_config
        print(f"Agent {agent.name} 已创建。")
        agents.append(agent)
    
    return agents