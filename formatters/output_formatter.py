class OutputFormatter:
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
            formatted_output.append(f"* {item}")
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