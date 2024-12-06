import http.client
import json
import locale
import os
from datetime import datetime
from typing import Dict, Any
from urllib.parse import urlencode


class DataJuriClient:
    def __init__(self, host: str, token: str):
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

    def format_date(self, date_str: str) -> str:
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

        data = datetime.strptime(date_str, '%Y-%m-%d')

        dia = data.strftime('%d')
        mes = data.strftime('%B').lower()
        ano = data.strftime('%Y')

        return f"{dia} de {mes} de {ano}"

    def get_process(self, process_id: str) -> Dict[str, Any]:
        """Busca dados do processo"""
        params = {
            'campos': 'tipoAcao,tempo_total,rmi,cliente.nome,advogadoCliente.nome,faseAtual.localidade',
            'criterio': f'id | igual a | {process_id}'
        }
        return self._make_request('/v1/entidades/Processo', params)

    def get_client(self, client_id: str) -> Dict[str, Any]:
        """Busca dados do cliente"""
        params = {
            'campos': 'nome,cpf,pis,dataNascimento,nomeMae',
            'criterio': f'id | igual a | {client_id}'
        }
        return self._make_request('/v1/entidades/PessoaFisica', params)

    def get_process_stage(self, processo_id: str) -> Dict[str, Any]:
        """Busca dados da fase do processo"""
        params = {
            'campos': 'faseAtual.localidade',
            'criterio': f'processo.id | igual a | {processo_id}'
        }
        return self._make_request('/v1/entidades/FaseProcesso', params)

    def get_process_request(self, processo_id: str) -> Dict[str, Any]:
        """Busca dados dos pedidos do processo"""
        params = {
            'campos': 'data_inicio_pedido,data_final_pedido,empresa,funcao,agentes_nocivos,provas',
            'criterio': f'processoId | igual a | {processo_id}'
        }
        return self._make_request('/v1/entidades/PedidoProcesso', params)

    def get_lawyer(self, advogado_id: str) -> Dict[str, Any]:
        """Busca dados do advogado"""
        params = {
            'campos': 'nome,nomeUsuario',
            'criterio': f'id | igual a | {advogado_id}'
        }
        return self._make_request('/v1/entidades/Usuario', params)

    def fill_template(self, process_id: str) -> Dict[str, Any]:

        # Busca dados do processo
        process_data = self.get_process(process_id)

        if int(process_data.get('listSize')) < 1:
            raise Exception(f'processo {process_id} não encontrado')
        # Busca dados do cliente
        client_id = process_data.get('rows')[0]['clienteId']
        client_data = self.get_client(client_id)

        if int(client_data.get('listSize')) < 1:
            raise Exception(f'cliente {client_id} não encontrado')

        # Busca dados dos pedidos
        requests_data = self.get_process_request(process_id)

        today = self.format_date(datetime.now().strftime('%Y-%m-%d'))
        # Monta o template
        template = {
            "ProcessoId": process_id,
            "localidade_fase_atual": process_data.get('rows')[0]['faseAtual.localidade'],
            "cliente": {
                "nome": client_data.get('rows')[0]['nome'],
                "cpf": client_data.get('rows')[0]['cpf'],
                "pis": client_data.get('rows')[0]['pis'],
                "data_nascimento": client_data.get('rows')[0]['dataNascimento'],
                "nome_mae": client_data.get('rows')[0]['nomeMae']
            },
            "tipo_acao": process_data.get('rows')[0]['tipoAcao'],
            "periodos_especiais": [
                {
                    "data_inicio": pedido.get('data_inicio_pedido', ''),
                    "data_final": pedido.get('data_final_pedido', ''),
                    "empresa": pedido.get('empresa', ''),
                    "funcao": pedido.get('funcao', ''),
                    "agentes_nocivos": [agente for agente in (pedido.get('agentes_nocivos', '').split('<br/>'))],
                    "provas": [provas for provas in (pedido.get('provas', '').split('<br/>'))]
                }
                for pedido in (requests_data.get('rows', []))
            ],
            "tempo_total": process_data.get('rows')[0]['tempo_total'],
            "rmi": process_data.get('rows')[0]['rmi'],
            "data_atual": today,
            "advogado": {
                "nome": os.getenv('DATA_JURI_SCRIPT:ADVOGADO'),
                "oab": os.getenv('DATA_JURI_SCRIPT:OAB')
            }
        }

        return template
