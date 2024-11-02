import re

class OutputFormatter:
    @staticmethod
    def _format_code_block(text):
        """Kod bloklarını markdown formatına dönüştürür"""
        if "```" in text:
            return text
        
        # Kod kalıplarını kontrol et
        code_patterns = [
            r'def\s+\w+\s*\([^)]*\)\s*:',
            r'class\s+\w+(\s*\([^)]*\))?\s*:',
            r'import\s+\w+',
            r'from\s+\w+\s+import',
            r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=',
            r'if\s+__name__\s*==\s*[\'"]__main__[\'"]',
            r'for\s+\w+\s+in\s+',
            r'while\s+.*:',
            r'try:',
            r'except',
            r'return\s+'
        ]
        
        if any(re.search(pattern, text) for pattern in code_patterns):
            lines = text.split('\n')
            first_indent = None
            for line in lines:
                if line.strip():
                    first_indent = len(line) - len(line.lstrip())
                    break
            
            if first_indent is not None:
                normalized_lines = []
                for line in lines:
                    if line.strip():
                        line = line[first_indent:] if len(line) > first_indent else line.lstrip()
                    normalized_lines.append(line)
                text = '\n'.join(normalized_lines)
            
            return f"```python\n{text.strip()}\n```"
        
        return text

    @staticmethod
    def format_analysis(analysis):
        """Analiz sonuçlarını markdown formatında döndürür"""
        if "error" in analysis:
            return f"## Hata\n{analysis['error']}"

        formatted_output = []
        formatted_output.append("# Kod Analiz Raporu\n")
        
        # Proje Amacı
        formatted_output.append("## Proje Amacı")
        formatted_output.append(analysis['proje_amaci'])
        formatted_output.append("")
        
        # Proje Özeti
        formatted_output.append("## Proje Özeti")
        formatted_output.append(analysis['proje_ozeti'])
        formatted_output.append("")
        
        # Kullanılan Teknolojiler
        formatted_output.append("## Kullanılan Teknolojiler")
        for tech in analysis['kullanilan_teknolojiler']:
            formatted_output.append(f"* {tech}")
        formatted_output.append("")
        
        # Genel Değerlendirme
        formatted_output.append("## Genel Değerlendirme")
        formatted_output.append(analysis['genel_degerlendirme'])
        formatted_output.append("")
        
        # Güçlü Yönler
        formatted_output.append("## Güçlü Yönler")
        for item in analysis['guclu_yonler']:
            formatted_output.append(f"* {item}")
        formatted_output.append("")
        
        # İyileştirme Alanları
        formatted_output.append("## İyileştirme Alanları")
        for item in analysis['iyilestirme_alanlari']:
            formatted_output.append(f"* {item}")
        formatted_output.append("")
        
        # Kod Örnekleri ve Öneriler
        formatted_output.append("## Kod Örnekleri ve Öneriler")
        for item in analysis['kod_ornekleri']:
            # Yeni format için kontrol
            if isinstance(item, dict) and 'aciklama' in item and 'kod' in item:
                # Önce açıklamayı ekle
                formatted_output.append(f"### İyileştirme Açıklaması")
                formatted_output.append(item['aciklama'])
                formatted_output.append("")
                # Sonra kodu ekle
                formatted_output.append("### Örnek Kod")
                formatted_output.append(OutputFormatter._format_code_block(item['kod']))
                formatted_output.append("")
            else:
                # Eski format için geriye dönük uyumluluk
                formatted_output.append(OutputFormatter._format_code_block(item))
                formatted_output.append("")
        
        # Güvenlik Önerileri
        formatted_output.append("## Güvenlik Önerileri")
        for item in analysis['guvenlik_onerileri']:
            formatted_output.append(f"* {item}")
        formatted_output.append("")
        
        # Performans Önerileri
        formatted_output.append("## Performans Önerileri")
        for item in analysis['performans_onerileri']:
            formatted_output.append(f"* {item}")
        
        return "\n".join(formatted_output)