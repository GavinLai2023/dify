from http import HTTPStatus
from typing import Optional, Generator, Union, List
import dashscope
from dashscope.api_entities.dashscope_response import DashScopeAPIResponse
from dashscope.common.error import AuthenticationError, RequestFailure, \
    InvalidParameter, UnsupportedModel, ServiceUnavailableError, UnsupportedHTTPMethod

from langchain.llms.tongyi import generate_with_retry, stream_generate_with_retry

from core.model_runtime.entities.message_entities import PromptMessage, PromptMessageTool, UserPromptMessage, AssistantPromptMessage, \
    SystemPromptMessage
from core.model_runtime.entities.llm_entities import LLMResult, LLMResultChunk, \
    LLMResultChunkDelta
from core.model_runtime.errors.invoke import InvokeConnectionError, InvokeServerUnavailableError, InvokeRateLimitError, \
    InvokeAuthorizationError, InvokeBadRequestError, InvokeError
from core.model_runtime.errors.validate import CredentialsValidateFailedError
from core.model_runtime.model_providers.__base.large_language_model import LargeLanguageModel

from ._client import EnhanceTongyi

class TongyiLargeLanguageModel(LargeLanguageModel):

    def _invoke(self, model: str, credentials: dict,
                prompt_messages: list[PromptMessage], model_parameters: dict,
                tools: Optional[list[PromptMessageTool]] = None, stop: Optional[List[str]] = None,
                stream: bool = True, user: Optional[str] = None) \
            -> Union[LLMResult, Generator]:
        """
        Invoke large language model

        :param model: model name
        :param credentials: model credentials
        :param prompt_messages: prompt messages
        :param model_parameters: model parameters
        :param tools: tools for tool calling
        :param stop: stop words
        :param stream: is stream response
        :param user: unique user id
        :return: full response or stream response chunk generator result
        """
        # invoke model
        return self._generate(model, credentials, prompt_messages, model_parameters, stop, stream, user)

    def get_num_tokens(self, model: str, prompt_messages: list[PromptMessage],
                       tools: Optional[list[PromptMessageTool]] = None) -> int:
        """
        Get number of tokens for given prompt messages

        :param model:
        :param prompt_messages:
        :param tools: tools for tool calling
        :return:
        """
        response = dashscope.Tokenization.call(
            model=model,
            prompt=self._convert_messages_to_prompt(prompt_messages),
        )
        
        if response.status_code == HTTPStatus.OK:
            return response['usage']['input_tokens']
        else:
            raise self._invoke_error_mapping[InvokeBadRequestError][0](response['message'])

    def validate_credentials(self, model: str, credentials: dict) -> None:
        """
        Validate model credentials

        :param model: model name
        :param credentials: model credentials
        :return:
        """
        try:
            self._generate(
                model=model,
                credentials=credentials,
                prompt_messages=[
                    UserPromptMessage(content="ping"),
                ],
                model_parameters={
                    "temperature": 0.5,
                },
                stream=False
            )
        except Exception as ex:
            raise CredentialsValidateFailedError(str(ex))

    def _generate(self, model: str, credentials: dict,
                  prompt_messages: list[PromptMessage], model_parameters: dict,
                  stop: Optional[List[str]] = None, stream: bool = True,
                  user: Optional[str] = None) -> Union[LLMResult, Generator]:
        """
        Invoke large language model

        :param model: model name
        :param credentials: credentials
        :param prompt_messages: prompt messages
        :param model_parameters: model parameters
        :param stop: stop words
        :param stream: is stream response
        :param user: unique user id
        :return: full response or stream response chunk generator result
        """
        extra_model_kwargs = {}
        if stop:
            extra_model_kwargs['stop_sequences'] = stop

        # transform credentials to kwargs for model instance
        credentials_kwargs = self._to_credential_kwargs(credentials)

        dashscope.api_key = credentials_kwargs['api_key']

        client = EnhanceTongyi(
            model_name=model,
            streaming=stream,
            dashscope_api_key=credentials_kwargs['api_key'],
        )

        params = {
            'model': model,
            'prompt': self._convert_messages_to_prompt(prompt_messages),
            **model_parameters
        }
        if stream:
            responses = stream_generate_with_retry(
                client, 
                stream=True,
                **params
            )

            return self._handle_generate_stream_response(model, credentials, responses, prompt_messages)

        response = generate_with_retry(
            client,
            **params,
        )
        return self._handle_generate_response(model, credentials, response, prompt_messages)
        
    def _handle_generate_response(self, model: str, credentials: dict, response: DashScopeAPIResponse,
                                  prompt_messages: list[PromptMessage]) -> LLMResult:
        """
        Handle llm response

        :param model: model name
        :param credentials: credentials
        :param response: response
        :param prompt_messages: prompt messages
        :return: llm response
        """
        # transform assistant message to prompt message
        assistant_prompt_message = AssistantPromptMessage(
            content=response.output.text
        )

        # transform usage
        usage = self._calc_response_usage(model, credentials, response.usage.input_tokens, response.usage.output_tokens)

        # transform response
        result = LLMResult(
            model=model,
            message=assistant_prompt_message,
            usage=usage,
        )

        return result

    def _handle_generate_stream_response(self, model: str, credentials: dict, responses: list[Generator],
                                         prompt_messages: list[PromptMessage]) -> Generator:
        """
        Handle llm stream response

        :param model: model name
        :param credentials: credentials
        :param response: response
        :param prompt_messages: prompt messages
        :return: llm response chunk generator result
        """
        for index, response in enumerate(responses):
            resp_finish_reason = response.output.finish_reason
            resp_content = response.output.text
            useage = response.usage

            if resp_finish_reason is None and (resp_content is None or resp_content == ''):
                continue

            # transform assistant message to prompt message
            assistant_prompt_message = AssistantPromptMessage(
                content=resp_content if resp_content else '',
            )

            if resp_finish_reason is not None:
                # transform usage
                usage = self._calc_response_usage(model, credentials, useage.input_tokens, useage.output_tokens)

                yield LLMResultChunk(
                    model=model,
                    delta=LLMResultChunkDelta(
                        index=index,
                        message=assistant_prompt_message,
                        finish_reason=resp_finish_reason,
                        usage=usage
                    )
                )
            else:
                yield LLMResultChunk(
                    model=model,
                    delta=LLMResultChunkDelta(
                        index=index,
                        message=assistant_prompt_message
                    )
                )

    def _to_credential_kwargs(self, credentials: dict) -> dict:
        """
        Transform credentials to kwargs for model instance

        :param credentials:
        :return:
        """
        credentials_kwargs = {
            "api_key": credentials['tongyi_api_key'],
        }

        return credentials_kwargs

    def _convert_one_message_to_text(self, message: PromptMessage) -> str:
        """
        Convert a single message to a string.

        :param message: PromptMessage to convert.
        :return: String representation of the message.
        """
        human_prompt = "\n\nHuman:"
        ai_prompt = "\n\nAssistant:"
        content = message.content

        if isinstance(message, UserPromptMessage):
            message_text = f"{human_prompt} {content}"
        elif isinstance(message, AssistantPromptMessage):
            message_text = f"{ai_prompt} {content}"
        elif isinstance(message, SystemPromptMessage):
            message_text = content
        else:
            raise ValueError(f"Got unknown type {message}")

        return message_text
    
    def _convert_messages_to_prompt(self, messages: List[PromptMessage]) -> str:
        """
        Format a list of messages into a full prompt for the Anthropic model

        :param messages: List of PromptMessage to combine.
        :return: Combined string with necessary human_prompt and ai_prompt tags.
        """
        messages = messages.copy()  # don't mutate the original list

        text = "".join(
            self._convert_one_message_to_text(message)
            for message in messages
        )

        # trim off the trailing ' ' that might come from the "Assistant: "
        return text.rstrip()

    @property
    def _invoke_error_mapping(self) -> dict[type[InvokeError], list[type[Exception]]]:
        """
        Map model invoke error to unified error
        The key is the error type thrown to the caller
        The value is the error type thrown by the model,
        which needs to be converted into a unified error type for the caller.

        :return: Invoke error mapping
        """
        return {
            InvokeConnectionError: [
                RequestFailure,
            ],
            InvokeServerUnavailableError: [
                ServiceUnavailableError,
            ],
            InvokeRateLimitError: [],
            InvokeAuthorizationError: [
                AuthenticationError,
            ],
            InvokeBadRequestError: [
                InvalidParameter,
                UnsupportedModel,
                UnsupportedHTTPMethod,
            ]
        }