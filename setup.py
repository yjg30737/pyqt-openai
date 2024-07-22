from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

setup(
    name='pyqt-openai',
    version='0.7.7',
    author='Jung Gyu Yoon',
    author_email='yjg30737@gmail.com',
    license='MIT',
    packages=find_packages(),
    package_data={'pyqt_openai.ico': ['close.svg', 'case.svg', 'copy.svg', 'copy_light.svg', 'openai.svg', 'discord.svg', 'github.svg', 'help.svg', 'customize.svg', 'history.svg',
                                      'user.svg', 'sidebar.svg', 'prompt.svg', 'save.svg', 'save_light.svg', 'stackontop.svg',
                                      'add.svg', 'delete.svg', 'setting.svg', 'search.svg',
                                      'next.svg', 'prev.svg', 'regex.svg', 'word.svg',
                                      'vertical_three_dots.svg',
                                      'add_light.svg', 'delete_light.svg',
                                      'import.svg',
                                      'favorite_yes.svg',
                                      'favorite_no.svg',
                                      'fullscreen.svg']},
    description='PyQt/PySide(Python cross-platform GUI toolkit) OpenAI Chatbot',
    url='https://github.com/yjg30737/pyqt-openai.git',
    long_description_content_type='text/markdown',
    long_description=long_description,
    install_requires=[
        'PyQt5 >= 5.14'
        ,'PyQt6'
        ,'qtpy'
        ,'aiohttp'
        ,'openai'
        ,'pyperclip'
        ,'jinja2'
        ,'llama-index'
        ,'requests'
        ,'langchain'
        ,'pillow'
        ,'replicate'
    ]
)
