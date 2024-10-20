# VividNode(pyqt-openai)
<div align="center">
  <img src="https://github.com/user-attachments/assets/ab169535-8af0-40c7-848d-59a7e5e4b304"/>

  <b>A cross-platform AI desktop chatbot application for LLM such as GPT, Claude, Gemini, Llama chatbot interaction and image generation, offering customizable features, local chat history, and enhanced performance—no browser required!<br><br>
  Basically for free, powered by GPT4Free(since v1.3.0).</b>

<hr>

  [![](https://dcbadge.vercel.app/api/server/cHekprskVE)](https://discord.gg/cHekprskVE)
  
  [![PyPI - Version](https://img.shields.io/pypi/v/pyqt-openai?logo=pypi&logoColor=white)](https://pypi.org/project/pyqt-openai/) [![Downloads](https://static.pepy.tech/badge/pyqt-openai)](https://pepy.tech/project/pyqt-openai) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyqt-openai?logo=python&logoColor=gold)](https://pypi.org/project/pyqt-openai/) ![commit](https://img.shields.io/github/commit-activity/w/yjg30737/pyqt-openai)
</div>

![image](https://github.com/user-attachments/assets/9231c79f-e4db-4c61-9b21-740e4fb609ec)

<hr>

## Help Needed 🆘

**Managing this project alone has become quite challenging so i'm reaching out for support.**
If you have experience with coding, documentation, design, or even providing constructive feedback, I would greatly appreciate your involvement. Your contribution could make a significant difference.

Your contribution, even just a fix a simple typo in readme or simple refactoring can be very helpful. Of course there are a lot of official TODOs i need helping hand as well. So [see here](https://github.com/yjg30737/pyqt-openai/blob/main/CONTRIBUTING.md) if you are willing to contribute.

You can contact me 24/7 by sending me an email to **yjg30737@gmail.com** or join [**Discord server**](https://discord.gg/cHekprskVE) to talk in real time.

## Test Scenario
This is the [default test scenario page](https://github.com/yjg30737/pyqt-openai/wiki/Test-Scenario). If you want to test it out and be sure nothing is wrong, try it :)

## Contributors
* **Me (WizMiner)** 😊
  * Creator of VividNode 🐐

## What is VividNode? 🤔

**VividNode** is a cross-platform desktop application that allows you to interact directly with LLM(GPT, Claude, Gemini, Llama) chatbots and generate images without needing a browser. Built with PySide6, VividNode (formerly known as pyqt-openai) supports Windows, Mac, and Linux, and securely stores your chat history locally in a database.

### Key Features:
- **Chat Interface**: Enjoy a seamless chat experience with a customizable interface, fast thread and message search, and advanced conversation settings. You can also import/export chat histories and use prompt management tools for efficient prompt engineering.
- **Image Generation**: Generate images using OpenAI’s DALL-E 3 or models from Replicate or GPT4Free, directly within your chat sessions. The app supports multi-image generation, automatic saving, and integrated image management.
- **Focus and Accessibility Modes**: Utilize Focus Mode, “Always on Top” Mode, transparency adjustments, and background notifications to keep the chat accessible and responsive without overwhelming system resources.
- **Customization and Shortcuts**: VividNode offers extensive customization options, including language settings, memory management, and a comprehensive list of keyboard shortcuts for faster operations.

With VividNode, you can experience a more powerful and resource-efficient alternative to browser-based GPT interfaces, making it easier to manage both text and image-based interactions.

<hr>

## Sidenote 🗒️
Although this is named 'pyqt-openai', the model does not use only OpenAI-related models, and the GUI is created using PySide6, not PyQt. 'pyqt-openai' was the package name decided initially, and we are still using it as changing the package name now would likely result in a huge disaster.

## How to Install
### Standard Way
1. git clone ~
2. cd pyqt-openai
3. pip install -r requirements.txt --upgrade
4. cd pyqt_openai
5. python main.py
### With Makefile
1. make venv
2. make run

### Wanna download this without doing stuffs like above? You can download installer or zip file <a href="https://github.com/yjg30737/pyqt-openai/releases">here.</a>

## How to Use 🧐
**<a href="https://medium.com/@yjg30737/what-is-vividnode-how-to-use-it-4d8a9269a3c0">QuickStart</a>**

## Troubleshooting
### Common Issues
#### Issues Related to PyAudio
- This issue is often due to the absence of PortAudio. Make sure to install PortAudio before you install PyAudio.
#### Issues Related to PySide6 During Installation 
- As of October 14, 2024, PySide6 supports Python versions above 3.9 and below 3.13. If support for Python 3.13 is added in the future, you can remove this note.
#### Handling Error Messages Related to Software Updates (Windows)
- If you encounter the following error message when trying to update VividNode via the auto-update feature: **PermissionError: [Errno 13] Permission denied**, To resolve this issue, run VividNode as an administrator.
#### Incomplete or Inaccurate Translations
- If you come across incomplete or unnatural translations, please update the **pyqt_openai/lang/translations.json** file.

If the solutions listed here don’t resolve your issue, please report it by [opening an issue](https://github.com/yjg30737/pyqt-openai/issues).

## Disclaimer
Please do not distribute this commercially without my permission, by claiming it as your own creation.
