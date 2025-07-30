from typing import Optional

from co_optimal.config.v1 import BaseSettingsWrapper

from co_optimal.utils.v1.enums import LLMEnums, OpenAIEnums


class LLMConfig(BaseSettingsWrapper):
    """
    Configuration class for the LLM model

    """

    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    MODEL_TEMPERATURE: Optional[float] = 0.8
    MODEL_CLASS: Optional[str] = LLMEnums.openai.value
    MODEL_NAME: Optional[str] = OpenAIEnums.gpt_4o_mini.value

    EXPONENTIAL_WAIT_MIN: Optional[int] = 1
    EXPONENTIAL_WAIT_MAX: Optional[int] = 60

    MAX_ATTEMPTS: Optional[int] = 6

    MAX_CONTEXT_LEN: Optional[int] = 4096


llm_config = LLMConfig()
