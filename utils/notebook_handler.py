import nbformat

class NotebookHandler:
    @staticmethod
    def extract_notebook_code(notebook_content):
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