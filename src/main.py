import json
from dotenv import load_dotenv
from src import GerarDocx as g
from src.DataJuriAuthenticate import DataJuriAuthenticate
from src.DataJuriClient import DataJuriClient
from src.GerarDocx import GerarDocx
from src.PreencherTemplate import arquivo_md



def main():
    # Configurações
    HOST = "api.datajuri.com.br"
    PROCESSO_ID = input("Digite o numero do processo: ")
    
    try:
        # Inicializa o cliente
        authenticate = DataJuriAuthenticate(HOST)
        client = DataJuriClient(HOST, authenticate.get_token())
        
        # Busca e preenche o template
        dados = client.preencher_template(PROCESSO_ID)
        documento, dados_tabela = arquivo_md('../template/retirement-request-template.md', dados)
        docx = GerarDocx()
        docx.convert_markdown_to_docx(f'{documento}', documento.replace(".md", ".docx"), dados_tabela)
        
        # Salva o resultado em um arquivo
        with open('../template/dados_template.json', 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
            
        print("Template preenchido com sucesso!")
        print("\nDados obtidos:")
        print(json.dumps(dados, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"Erro: {e}")


if __name__ == "__main__":
    load_dotenv()
    main()
