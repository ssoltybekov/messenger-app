from typing import List
from app.schemas.summarize import ChatMessage
from transformers import BartTokenizer, BartForConditionalGeneration
import torch
from app.services.translation import translate_text

def split_into_chunks(messages: List[ChatMessage], max_chars: int = 3000) -> List[str]:
    chunks = []
    current_chunk = ""

    for msg in messages:
        formatted_msg = f"{msg.author}: {msg.text}\n"
        msg_len = len(formatted_msg)

        if len(current_chunk) + msg_len < max_chars:
            current_chunk += formatted_msg
        else:
            chunks.append(current_chunk.strip())
            current_chunk = formatted_msg
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

_summarizer_cache = None

def get_summarizer():
    global _summarizer_cache
    if _summarizer_cache is not None:
        return _summarizer_cache

    model_name = "facebook/bart-large-cnn"
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"--- Использование устройства: {device} ---")

    try:
        tokenizer = BartTokenizer.from_pretrained(model_name)
        
        model = BartForConditionalGeneration.from_pretrained(model_name).to(device)
        
        _summarizer_cache = (model, tokenizer, device) 
        return _summarizer_cache
    except Exception as e:
        raise RuntimeError(f"Ошибка загрузки BART: {e}")
    
def summarize_chunk(chunk: str) -> str:
    model, tokenizer, device = get_summarizer()

    inputs = tokenizer(
        chunk, 
        max_length=1024, 
        truncation=True, 
        return_tensors="pt"
    ).to(device)

    with torch.no_grad():
        summary_ids = model.generate(
            inputs["input_ids"],
            max_length=150,      
            min_length=40,      
            num_beams=4,         
            early_stopping=True 
        )

    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    
    return summary

def summarize_messages(messages, target_lang) -> str:
    chunks = split_into_chunks(messages)
    if not chunks:
        return ""
    
    summaries = []
    for chunk in chunks:
        chunk_sum = summarize_chunk(chunk)
        summaries.append(chunk_sum)
    
    if len(summaries) > 1:
        combined_text = " ".join(summaries)
        final_summary = summarize_chunk(combined_text)
    else:
        final_summary = summaries[0]

    if target_lang != "en":
        final_summary = translate_text(final_summary, source_lang="en", target_lang=target_lang)

    return final_summary
