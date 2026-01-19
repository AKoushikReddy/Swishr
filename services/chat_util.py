from llama_index.core.llms import ChatMessage, MessageRole
from llm_factory.get_llm import get_model


def get_answer(model_name, chat_history, stream: bool = False):
    """
    Get response from the model.

    - Supports streaming when stream=True (yields token deltas for st.write_stream)
    - Keeps your NBA-only restriction
    - Falls back to normal response when stream=False
    """
    llm = get_model(model_name)

    # Cleaned-up system prompt (NBA-only focus)
    messages = [
        ChatMessage(
            role=MessageRole.SYSTEM,
            content="You are a helpful chat assistant who answers questions ONLY about basketball and the National Basketball Association (NBA). "
                    "For any other topic, reply: 'Sorry, I can only talk about NBA.' "
                    "Strictly no other topics allowed. Let's only talk about basketball here."
        )
    ]

    # Add the conversation history
    messages.extend(
        ChatMessage(role=MessageRole[msg["role"].upper()], content=msg["content"])
        for msg in chat_history
    )

    if stream:
        # Streaming mode - yield token deltas for smooth typing effect in Streamlit
        stream_response = llm.stream_chat(messages=messages)
        for token in stream_response:
            yield token.delta  # Each delta is the new text chunk
    else:
        # Normal mode (non-streaming)
        response = llm.chat(messages=messages)
        return response.message.content

# Example usage (unchanged)
# model_name = "gemma2:2b"
# chat_history = [
#     {"role": "user", "content": "What is Artificial Intelligence?"}
# ]
# response = get_answer(model_name, chat_history)
# print(response)