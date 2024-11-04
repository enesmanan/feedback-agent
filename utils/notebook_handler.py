import nbformat
import re

class NotebookHandler:
    def __init__(self):
        """Initialize NotebookHandler"""
        self.known_imports = set([
            'pandas', 'numpy', 'matplotlib', 'seaborn', 'sklearn', 'tensorflow',
            'torch', 'keras', 'scipy', 'requests', 'beautifulsoup4', 'flask',
            'django', 'sqlalchemy', 'pytest', 'unittest', 'os', 'sys', 'json',
            'csv', 'random', 'datetime', 'time', 'math', 're', 'collections'
        ])

    def extract_notebook_code(self, notebook_content):
        """Extract code and markdown content from notebook"""
        try:
            notebook = nbformat.reads(notebook_content, as_version=4)
            code_content = []
            markdown_content = []
            imports = set()
            
            current_section = None
            section_content = []
            
            for cell in notebook.cells:
                # Markdown hücrelerini işle
                if cell.cell_type == "markdown":
                    markdown_text = cell.source.strip()
                    if markdown_text:
                        # Yeni bir bölüm başlığı mı kontrol et
                        header_match = re.match(r'^#+ (.+)', markdown_text)
                        if header_match:
                            # Önceki bölümü kaydet
                            if current_section and section_content:
                                markdown_content.append({
                                    'section': current_section,
                                    'content': '\n'.join(section_content)
                                })
                            # Yeni bölümü başlat
                            current_section = header_match.group(1).strip()
                            section_content = [markdown_text]
                        else:
                            if current_section:
                                section_content.append(markdown_text)
                            else:
                                markdown_content.append({
                                    'section': 'General',
                                    'content': markdown_text
                                })

                # Kod hücrelerini işle
                elif cell.cell_type == "code":
                    code_text = cell.source.strip()
                    if code_text:
                        # Import ifadelerini tespit et
                        imports.update(self._extract_imports(code_text))
                        
                        # Hücre çıktılarını kontrol et
                        outputs = []
                        if hasattr(cell, 'outputs'):
                            for output in cell.outputs:
                                if output.get('output_type') == 'error':
                                    # Hata varsa kaydet
                                    outputs.append({
                                        'type': 'error',
                                        'content': output.get('traceback', [''])[0]
                                    })
                                elif output.get('output_type') == 'stream':
                                    # Print çıktılarını kaydet
                                    outputs.append({
                                        'type': 'stream',
                                        'content': output.get('text', '')
                                    })
                        
                        code_content.append({
                            'code': code_text,
                            'outputs': outputs
                        })

            # Son bölümü ekle
            if current_section and section_content:
                markdown_content.append({
                    'section': current_section,
                    'content': '\n'.join(section_content)
                })

            # Markdown içeriğini analiz et
            documentation = self._analyze_markdown_content(markdown_content)
            
            return {
                'code': '\n\n'.join(cell['code'] for cell in code_content),
                'code_cells': code_content,
                'markdown_content': markdown_content,
                'documentation': documentation,
                'imports': list(imports),
                'has_errors': any(any(output['type'] == 'error' for output in cell['outputs']) 
                                for cell in code_content),
                'cell_count': {
                    'code': len(code_content),
                    'markdown': len(markdown_content)
                }
            }

        except Exception as e:
            raise Exception(f"Notebook içeriği işlenirken hata oluştu: {str(e)}")

    def _extract_imports(self, code):
        """Extract imported libraries from code"""
        imports = set()
        
        # import x pattern
        import_matches = re.findall(r'import\s+(\w+)', code)
        imports.update(import_matches)
        
        # from x import y pattern
        from_matches = re.findall(r'from\s+(\w+)\s+import', code)
        imports.update(from_matches)
        
        # Sadece bilinen kütüphaneleri döndür
        return {imp for imp in imports if imp in self.known_imports}

    def _analyze_markdown_content(self, markdown_cells):
        """Analyze markdown content for documentation"""
        documentation = {
            'project_description': '',
            'setup_instructions': '',
            'usage_examples': [],
            'parameters': [],
            'requirements': [],
            'notes': [],
            'references': []
        }

        for cell in markdown_cells:
            content = cell['content'].lower()
            original_content = cell['content']
            
            # Proje açıklaması
            if any(keyword in content for keyword in ['overview', 'introduction', 'description', 'about']):
                documentation['project_description'] = original_content
            
            # Kurulum talimatları
            elif any(keyword in content for keyword in ['setup', 'installation', 'getting started']):
                documentation['setup_instructions'] = original_content
            
            # Kullanım örnekleri
            elif any(keyword in content for keyword in ['usage', 'example', 'how to']):
                documentation['usage_examples'].append(original_content)
            
            # Parametreler
            elif any(keyword in content for keyword in ['parameter', 'argument', 'config']):
                documentation['parameters'].append(original_content)
            
            # Gereksinimler
            elif any(keyword in content for keyword in ['requirement', 'dependency', 'prerequisites']):
                documentation['requirements'].append(original_content)
            
            # Notlar
            elif any(keyword in content for keyword in ['note', 'warning', 'important', 'attention']):
                documentation['notes'].append(original_content)
            
            # Referanslar
            elif any(keyword in content for keyword in ['reference', 'citation', 'source']):
                documentation['references'].append(original_content)

        return documentation

    def get_code_summary(self, code_cells):
        """Generate a summary of the code content"""
        summary = {
            'total_lines': 0,
            'has_functions': False,
            'has_classes': False,
            'complexity_indicators': {
                'nested_loops': 0,
                'conditional_statements': 0,
                'function_definitions': 0,
                'class_definitions': 0
            }
        }

        for cell in code_cells:
            code = cell['code']
            # Satır sayısı
            summary['total_lines'] += len(code.split('\n'))
            
            # Fonksiyon ve sınıf kontrolü
            if 'def ' in code:
                summary['has_functions'] = True
                summary['complexity_indicators']['function_definitions'] += len(re.findall(r'\bdef\s+\w+', code))
            
            if 'class ' in code:
                summary['has_classes'] = True
                summary['complexity_indicators']['class_definitions'] += len(re.findall(r'\bclass\s+\w+', code))
            
            # Karmaşıklık göstergeleri
            summary['complexity_indicators']['nested_loops'] += len(re.findall(r'\bfor\b.*\bfor\b|\bwhile\b.*\bwhile\b', code))
            summary['complexity_indicators']['conditional_statements'] += len(re.findall(r'\bif\b|\belif\b|\belse\b', code))

        return summary

    def is_notebook_organized(self, markdown_cells, code_cells):
        """Check if the notebook is well-organized"""
        return {
            'has_introduction': any('introduction' in cell['content'].lower() for cell in markdown_cells),
            'has_sections': any(cell['section'] != 'General' for cell in markdown_cells),
            'has_documentation': len(markdown_cells) > 0,
            'code_markdown_ratio': len(code_cells) / (len(markdown_cells) + 1),  # +1 to avoid division by zero
            'avg_code_cell_length': sum(len(cell['code'].split('\n')) for cell in code_cells) / (len(code_cells) + 1)
        }