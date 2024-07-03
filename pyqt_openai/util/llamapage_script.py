from llama_index.core import VectorStoreIndex, SimpleDirectoryReader


class GPTLLamaIndexWrapper:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._directory = './example'
        self._query_engine = None

    def set_directory(self, directory):
        try:
            self._directory = directory
            documents = SimpleDirectoryReader(self._directory, required_exts=['.txt']).load_data()
            index = VectorStoreIndex.from_documents(documents)
            self._query_engine = index.as_query_engine()
        except Exception as e:
            print(e)

    def get_directory(self):
        return self._directory

    def get_response(self, text):
        try:
            if self._query_engine:
                resp = self._query_engine.query(
                    text,
                )
                return resp.response
            else:
                raise Exception('Query engine not initialized. Maybe you need to set the directory first. Check the directory path.')
        except Exception as e:
            return str(e)