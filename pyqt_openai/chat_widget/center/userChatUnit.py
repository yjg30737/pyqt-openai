from __future__ import annotations

from pyqt_openai.chat_widget.center.chatUnit import ChatUnit


class UserChatUnit(ChatUnit):
    def __init__(self, parent=None):
        super().__init__(parent)
