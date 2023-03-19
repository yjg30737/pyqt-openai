# pyqt-openai
Example of using OpenAI with PyQt (Python cross-platform GUI toolkit)

This shows an example of using OpenAI with PyQt as a chatbot. 

The OpenAI model this package uses is the <a href="https://platform.openai.com/docs/models/gpt-3-5">gpt-3.5-turbo</a> model(which is nearly as functional as <b>ChatGPT</b>) by default.

Image generation feature available since v0.0.16. You can see the detail in <a href="https://platform.openai.com/docs/guides/images/introduction">official OpenAI</a> site. Currently this feature is very basic now.

You can select other model with the combobox on the sidebar at the right side of the window.

An internet connection is required.

## Requirements
* PyQt5
* aiohttp - It needs to be installed for the current version of OpenAI.
* openai

## Preview
This is using GPT-3.5 turbo model.

![image](https://user-images.githubusercontent.com/55078043/226176448-57ea6ef1-3672-44ff-a27b-4b42e2c5e357.png)

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
* <s>logging</s>
* fine-tuning (with JSONL) - currently working
* Add the fine-tuned model in combo box
* Sync the fine-tunes, analysis (with wanDB)
* show the explanation of every model and terms related to AI (e.g. temperature, topp..)
* <s>Basic style</s>
* highlight the source
* Add the basic example sources of making deep learning model with PyTorch
