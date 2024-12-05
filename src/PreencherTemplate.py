from datetime import datetime
from typing import Any


def arquivo_md(documento: str, dados: dict[str, Any]):
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

    periods_text = ""
    for period in dados['periodos_especiais']:
        periods_text += "| Campo | Valor |\n"
        periods_text += "|-------|-------|\n"
        periods_text += f"|**Período:** De| {period['data_inicio']} a {period['data_final']}|\n"
        periods_text += f"|**Empresa:**| {period['empresa']}|\n"
        periods_text += f"|**Função:**| {period['funcao']}|\n"
        periods_text += f"|**Agentes nocivos:**| {', '.join(filter(None, period['agentes_nocivos']))}|\n\n"

    content = content.replace(
        "| Campo | Valor |\n"
        "|-------|-------|\n"
        "| **Período:** | De [data_inicio] a [data_fim] |\n"
        "| **Empresa:** | [empresa] |\n| **Função:** | [funcao] |\n"
        "| **Agentes nocivos:** | [agentes_nocivos] |\n"
        "| **Provas pré-constituídas:** | [provas] |\n\n",
        periods_text)

    # Generate filename with current date
    today = datetime.now().strftime('%Y-%m-%d')
    filename = f'retirement-request-template_{today}.md'

    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f'Document saved as: {filename}')

    return filename
