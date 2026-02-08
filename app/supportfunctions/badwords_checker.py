import asyncio
from typing import List, Set, Dict
import re
import pymorphy3
from functools import lru_cache

class SimpleProfanityFilter:
    def __init__(self):
        self.morph = pymorphy3.MorphAnalyzer()
        
        self.bad_lemmas = {
            'мудак', 'мудила', 'козел', 'скотина',
            'сволочь', 'подонок', 'ублюдок', 'тварь',
            'черт', 'чертов', 'дьявол',
            'идиот', 'дебил', 'дурак', 'дура',
            'тупица', 'олень', 'баран',
            'сука', 'сучка', 'сукин',
            'падла', 'падло',
            'жопа', 'задница', 'зад',
            'срать', 'дерьмо', 'говно',
            'моча', 'ссать', 'писать',
            'сиськи', 'срака',
            'чурка', 'чурбан',
            'хач', 'черножопый',
            'педик', 'пидор', 'гомик',
            'жид', 'еврей',
            'таджик', 'узбек', 'цыган',
            'шлюха', 'проститутка', 'блядунья',
            'шмара', 'потаскуха',
            'стерва', 'стерво',
            'отстой', 'гадость', 'мерзость',
            'хрен', 'хрень', 'хренов',
            'падла', 'мразь',
            'убей', 'убить', 'зарежь',
            'сдохни', 'сдохнуть',
            'пидорас', 'сучка'
        }
    
    @lru_cache(maxsize=10000)
    def get_word_lemma(self, word: str) -> str:
        """Получаем лемму (нормальную форму) слова"""
        parsed = self.morph.parse(word.lower())
        if parsed:
            return parsed[0].normal_form
        return word.lower()
    
    async def check_text(self, text: str) -> Dict:
        """
        Асинхронная проверка текста
        
        Args:
            text: входной текст
            
        Returns:
            Dict с результатами проверки
        """
        words = re.findall(r'\b[а-яё]+\b', text.lower())
        
        found_bad_words = []
        
        for word in words:
            lemma = await asyncio.get_event_loop().run_in_executor(
                None,
                self.get_word_lemma,
                word
            )
            
            if lemma in self.bad_lemmas:
                found_bad_words.append(word)
        
        return {
            "has_profanity": len(found_bad_words) > 0,
            "bad_words": found_bad_words,
            "total_words": len(words),
            "bad_word_count": len(found_bad_words)
        }
    
    async def check_multiple_texts(self, texts: List[str]) -> List[Dict]:
        tasks = [self.check_text(text) for text in texts]
        return await asyncio.gather(*tasks)
