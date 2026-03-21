from transformers import MarianMTModel, MarianTokenizer
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
import torch

_models_cache = {}

class TranslationError(Exception):
    pass

class ModelNotFoundError(TranslationError):
    pass

def get_model(source_lang: str, target_lang: str):
    model_key = f"{source_lang}-{target_lang}"
    model_name = f"Helsinki-NLP/opus-mt-{model_key}"

    if model_key not in _models_cache:
        try:
            print(f"--- Загрузка новой модели: {model_name} ---")
            tokenizer = MarianTokenizer.from_pretrained(model_name)
            model = MarianMTModel.from_pretrained(model_name)
            _models_cache[model_key] = (model, tokenizer)
        except Exception as e:
            print(f"Ошибка загрузки модели {model_name}: {e}")
            raise ModelNotFoundError(f"Модель для перевода с '{source_lang}' на '{target_lang}' не найдена."
            )
        
    return _models_cache[model_key]

DetectorFactory.seed = 0

def detect_language(text: str) -> str:
    if not text or not text.strip():
        return "en"
    
    try:
        lang = detect(text)
        return lang
    except LangDetectException:
        return "en"
    
def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    model, tokenizer = get_model(source_lang, target_lang)

    try:
        inputs = tokenizer(
            text, 
            return_tensors="pt", 
            padding=True, 
            truncation=True, 
            max_length=512
        )

        with torch.no_grad(): 
            translated_tokens = model.generate(**inputs)

        result = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)

        return result

    except Exception as e:
        raise TranslationError(f"Ошибка при генерации перевода: {str(e)}")