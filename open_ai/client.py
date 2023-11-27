from openai import OpenAI
import base64


class OpenAIClient:
    def __init__(self):
        self.client = OpenAI()
        self.default_model = 'gpt-4-1106-preview'
        self.vision_model = 'gpt-4-vision-preview'
        self.image_generation_model = 'dall-e-3'

    def plant_checker(self, plant_name: str):
        """
        Given a plant name, will call openai to generate a response on how to take care of the plant.
        The response will be in JSON format and compliant with the pyPlants.models.Plant model.
        """
        default_language = "french"
        response = self.client.chat.completions.create(
            model=self.default_model,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You're a plant expert, designed to help users to take care of their plants."
                               "For each given plant, you should always provide the following information in the JSON format:"
                               f"- description: A description of the plant in {default_language} (string)"
                               "- water_frequency_summer: Summer Watering frequency, in days (integer)"
                               "- water_frequency_winter: Winter Watering frequency, in days (integer)"
                               "- sunlight: How much sunlight it needs (light_exposure, partial_shade or shade)"
                               "- sun_exposure: What type of sun exposure (direct_sun or no_direct_sun)"
                               "- fertilizer: If it needs to be fertilized (True or False)"
                               "- fertilizer_season: The fertilizing season (spring, summer, fall or winter, 1 choice only) if it needs to be fertilized"
                               "- repotting: If it needs to be repotted (True or False)"
                               "- repotting_season: The repotting season (spring, summer, fall or winter, 1 choice only) if it needs to be repotted"
                               "- leaf_mist: If its leaves need to be misted (True or False)"
                               f"- extra_tips: Provide any additional tips for taking care of the plant (string) - in {default_language}, for non plant experts"
                },
                {
                    "role": "user",
                    "content": f"How should I take care of my {plant_name}?"
                }
            ]
        )
        return response

    def plant_recognizer(self):
        """
        Given an image of a plant, will call openai to generate a response on what plant it is.
        """
        image_path = "open_ai/test_plant.jpg"
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        response = self.client.chat.completions.create(
            model=self.vision_model,
            messages=[
                {
                    "role": "system",
                    "content": "You're a plant expert, designed to help users to take care of their plants. "
                               "You can recognize plants provided by the user and ONLY answer with the name of the plant."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "What is the name of this plant?"
                        },
                        {
                            "type": "image",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_string}"
                            }
                        }
                    ]
                }
            ]
        )
        return response

    def plant_image_generator(self, plant_name: str):
        response = self.client.images.generate(
            model=self.image_generation_model,
            prompt=f"A vibrant illustration of a {plant_name} plant, with a smooth, shiny finish and bright, popping colors. The plant should be centered within a circular badge that glows with a radiant light effect, giving a sense of premium quality. The background should feature a light gradient that complements the colors of the plant. The artwork should be detailed with a clear outline and a slight drop shadow for depth, resembling a high-quality sticker design.",
            size="1024x1024",
            quality="standard",
            n=1
        )
        return response


