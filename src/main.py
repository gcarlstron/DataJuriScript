import json
from dotenv import load_dotenv
from src.DataJuriAuthenticate import DataJuriAuthenticate
from src.DataJuriClient import DataJuriClient
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
        documento = arquivo_md('../template/retirement-request-template.md', dados)
        
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
