# VividNode(pyqt-openai)

![VividNode Logo](https://github.com/user-attachments/assets/ab169535-8af0-40c7-848d-59a7e5e4b304)

**A cross-platform AI desktop chatbot application for LLM such as GPT, Claude, Gemini, Llama chatbot interaction and image generation, offering customizable features, local chat history, and enhanced performance—no browser required!

Basically for free, powered by GPT4Free and LiteLLM.**

---

[![Discord Server](https://dcbadge.vercel.app/api/server/cHekprskVE)](https://discord.gg/cHekprskVE)

  [![PyPI - Version](https://img.shields.io/pypi/v/pyqt-openai?logo=pypi&logoColor=white)](https://pypi.org/project/pyqt-openai/) [![Downloads](https://static.pepy.tech/badge/pyqt-openai)](https://pepy.tech/project/pyqt-openai) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyqt-openai?logo=python&logoColor=gold)](https://pypi.org/project/pyqt-openai/) ![commit](https://img.shields.io/github/commit-activity/w/yjg30737/pyqt-openai)
</div>

![image](https://github.com/user-attachments/assets/9f5f2ca0-b191-4655-b671-ae0834e1a0b1)

---

## What is VividNode? 🤔

**VividNode** is a cross-platform desktop application that allows you to interact directly with LLM(GPT, Claude, Gemini, Llama) chatbots and generate images without needing a browser. Built with PySide6, VividNode (formerly known as pyqt-openai) supports Windows, Mac, and Linux, and securely stores your chat history locally in a database.

### Key Features

- **Chat Interface**: Enjoy a seamless chat experience with a customizable interface, fast thread and message search, and advanced conversation settings. You can also import/export chat histories and use prompt management tools for efficient prompt engineering.
- **Image Generation**: Generate images using OpenAI's DALL-E 3 or models from Replicate or GPT4Free, directly within your chat sessions. The app supports endless image generation, randomly generated prompt, automatic saving, and integrated image management.
- **Focus and Accessibility Modes**: Utilize Focus Mode, "Always on Top" Mode, transparency adjustments, and background notifications to keep the chat accessible and responsive without overwhelming system resources.
- **Customization and Shortcuts**: VividNode offers extensive customization options, including language settings, memory management, and a comprehensive list of keyboard shortcuts for faster operations.
- **Support for interactive chatting (STT & TTS)**: It features a recording function using OpenAI's STT capabilities and allows responses to be heard in various voices through OpenAI Whisper or the TTS functionality of the Edge browser (using edge-tts, which is free).

With VividNode, you can experience a more powerful and resource-efficient alternative to browser-based GPT interfaces, making it easier to manage both text and image-based interactions.

---

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

### Wanna download this without doing stuffs like above? You can download installer or zip file [here](https://github.com/yjg30737/pyqt-openai/releases)

## How to Use 🧐

**[QuickStart](https://medium.com/@yjg30737/what-is-vividnode-how-to-use-it-4d8a9269a3c0)**

## Test Scenario

This is the [default test scenario page](https://github.com/yjg30737/pyqt-openai/wiki/Test-Scenario). If you want to test it out and be sure nothing is wrong, try it :)

## Troubleshooting

### Common Issues

#### Issues Related to PyAudio

- This issue is often due to the absence of PortAudio. Make sure to install PortAudio before you install PyAudio.

#### Issues Related to PySide6 During Installation

- As of October 14, 2024, PySide6 supports Python versions above 3.9 and below 3.13. If support for Python 3.13 is added in the future, you can remove this note.

#### Handling Error Messages Related to Software Updates (Windows)

- If you encounter the following error message when trying to update VividNode via the auto-update feature: **PermissionError: [Errno 13] Permission denied**, To resolve this issue, run VividNode as an administrator.
- Also, if VividNode keeps asking "Wanna update?" even though you've updated it already, just install this again and everything will be fine.

#### Runtime error

![image](https://github.com/user-attachments/assets/f53b44bb-1572-48ce-a9a0-a5da2b338d09)

- If you see the error above, run the application again. It is likely to be shown in old version(below v1.5.0) so update to the latest version.

#### Incomplete or Inaccurate Translations

- If you come across incomplete or unnatural translations, please update the **pyqt_openai/lang/translations.json** file.

If the solutions listed here don't resolve your issue, please report it by [opening an issue](https://github.com/yjg30737/pyqt-openai/issues).

## Help Needed 🆘

**Managing this project alone has become quite challenging so i'm reaching out for support.**
If you have experience with coding, documentation, design, or even providing constructive feedback, I would greatly appreciate your involvement. Your contribution could make a significant difference.

Your contribution, even just a fix a simple typo in readme or simple refactoring can be very helpful. Of course there are a lot of official TODOs i need helping hand as well. So [see here](https://github.com/yjg30737/pyqt-openai/blob/main/CONTRIBUTING.md) if you are willing to contribute.

You can contact me 24/7 by sending me an email to **<yjg30737@gmail.com>** or join [**Discord server**](https://discord.gg/cHekprskVE) to talk in real time

## Contributors

- **Me (WizMiner)** 😊
  - Creator of VividNode 🐐

## Disclaimer

Please do not distribute this commercially without my permission, by claiming it as your own creation.
