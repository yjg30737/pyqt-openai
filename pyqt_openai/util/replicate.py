from __future__ import annotations

import base64
import os

import replicate
import requests

from pyqt_openai.models import ImagePromptContainer


def download_image_as_base64(url: str):
    response = requests.get(url)
    response.raise_for_status()  # Check if the URL is correct and raise an exception if there is a problem
    image_data = response.content
    base64_encoded = base64.b64decode(base64.b64encode(image_data).decode("utf-8"))
    return base64_encoded


class ReplicateWrapper:
    def __init__(self, api_key):
        self.__api_key = api_key

    @property
    def api_key(self):
        return self.__api_key

    @api_key.setter
    def api_key(self, value):
        self.__api_key = value
        os.environ["REPLICATE_API_KEY"] = self.__api_key

    def is_available(self):
        return True if self.__api_key is not None else False

    def get_image_response(self, model, input_args):
        try:
            model = (
                "lucataco/playground-v2.5-1024px-aesthetic:419269784d9e00c56e5b09747cfc059a421e0c044d5472109e129b746508c365"
                if model is None
                else model
            )

            input_args = (
                {
                    "width": 768,
                    "height": 768,
                    "prompt": "Astronaut in a jungle, cold color palette, muted colors, detailed, 8k",
                    "negative_prompt": "ugly, deformed, noisy, blurry, distorted",
                }
                if input_args is None
                else input_args
            )

            input_args["num_outputs"] = (
                1 if "num_outputs" not in input_args else input_args["num_outputs"]
            )
            input_args["guidance_scale"] = (
                3
                if "guidance_scale" not in input_args
                else input_args["guidance_scale"]
            )
            input_args["apply_watermark"] = (
                True
                if "apply_watermark" not in input_args
                else input_args["apply_watermark"]
            )
            input_args["prompt_strength"] = (
                0.8
                if "prompt_strength" not in input_args
                else input_args["prompt_strength"]
            )
            input_args["num_inference_steps"] = (
                50
                if "num_inference_steps" not in input_args
                else input_args["num_inference_steps"]
            )
            input_args["refine"] = (
                "expert_ensemble_refiner"
                if "refine" not in input_args
                else input_args["refine"]
            )

            output = replicate.run(model, input=input_args)

            if output is not None and len(output) > 0:
                arg = {
                    "model": model,
                    "prompt": input_args["prompt"],
                    "size": f"{input_args['width']}x{input_args['height']}",
                    "quality": "high",
                    "data": download_image_as_base64(output[0]),
                    "style": "",
                    "revised_prompt": "",
                    "width": input_args["width"],
                    "height": input_args["height"],
                    "negative_prompt": input_args["negative_prompt"],
                }
                arg = ImagePromptContainer(**arg)
                return arg
            raise Exception("No output")
        except Exception as e:
            raise e
