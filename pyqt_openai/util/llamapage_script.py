import os, openai

from llama_index import GPTVectorStoreIndex, SimpleDirectoryReader, LLMPredictor, ServiceContext
from langchain.chat_models import ChatOpenAI



class GPTLLamaIndexClass:
    def __init__(self):
        self.__initVal()
        self.__directory = None

    def __initVal(self) -> None:
        """
        default value of llamaindex
        :return:
        """
        self.__chunk_size_limit = 512
        self.__similarity_top_k = 3

    def set_directory(self, directory):
        self.__directory = directory
        self.__documents = SimpleDirectoryReader(self.__directory).load_data()

    def get_directory(self):
        return self.__directory

    def set_openai_arg(self, **args):
        self.__openai_arg = args
        self.__init_engine()

    def set_chunk_size_limit(self, chunk_size_limit):
        self.__chunk_size_limit = chunk_size_limit

    def set_similarity_top_k(self, similarity_top_k):
        self.__similarity_top_k = similarity_top_k

    def __init_engine(self):
        try:
            query_engine_streaming = self.__openai_arg['stream']

            keys_to_keep = ['model', 'temperature']

            # Create a new dictionary with the desired keys
            filtered_dict = {key: self.__openai_arg[key] for key in keys_to_keep}

            # If you want to modify the original dictionary in-place, you can use this:
            self.__openai_arg.clear()
            self.__openai_arg.update(filtered_dict)

            llm_predictor = LLMPredictor(llm=ChatOpenAI(**self.__openai_arg, streaming=True))
            service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, chunk_size_limit=self.__chunk_size_limit)
            index = GPTVectorStoreIndex.from_documents(self.__documents, service_context=service_context)

            self.__query_engine = index.as_query_engine(
                service_context=service_context,
                similarity_top_k=self.__similarity_top_k,
                streaming=query_engine_streaming
            )
        except Exception as e:
            raise Exception

    def get_response(self, text):
        response = self.__query_engine.query(
            text,
        )

        return response


# openai_arg = {
#                     'model': 'gpt-3.5-turbo',
#                     'temperature': 0.7,
#                     'top_p': 1,
#                     'frequency_penalty': 0,
#                     'presence_penalty': 0,
#                     'stream': False,
#                 }
#
# c = GPTLLamaIndexClass()
# c.set_directory('./llama_example')
# c.set_openai_arg(**openai_arg)
#
# response = c.get_response(
#     "Hello, who is yjg30737 and what language is he good at?",
# )
# print(response)
# response = c.get_response(
#     "What is pyqt-openai?",
# )
# print(response)
# response = c.get_response(
#     "Can i use gpt-4 in pyqt-openai?",
# )
# print(response)
# # BeautifulSoupWebReader
# # DiscordReader
# # GithubRepositoryReader