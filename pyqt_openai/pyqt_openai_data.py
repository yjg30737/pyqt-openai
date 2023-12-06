import openai

from pyqt_openai.sqlite import SqliteDatabase

DB = SqliteDatabase()

# if openai version is below 1.0, this will be empty and not being used
OPENAI_STRUCT = ''
if openai.__version__ >= str(1.0):
    from openai import OpenAI

    # initialize
    OPENAI_STRUCT = OpenAI(api_key='')

# https://platform.openai.com/docs/models/model-endpoint-compatibility
ENDPOINT_DICT = {
    '/v1/chat/completions': ['gpt-4', 'gpt-4-1106-preview',
                             'gpt-3.5-turbo', 'gpt-3.5-turbo-16k'],
    '/v1/completions': [
        'text-davinci-003', 'text-davinci-002', 'text-curie-001', 'text-babbage-001', 'text-ada-001', 'davinci',
        'curie', 'babbage', 'ada'
    ],
    '/v1/edits': ['text-davinci-edit-001', 'code-davinci-edit-001'],
    '/v1/audio/transcriptions': ['whisper-1'],
    '/v1/audio/translations': ['whisper-1'],
    '/v1/fine-tunes': ['davinci', 'curie', 'babbage', 'ada'],
    '/v1/embeddings': ['text-embedding-ada-002', 'text-search-ada-doc-001'],
    '/vi/moderations': ['text-moderation-stable', 'text-moderation-latest']
}

# This doesn't need endpoint
DALLE_ARR = ['dall-e-2', 'dall-e-3']

def getModelEndpoint(model):
    for k, v in ENDPOINT_DICT.items():
        endpoint_group = list(v)
        if model in endpoint_group:
            return k

def getChatModel():
    return ENDPOINT_DICT['/v1/chat/completions']