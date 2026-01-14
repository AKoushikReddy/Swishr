from llama_index.core import PromptTemplate
from llm_factory.get_llm import get_model

def get_chat_title(model, user_query):
    llm = get_model(model)
    title_prompt_template=("You are a helpful NBA assistant that generates short, clear, and catchy titles.\n\n"
                       "Task:\n- Read the given user query.\n- Create a concise title (max 7 words).\n"
                       "- The title should summarize the intent of the query.\n"
                       "- Avoid unnecessary words, punctuation, or filler.\n"
                       "- Keep it professional and easy to understand.\n\n"
                       "User Query:\n{user_query}\n\n"
                       "Output:\nTitle:")
    title_prompt = PromptTemplate(title_prompt_template).format(user_query=user_query)
    title = llm.complete(prompt=title_prompt).text
    return title

# Example usage
# model = "llama3:latest"
# user_query = "Is Nikola Jokic Better than Lebron James"
# title = get_chat_title(model, user_query)
# print(title)
