import openai

# static
# https://platform.openai.com/docs/models/model-endpoint-compatibility
ENDPOINT_DICT = {
    '/v1/chat/completions': ['gpt-4', 'gpt-4-0314', 'gpt-4-32k', 'gpt-4-32k-0314', 'gpt-3.5-turbo', 'gpt-3.5-turbo-0301'],
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

def getModelEndpoint(model):
    for k, v in ENDPOINT_DICT.items():
        endpoint_group = list(v)
        if model in endpoint_group:
            return k

def getLatestModel():
    return ['gpt-3.5-turbo',
            'gpt-3.5-turbo-0301',
            'text-davinci-003',
            'text-davinci-002',
            'code-davinci-002']

# dynamic
class ModelData:
    def __init__(self):
        super().__init__()
        self.__modelList = []

    def setModelData(self):
        self.__modelList = openai.Model.list()['data']

    def getModelData(self):
        return self.__modelList

    def getPermissionProperty(self, model_name, property):
        return [model['permission'][0][property] for model in self.__modelList if model['id'] == model_name][0]