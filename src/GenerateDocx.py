import markdown
from bs4 import BeautifulSoup
from docx.shared import RGBColor
from docx import Document


class GenerateDocx:

    def add_table_docx(self, doc, table_data: dict[str, str]):
        for para in doc.paragraphs:
            if '[[ tabela ]]' in para.text:

                para.text = para.text.replace('[[ tabela ]]', '')
                tabela = doc.add_table(rows=len(table_data) + 1, cols=2)
                tabela.style = 'Table Grid'

                headers = ['Campo', 'Valor']
                for i, header in enumerate(headers):
                    tabela.cell(0, i).text = header

                for i, data_dict in enumerate(table_data):
                    for k, v in data_dict.items():
                        tabela.cell(i+1, 0).text = k
                        tabela.cell(i+1, 1).text = v

                tabela.add_row()
                break

    def convert_markdown_to_docx(self, markdown_file, output_file, dados_tabela, styles=None):

        with open(markdown_file, 'r', encoding='utf-8') as file:
            documento = file.read()

        doc = Document()
        html = markdown.markdown(documento)
        soup = BeautifulSoup(html, 'html.parser')

        for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol']):
            if element.name.startswith('h'):
                p = doc.add_paragraph(element.text)
                p.style = f'Heading {element.name[1]}'
            elif element.name == 'p':
                if '[[ tabela ]]' in element.text:
                    doc.add_paragraph(element.text)
                    self.add_table_docx(doc, dados_tabela)
                else:
                    for child in element.children:
                        p = doc.add_paragraph()
                        if isinstance(child, str):
                            run = p.add_run(child)
                        else:
                            run = p.add_run(child.text)
                            if child.name == 'strong':
                                run.bold = True
                            elif child.name == 'em':
                                run.italic = True
                            elif child.name == 'a':
                                run.font.color.rgb = RGBColor(0, 0, 255)
                                run.underline = True
            elif element.name in ['ul', 'ol']:
                for li in element.find_all('li'):
                    estilo = 'List Bullet' if element.name == 'ul' else 'List Number'
                    doc.add_paragraph(li.text, style=estilo)

        doc.save(output_file)
