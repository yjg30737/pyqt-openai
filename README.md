# pyqt-openai
<div align="center">
  <img src="https://user-images.githubusercontent.com/55078043/229002952-9afe57de-b0b6-400f-9628-b8e0044d3f7b.png" width="150px" height="150px"><br/><br/>
  
  [![](https://dcbadge.vercel.app/api/server/cHekprskVE)](https://discord.gg/cHekprskVE)
  
  [![](https://img.shields.io/badge/한국어-readme-green)](https://github.com/yjg30737/pyqt-openai/blob/main/README.kr.md)

</div>

PyQt/PySide(Python cross-platform GUI toolkit) OpenAI Chatbot which supports more than 8 languages (you can see the list below)

<b>This supports Windows, MacOS, Linux.</b>

You can use OpenAI models(GPT4o, GPT4o-mini, DALL-E, etc.), Replicate image generation models with PyQt.

The major advantage of this package is that you don't need to know other language aside from Python.

If you want to study openai with Python-only good old desktop software, this is for you.

This is using <b>sqlite</b> as a database.

You can select the model and change each parameters of openai from the right side bar.

Also you can combine openai with llama-index feature to make GPT model answer your question based on information you had provided!

If you have any questions or you want to make AI related software with PyQt or PySide, feel free to join Discord server of pyqt-openai.

And if you would like to support this project, you can click the button below to make a donation. Your contribution will greatly assist various projects, including this one!

<a href="https://www.buymeacoffee.com/yjg30737" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
<a href="https://paypal.me/yjg30737">
  <img src="https://github.com/yjg30737/yjg30737/assets/55078043/3366b496-3e1e-491c-841e-19871da55c40" alt="Donate with PayPal" style="height: 60px; width: 170px" />
</a>

## Table of Contents
* [Feature](#feature)
* [Supported Languages](#supported-languages)
* [Requirements](#requirements)
* [Preview and Usage](#preview-and-usage)
  * [Overview](#overview)
  * [Conversation](#conversation)
  * [Prompt Generator](#prompt-generator)
  * [Use GPT Vision](#use-gpt-vision)
  * [Image Generation](#image-generation)
* [How to Install](#how-to-install)
* [Troubleshooting](#troubleshooting)
* [Contact](#contact)
* [Note](#note)
* [LICENSE](#license)
* [Disclaimer](#disclaimer)

## Feature
* Basically this is <b>desktop application version of ChatGPT</b> with image generation tool. 
  * Text streaming (enable by default, you can disable it)
  * AI remembers past conversation
  * Support copy button
  * Able to stop response in the middle of text generation
* <b>Conversation(=Thread) management</b>
  * Add & delete conversations
  * Export conversations - JSON file, text files compressed file, html files compressed file (both are zip)
  * Import conversations from pyqt-openai, GPT
  * Rename conversation
  * "Favorite" feature
  * everything above is saved in an SQLite database file named conv.db. (File's name can be changed by yourself)
* Support controlling parameters(temperature, top_p, etc) just like openai playground
* Able to see the reason why stream is finished
* Support token count (only for non-streaming response)
* Support <b>prompt generator</b> (manageable, autosaved in database) 
* Support <b>slash commands</b>
* Support beginning and ending part of the prompt
* You can <b>run this in background</b> application
  * notification will pop up when response is generated
* You can make window stack on top or control its transparency
* Image generation (DALL-E3 from openai, a bunch of image models in Replicate)
  * Support saving generated image to local
  * Support continue generation
  * Notification when task completes
* You can copy and download the image directly as well. just hover the mouse cursor over the image.
* You can <b>fine-tune</b> openai with llama-index.
* Support text(*.txt), image(*.png, *.jpg) file uploading
* Support searching title and content in the conversation
* Support "find text" feature (match word, case-sensitive, regex, etc.)
* Support customizing feature (homepage, user and AI profile image)
* Full screen feature

## Supported Languages
* English
* Spanish
* Chinese
* Russian
* Korean
* French
* German
* Italian
* Hindi
* Arabic
* Japanese

If you have any additional languages you would like to add, please feel free to make a request by mail, issue, discord, etc at any time.

## Requirements
* qtpy - the package allowing you to write code that works with both PyQt5, PyQt6, PySide6
* PyQt5 >= 5.14 or PyQt6 (or PySide6 if you want)
* openai
* aiohttp - for openai dependency 
* pyperclip - to copy prompt text from prompt generator
* jinja2 - for saving the conversation with html file
* llama-index - to fine-tune gpt with llamaindex
* requests - for getting response from web
* langchain - for connecting llama-index with gpt
* pillow - for preventing ModuleNotFoundError from llama-index
* replicate - for supporting Replicate

You can install these requirements with only one line command "pip install -r requirements.txt". Just see "How to Install" section below.

## Preview and Usage
#### Note: A lot of previews below are not from latest version. It is slightly different with current GUI. So if you want to really know what this looks like, see it by yourself :) But i will definitely change any image(s) which should be changed.

### Overview
![image](https://github.com/yjg30737/pyqt-openai/assets/55078043/00aab779-37bd-45e8-b21c-9f4ed3e473e8)
<b>You have to write your openai api key inside the red box.</b> see [How to install](#how-to-install)

You can change screen between text chatbot and image generating tool screen.

![image](https://github.com/yjg30737/pyqt-openai/assets/55078043/78260aaf-2626-4267-9309-07655cab2061)

### Using LlamaIndex
![image](https://github.com/yjg30737/pyqt-openai/assets/55078043/e161b551-91dc-4c4d-8a33-28179d72fb64)

If you want to use this with your personal chatbot based on data you've given, then you can check the llamaindex checkbox and go to the tab, select the directory which includes .txt files containing the data.

### Conversation
#### Preview 1
I recorded this preview long time ago so GUI is different from the current version, but way of operating it is pretty much the same.

https://user-images.githubusercontent.com/55078043/236583883-8e9732a3-1223-4b28-85f1-f60d8b2d6ced.mp4
#### Preview 2 (using prompt feature)

https://github.com/yjg30737/pyqt-openai/assets/55078043/841a1505-f1cc-452e-99ab-0a9c661e6ead

#### Conversation Save Feature
![image](https://github.com/yjg30737/pyqt-openai/assets/55078043/908ed185-06a6-4f7a-9626-92141ba24e1a)

You can save checked conversation units to SQlite db file or compressed file (zip) which contains each conversation as text/html file.

### Prompt Generator
#### How to Generate
This application has two types of prompts. One is <b>"Properties"</b> and the other one is <b>"Template"</b>. Properties are sets of attributes that are useful for forming the premises of a question. Templates are sentences that correspond to a single command. You can input a command to generate a sentence. This can be used as a question in itself.

Both types can be managed as groups. After cloning or installing, if you run the program immediately, you will be able to see the default group and the items included in the group, just like the screen.

For properties, there is a group named "Default" that provides a set of attributes referenced <a href="https://gptforwork.com/tools/prompt-generator">here</a>.

For templates, there are the "awesome_chatGPT_prompt" and "alex_brogan" (example prompt for Alex Brogan) groups provided. Any custom template items created prior to version 0.1.6 will be moved to the Miscellaneous group.

![prompt_list_image](https://github.com/yjg30737/pyqt-openai/assets/55078043/ce40139a-c03f-42ef-abd8-4a610d762394)

With using these prompts you can pretty much get any response you want.

You can use the additional prompt feature by "prompt menu" right next to "prompt input" field.

![image](https://github.com/yjg30737/pyqt-openai/assets/55078043/c9ca84af-0088-4435-854d-7feca9e2e663)

Since v0.1.6, awesome-chatgpt-prompt is included as template group by default.

#### Prompt Generator Preview
Generating the prompt (Properties)

https://github.com/yjg30737/pyqt-openai/assets/55078043/e168c0e6-41b4-4ad5-95e6-3c42c9c23602

I recorded using the Windows recording feature. As a result, the "Add Dialog" that prompts for entering a group name does not appear in the preview. When you add a group, you will see the Add Dialog as expected.

Then, how to generate template type prompt? Click any item in the group, it will be shown in the preview.

You can copy that generated text with clicking "copy" button and include it to your prompt input.

If you add a property group or template group with items, you can use it as a command by typing its name to the prompt input.

<b>Use prompt as a command</b>

https://github.com/yjg30737/pyqt-openai/assets/55078043/df0d3923-1fbe-4dda-af6f-4e4d1e572553

In this preview, i pressed the keyboard shortcut of each actions(show beginning, show ending, support prompt command) to use it rather than clicking them with mouse.

I made the command suggestion GUI resemble the Discord command autocomplete popup, with which a lot of people have become accustomed.

### Use GPT Vision
#### How to Use it
1. Select "gpt-4-vision-preview"

![image](https://github.com/yjg30737/pyqt-openai/assets/55078043/1d1ce632-3078-4cb7-863e-fc447b146f8a)

2. Select image files from local with clicking "Upload Files"

![image](https://github.com/yjg30737/pyqt-openai/assets/55078043/aef216d5-9b7c-4f22-9bc3-88c90f4d9e73)

3. Ask something about images

![image](https://github.com/yjg30737/pyqt-openai/assets/55078043/3ef4f091-9f5f-46b3-a160-be35215977c7)


### Image Generation

![image](https://github.com/yjg30737/pyqt-openai/assets/55078043/7f240ab3-f4d7-4d8b-b1c8-cb269f25e05b)

## How to Install
1. git clone ~
2. cd pyqt-openai
3. pip install -r requirements.txt --upgrade
4. cd pyqt_openai
5. You should put your api key in the line edit. You can get it in <a href="https://platform.openai.com/account/api-keys">official site</a> of openai. Sign up and log in before you get it.

Be sure, this is a very important API key that belongs to you only, so you should remember it and keep it secure.

6. python main.py

If installation doesn't work, you can contact me with bring up new issue in issue tab or check the troubleshooting below even it is only about very specific error.

### Note
If you use Linux and see this error:
```
qt.qpa.plugin: could not load the qt platform plugin "xcb" in "" even though it was found

this application failed to start because no qt platform plugin could be initialized, reinstalling the application may fix this problem
```

run this command:
```
sudo apt-get install libxcb-xinerama0
```

## Troubleshooting
### How to fix qt.qpa.plugin: Could not find the Qt platform plugin "windows" in "" error

Please check that the path does not contain any other invalid languages.

### subprocess-exited-with-error
If you see this error while installing the openai package
```
subprocess-exited-with-error
```
download the package itself from <a href="https://pypi.org/project/openai/#files">pypi</a>. 

Unzip it, access the package directory, type 
```
python setup.py install
```

That will install the openai.

Note: I don't know this can happen in newer version of openai as well, so tell me if you know about something

### qtpy.QtBindingsNotFoundError: No Qt bindings could be found
first, do this:
```
pip uninstall -r requirements.txt
```
second, do this:
```
pip install -r requirements.txt --upgrade
```
then it will work :)

## Contact
You can join pyqt-openai's <a href="https://discord.gg/cHekprskVE">Discord Server</a> to have a conversation about it or AI-related stuff 🙂

## Note
I recommend to install sqlite management software. It's not necessary to run this app (obviously), but it's good practice to manage database about conversation history with AI and to know how this works.

## LICENSE
```
MIT License

Copyright (c) 2023-2024 Jung Gyu Yoon

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Disclaimer

Please do not distribute this commercially without my permission, by claiming it as your own creation.
