from llama_index.llms.ollama import Ollama
from config.settings import Settings

_model_name = None
_current_instance = None
settings = Settings()

def get_model(model_name):
    global _model_name, _current_instance
    if _model_name == _current_instance and _current_instance is not None:
        return _current_instance
    llm = Ollama(base_url=settings.OLLAMA_URL, model=model_name)
    _current_instance = llm
    _model_name = model_name
    return _current_instance

# CHECK
# check_llm = get_model("llama3.1:latest")
# print(check_llm)
# print(type(check_llm))
