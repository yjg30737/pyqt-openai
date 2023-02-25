# pyqt-openai
Example of using OpenAI with PyQt (Python cross-platform GUI toolkit)

This shows an example of using OpenAI with PyQt as a chatbot. 

The OpenAI model this package uses is the <a href="https://beta.openai.com/docs/models/gpt-3">text-davinci-003</a> model of GPT-3 by default.

You can select other model with the combobox on the sidebar at the right side of the window.

An internet connection is required. 

## Requirements
* PyQt5
* aiohttp - It needs to be installed for the current version of OpenAI.
* openai

## Preview
![image](https://user-images.githubusercontent.com/55078043/218295611-e50f448f-f6c5-4caf-8aa0-4927ad845935.png)

## How to play
1. git clone ~
2. from the root directory, type "cd pyqt_openai"
3. in the pyqt_openai directory, you'll see the "main.py" file. Open it and you can see lines below
```python
# this API key should be yours
# openai.api_key = '[MY_OPENAPI_API_KEY]'
```
  You should get your [MY_OPENAPI_API_KEY]. You can get it in <a href="https://platform.openai.com/account/api-keys">official site</a> of openai. Sign up and log in before you get it.

Be sure, this is a very important API key that belongs to you only, so you should remember it and keep it secure.
4. python main.py

If installation doesn't work, check the troubleshooting below.

## Troubleshooting
If you see this error while installing the openai package
```
subprocess-exited-with-error
```
you can shout a curse word and just download the package itself from <a href="https://pypi.org/project/openai/#files">pypi</a>. 

Unzip it, access the package directory, type 
```
python setup.py install
```

That will install the openai.

## TODO list
* <s>logging</s>
* feeding (with PyTorch)
* AI analysis (with wanDB)
* show the explanation of every model and terms related to AI (e.g. temperature, topp..)
* Basic style
* highlight the source
