from dataclasses import dataclass

@dataclass
class ImagePromptContainer:
    prompt: str = ""
    n: str = ""
    size: str = ""
    quality: str = ""
    data: str = ""
    style: str = ""
    revised_prompt: str = ""
    width: str = ""
    height: str = ""

    negative_prompt: str = ""
