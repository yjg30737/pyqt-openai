# pyqt-openai
Example of using OpenAI with PyQt (Python cross-platform GUI toolkit)

This shows an example of using OpenAI with PyQt as a chatbot. 

The OpenAI model this package uses is the <a href="https://beta.openai.com/docs/models/gpt-3">text-davinci-003</a> model of GPT-3.

An internet connection is required. 

## Requirements
* PyQt5
* aiohttp - It needs to be installed for the current version of OpenAI.
* openai

## Preview
### Preview 1

![image](https://user-images.githubusercontent.com/55078043/216815117-a8c58337-bd0e-44a4-923f-3d58b33d61b6.png)

### Preview 2

![image](https://user-images.githubusercontent.com/55078043/216815122-3cf33222-8c7d-4ab0-af32-ddb229084605.png)

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
* make user able to select the model
* highlight the source
* feeding
* AI analysis
