import os

import streamlit as st
from dotenv import load_dotenv
from DataJuriAuthenticate import DataJuriAuthenticate
from DataJuriClient import DataJuriClient
from main import process_document
from datetime import datetime, timedelta, date


def load_processes(page: int, page_size: int, process_id: str = None,
                   client_name: str = None, start_date: str = None,
                   end_date: str = None) -> dict:
    host = "api.datajuri.com.br"
    authenticate = DataJuriAuthenticate(host)
    client = DataJuriClient(host, authenticate.get_token())

    params = {
        'campos': 'pasta,tipoAcao,cliente.nome,dataAbertura',
        'page': page,
        'pageSize': page_size
    }

    criterios = []
    if process_id:
        criterios.append(f"id | igual a | {process_id}")
    if client_name:
        criterios.append(f"cliente.nome | contém | {client_name}")
    if start_date:
        criterios.append(f"dataAbertura | maior ou igual | {start_date}")
    if end_date:
        criterios.append(f"dataAbertura | menor ou igual | {end_date}")

    if criterios:
        params['criterio'] = "\n".join(criterios)

    return client._make_request('/v1/entidades/Processo', params)


def main():
    today = datetime.today()
    MIN_DATE = date(1900, 1, 1)
    st.title("Requerimentos de Aposentadoria")

    # Filters
    col1, col2 = st.columns(2)
    with col1:
        process_id = st.text_input("ID do Processo")
        client_name = st.text_input("Nome do Cliente")

    with col2:
        start_date = st.date_input("Data Inicial",
                                   value=datetime.now() - timedelta(days=30), max_value=today, min_value=MIN_DATE)
        end_date = st.date_input("Data Final",
                                 value=datetime.now(), max_value=today, min_value=MIN_DATE)

    # Pagination controls
    page_size = 10
    if 'page' not in st.session_state:
        st.session_state.page = 1

    # Load processes with filters
    response = load_processes(
        st.session_state.page,
        page_size,
        process_id,
        client_name,
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )

    processes = response.get('rows', [])
    total_records = response.get('listSize', 0)
    total_pages = -(-total_records // page_size)  # Ceiling division

    # Process list
    process_options = []
    for process in processes:
        display_text = (f"{process.get('pasta', 'N/A')} - "
                        f"{process.get('tipoAcao', 'N/A')} - "
                        f"{process.get('cliente.nome', 'N/A')} - "
                        f"{process.get('dataAbertura', 'N/A')}")
        process_options.append({"text": display_text, "id": process.get('id')})

    # Display processes
    if process_options:
        st.write(f"Processos encontrados: {total_records}")
        selected_process = st.selectbox(
            "Selecione o processo:",
            options=range(len(process_options)),
            format_func=lambda x: process_options[x]["text"]
        )
        if st.button("Gerar Requerimento"):
            process_id = process_options[selected_process]["id"]
            result = process_document(process_id)

            # Se o documento foi gerado com sucesso
            if not result.startswith("Erro"):
                # Constrói o caminho do arquivo
                docx_path = result

                # Lê o arquivo
                with open(docx_path, "rb") as file:
                    btn = st.download_button(
                        label="Baixar Requerimento",
                        data=file,
                        file_name=result,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
            else:
                st.error(result)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← Anterior") and st.session_state.page > 0:
            st.session_state.page -= 1
            st.rerun()

    with col2:
        st.write(f"Página {st.session_state.page} de {total_pages}")

    with col3:
        if st.button("Próximo →") and st.session_state.page < total_pages:
            st.session_state.page += 1
            st.rerun()


if __name__ == "__main__":
    load_dotenv()
    main()
