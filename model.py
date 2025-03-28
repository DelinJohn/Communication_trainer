from tenacity import retry, stop_after_attempt, wait_exponential
import os
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
load_dotenv()



key=os.environ.get("OPENAI_API_KEY")
model_provider=os.environ.get('GPT_model_provider')
model_name=os.environ.get('GPT_model')


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def model_type(model_name,key,model_provider):

    """This fucntion is responsible for selection of the llm"""
    if not key:
        raise ValueError("API KEY is missing. Please set it in your environment variables.")
    if not model_name:
        raise ValueError("model name is missing")
    
    if not model_provider:
        raise ValueError("model provider is missing")
    os.environ["API_KEY"]=key
    model = init_chat_model(model_name, model_provider=model_provider)
    return model

llm=model_type(model_name,key,model_provider)