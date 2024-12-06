import json
from dotenv import load_dotenv
from src.DataJuriAuthenticate import DataJuriAuthenticate
from src.DataJuriClient import DataJuriClient
from src.GenerateDocx import GenerateDocx
from src.FillTemplate import create_md_file



def main():
    # Configurações
    host = "api.datajuri.com.br"
    process_id = input("Digite o numero do processo: ")
    template_folder = '../template'
    documents_folder = '../documents'
    
    try:
        # Inicializa o cliente
        authenticate = DataJuriAuthenticate(host)
        client = DataJuriClient(host, authenticate.get_token())
        
        # Busca e preenche o template
        template_data = client.fill_template(process_id)
        document_name, table_data = create_md_file(f'{template_folder}/retirement-request-template.md', template_data)
        docx = GenerateDocx()
        docx.convert_markdown_to_docx(f'{document_name}',
                                      f'{documents_folder}/{document_name.replace(".md", ".docx")}', table_data)
        
        # Salva o resultado em um arquivo
        with open('../template/dados_template.json', 'w', encoding='utf-8') as f:
            json.dump(template_data, f, ensure_ascii=False, indent=2)
            
        print("Template preenchido com sucesso!")
        print("\nDados obtidos:")
        print(json.dumps(template_data, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"Erro: {e}")


if __name__ == "__main__":
    load_dotenv()
    main()
