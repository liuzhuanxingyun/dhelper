import os
from openai import OpenAI
from typing import List, Dict, Any

class Agent:
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

def build_multiagent_team(config: Dict[str, Any], agents_info: List[Dict[str, Any]]) -> List[Agent]:
    agents = []
    for info in agents_info:
        agent = Agent(
            name=info["name"],
            role=info["role"],
            system_prompt=info["system_prompt"],
            config=config
        )
        # # 发送“你是谁”确认Agent是否创建成功 (建议在稳定后注释掉)
        # identity_response = agent.think("你是谁")
        # if identity_response and not identity_response.startswith("Error"):
        #     print(f"Agent {agent.name} 创建成功: {identity_response}")
        #     agents.append(agent)
        # else:
        #     print(f"Agent {agent.name} 创建失败: {identity_response}")
        print(f"Agent {agent.name} 已创建。")
        agents.append(agent)
    
    return agents