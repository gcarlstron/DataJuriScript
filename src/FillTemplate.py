from datetime import datetime
from typing import Any


def create_md_file(documento: str, dados: dict[str, Any]):
    with open(documento, 'r', encoding='utf-8') as file:
        template = file.read()

    replacements = {
        '[localidade_fase_atual]': dados['localidade_fase_atual'],
        '[cliente]': dados['cliente']['nome'],
        '[CPF]': dados['cliente']['cpf'],
        '[PIS]': dados['cliente']['pis'] or '[não informado]',
        '[data_nascimento]': dados['cliente']['data_nascimento'],
        '[nome_mae]': dados['cliente']['nome_mae'] or '[não informado]',
        '[tipo_acao]': dados['tipo_acao'],
        '[tempo_total]': dados['tempo_total'],
        '[RMI]': f"R$ {dados['rmi']}",
        '[data_atual]': dados['data_atual'],
        '[advogado_cliente]': dados['advogado']['nome'],
        '[oab_advogado_cliente]': dados['advogado']['oab']
    }

    content = template
    for key, value in replacements.items():
        content = content.replace(key, str(value))

    tables = ""
    data_table = []
    for period in dados['periodos_especiais']:
        tables += "[[ tabela ]]\n\n"
        period['agentes_nocivos'] = ", ".join(period['agentes_nocivos'])
        data_table.append(period)

    content = content.replace(
        "| Campo | Valor |\n"
        "|-------|-------|\n"
        "| **Período:** | De [data_inicio] a [data_fim] |\n"
        "| **Empresa:** | [empresa] |\n| **Função:** | [funcao] |\n"
        "| **Agentes nocivos:** | [agentes_nocivos] |\n"
        "| **Provas pré-constituídas:** | [provas] |\n\n",
        tables)

    # Generate filename with current date
    today = datetime.now().strftime('%Y-%m-%d')
    filename = f'retirement-request-template_{today}.md'

    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f'Document saved as: {filename}')

    return filename, data_table
