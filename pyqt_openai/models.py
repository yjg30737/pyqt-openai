from dataclasses import dataclass, fields

from pyqt_openai.res.language_dict import LangClass


@dataclass
class Container:
    def __init__(self, **kwargs):
        """
        You don't have to call this if you want to use default class variables
        """
        for k in self.__annotations__:
            setattr(self, k, kwargs.get(k, ""))
        for key, value in kwargs.items():
            if key in self.__annotations__:
                setattr(self, key, value)

    @classmethod
    def get_keys(cls):
        return [field.name for field in fields(cls)]

    @classmethod
    def get_keys_for_insert(cls, excludes: list = None):
        """
        Function that returns the keys of the target data type as a list.
        Exclude the keys in the "excludes" list.
        """
        if excludes is None:
            excludes = []
        arr = cls.get_keys()
        for exclude in excludes:
            if exclude in arr:
                arr.remove(exclude)
        return arr

    def get_values_for_insert(self, excludes: list = None):
        """
        Function that returns the values of the target data type as a list.
        """
        if excludes is None:
            excludes = []
        arr = [getattr(self, key) for key in self.get_keys_for_insert(excludes)]
        return arr

    def get_items(self, excludes: list = None):
        """
        Function that returns the items of the target data type as a list.
        """
        if excludes is None:
            excludes = []
        return {key: getattr(self, key) for key in self.get_keys_for_insert(excludes)}.items()

    def create_insert_query(self, table_name: str, excludes: list = None):
        if excludes is None:
            excludes = []
        """
        Function to dynamically generate an SQLite insert statement.
        Takes the table name as a parameter.
        """
        field_names = self.get_keys_for_insert(excludes)
        columns = ', '.join(field_names)
        placeholders = ', '.join(['?' for _ in field_names])
        query = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
        return query

@dataclass
class SettingsParamsContainer(Container):
    lang: str = LangClass.lang_changed()
    db: str = 'conv'
    do_not_ask_again: bool = False
    notify_finish: bool = False
    show: bool = False

@dataclass
class ImagePromptContainer(Container):
    id: str = ""
    model: str = ""
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
    update_dt: str = ""
    insert_dt: str = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)