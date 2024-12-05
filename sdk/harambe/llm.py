from typing import Dict, List, Literal

from openai import OpenAI

from harambe.settings import get_settings

LLM_AGENTS = Literal["openai"]


class LLMManager:
    def __init__(self, agent: LLM_AGENTS = "openai", model: str = "gpt-4o-mini"):
        self.agent_name = agent
        self.model = model

        if agent == "openai":
            self.agent = OpenAI(api_key=get_settings().openai_api_key)

    def query(self, prompts: List[Dict[str, str]]) -> str:
        """
        Query the LLM agent with the given prompts.
        Parameters:
            prompts: List[{ type, content}]
            type: one of ["text", "image"]
            content: "string"

        Returns:
            response: The response from the LLM agent.
        """

        if self.agent_name == "openai":
            content = []
            for prompt in prompts:
                if prompt["type"] == "text":
                    content.append({"type": "text", "text": prompt["content"]})

                if prompt["type"] == "image":
                    content.append(
                        {"type": "image", "image_url": {"url": f"{prompt['content']}"}}
                    )

            response = self.agent.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": content}],
            )

            return response.choices[0].message.content
