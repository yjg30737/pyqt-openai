from dataclasses import dataclass, fields


@dataclass
class ChatContainer:
    id: str = ""
    model: str = ""
    update_dt: str = ""
    insert_dt: str = ""

    def __init__(self, **kwargs):
        for k in self.__annotations__:
            setattr(self, k, kwargs.get(k, ""))
        for key, value in kwargs.items():
            if key in self.__annotations__:
                setattr(self, key, value)

    @staticmethod
    def get_keys():
        return [field.name for field in fields(ImageChatContainer)]

    @staticmethod
    def get_keys_for_insert():
        """
        Function that returns the keys of the target data type as a list.
        Delete id, update_dt and insert_dt from the list.
        """
        arr = ImageChatContainer.get_keys()
        arr.remove('id')
        arr.remove('update_dt')
        arr.remove('insert_dt')
        return arr

    def get_values_for_insert(self):
        """
        Function that returns the values of the target data type as a list.
        Delete ID, update_dt and insert_dt from the list.
        """
        arr = [getattr(self, key) for key in self.get_keys_for_insert()]
        return arr

    def create_insert_query(self, table_name: str):
        """
        Function to dynamically generate an SQLite insert statement.
        Takes the table name as a parameter.
        """
        field_names = self.get_keys_for_insert()
        columns = ', '.join(field_names)
        placeholders = ', '.join(['?' for _ in field_names])
        query = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
        return query


@dataclass
class TextChatContainer(ChatContainer):
    role: str = ""
    content: str = ""
    finish_reason: str = ""
    prompt_tokens: str = ""
    completion_tokens: str = ""


@dataclass
class FavoriteChatContainer(TextChatContainer):
    favorite_type: str = ""
    id_fk: str = ""
    favorite_dt: str = ""


@dataclass
class ImageChatContainer(ChatContainer):
    prompt: str = ""
    n: str = ""
    size: str = ""
    quality: str = ""
    data: str = ""
    style: str = ""
    revised_prompt: str = ""
    width: str = ""
    height: str = ""
    negative_prompt: str = ""