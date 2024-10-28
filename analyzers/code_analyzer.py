from openai import OpenAI
import json
import re
from config.settings import SYSTEM_PROMPT, OPENAI_MODEL, TEMPERATURE, ANALYSIS_TEMPLATE

class CodeAnalyzer:
    def __init__(self, openai_api_key):
        self.client = OpenAI(api_key=openai_api_key)

    def analyze_code(self, code):
        """GPT-4 kullanarak kodu analiz eder"""
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Lütfen bu Python kodunu analiz et:\n\n{code}"}
                ],
                temperature=TEMPERATURE
            )

            content = response.choices[0].message.content.strip()
            
            # Locate and parse the JSON content
            analysis = self._parse_json_response(content)
            
            # eksik var mi
            analysis = self._validate_analysis(analysis)

            return analysis

        except Exception as e:
            return {**ANALYSIS_TEMPLATE, "proje_ozeti": f"Hata: {str(e)}"}

    def _parse_json_response(self, content):
        """GPT yanıtından JSON içeriğini parse eder"""
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                return json.loads(json_match.group(0))
            return ANALYSIS_TEMPLATE

    def _validate_analysis(self, analysis):
        """Analiz sonuçlarını validate eder ve eksik alanları doldurur"""
        required_fields = [
            "proje_amaci", "proje_ozeti", "kullanilan_teknolojiler",
            "genel_degerlendirme", "guclu_yonler", "iyilestirme_alanlari",
            "kod_ornekleri", "guvenlik_onerileri", "performans_onerileri"
        ]
        
        for field in required_fields:
            if field not in analysis:
                analysis[field] = "Belirlenemedi" if field in ["proje_amaci", "proje_ozeti", "genel_degerlendirme"] else ["Belirlenemedi"]
        
        return analysis