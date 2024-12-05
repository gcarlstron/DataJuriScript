import json
from src.DataJuriClient import DataJuriClient


def main():
    # Configurações
    HOST = "api.datajuri.com.br"
    TOKEN = input("Digite o token: ")
    PROCESSO_ID = input("Digite o numero do processo: ")
    
    try:
        # Inicializa o cliente
        client = DataJuriClient(HOST, TOKEN)
        
        # Busca e preenche o template
        template = client.preencher_template(PROCESSO_ID)
        
        # Salva o resultado em um arquivo
        with open('../template/template_preenchido.json', 'w', encoding='utf-8') as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
            
        print("Template preenchido com sucesso!")
        print("\nDados obtidos:")
        print(json.dumps(template, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"Erro ao preencher template: {e}")

if __name__ == "__main__":
    main()
