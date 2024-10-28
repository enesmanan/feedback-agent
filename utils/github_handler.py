import requests
import re

class GitHubHandler:
    @staticmethod
    def get_raw_github_url(github_url):
        """Normal GitHub URL'sini raw içerik URL'sine dönüştürür"""
        pattern = r'https://github\.com/([^/]+)/([^/]+)/blob/([^/]+)/(.+)'
        match = re.match(pattern, github_url)
        
        if not match:
            raise ValueError("Geçersiz GitHub URL'si")
            
        user, repo, branch, path = match.groups()
        raw_url = f'https://raw.githubusercontent.com/{user}/{repo}/{branch}/{path}'
        return raw_url

    @staticmethod
    def get_file_content(url):
        """GitHub URL'inden dosya içeriğini alır"""
        try:
            raw_url = GitHubHandler.get_raw_github_url(url)
            response = requests.get(raw_url)
            response.raise_for_status()
            return response.text
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Dosya alınırken hata oluştu: {str(e)}")