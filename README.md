# pyqt-openai
<p align="center">
  <img src="https://user-images.githubusercontent.com/55078043/229002952-9afe57de-b0b6-400f-9628-b8e0044d3f7b.png">
</p>
Example of using OpenAI with PyQt (Python cross-platform GUI toolkit)

This shows an example of using OpenAI with PyQt as a chatbot.

The major advantage of this package is that you don't need to know other language aside from Python.

If you want to study openai with Python-only good old desktop software, this is for you.

The OpenAI model this package uses is the <a href="https://platform.openai.com/docs/models/gpt-3-5">gpt-3.5-turbo</a> model(which is nearly as functional as <b>ChatGPT</b>) by default.

Image generation feature available since v0.0.16. You can see the detail in <a href="https://platform.openai.com/docs/guides/images/introduction">official OpenAI</a> site. Currently this feature is very basic now.

This is using <b>sqlite</b> as a database.

You can select other model with the combobox on the sidebar at the right side of the window.

An internet connection is required.

## Contact
You can join pyqt-openai's <a href="https://discord.gg/cHekprskVE">Discord Server</a> to have a conversation about it or AI-related stuff 🙂

## Note
Some of the features are still being tested.

## Feature
* basically this is desktop application version of ChatGPT
- text streaming (enable by default, you can disable it)
- AI remembers past conversation
* you can save the conversation history with sqlite database
* support image generation with DALL-E
* you can test any models, including gpt3.5
* you can run this in background application
* you can make window stack on top or control its transparency 

## Requirements
* qtpy - the package allowing you to write code that works with both PyQt and PySide
* PyQt5 >= 5.14 or PySide6
* openai

## Preview
This is using GPT-3.5 turbo model by default.

### Homepage
![image](https://user-images.githubusercontent.com/55078043/230718379-d8f85397-74e9-483a-8686-5ce59ead70a3.png)
<b>You have to write your openai api key inside the red box.</b> see [How to play](#how-to-play)

### Conversation preview
#### Image
![image](https://user-images.githubusercontent.com/55078043/230718925-bc36693b-1ad6-472f-ab08-63517e3a433f.png)
#### Video
https://user-images.githubusercontent.com/55078043/230719180-3e665a05-959c-4b49-b693-7046a538630e.mp4

## How to play
1. git clone ~
2. from the root directory, type "cd pyqt_openai"
3. You should put your api key in the line edit. You can get it in <a href="https://platform.openai.com/account/api-keys">official site</a> of openai. Sign up and log in before you get it. <b>By the way, this is free trial, not permanently free. See <a href="https://platform.openai.com/account/billing/overview">this</a> after you have logged in.</b>

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
* redesign the right side bar
* prompt generator
* support MidJourney or Stable Diffusion or both
* show the explanation of every model and terms related to AI (e.g. temperature, topp..)
* save conversation history with other format (xlsx, csv, etc.)
* tokenizer
* highlight the source (optional, eventually)
* support multiple language
* use SQLAlchemy (maybe not)
* show reason when the chat input is disabled for some reasons
* add the basic example sources of making deep learning model with PyTorch (eventually)

## See Also
* <a href="https://learn.microsoft.com/en-us/azure/cognitive-services/openai/overview">Azure OpenAI service</a>
* <a href="https://openai.com/waitlist/gpt-4-api">join gpt4 waitlist</a>
* <a href="https://https://openai.com/waitlist/plugins">join chatgpt plugins waitlist</a>

