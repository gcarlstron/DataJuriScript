import json
from dotenv import load_dotenv
from DataJuriAuthenticate import DataJuriAuthenticate
from DataJuriClient import DataJuriClient
from GenerateDocx import GenerateDocx
from FillTemplate import create_md_file


def process_document(process_id: str):
    # Configurações
    host = "api.datajuri.com.br"
    template_folder = '../template'
    documents_folder = '../documents'

    try:
        # Inicializa o cliente
        authenticate = DataJuriAuthenticate(host)
        client = DataJuriClient(host, authenticate.get_token())

        # Busca e preenche o template
        template_data = client.fill_template(str(process_id))
        document_name, table_data = create_md_file(f'{template_folder}/retirement-request-template.md', template_data)
        docx = GenerateDocx()
        result = docx.convert_markdown_to_docx(f'{document_name}',
                                      f'{documents_folder}/{document_name.replace(".md", ".docx")}', table_data)

        # Salva o resultado em um arquivo
        with open('../template/dados_template.json', 'w', encoding='utf-8') as f:
            json.dump(template_data, f, ensure_ascii=False, indent=2)

        return result

    except Exception as e:
        return f"Erro: {e}"


if __name__ == "__main__":
    load_dotenv()
    process_document("494157")
