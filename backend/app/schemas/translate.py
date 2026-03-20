from pydantic import BaseModel, Field, StringConstraints
from typing import Optional, Annotated

LanguageCode = Annotated[
    str, 
    StringConstraints(min_length=2, max_length=2, to_lower=True, pattern=r"^[a-z]{2}$")
]

class TranslationRequest(BaseModel):
    text: str = Field(
        ..., 
        min_length=1, 
        max_length=1000, 
        description="Текст для перевода (макс. 1000 символов)"
    )
    
    target_lang: LanguageCode = Field(
        ..., 
        description="Код целевого языка (напр. 'en', 'ru', 'de')"
    )
    
    source_lang: Optional[LanguageCode] = Field(
        None, 
        description="Код исходного языка. Если не указан — определим автоматически"
    )

class TranslationResponse(BaseModel):
    translated_text: str
    source_lang: LanguageCode
    target_lang: LanguageCode