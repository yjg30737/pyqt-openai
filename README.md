# pyqt-openai
<div align="center">
  <img src="https://user-images.githubusercontent.com/55078043/229002952-9afe57de-b0b6-400f-9628-b8e0044d3f7b.png" width="240px" height="240px"><br/><br/>
<h3>Multi-purpose Text & Image Generation Desktop Chatbot (supporting various models including GPT).</h3>
  
Join our <a href="https://discord.gg/cHekprskVE">Discord Channel</a> for questions or discussions! 
Also we need contributor. Feel free to join the server !
</div>

![image](https://github.com/user-attachments/assets/f5281b7e-1414-4335-adb4-a92928cd609e)

<hr/>

This application is developed using PyQt/PySide.

It supports Windows, macOS, and Linux.

It uses SQLite as a database.

You can use OpenAI models (GPT-4, GPT-4 Mini, DALL-E, etc.) and Replicate image generation models with PyQt.

The major advantage of this package is that you don't need to know any language aside from Python.

If you want to study OpenAI with Python-only in a good old desktop software environment, this is for you.

You can select the model and adjust each parameter of OpenAI from the right sidebar.

Additionally, you can combine OpenAI with the Llama-Index feature to make the GPT model answer your questions based on the information you have provided!

If you have any questions or if you want to develop AI-related software with PyQt or PySide, feel free to join the Discord server!

If you would like to support this project, please click the button below to make a donation. Your contribution will greatly assist various projects, including this one!

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
* [How to Install](#how-to-install)
* [Troubleshooting](#troubleshooting)
* [Note](#note)
* [Disclaimer](#disclaimer)

## Feature
* Basically this is <b>desktop application version of ChatGPT</b> with image generation tool. 
* <b>Conversation(=Thread) management</b>
  * Add & delete conversations
  * Export & Import conversations (including import from ChatGPT)
  * "Favorite" feature
  * Support JSON mode
  * Everything above is saved in an SQLite database file named conv.db. (File's name can be changed by yourself)
* Support text(*.txt), image(*.png, *.jpg) file uploading
* Support controlling parameters(temperature, top_p, etc)
* You can see the reason why stream is finished.
* Support token count (only for non-streaming response)
* Support <b>prompt generator</b> (manageable, autosaved in database)
  * Support import & export prompt group as JSON
* Full screen feature
* Support <b>slash commands</b>
* Support beginning and ending part of the prompt
* You can <b>run this in background</b>
  * Notification will pop up when response is generated
* You can make window stack on top or control its transparency
* Image generation (DALL-E3 from openai, a bunch of image models in Replicate)
  * Support saving generated image to local
  * Support continue generation
  * Notification when task completes
* Support llamaindex
* Support customizing feature (homepage, user and AI profile image, font settings)
* Support light/dark theme based on your system settings (Above Qt6 only)

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
* Bengali
* Urdu
* Indonesian
* Portuguese

If you have any additional languages you would like to add, please feel free to make a request by mail, issue, discord, etc at any time.

Also you can submit a pull request if you want to update any words naturally by modify "translations.json" in "lang" directory.

## Requirements
* Python >= 3.9 
* qtpy - the package allowing you to write code that works with both PyQt5, PyQt6, PySide6
* PyQt5 >= 5.14 or PyQt6 (or PySide6 if you want)
  * I personally recommend Qt6. 
* openai
* aiohttp - for openai dependency 
* pyperclip - to copy prompt text from prompt generator
* jinja2 - for saving the conversation with html file
* llama-index - to fine-tune gpt with llamaindex
* requests - for getting response from web
* langchain - for connecting llama-index with gpt
* pillow - for preventing ModuleNotFoundError from llama-index
* replicate - for supporting Replicate
* toml - For reading pyproject.toml below 3.11

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

## How to Install
1. git clone ~
2. cd pyqt-openai
3. pip install -r requirements.txt --upgrade
4. cd pyqt_openai
5. You should put your api key in the line edit. You can get it in <a href="https://platform.openai.com/account/api-keys">official site</a> of openai. Sign up and log in before you get it.
6. python main.py

## Install with pyproject.toml 
1. git clone ~
2. Run shell as Administrator
3. cd pyqt-openai
4. pip install .
5. pyqt-openai

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

### qtpy.QtBindingsNotFoundError: No Qt bindings could be found
First, do this:
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

## Disclaimer

Please do not distribute this commercially without my permission, by claiming it as your own creation.
