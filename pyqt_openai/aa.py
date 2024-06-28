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

arg = {'prompt': 'Astronaut in a jungle, cold color palette, muted colors, detailed, 8k', 'negative_prompt': 'ugly, deformed, noisy, blurry, distorted', 'width': 768, 'height': 768}
arg = ImagePromptContainer(**arg)
print(arg.__dict__)