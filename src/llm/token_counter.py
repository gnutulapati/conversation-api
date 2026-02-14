import tiktoken
import logging

logger = logging.getLogger(__name__)

def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """
    Count the number of tokens in a string.
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # Fallback to cl100k_base for newer models or unknown ones
        encoding = tiktoken.get_encoding("cl100k_base")
        
    return len(encoding.encode(text))

def count_message_tokens(messages: list, model: str = "gpt-3.5-turbo") -> int:
    """
    Count tokens for a list of messages.
    Generic approximation for chat format.
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
         encoding = tiktoken.get_encoding("cl100k_base")

    num_tokens = 0
    for message in messages:
        # approx 4 tokens per message (role, content, etc overhead)
        num_tokens += 4
        for key, value in message.items():
            num_tokens += len(encoding.encode(str(value)))
    num_tokens += 2  # priming
    return num_tokens
