from core.moderation.base import BaseModeration

class OpenAIModeration(BaseModeration):
    type = "openai"

    @classmethod
    def validate_config(cls, config: dict):
        cls._validate_inputs_and_outputs_config(config, True)