import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration, T5Config

from config import *

class t5():
    MAX_LEN = T5_MAX_LEN
    def __init__(self, device_type="cpu"):
        self.device = torch.device(device_type)
        self.model = T5ForConditionalGeneration.from_pretrained('t5-large').to(self.device)#-small')
        self.tokenizer = T5Tokenizer.from_pretrained('t5-large')#-small')

    def summarize(self, text):
        if len(text) <= 250:
            return text

        preprocess_text = text.strip().replace("\n","")
        t5_prepared_text = "summarize: " + preprocess_text


        tokenized_text = self.tokenizer.encode(
            t5_prepared_text,
            max_length=self.MAX_LEN,
            return_tensors="pt"
        ).to(self.device)

        # summarize
        summary_ids = self.model.generate(
            tokenized_text,
            num_beams=4,
            no_repeat_ngram_size=2,
            min_length=30,
            max_length=250,#100,
            early_stopping=True
        ).to(self.device)

        output = self.tokenizer.decode(
            summary_ids[0],
            skip_special_tokens=True
        )

        return output
