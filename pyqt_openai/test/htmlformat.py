# save with json
# # make a new conversation unit
# def makeNewConvJson():
#     # Open the JSON file and load its contents into a Python dictionary
#     with open('conv_history.json', 'r') as f:
#         data = json.load(f)
#
#     with open('conv_history.json', 'w') as f:
#         lst = data['each_conv_lst']
#         max_id = max(lst, key=lambda x: x["id"])["id"]+1
#         data['each_conv_lst'].append({ 'id': max_id, 'title': 'New Chat', 'conv_data': [] })
#         f.write(json.dumps(data) + '\n')
#
# # update conversation unit
# def updateConvJson(id, title=None, conv_unit=None):
#     # Open the JSON file and load its contents into a Python dictionary
#     with open('conv_history.json', 'r') as f:
#         data = json.load(f)
#
#     with open('conv_history.json', 'w') as f:
#         lst = data['each_conv_lst']
#         obj = list(filter(lambda x: x["id"] == 1, lst))[0]
#         if title:
#             obj['title'] = title
#         if conv_unit:
#             obj['conv_data'].append(conv_unit)
#         json.dump(data, f)
#
# makeNewConvJson()
# updateConvJson(1, 'New Chat')
# updateConvJson(1, conv_unit=conv)

# hyperlink
# from pygments import highlight
# from pygments.lexers import PythonLexer
# from pygments.formatters import HtmlFormatter
#
# code = """
# def hello_world():
#     print("Hello, world!")
# """
#
# lexer = PythonLexer()
# formatter = HtmlFormatter(style='colorful')
#
# css_styles = formatter.get_style_defs('.highlight')
#
# html_code = f"""
# <html>
#     <head>
#         <style>
#             {css_styles}
#         </style>
#     </head>
#     <body>
#         {highlight(code, lexer, formatter)}
#     </body>
# </html>
# """
#
# print(html_code)
#