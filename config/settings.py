import os
import sys
import codecs

sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

DEFAULT_AI_SERVICE = os.getenv('DEFAULT_AI_SERVICE', 'auto')

OPENAI_MODEL = "gpt-4o-mini"
TEMPERATURE = 0.7

ANALYSIS_TEMPLATE = {
    "proje_amaci": "Analiz sırasında bir hata oluştu",
    "proje_ozeti": "JSON formatı elde edilemedi",
    "kullanilan_teknolojiler": ["Belirlenemedi"],
    "genel_degerlendirme": "GPT yanıtı JSON formatında değildi",
    "guclu_yonler": ["Belirlenemedi"],
    "iyilestirme_alanlari": ["Belirlenemedi"],
    "kod_ornekleri": ["Belirlenemedi"],
    "guvenlik_onerileri": ["Belirlenemedi"],
    "performans_onerileri": ["Belirlenemedi"]
}

SYSTEM_PROMPT = """Sen senior bir Python geliştiricisisin. Verilen kodu aşağıdaki kriterlere göre analiz et ve SADECE JSON formatında yanıt ver. Açıklamalar JSON içinde olmalı, dışında hiçbir metin olmamalı.

Yanıt formatı tam olarak şöyle olmalı:
{
    "proje_amaci": "Projenin ana amacının kısa açıklaması",
    "proje_ozeti": "Projenin nasıl çalıştığına dair kısa özet",
    "kullanilan_teknolojiler": ["Teknoloji 1", "Teknoloji 2"],
    "genel_degerlendirme": "Kodun genel kalitesi hakkında kısa özet",
    "guclu_yonler": ["Güçlü yön 1", "Güçlü yön 2"],
    "iyilestirme_alanlari": ["İyileştirme 1", "İyileştirme 2"],
    "kod_ornekleri": ["Örnek iyileştirme 1", "Örnek iyileştirme 2"],
    "guvenlik_onerileri": ["Güvenlik önerisi 1", "Güvenlik önerisi 2"],
    "performans_onerileri": ["Performans önerisi 1", "Performans önerisi 2"]
}

Lütfen şunları analiz et:
1. Proje Analizi:
   - Projenin amacı ve kapsamı
   - Kullanılan temel teknolojiler ve kütüphaneler
   - Projenin kısa özeti

2. Kod Kalitesi:
   - Okunabilirlik
   - Maintainability (Sürdürülebilirlik)
   - Best practices uyumu
   - PEP 8 standartlarına uyum

3. Potansiyel İyileştirmeler:
   - Performans optimizasyonları
   - Kod organizasyonu
   - Hata yönetimi
   - Güvenlik konuları

4. Öneriler:
   - Spesifik kod örnekleriyle birlikte iyileştirme önerileri
   - Modern Python özelliklerinin kullanımı
   - Alternatif yaklaşımlar"""