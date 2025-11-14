import os
from openai import OpenAI
from typing import List, Dict, Any

class BaseAgent:
    def __init__(self, name: str, role: str, system_prompt: str, config: Dict[str, Any]):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.config = config
        # 创建OpenAI客户端
        self.client = OpenAI(
            api_key=self.config["LLM"]["api_key"],
            base_url=self.config["LLM"]["base_url"]
        )

    def think(self, input_data: str) -> str:
        try:
            completion = self.client.chat.completions.create(
                model=self.config["LLM"]["model"],
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": input_data}
                ],
                temperature=self.config["LLM"]["temperature"],
                max_tokens=self.config["LLM"]["max_tokens"],
                stream=False
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"

def build_multiagent_team(config: Dict[str, Any], agents_info: List[Dict[str, Any]]) -> List[BaseAgent]:
    agents = []
    for info in agents_info:
        name = info["name"]
        role = info["role"]
        system_prompt = info["system_prompt"]
        
        # 动态创建子类（继承BaseAgent）
        class_name = name + "Agent"
        def __init__(self, config):
            BaseAgent.__init__(self, name, role, system_prompt, config)
        
        cls = type(class_name, (BaseAgent,), {'__init__': __init__})
        
        # 创建实例
        agent = cls(config)
        print(f"Agent {agent.name} 已创建。")
        agents.append(agent)
    
    return agents