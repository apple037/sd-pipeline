class TextToImageRequest:
    def __init__(self, prompt, negative_prompt, width, height, output):
        self.prompt = prompt
        self.negative_prompt = negative_prompt
        self.width = width
        self.height = height
        self.output = output

    def to_json(self):
        return {
            'prompt': self.prompt,
            'negative_prompt': self.negative_prompt,
            'width': self.width,
            'height': self.height,
            'output': self.output,
        }


class TextToImageResponse:
    def __init__(self, image_url):
        self.image_url = image_url


class Avatar:
    def __init__(self, name, category):
        self.name = name
        self.category = category

    def to_dict(self):
        return {
            'name': self.name,
            'category': self.category
        }

    @staticmethod
    def from_dict(data):
        return Avatar(
            name=data.get('name'),
            category=data.get('category', [])
        )


class pipelineJob:
    def __init__(self, name_list, prompt_count, count, width, height, to_gcp):
        self.name_list = name_list
        self.prompt_count = prompt_count
        self.count = count
        self.width = width
        self.height = height
        self.to_gcp = to_gcp

    def to_dict(self):
        return {
            'name_list': self.name_list,
            'prompt_count': self.prompt_count,
            'count': self.count,
            'width': self.width,
            'height': self.height,
            'to_gcp': self.to_gcp
        }
