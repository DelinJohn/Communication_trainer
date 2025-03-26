
# import os
# from langchain.chat_models import init_chat_model
# from langchain_ollama import ChatOllama



# key=os.environ.get("GROQ_API_KEY")
# model_provider="groq"
# model_name="deepseek-r1-distill-llama-70b"


# def model_type(model_name,key,model_provider):
#     if not key:
#         raise ValueError("API KEY is missing. Please set it in your environment variables.")
#     if not model_name:
#         raise ValueError("model name is missing")
    
#     if not model_provider:
#         raise ValueError("model provider is missing")
#     os.environ["GROQ_API_KEY"]=key
#     model = init_chat_model(model_name, model_provider=model_provider)
#     return model

# llm=model_type(model_name,key,model_provider)

# import os
# import time
# from langchain.chat_models import init_chat_model
# from langchain.schema import HumanMessage

# # Configure retry parameters
# MAX_RETRIES = 3
# BASE_DELAY = 1  # seconds

# key = os.environ.get("GROQ_API_KEY")
# model_provider = "groq"
# model_name = "deepseek-r1-distill-llama-70b"

# def handle_api_error(error):
#     """Convert technical errors to user-friendly messages"""
#     error_messages = {
#         "rate_limit_exceeded": "Please wait a moment and try again...",
#         "service_unavailable": "Service is temporarily unavailable...",
#         "authentication_error": "API key validation failed...",
#         "default": "Something went wrong. Please try again later..."
#     }
#     return error_messages.get(error, error_messages["default"])

# def model_type(model_name, key, model_provider):
#     """Initialize model with retry logic"""
#     if not all([key, model_name, model_provider]):
#         raise ValueError("Missing required configuration parameters")
    
#     os.environ["GROQ_API_KEY"] = key
    
#     for attempt in range(MAX_RETRIES):
#         try:
#             model = init_chat_model(model_name, model_provider=model_provider)
#             return model
#         except Exception as e:
#             error_type = str(e).lower()
#             delay = BASE_DELAY * (2 ** attempt)
            
#             if 'rate limit' in error_type:
#                 print(f"Rate limited. Retrying in {delay} seconds...")
#                 time.sleep(delay)
#             elif 'service unavailable' in error_type:
#                 print(f"Service unavailable. Retry {attempt+1}/{MAX_RETRIES}")
#                 time.sleep(delay)
#             else:
#                 raise ValueError(handle_api_error(error_type))
    
#     raise Exception("Failed to initialize model after multiple attempts")

# def safe_completion(prompt):
#     """Safe execution with error handling"""
#     try:
#         return llm.invoke([HumanMessage(content=prompt)])
#     except Exception as e:
#         return handle_api_error(str(e))

# # Initialize with error handling
# try:
#     llm = model_type(model_name, key, model_provider)
# except Exception as e:
#     print(f"Initialization Error: {handle_api_error(str(e))}")
#     # Fallback logic or exit gracefully