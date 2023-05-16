# pyqt-openai
<p align="center">
  <img src="https://user-images.githubusercontent.com/55078043/229002952-9afe57de-b0b6-400f-9628-b8e0044d3f7b.png">
</p>

Example of using OpenAI with PyQt (Python cross-platform GUI toolkit)

This shows an example of using OpenAI with PyQt as a chatbot and using DALL-E or Stable Diffusion as a image generation tool.

Even though this project has become too huge to be called an 'example'.

The major advantage of this package is that you don't need to know other language aside from Python.

If you want to study openai with Python-only good old desktop software, this is for you.

The OpenAI model this package uses is the <a href="https://platform.openai.com/docs/models/gpt-3-5">gpt-3.5-turbo</a> model(which is nearly as functional as <b>ChatGPT</b>) by default. You can use gpt-4 as well.

Image generation feature(DALL-E and Stable Diffusion) available since v0.1.4.

<b>Stable Diffusion</b> used [DreamStudio API](https://dreamstudio.ai/). This is not entirely free like stable-diffusion-webgui. 

But this is very lightweight and more accessible. don't need CUDA, torch, expansive PC, anything.

This is using <b>sqlite</b> as a database.

You can select the model at the right side bar.

An internet connection is required.

## Contact
You can join pyqt-openai's <a href="https://discord.gg/cHekprskVE">Discord Server</a> to have a conversation about it or AI-related stuff 🙂

## Note
Some of the features are still being tested.

I recommend to install sqlite management software. It's not necessary to run this app (obviously), but it's good practice to manage database about conversation history with AI and to know how this works.

## Feature
* basically this is <b>desktop application version of ChatGPT</b>
  * text streaming (enable by default, you can disable it)
  * AI remembers past conversation
* conversation management
  * add & delete conversations
  * save conversations
  * rename conversation
  * everything above is saved in an SQLite database file named conv.db.
* support GPT-4 and every other models below GPT3
* support prompt generator (manageable)
* support beginning and ending part of the prompt
* you can run this in background application
  * notification will pop up when response is generated
* you can make window stack on top or control its transparency
* image generation (DALL-E, Stable Diffusion with DreamStudio API)

## Requirements
* qtpy - the package allowing you to write code that works with both PyQt and PySide
* PyQt5 >= 5.14 or PySide6
* openai
* pyperclip - to copy prompt template from prompt generator
* stability_sdk - for Stable Diffusion

## Preview
This is using GPT-3.5 turbo model by default. 

### Homepage
#### Note: Some of these previews are not the latest.
![image](https://user-images.githubusercontent.com/55078043/236657804-bf299150-961a-4f80-9820-b45401f8bb7c.png)
<b>You have to write your openai api key inside the red box.</b> see [How to play](#how-to-play)

### Overview
![image](https://user-images.githubusercontent.com/55078043/236657785-69825ff8-8cce-4759-8468-4630010edd5b.png)

### Conversation preview
#### Preview Image
![image](https://user-images.githubusercontent.com/55078043/236583716-a18b30b0-7b67-412e-b633-7daa8e41b525.png)
#### Preview Video
https://user-images.githubusercontent.com/55078043/236583883-8e9732a3-1223-4b28-85f1-f60d8b2d6ced.mp4

### Prompt Generator
#### Preview 1 (v0.1.22)
https://user-images.githubusercontent.com/55078043/236584481-b7bb5246-6bf4-4343-ba6c-a343bb11cda7.mp4
#### Preview 2 (v0.1.3)
https://user-images.githubusercontent.com/55078043/236658468-9947a417-99b3-4e44-8849-a676308a0239.mp4

So sorry to weak preview, but i have a lot of idea about this prompt generator! Just wait.

#### Image Generation
![image](https://github.com/yjg30737/pyqt-openai/assets/55078043/6fd4143f-1d32-4cfc-9182-991fad6f3757)

Again, weak preview (i just gave prompt text as "A" which is pathetic) but please consider this is very first version of sd image generation (v0.1.4) so just wait

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
* auto-complete prompt command
* DB for images (to further experiement of both DALL-E and Stable Diffusion or other image generation engine)
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
* <a href="https://openai.com/waitlist/gpt-4-api">join gpt4 waitlist</a> - i took 1 month to get access from it
* <a href="https://https://openai.com/waitlist/plugins">join chatgpt plugins waitlist</a>

