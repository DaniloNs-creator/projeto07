import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

import subprocess  # Importando diretamente, pois faz parte da biblioteca padrão

# Atualizando o pip antes de qualquer outra instalação
subprocess.check_call(["python", '-m', 'pip', 'install', '--upgrade', 'pip'])

# Certifique-se de que o módulo matplotlib está instalado
try:
    import matplotlib
except ModuleNotFoundError:
    subprocess.check_call(["python", '-m', 'pip', 'install', 'matplotlib'])
    import matplotlib

# Certifique-se de que o módulo plotly está instalado
try:
    import plotly.graph_objects as go
except ModuleNotFoundError:
    subprocess.check_call(["python", '-m', 'pip', 'install', 'plotly'])
    import plotly.graph_objects as go



# Função para exportar os dados para um arquivo Excel, incluindo os enunciados
def exportar_para_excel_completo(respostas, perguntas_hierarquicas, categorias, valores):
    # Criando um DataFrame com as perguntas e respostas
    linhas = []
    for item, conteudo in perguntas_hierarquicas.items():
        for subitem, subpergunta in conteudo["subitens"].items():
            linhas.append({"Pergunta": subpergunta, "Resposta": respostas[subitem]})
    df_respostas = pd.DataFrame(linhas)

    # Criando um DataFrame com os valores do gráfico
    df_grafico = pd.DataFrame({'Categoria': categorias, 'Porcentagem': valores})

    # Salvando ambos em um arquivo Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Salvando as respostas em uma aba
        df_respostas.to_excel(writer, index=False, sheet_name='Respostas')

        # Salvando os dados do gráfico em outra aba
        df_grafico.to_excel(writer, index=False, sheet_name='Gráfico')

    return output.getvalue()

# Variável de controle para verificar se o usuário já preencheu a tela inicial
if "formulario_preenchido" not in st.session_state:
    st.session_state.formulario_preenchido = False

# Tela inicial para preencher informações do usuário
if not st.session_state.formulario_preenchido:
    st.title("MATRIZ DE MATURIDADE DE COMPLIANCE E PROCESSOS")
    st.subheader("Por favor, preencha suas informações antes de prosseguir")

    nome = st.text_input("Nome")
    email = st.text_input("E-mail")
    empresa = st.text_input("Empresa")
    telefone = st.text_input("Telefone")

    if st.button("Prosseguir"):
        if nome and email and empresa and telefone:  # Verifica se todos os campos foram preenchidos
            # Armazenando os dados na sessão
            st.session_state.nome = nome
            st.session_state.email = email
            st.session_state.empresa = empresa
            st.session_state.telefone = telefone
            st.session_state.formulario_preenchido = True
            st.success("Informações preenchidas com sucesso! Você pode prosseguir para o questionário.")
        else:
            st.error("Por favor, preencha todos os campos antes de prosseguir.")
else:
    # Tela de questionário
    st.title("Formulário com Itens Expansíveis e Gráfico de Radar")

    # Lendo as perguntas do arquivo CSV
    caminho_arquivo = "https://github.com/DaniloNs-creator/projeto01/raw/main/Pasta1.csv"
    try:
        perguntas_df = pd.read_csv(caminho_arquivo)

        # Verificando se a coluna 'classe' e 'pergunta' existem
        if not {'classe', 'pergunta'}.issubset(perguntas_df.columns):
            st.error("Certifique-se de que o arquivo CSV contém as colunas 'classe' e 'pergunta'.")
        else:
            # Organizando os dados em hierarquia
            perguntas_hierarquicas = {}
            respostas = {}

            for _, row in perguntas_df.iterrows():
                classe = str(row['classe'])
                pergunta = row['pergunta']

                # Identificando níveis de hierarquia
                if classe.endswith(".0"):  # Número inteiro como título
                    perguntas_hierarquicas[classe] = {"titulo": pergunta, "subitens": {}}
                else:  # Subitem com perguntas subordinadas
                    item_principal = classe.split(".")[0] + ".0"
                    if item_principal not in perguntas_hierarquicas:
                        perguntas_hierarquicas[item_principal] = {"titulo": "", "subitens": {}}
                    perguntas_hierarquicas[item_principal]["subitens"][classe] = pergunta

            # Exibindo os itens como expansores
            st.write("Por favor, responda às perguntas dentro de cada item:")
            for item, conteudo in perguntas_hierarquicas.items():
                with st.expander(f"{item} - {conteudo['titulo']}"):  # Bloco expansível para cada item
                    for subitem, subpergunta in conteudo["subitens"].items():
                        respostas[subitem] = st.number_input(f"{subitem} - {subpergunta}", min_value=0, max_value=5, step=1)

            # Botão para enviar os dados e gerar o gráfico
            if st.button("Enviar Dados e Gerar Gráfico"):
                st.write(f"Obrigado, {st.session_state.nome}!")
                st.write("Respostas enviadas com sucesso!")

                # Calculando os valores em porcentagem para o gráfico de radar
                categorias = []
                valores = []
                for item, conteudo in perguntas_hierarquicas.items():
                    soma_respostas = sum(respostas[subitem] for subitem in conteudo["subitens"].keys())
                    num_perguntas = len(conteudo["subitens"])
                    if num_perguntas > 0:
                        valor_percentual = (soma_respostas / (num_perguntas * 5)) * 100
                        categorias.append(conteudo["titulo"])
                        valores.append(valor_percentual)

                # Verificando se as listas têm o mesmo comprimento
                if len(categorias) != len(valores):
                    st.error("Erro: As listas de categorias e valores têm tamanhos diferentes.")
                else:
                    # Configurando o gráfico de radar
                    if categorias:
                        valores += valores[:1]  # Fechando o gráfico
                        categorias += categorias[:1]  # Fechando o gráfico

                        # Criando o gráfico usando Plotly
                        import plotly.graph_objects as go

                        fig = go.Figure()

                        fig.add_trace(go.Scatterpolar(
                            r=valores,
                            theta=categorias,
                            fill='toself'
                        ))

                        fig.update_layout(
                            polar=dict(
                                radialaxis=dict(
                                    visible=True,
                                    range=[0, 100]
                                )),
                            showlegend=False
                        )

                        st.plotly_chart(fig)

                        # Gerando o arquivo Excel para download
                        excel_data = exportar_para_excel_completo(respostas, perguntas_hierarquicas, categorias[:-1], valores[:-1])
                        st.download_button(
                            label="Exportar para Excel",
                            data=excel_data,
                            file_name="respostas_e_grafico.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        )

    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar o arquivo: {e}")
