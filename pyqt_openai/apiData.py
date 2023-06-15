import openai

# static
# https://platform.openai.com/docs/models/model-endpoint-compatibility
ENDPOINT_DICT = {
    '/v1/chat/completions': ['gpt-4', 'gpt-4-0613', 'gpt-4-32k', 'gpt-4-32k-0613',
                             'gpt-3.5-turbo', 'gpt-3.5-turbo-0613', 'gpt-3.5-turbo-16k', 'gpt-3.5-turbo-16k-0613', 'gpt-3.5-turbo-0301'],
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

# new
def getCompletionModel():
    return [
        'text-davinci-003',
        'text-davinci-002',
        'text-curie-001',
        'text-babbage-001',
        'text-ada-001'
    ]

def getChatModel():
    return ENDPOINT_DICT['/v1/chat/completions']

# dynamic
class ModelData:
    def __init__(self):
        super().__init__()
        self.__modelList = []

    def setModelData(self):
        """
        this is only used in completion type, so subtract chat model from it
        :return:
        """
        self.__modelList = list(filter(lambda x: x['id'] not in getChatModel(), openai.Model.list()['data']))

    def getModelData(self):
        return self.__modelList

    def getPermissionProperty(self, model_name, property):
        return [model['permission'][0][property] for model in self.__modelList if model['id'] == model_name][0]