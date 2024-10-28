from openai import OpenAI
import requests
import base64
import json
import re
import nbformat
import sys
import codecs

sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

class CodeAnalyzer:
    def __init__(self, openai_api_key):
        self.openai_api_key = openai_api_key
        self.client = OpenAI(api_key=openai_api_key)

    def get_raw_github_url(self, github_url):
        """Normal GitHub URL'sini raw içerik URL'sine dönüştürür"""
        pattern = r'https://github\.com/([^/]+)/([^/]+)/blob/([^/]+)/(.+)'
        match = re.match(pattern, github_url)
        
        if not match:
            raise ValueError("Geçersiz GitHub URL'si")
            
        user, repo, branch, path = match.groups()
        raw_url = f'https://raw.githubusercontent.com/{user}/{repo}/{branch}/{path}'
        return raw_url

    def get_file_content(self, url):
        """GitHub URL'inden dosya içeriğini alır"""
        try:
            raw_url = self.get_raw_github_url(url)
            response = requests.get(raw_url)
            response.raise_for_status()
            
            if url.endswith('.py'):
                return response.text
            elif url.endswith('.ipynb'):
                return self._extract_notebook_code(response.text)
            else:
                raise ValueError("Desteklenmeyen dosya formatı. Sadece .py ve .ipynb dosyaları desteklenir.")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Dosya alınırken hata oluştu: {str(e)}")

    def _extract_notebook_code(self, notebook_content):
        """Jupyter notebook'tan Python kodunu çıkarır"""
        try:
            notebook = nbformat.reads(notebook_content, as_version=4)
            code = ""
            for cell in notebook.cells:
                if cell.cell_type == "code":
                    code += cell.source + "\n\n"
            return code
        except Exception as e:
            raise Exception(f"Notebook içeriği işlenirken hata oluştu: {str(e)}")

    def analyze_with_gpt4(self, code):
        """GPT-4 kullanarak kodu analiz eder"""
        try:
            system_prompt = """Sen senior bir Python geliştiricisisin. Verilen kodu aşağıdaki kriterlere göre analiz et ve SADECE JSON formatında yanıt ver. Açıklamalar JSON içinde olmalı, dışında hiçbir metin olmamalı.

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

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Lütfen bu Python kodunu analiz et:\n\n{code}"}
                ],
                temperature=0.7
            )

            content = response.choices[0].message.content.strip()
            
            # JSON içeriğini bul
            try:
                # Eğer content direkt JSON ise
                analysis = json.loads(content)
            except json.JSONDecodeError:
                # Eğer JSON yanıtın içinde bir yerdeyse
                import re
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    analysis = json.loads(json_match.group(0))
                else:
                    # Create a default analysis object
                    analysis = {
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

            # Check for missing fields and add default values
            required_fields = [
                "proje_amaci", "proje_ozeti", "kullanilan_teknolojiler",
                "genel_degerlendirme", "guclu_yonler", "iyilestirme_alanlari",
                "kod_ornekleri", "guvenlik_onerileri", "performans_onerileri"
            ]
            
            for field in required_fields:
                if field not in analysis:
                    analysis[field] = "Belirlenemedi" if field in ["proje_amaci", "proje_ozeti", "genel_degerlendirme"] else ["Belirlenemedi"]

            return analysis

        except Exception as e:
            return {
                "proje_amaci": "Analiz sırasında bir hata oluştu",
                "proje_ozeti": f"Hata: {str(e)}",
                "kullanilan_teknolojiler": ["Belirlenemedi"],
                "genel_degerlendirme": "Analiz tamamlanamadı",
                "guclu_yonler": ["Belirlenemedi"],
                "iyilestirme_alanlari": ["Belirlenemedi"],
                "kod_ornekleri": ["Belirlenemedi"],
                "guvenlik_onerileri": ["Belirlenemedi"],
                "performans_onerileri": ["Belirlenemedi"]
            }

    def format_analysis(self, analysis):
        """Analiz sonuçlarını okunabilir bir formata dönüştürür"""
        if "error" in analysis:
            return f"Hata: {analysis['error']}"

        formatted_output = []
        formatted_output.append("\nKod Analiz Raporu")
        formatted_output.append("=================")
        
        formatted_output.append("\nProje Amaci")
        formatted_output.append("-----------")
        formatted_output.append(analysis['proje_amaci'])
        
        formatted_output.append("\nProje Ozeti")
        formatted_output.append("-----------")
        formatted_output.append(analysis['proje_ozeti'])
        
        formatted_output.append("\nKullanilan Teknolojiler")
        formatted_output.append("---------------------")
        for tech in analysis['kullanilan_teknolojiler']:
            formatted_output.append(f"* {tech}")
        
        formatted_output.append("\nGenel Degerlendirme")
        formatted_output.append("------------------")
        formatted_output.append(analysis['genel_degerlendirme'])
        
        formatted_output.append("\nGuclu Yonler")
        formatted_output.append("-----------")
        for item in analysis['guclu_yonler']:
            formatted_output.append(f"* {item}")
        
        formatted_output.append("\nIyilestirme Alanlari")
        formatted_output.append("------------------")
        for item in analysis['iyilestirme_alanlari']:
            formatted_output.append(f"* {item}")
        
        formatted_output.append("\nKod Ornekleri ve Oneriler")
        formatted_output.append("-----------------------")
        for item in analysis['kod_ornekleri']:
            formatted_output.append(f"* {item}")
        
        formatted_output.append("\nGuvenlik Onerileri")
        formatted_output.append("-----------------")
        for item in analysis['guvenlik_onerileri']:
            formatted_output.append(f"* {item}")
        
        formatted_output.append("\nPerformans Onerileri")
        formatted_output.append("------------------")
        for item in analysis['performans_onerileri']:
            formatted_output.append(f"* {item}")
        
        return "\n".join(formatted_output)

    def provide_feedback(self, github_url):
        """GitHub URL'si için geri bildirim sağlar"""
        try:
            # Retrieve the code from GitHub
            code = self.get_file_content(github_url)
            
            # Analyze with GPT-4
            analysis = self.analyze_with_gpt4(code)
            
            # Format the results
            feedback = self.format_analysis(analysis)
            
            return feedback
            
        except Exception as e:
            return f"Hata oluştu: {str(e)}"

if __name__ == "__main__":
    openai_api_key = "OPENAI_API_KEY"
    analyzer = CodeAnalyzer(openai_api_key)
    
    github_url = "https://github.com/emirryilmazz/Fish-Classification/blob/main/main.ipynb"
    feedback = analyzer.provide_feedback(github_url)
    print(feedback)