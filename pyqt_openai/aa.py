# from dataclasses import dataclass, fields, asdict
#
#
# @dataclass
# class ImagePromptContainer:
#     ID: str = ""
#     model: str = ""
#     prompt: str = ""
#     n: str = ""
#     size: str = ""
#     quality: str = ""
#     data: str = ""
#     style: str = ""
#     revised_prompt: str = ""
#     width: str = ""
#     height: str = ""
#     negative_prompt: str = ""
#     update_dt: str = ""
#     insert_dt: str = ""
#
#
#     def __init__(self, **kwargs):
#         for k in self.__annotations__:
#             setattr(self, k, kwargs.get(k, ""))
#         for key, value in kwargs.items():
#             if key in self.__annotations__:
#                 setattr(self, key, value)
#
#     @staticmethod
#     def get_keys():
#         return [field.name for field in fields(ImagePromptContainer)]
#
#     @staticmethod
#     def get_keys_for_insert():
#         """
#         Function that returns the keys of the target data type as a list.
#         Delete ID, update_dt and insert_dt from the list.
#         """
#         arr = ImagePromptContainer.get_keys()
#         arr.remove('ID')
#         arr.remove('update_dt')
#         arr.remove('insert_dt')
#         return arr
#
#     def create_insert_query(self, table_name: str):
#         """
#         Function to dynamically generate an SQLite insert statement.
#         Takes the table name as a parameter.
#         """
#         field_names = self.get_keys_for_insert()
#         columns = ', '.join(field_names)
#         placeholders = ', '.join(['?' for _ in field_names])
#         query = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
#         return query
# #
# #
# arg = {'prompt': 'Astronaut in a jungle, cold color palette, muted colors, detailed, 8k', 'negative_prompt': 'ugly, deformed, noisy, blurry, distorted', 'width': 768, 'height': 768}
# arg = ImagePromptContainer(**arg)
# print('dict:', asdict(arg))
# print('keys:', ImagePromptContainer.get_keys())
# print('query:', arg.create_insert_query('images'))
# print('subscribe:', arg.prompt)