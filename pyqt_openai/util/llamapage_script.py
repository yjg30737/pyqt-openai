import os

from llama_index import GPTVectorStoreIndex, SimpleDirectoryReader, LLMPredictor, ServiceContext
from langchain.chat_models import ChatOpenAI

# os.environ['OPENAI_API_KEY'] = 'YOUR_API_KEY'
# this app will set api key to environment variable and save it in openai_ini.ini
# openai_ini.ini will be generated if api key you entered is valid


class GPTLLamaIndexClass:
    def __init__(self):
        self.__initVal()
        self.__init()

    def __initVal(self):
        self.__directory = './example'
        self.__model = 'gpt-3.5-turbo'
        self.__temperature = 0.7
        self.__streaming = True
        self.__chunk_size_limit = 512
        self.__similarity_top_k = 3

    def setDirectory(self, directory):
        self.__directory = directory

    def __init(self):
        documents = SimpleDirectoryReader(self.__directory).load_data()

        llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=self.__temperature, model_name=self.__model, streaming=self.__streaming))

        service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, chunk_size_limit=self.__chunk_size_limit)
        index = GPTVectorStoreIndex.from_documents(documents, service_context=service_context)

        self.__query_engine = index.as_query_engine(
            service_context=service_context,
            similarity_top_k=self.__similarity_top_k,
            streaming=True
        )

    def getResponse(self, text):
        response = self.__query_engine.query(
            text,
        )

        return response

# BeautifulSoupWebReader
# DiscordReader
# GithubRepositoryReader