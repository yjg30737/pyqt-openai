# pyqt-openai
<div align="center">
  <img src="https://user-images.githubusercontent.com/55078043/229002952-9afe57de-b0b6-400f-9628-b8e0044d3f7b.png" width="150px" height="150px"><br/><br/>
  
  [![](https://dcbadge.vercel.app/api/server/cHekprskVE)](https://discord.gg/cHekprskVE)
  
  [![](https://img.shields.io/badge/한국어-readme-green)](https://github.com/yjg30737/pyqt-openai/blob/main/README.kr.md)

</div>

PyQt/PySide(Python cross-platform GUI toolkit) OpenAI Chatbot which supports more than 8 languages (you can see the list below) 

You can use OpenAI models(GPT4, DALL-E, etc.) with PyQt as a chatbot.

The major advantage of this package is that you don't need to know other language aside from Python.

If you want to study openai with Python-only good old desktop software, this is for you.

The OpenAI model this package uses is the <a href="https://platform.openai.com/docs/models/gpt-3-5">gpt-3.5-turbo</a> model by default. You can use gpt-4 as well.

Image generation feature(DALL-E) is also available.

This is using <b>sqlite</b> as a database.

You can select the model and change each parameters of openai from the right side bar.

Also you can combine openai with llama-index feature to make gpt model answer your question based on information you had provided!

An internet connection is required.

If you have any questions or you want to make AI related software with PyQt or PySide, feel free to join Discord server of pyqt-openai.

## Table of Contents
* [Feature](#feature)
* [Supported Languages](#supported-languages)
* [Requirements](#requirements)
* [Preview and Usage](#preview-and-usage)
* [How to Install](#how-to-install)
* [Troubleshooting](#troubleshooting)
* [Contact](#contact)
* [Note](#note)
* [See Also](#see-also)

## Feature
* basically this is <b>desktop application version of ChatGPT</b> with image generation tool. 
  * text streaming (enable by default, you can disable it)
  * AI remembers past conversation
  * support copy button
  * able to stop response in the middle of text generation
* <b>conversation management</b>
  * add & delete conversations
  * save conversations - SQlite db, text files compressed file, html files compressed file (both are zip)
  * rename conversation
  * everything above is saved in an SQLite database file named conv.db.
* support controlling parameters(temperature, top_p, etc) just like openai playground
* able to see the reason why stream is finished
* support latest model such as <b>GPT-4-32k-0613</b>
* support <b>prompt generator</b> (manageable, autosaved in database) 
* support <b>slash commands</b>
* support beginning and ending part of the prompt
* you can <b>run this in background</b> application
  * notification will pop up when response is generated
* you can make window stack on top or control its transparency
* image generation (DALL-E)
* you can copy and download the image if you want. just hover the mouse cursor over the image.
* you can <b>fine-tune</b> openai with llama-index.
* support text-based file uploading

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

If you have any additional languages you would like to add, please feel free to make a request by mail, issue, discord, etc at any time.

## Requirements
* qtpy - the package allowing you to write code that works with both PyQt and PySide
* PyQt5 >= 5.14 or PySide6
* openai
* aiohttp - for openai dependency 
* pyperclip - to copy prompt text from prompt generator
* jinja2 - for saving the conversation with html file
* llama-index - to fine-tune

## Preview and Usage
#### Note: A lot of previews below are not from latest version. It is slightly different with current GUI. So if you want to really know what this looks like, you can just see it for yourself :)

### Overview
#### Windows
![image](https://github.com/yjg30737/pyqt-openai/assets/55078043/51667298-2c3f-4846-a8c9-ec56331b8361)
<b>You have to write your openai api key inside the red box.</b> see [How to install](#how-to-install)

You can change screen between text chatbot and image generating tool screen.

![image](https://github.com/yjg30737/pyqt-openai/assets/55078043/78260aaf-2626-4267-9309-07655cab2061)

#### Linux (Ubuntu)
![image](https://github.com/yjg30737/pyqt-openai/assets/55078043/4005c085-53f4-406f-adb0-4fb4d87d88ba)

#### MacOS
![image](https://github.com/yjg30737/pyqt-openai/assets/55078043/4fec8f14-3768-49e8-9ad6-a4fbf240e643)

Thanks to Werranton, who gave me the pyqt-openai window example image from macOS :)

(He has changed the pyqt-openai's overall theme personally)

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

## TODO list
* tokenizer

## See Also
* <a href="https://learn.microsoft.com/en-us/azure/cognitive-services/openai/overview">Azure OpenAI service</a>
* <a href="https://openai.com/waitlist/gpt-4-api">join gpt4 waitlist</a> - i took 1 month to get access from it
* <a href="https://https://openai.com/waitlist/plugins">join chatgpt plugins waitlist</a>

