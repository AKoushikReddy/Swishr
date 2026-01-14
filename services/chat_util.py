from llama_index.core.llms import ChatMessage, MessageRole
from llm_factory.get_llm import get_model

def get_answer(model_name, chat_history):
    llm = get_model(model_name)

    # Always prepend a system message
    messages = [
        ChatMessage(role=MessageRole.SYSTEM, content="You are a helpful chat assistant.Who talks only about National Basketball Association, Anything else you should reply, Sorry can only talk about NBA. Strictly You are not supposed to have conversations about anything "
                                                     "else other than basketball. No other topic should be allowed or taken for a prompt.\n Lets only talk about basketball here.... should be the response."

                                    )

    ]

    # Append the rest of the history
    messages.extend(
        ChatMessage(role=MessageRole[msg["role"].upper()], content=msg["content"])
        for msg in chat_history
    )

    response = llm.chat(messages=messages)
    return response.message.content

# # example usage
# model_name = "gemma2:2b"
# chat_history = [
#     {"role": "user", "content": "What is Artificial Intelligence?"}
# ]
# response = get_answer(model_name, chat_history)
# print(response)

