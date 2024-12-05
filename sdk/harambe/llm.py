from typing import Dict, List, Literal, Optional

from openai import OpenAI

from harambe.settings import get_settings

LLM_AGENTS = Literal["openai"]


class LLMManager:
    def __init__(self, agent: Optional[LLM_AGENTS] = None, model: Optional[str] = None):
        self.agent_name = "openai" if agent is None else agent
        self.model = "gpt-4o-mini" if model is None else model

        if self.agent_name == "openai":
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
                        {
                            "type": "image_url",
                            "image_url": {"url": f"{prompt['content']}"},
                        }
                    )

            response = self.agent.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": content}],
            )

            return response.choices[0].message.content
