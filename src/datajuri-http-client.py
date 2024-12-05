import http.client
import json
from datetime import datetime
from urllib.parse import urlencode
from typing import Dict, Any, Optional


class DataJuriClient:
    def __init__(self, host: str, token: str):
        """
        Inicializa o cliente com host e token
        
        Args:
            host: Hostname da API (ex: 'api.datajuri.com.br')
            token: Token de autenticação
        """
        self.host = host
        self.token = token
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, path: str, params: Dict[str, str]) -> Dict:
        """Faz uma requisição GET para a API"""
        conn = http.client.HTTPSConnection(self.host)
        
        # Monta a query string
        query = urlencode(params)
        full_path = f"{path}?{query}"
        
        try:
            conn.request('GET', full_path, headers=self.headers)
            response = conn.getresponse()
            data = response.read().decode()
            
            if response.status != 200:
                raise Exception(f"Erro na API: {response.status} - {data}")
                
            return json.loads(data)
        finally:
            conn.close()
    
    def get_processo(self, processo_id: str) -> Dict[str, Any]:
        """Busca dados do processo"""
        params = {
            'campos': 'tipoAcao,tempo_total,rmi,cliente.nome,advogadoCliente.nome,faseAtual.localidade',
            'criterio': f'id | igual a | {processo_id}'
        }
        return self._make_request('/v1/entidades/Processo', params)

    def get_client(self, client_id: str) -> Dict[str, Any]:
        """Busca dados do cliente"""
        params = {
            'campos': 'nome,cpf,pis,dataNascimento,nomeMae',
            'criterio': f'id | igual a | {client_id}'
        }
        return self._make_request('/v1/entidades/PessoaFisica', params)

    def get_fase_processo(self, processo_id: str) -> Dict[str, Any]:
        """Busca dados da fase do processo"""
        params = {
            'campos': 'faseAtual.localidade',
            'criterio': f'processo.id | igual a | {processo_id}'
        }
        return self._make_request('/v1/entidades/FaseProcesso', params)
    
    def get_pedidos_processo(self, processo_id: str) -> Dict[str, Any]:
        """Busca dados dos pedidos do processo"""
        params = {
            'campos': 'data_inicio_pedido,data_final_pedido,empresa,funcao,agentes_nocivos,provas_aposentadoria',
            'criterio': f'processo.id | igual a | {processo_id}'
        }
        return self._make_request('/v1/entidades/PedidoProcesso', params)

    def get_advogado(self, advogado_id: str) -> Dict[str, Any]:
        """Busca dados do advogado"""
        params = {
            'campos': 'nome,nomeUsuario',
            'criterio': f'id | igual a | {advogado_id}'
        }
        return self._make_request('/v1/entidades/Usuario', params)

    def preencher_template(self, processo_id: str) -> Dict[str, Any]:

        # Busca dados do processo
        processo_data = self.get_processo(processo_id)

        # Busca dados do cliente
        client_id = processo_data['rows'][0]['clienteId']
        client_data = self.get_client(client_id)
        
        # Busca dados dos pedidos
        pedidos_data = self.get_pedidos_processo(processo_id)

        # Monta o template
        template = {
            "localidade_fase_atual": processo_data.get('rows')[0]['faseAtual.localidade'],
            "cliente": {
                "nome": client_data.get('rows')[0]['nome'],
                "cpf": client_data.get('rows')[0]['cpf'],
                "pis": client_data.get('rows')[0]['pis'],
                "data_nascimento": client_data.get('rows')[0]['dataNascimento'],
                "nome_mae": client_data.get('rows')[0]['nomeMae']
            },
            "tipo_acao": processo_data.get('rows')[0]['tipoAcao'],
            "periodos_especiais": [
                {
                    "data_inicio": pedido['data_inicio_pedido'],
                    "data_final": pedido['data_final_pedido'],
                    "empresa": pedido['empresa'],
                    "funcao": pedido['funcao'],
                    "agentes_nocivos": pedido['agentes_nocivos'],
                    "provas": pedido['provas_aposentadoria']
                }
                for pedido in (pedidos_data.get('rows') if pedidos_data.get('rows') else [])
            ],
            "tempo_total": processo_data.get('rows')[0]['tempo_total'],
            "rmi": processo_data.get('rows')[0]['rmi'],
            "data_atual": datetime.now().strftime('%Y-%m-%d'),
            "advogado": {
                "nome": processo_data.get('rows')[0]['advogadoCliente.nome'],
                "oab": "Oab/rs 72.493"
            }
        }
        
        return template


def main():
    # Configurações
    HOST = "api.datajuri.com.br"
    TOKEN = input("Digite o token: ")
    PROCESSO_ID = input("Digite o numero do processo")  # ID do processo que você quer buscar
    
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
