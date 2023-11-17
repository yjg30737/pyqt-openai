import openai

# if openai version is below 1.0, this will be empty and not being used
OPENAI_STRUCT = ''
if openai.__version__ >= str(1.0):
    from openai import OpenAI

    # initialize
    OPENAI_STRUCT = OpenAI(api_key='')