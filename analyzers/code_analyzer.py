from openai import OpenAI
import google.generativeai as genai
import json
import re
from config.settings import (
    SYSTEM_PROMPT, 
    OPENAI_MODEL, 
    TEMPERATURE, 
    ANALYSIS_TEMPLATE,
    DEFAULT_AI_SERVICE
)

class AIServiceFactory:
    @staticmethod
    def get_service(api_keys):
        """Returns the appropriate AI service based on available API keys and configuration"""
        service = DEFAULT_AI_SERVICE

        if service == "auto":
            # Automatically choose based on available keys
            if api_keys.get("OPENAI_API_KEY"):
                service = "openai"
            elif api_keys.get("GEMINI_API_KEY"):
                service = "gemini"
            else:
                raise ValueError("No valid API key found for any AI service")

        if service == "openai" and not api_keys.get("OPENAI_API_KEY"):
            raise ValueError("OpenAI API key not found")
        elif service == "gemini" and not api_keys.get("GEMINI_API_KEY"):
            raise ValueError("Gemini API key not found")

        return service

class CodeAnalyzer:
    def __init__(self, api_keys):
        """Initialize with a dictionary of API keys"""
        self.api_keys = api_keys
        self.service = AIServiceFactory.get_service(api_keys)
        
        if self.service == "openai":
            self.client = OpenAI(api_key=api_keys["OPENAI_API_KEY"])
        elif self.service == "gemini":
            genai.configure(api_key=api_keys["GEMINI_API_KEY"])
            self.client = genai.GenerativeModel('gemini-pro')

    def analyze_code(self, code):
        """Analyzes code using the selected AI service"""
        try:
            if self.service == "openai":
                return self._analyze_with_openai(code)
            else:
                return self._analyze_with_gemini(code)
        except Exception as e:
            return {**ANALYSIS_TEMPLATE, "proje_ozeti": f"Hata: {str(e)}"}

    def _analyze_with_openai(self, code):
        """Analyze code using OpenAI's GPT-4"""
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
            analysis = self._parse_json_response(content)
            return self._validate_analysis(analysis)

        except Exception as e:
            return {**ANALYSIS_TEMPLATE, "proje_ozeti": f"OpenAI Hatası: {str(e)}"}

    def _analyze_with_gemini(self, code):
        """Analyze code using Google's Gemini"""
        try:
            # Adapt the system prompt for Gemini
            gemini_prompt = f"{SYSTEM_PROMPT}\n\nKod:\n{code}"
            
            response = self.client.generate_content(gemini_prompt)
            
            # Extract JSON from Gemini's response
            content = response.text.strip()
            analysis = self._parse_json_response(content)
            return self._validate_analysis(analysis)

        except Exception as e:
            return {**ANALYSIS_TEMPLATE, "proje_ozeti": f"Gemini Hatası: {str(e)}"}

    def chat_about_code(self, message, code_context):
        """Chat about code using the selected AI service"""
        try:
            if self.service == "openai":
                return self._chat_with_openai(message, code_context)
            else:
                return self._chat_with_gemini(message, code_context)
        except Exception as e:
            return f"Sohbet hatası: {str(e)}"

    def _chat_with_openai(self, message, code_context):
        """Chat using OpenAI's GPT-4"""
        response = self.client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "Sen bir kod analiz asistanısın. Kullanıcının projesi hakkındaki sorularını yanıtla."},
                {"role": "user", "content": f"Proje kodu:\n{code_context}\n\nSoru: {message}"}
            ]
        )
        return response.choices[0].message.content

    def _chat_with_gemini(self, message, code_context):
        """Chat using Google's Gemini"""
        prompt = f"""Sen bir kod analiz asistanısın. Kullanıcının projesi hakkındaki sorularını yanıtla.

Proje kodu:
{code_context}

Soru: {message}"""
        
        response = self.client.generate_content(prompt)
        return response.text

    def _parse_json_response(self, content):
        """Parse JSON response from AI services"""
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON if it's embedded in text
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except:
                    return ANALYSIS_TEMPLATE
            return ANALYSIS_TEMPLATE

    def _validate_analysis(self, analysis):
        """Validate and fill missing fields in analysis"""
        required_fields = [
            "proje_amaci", "proje_ozeti", "kullanilan_teknolojiler",
            "genel_degerlendirme", "guclu_yonler", "iyilestirme_alanlari",
            "kod_ornekleri", "guvenlik_onerileri", "performans_onerileri"
        ]
        
        for field in required_fields:
            if field not in analysis:
                analysis[field] = "Belirlenemedi" if field in ["proje_amaci", "proje_ozeti", "genel_degerlendirme"] else ["Belirlenemedi"]
        
        return analysis