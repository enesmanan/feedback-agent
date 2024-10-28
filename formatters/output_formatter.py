class OutputFormatter:
    @staticmethod
    def format_analysis(analysis):
        """Analiz sonuçlarını okunabilir bir formata dönüştürür"""
        if "error" in analysis:
            return f"Hata: {analysis['error']}"

        formatted_output = []
        formatted_output.append("\nKod Analiz Raporu")
        formatted_output.append("=================")
        
        sections = [
            ("Proje Amaci", "proje_amaci", "-----------"),
            ("Proje Ozeti", "proje_ozeti", "-----------"),
            ("Kullanilan Teknolojiler", "kullanilan_teknolojiler", "---------------------"),
            ("Genel Degerlendirme", "genel_degerlendirme", "------------------"),
            ("Guclu Yonler", "guclu_yonler", "-----------"),
            ("Iyilestirme Alanlari", "iyilestirme_alanlari", "------------------"),
            ("Kod Ornekleri ve Oneriler", "kod_ornekleri", "-----------------------"),
            ("Guvenlik Onerileri", "guvenlik_onerileri", "-----------------"),
            ("Performans Onerileri", "performans_onerileri", "------------------")
        ]

        for title, key, separator in sections:
            formatted_output.append(f"\n{title}")
            formatted_output.append(separator)
            if isinstance(analysis[key], list):
                for item in analysis[key]:
                    formatted_output.append(f"* {item}")
            else:
                formatted_output.append(analysis[key])

        return "\n".join(formatted_output)