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
        """Returns the appropriate AI service based on available API keys"""
        if api_keys.get("OPENAI_API_KEY"):
            return "openai"
        elif api_keys.get("GEMINI_API_KEY"):
            return "gemini"
        else:
            raise ValueError("No valid API key found for any AI service")

class CodeAnalyzer:
    def __init__(self, api_keys):
        """Initialize with API keys"""
        self.api_keys = api_keys
        self.service = AIServiceFactory.get_service(api_keys)
        self.ANALYSIS_TEMPLATE = ANALYSIS_TEMPLATE
        
        if self.service == "openai":
            self.client = OpenAI(api_key=api_keys["OPENAI_API_KEY"])
        elif self.service == "gemini":
            genai.configure(api_key=api_keys["GEMINI_API_KEY"])
            self.client = genai.GenerativeModel('gemini-pro')

    def analyze_code(self, code, notebook_data=None):
        """Main analysis function"""
        try:
            if self.service == "openai":
                analysis = self._analyze_with_openai(code, notebook_data)
            else:
                analysis = self._analyze_with_gemini(code, notebook_data)
            
            # Validate and clean the analysis results
            analysis = self._validate_and_clean_analysis(analysis)
            return analysis
            
        except Exception as e:
            print(f"Analysis error: {str(e)}")
            return self.ANALYSIS_TEMPLATE

    def _analyze_with_openai(self, code, notebook_data=None):
        """Analyze code using OpenAI's GPT-4"""
        try:
            # Prepare context with code and documentation if available
            context = code
            if notebook_data:
                markdown_sections = []
                if notebook_data.get('documentation'):
                    doc = notebook_data['documentation']
                    if doc['project_description']:
                        markdown_sections.append(f"# Project Description\n{doc['project_description']}")
                    if doc['usage_examples']:
                        markdown_sections.append(f"# Usage Examples\n{' '.join(doc['usage_examples'])}")
                    if doc['parameters']:
                        markdown_sections.append(f"# Parameters\n{' '.join(doc['parameters'])}")
                    if doc['notes']:
                        markdown_sections.append(f"# Notes\n{' '.join(doc['notes'])}")

                if markdown_sections:
                    context = f"""# Documentation
{' '.join(markdown_sections)}

# Code
{code}"""

            prompt = f"""Lütfen aşağıdaki Python kodunu detaylı olarak analiz et.
            {' Kod ile birlikte verilen dokümantasyonu da dikkate al.' if notebook_data else ''}
            Yanıtını kesinlikle belirtilen JSON formatında ver ve hiçbir ek açıklama ekleme.
            Her bölüm için detaylı ve yapıcı geri bildirimler sağla.

            {SYSTEM_PROMPT}

            Analiz edilecek içerik:
            {context}"""

            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Sen deneyimli bir Python kod analisti ve geliştiricisisin."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content.strip()
            return json.loads(content)

        except Exception as e:
            print(f"OpenAI API error: {str(e)}")
            return self.ANALYSIS_TEMPLATE

    def _analyze_with_gemini(self, code, notebook_data=None):
        """Analyze code using Google's Gemini"""
        try:
            # Prepare context with code and documentation if available
            context = code
            if notebook_data:
                markdown_sections = []
                if notebook_data.get('documentation'):
                    doc = notebook_data['documentation']
                    if doc['project_description']:
                        markdown_sections.append(f"# Project Description\n{doc['project_description']}")
                    if doc['usage_examples']:
                        markdown_sections.append(f"# Usage Examples\n{' '.join(doc['usage_examples'])}")
                    if doc['parameters']:
                        markdown_sections.append(f"# Parameters\n{' '.join(doc['parameters'])}")
                    if doc['notes']:
                        markdown_sections.append(f"# Notes\n{' '.join(doc['notes'])}")

                if markdown_sections:
                    context = f"""# Documentation
{' '.join(markdown_sections)}

# Code
{code}"""

            prompt = f"""Lütfen aşağıdaki Python kodunu analiz et ve sonucu TAM OLARAK aşağıdaki JSON formatında döndür:

            {SYSTEM_PROMPT}

            Analiz edilecek içerik:
            {context}

            Önemli kurallar:
            1. Yanıt MUTLAKA geçerli bir JSON olmalı
            2. Tüm alanlar doldurulmalı, boş bırakılmamalı
            3. Dokümantasyondaki bilgiler de dikkate alınmalı
            4. Her kod örneği için detaylı açıklama eklenmeli
            5. Her bölüm için kapsamlı analiz yapılmalı
            6. Yanıtta JSON dışında hiçbir ek metin olmamalı"""

            response = self.client.generate_content(prompt)
            content = response.text.strip()
            
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                content = content[json_start:json_end]
            
            try:
                analysis = json.loads(content)
                return self._fix_gemini_output(analysis)
            except json.JSONDecodeError:
                return self._extract_analysis_from_text(content)
                
        except Exception as e:
            print(f"Gemini API error: {str(e)}")
            return self.ANALYSIS_TEMPLATE

    def _fix_gemini_output(self, analysis):
        """Fix and validate Gemini output format"""
        if 'kod_ornekleri' in analysis:
            if isinstance(analysis['kod_ornekleri'], list):
                fixed_examples = []
                for example in analysis['kod_ornekleri']:
                    if isinstance(example, dict) and 'aciklama' in example and 'kod' in example:
                        fixed_examples.append(example)
                    elif isinstance(example, str):
                        fixed_examples.append({
                            "aciklama": "Önerilen kod iyileştirmesi",
                            "kod": example
                        })
                analysis['kod_ornekleri'] = fixed_examples
            else:
                analysis['kod_ornekleri'] = [{
                    "aciklama": "Önerilen kod iyileştirmesi",
                    "kod": "# Örnek kod hazırlanıyor"
                }]
        
        # Liste olması gereken alanları kontrol et
        list_fields = ['kullanilan_teknolojiler', 'guclu_yonler', 'iyilestirme_alanlari', 
                      'guvenlik_onerileri', 'performans_onerileri']
        
        for field in list_fields:
            if field in analysis and not isinstance(analysis[field], list):
                analysis[field] = [str(analysis[field])]
            elif field not in analysis:
                analysis[field] = ["Analiz tamamlanıyor..."]
        
        return analysis

    def _validate_and_clean_analysis(self, analysis):
        """Validate and clean the analysis results"""
        required_fields = [
            "proje_amaci", "proje_ozeti", "kullanilan_teknolojiler",
            "genel_degerlendirme", "guclu_yonler", "iyilestirme_alanlari",
            "kod_ornekleri", "guvenlik_onerileri", "performans_onerileri"
        ]
        
        for field in required_fields:
            if field not in analysis or not analysis[field]:
                if field in ["proje_amaci", "proje_ozeti", "genel_degerlendirme"]:
                    analysis[field] = "Analiz tamamlanıyor..."
                elif field == "kod_ornekleri":
                    analysis[field] = [{
                        "aciklama": "Kod önerisi hazırlanıyor...",
                        "kod": "# Örnek kod hazırlanıyor"
                    }]
                else:
                    analysis[field] = ["Analiz tamamlanıyor..."]
        
        return analysis

    def _extract_analysis_from_text(self, text):
        """Extract structured analysis from unstructured text"""
        try:
            # Try to find and parse JSON-like content
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                try:
                    analysis = json.loads(json_match.group(0))
                    return self._fix_gemini_output(analysis)
                except:
                    pass

            # Extract content using patterns
            analysis = {}
            
            # Extract main sections
            sections = {
                'proje_amaci': r'"proje_amaci":\s*"([^"]*)"',
                'proje_ozeti': r'"proje_ozeti":\s*"([^"]*)"',
                'genel_degerlendirme': r'"genel_degerlendirme":\s*"([^"]*)"'
            }
            
            for key, pattern in sections.items():
                match = re.search(pattern, text)
                analysis[key] = match.group(1) if match else "Analiz tamamlanıyor..."
            
            # Extract list sections
            list_sections = {
                'kullanilan_teknolojiler': r'"kullanilan_teknolojiler":\s*\[(.*?)\]',
                'guclu_yonler': r'"guclu_yonler":\s*\[(.*?)\]',
                'iyilestirme_alanlari': r'"iyilestirme_alanlari":\s*\[(.*?)\]',
                'guvenlik_onerileri': r'"guvenlik_onerileri":\s*\[(.*?)\]',
                'performans_onerileri': r'"performans_onerileri":\s*\[(.*?)\]'
            }
            
            for key, pattern in list_sections.items():
                matches = re.findall(pattern, text, re.DOTALL)
                if matches:
                    items = re.findall(r'"([^"]*)"', matches[0])
                    analysis[key] = items if items else ["Analiz tamamlanıyor..."]
                else:
                    analysis[key] = ["Analiz tamamlanıyor..."]
            
            # Extract code examples
            code_pattern = r'```python\s*(.*?)\s*```'
            code_blocks = list(re.finditer(code_pattern, text, re.DOTALL))
            examples = []
            
            for block in code_blocks:
                code = block.group(1).strip()
                if code:
                    examples.append({
                        "aciklama": "Önerilen kod iyileştirmesi",
                        "kod": code
                    })
            
            analysis["kod_ornekleri"] = examples if examples else [{
                "aciklama": "Kod önerisi hazırlanıyor...",
                "kod": "# Örnek kod hazırlanıyor"
            }]
            
            return analysis

        except Exception as e:
            print(f"Text extraction error: {str(e)}")
            return self.ANALYSIS_TEMPLATE

    def chat_about_code(self, message, code_context):
        """Chat about code using the selected AI service"""
        try:
            if self.service == "openai":
                return self._chat_with_openai(message, code_context)
            else:
                return self._chat_with_gemini(message, code_context)
        except Exception as e:
            return f"Chat error: {str(e)}"

    def _chat_with_openai(self, message, code_context):
        """Chat using OpenAI's GPT-4"""
        response = self.client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """Sen deneyimli bir Python geliştiricisin. 
                    Kullanıcının sorularına net, açıklayıcı ve yapıcı yanıtlar ver.
                    Kod örnekleri verirken açıklamalarını da ekle."""
                },
                {
                    "role": "user",
                    "content": f"Kod:\n{code_context}\n\nSoru: {message}"
                }
            ],
            #temperature=0.5
        )
        return response.choices[0].message.content

    def _chat_with_gemini(self, message, code_context):
        """Chat using Google's Gemini"""
        prompt = f"""Sen deneyimli bir Python geliştiricisin. 
        Kullanıcının sorularına net, açıklayıcı ve yapıcı yanıtlar ver.
        Kod örnekleri verirken açıklamalarını da ekle.

        Kod:
        {code_context}

        Soru: {message}"""
        
        response = self.client.generate_content(prompt)
        return response.text