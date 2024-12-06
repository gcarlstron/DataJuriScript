import http.client
import json
import os
from datetime import datetime
from typing import Dict, Any
from urllib.parse import urlencode


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
            'criterio': f'processoId | igual a | {processo_id}'
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

        if int(processo_data.get('listSize')) < 1:
            raise Exception(f'processo {processo_id} não encontrado')
        # Busca dados do cliente
        client_id = processo_data.get('rows')[0]['clienteId']
        client_data = self.get_client(client_id)

        if int(client_data.get('listSize')) < 1:
            raise Exception(f'cliente {client_id} não encontrado')

        # Busca dados dos pedidos
        pedidos_data = self.get_pedidos_processo(processo_id)

        # Monta o template
        template = {
            "ProcessoId": processo_id,
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
                    "data_inicio": pedido.get('data_inicio_pedido', ''),
                    "data_final": pedido.get('data_final_pedido', ''),
                    "empresa": pedido.get('empresa', ''),
                    "funcao": pedido.get('funcao', ''),
                    "agentes_nocivos": [agente for agente in (pedido['agentes_nocivos'].split('<br/>'))],
                    "provas": pedido.get('provas_aposentadoria', '')
                }
                for pedido in (pedidos_data.get('rows', []))
            ],
            "tempo_total": processo_data.get('rows')[0]['tempo_total'],
            "rmi": processo_data.get('rows')[0]['rmi'],
            "data_atual": datetime.now().strftime('%Y-%m-%d'),
            "advogado": {
                "nome": os.getenv('DATA_JURI_SCRIPT:ADVOGADO'),
                "oab": os.getenv('DATA_JURI_SCRIPT:OAB')
            }
        }

        return template