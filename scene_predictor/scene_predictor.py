import torch

from transformers import BertTokenizer
from PIL import Image

from .models import caption
from .datasets import coco
from .configuration import Config


config = Config()

# using version v1
model = torch.hub.load('saahiluppal/catr', 'v1', pretrained=True)

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

start_token = tokenizer.convert_tokens_to_ids(tokenizer._cls_token)
end_token = tokenizer.convert_tokens_to_ids(tokenizer._sep_token)


def preprocess_image(np_image): 
    image = Image.fromarray(np_image)
    image = coco.val_transform(image)
    image = image.unsqueeze(0)
    return image

def create_caption_and_mask(start_token, max_length):
    caption_template = torch.zeros((1, max_length), dtype=torch.long)
    mask_template = torch.ones((1, max_length), dtype=torch.bool)

    caption_template[:, 0] = start_token
    mask_template[:, 0] = False

    return caption_template, mask_template



caption, cap_mask = create_caption_and_mask(
    start_token, config.max_position_embeddings)


@torch.no_grad()
def evaluate(image):
    model.eval()
    for i in range(config.max_position_embeddings - 1):
        predictions = model(image, caption, cap_mask)
        predictions = predictions[:, i, :]
        predicted_id = torch.argmax(predictions, axis=-1)

        if predicted_id[0] == 102:
            return caption

        caption[:, i+1] = predicted_id[0]
        cap_mask[:, i+1] = False

    return caption


def describe_scene(image):
    image = preprocess_image(image)
    output = evaluate(image)
    result = tokenizer.decode(output[0].tolist(), skip_special_tokens=True)
    return result.capitalize()
    # print(result.capitalize())