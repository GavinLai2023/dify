import sys
from typing import Optional, List

from core.model_runtime.callbacks.base_callback import Callback
from core.model_runtime.entities.llm_entities import LLMResultChunk, LLMResult
from core.model_runtime.entities.message_entities import PromptMessageTool, PromptMessage
from core.model_runtime.model_providers.__base.ai_model import AIModel


class LoggingCallback(Callback):
    def on_before_invoke(self, llm_instance: AIModel, model: str, credentials: dict,
                         prompt_messages: list[PromptMessage], model_parameters: dict,
                         tools: Optional[list[PromptMessageTool]] = None, stop: Optional[List[str]] = None,
                         stream: bool = True, user: Optional[str] = None) -> None:
        """
        Before invoke callback

        :param llm_instance: LLM instance
        :param model: model name
        :param credentials: model credentials
        :param prompt_messages: prompt messages
        :param model_parameters: model parameters
        :param tools: tools for tool calling
        :param stop: stop words
        :param stream: is stream response
        :param user: unique user id
        """
        self.print_text("\n[on_llm_before_invoke]\n", color='blue')
        self.print_text(f"Model: {model}\n", color='blue')
        self.print_text(f"Parameters:\n", color='blue')
        for key, value in model_parameters.items():
            self.print_text(f"\t{key}: {value}\n", color='blue')

        if stop:
            self.print_text(f"\tstop: {stop}\n", color='blue')

        if tools:
            self.print_text(f"\tTools:\n", color='blue')
            for tool in tools:
                self.print_text(f"\ttool: {tool.name}\n", color='blue')

        self.print_text(f"Stream: {stream}\n", color='blue')

        if user:
            self.print_text(f"User: {user}\n", color='blue')

        self.print_text(f"Prompt messages:\n", color='blue')
        for prompt_message in prompt_messages:
            if prompt_message.name:
                self.print_text(f"\tname: {prompt_message.name}\n", color='blue')

            self.print_text(f"\trole: {prompt_message.role.value}\n", color='blue')
            self.print_text(f"\tcontent: {prompt_message.content}\n", color='blue')

        if stream:
            self.print_text("\n[on_llm_new_chunk]")

    def on_new_chunk(self, llm_instance: AIModel, chunk: LLMResultChunk, model: str, credentials: dict,
                     prompt_messages: list[PromptMessage], model_parameters: dict,
                     tools: Optional[list[PromptMessageTool]] = None, stop: Optional[List[str]] = None,
                     stream: bool = True, user: Optional[str] = None):
        """
        On new chunk callback

        :param llm_instance: LLM instance
        :param chunk: chunk
        :param model: model name
        :param credentials: model credentials
        :param prompt_messages: prompt messages
        :param model_parameters: model parameters
        :param tools: tools for tool calling
        :param stop: stop words
        :param stream: is stream response
        :param user: unique user id
        """
        sys.stdout.write(chunk.delta.message.content)
        sys.stdout.flush()

    def on_after_invoke(self, llm_instance: AIModel, result: LLMResult, model: str, credentials: dict,
                        prompt_messages: list[PromptMessage], model_parameters: dict,
                        tools: Optional[list[PromptMessageTool]] = None, stop: Optional[List[str]] = None,
                        stream: bool = True, user: Optional[str] = None) -> None:
        """
        After invoke callback

        :param llm_instance: LLM instance
        :param result: result
        :param model: model name
        :param credentials: model credentials
        :param prompt_messages: prompt messages
        :param model_parameters: model parameters
        :param tools: tools for tool calling
        :param stop: stop words
        :param stream: is stream response
        :param user: unique user id
        """
        self.print_text("\n[on_llm_after_invoke]\n", color='yellow')
        self.print_text(f"Content: {result.message.content}\n", color='yellow')

        if result.message.tool_calls:
            self.print_text(f"Tool calls:\n", color='yellow')
            for tool_call in result.message.tool_calls:
                self.print_text(f"\t{tool_call.id}\n", color='yellow')

        self.print_text(f"Model: {result.model}\n", color='yellow')
        self.print_text(f"Usage: {result.usage}\n", color='yellow')
        self.print_text(f"System Fingerprint: {result.system_fingerprint}\n", color='yellow')

    def on_invoke_error(self, llm_instance: AIModel, ex: Exception, model: str, credentials: dict,
                        prompt_messages: list[PromptMessage], model_parameters: dict,
                        tools: Optional[list[PromptMessageTool]] = None, stop: Optional[List[str]] = None,
                        stream: bool = True, user: Optional[str] = None) -> None:
        """
        Invoke error callback

        :param llm_instance: LLM instance
        :param ex: exception
        :param model: model name
        :param credentials: model credentials
        :param prompt_messages: prompt messages
        :param model_parameters: model parameters
        :param tools: tools for tool calling
        :param stop: stop words
        :param stream: is stream response
        :param user: unique user id
        """
        self.print_text("\n[on_llm_invoke_error]\n", color='red')
        self.print_text(f"Exception: {ex}\n", color='red')