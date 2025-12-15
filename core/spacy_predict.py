import spacy
import os
from core.utils import resource_path

MODEL = resource_path("models")
MODEL_PATH = os.path.join(MODEL, "spacy-trf-model")

class NERPredictor:
    def __init__(self, model_path=MODEL_PATH):
        self.nlp = spacy.load(model_path)

    def predict(self, text):
        doc = self.nlp(text)
        entities = {}
        for ent in doc.ents:
            if(ent.label_ not in entities):
                entities[ent.label_] = []
            entities[ent.label_].append(ent.text)
        return entities