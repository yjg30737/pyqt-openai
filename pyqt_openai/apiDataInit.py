import openai

# openai.api_key

ALLOW_FINETUNING_DATA = {}

def getModelList():
    return openai.Model.list()['data']

model_list = getModelList()
for model in model_list:
    print(model.id)
    print(model.permission[0]['allow_fine_tuning'])