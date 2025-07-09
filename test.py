import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

st.title("🕵️‍♂️ Juros Abusivo?")

linkedin_url = "https://www.linkedin.com/in/alessander-carvalho-454426212/"

# Caminho para a pasta com os arquivos
PASTA_DADOS = "DADOS"# Lista os arquivos JSON
arquivos_json = [f for f in os.listdir(PASTA_DADOS) if f.endswith(".json")]

# Cria uma lista apenas com os nomes "limpos" (sem .json)
nomes_exibidos = [os.path.splitext(f)[0] for f in arquivos_json]

# Cria um dicionário de mapeamento: Nome bonito → nome real
mapa_arquivos = dict(zip(nomes_exibidos, arquivos_json))

# Dropdown para seleção
nome_escolhido = st.selectbox("Selecione a modalidade", nomes_exibidos)

# Obtem o nome real do arquivo
arquivo_escolhido = mapa_arquivos[nome_escolhido]

if arquivo_escolhido:
    caminho_completo = os.path.join(PASTA_DADOS, arquivo_escolhido)

    try:
        with open(caminho_completo, "r", encoding="utf-8") as f:
            dados = json.load(f)

        # Criar o DataFrame e tratar colunas
        df = pd.DataFrame(dados)
        df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
        df["valor"] = df["valor"].str.replace(",", ".").astype(float)
        df = df.rename(columns={"data": "data_referencia", "valor": "taxa_media"})

        #st.dataframe(df.tail())

        # Entradas do usuário
        col1, col2 = st.columns(2)
        with col1:
            data_user = st.date_input("📅 Data do contrato", value=df["data_referencia"].max().date())
            st.write(f"🗓️ Data selecionada: **{data_user.strftime('%d/%m/%Y')}**")
        with col2:
            taxa_user = st.number_input("💸 Taxa contratada (% ao mês)", min_value=0.0, step=0.01)

        tolerancia_pct = st.number_input("Informe a tolerância sobre a taxa média (%)", min_value=0.0, value=150.0, step=1.0)
        fator = 1 + (tolerancia_pct / 100)  # Converte 50% para 1.5x

        if st.button("Verificar"):
            data_dt = pd.to_datetime(data_user)
            taxa_media = df[df["data_referencia"] == data_dt]

            if taxa_media.empty:
                st.warning("⚠️ Não há dados para a data selecionada.")
            else:
                taxa_ref = float(taxa_media["taxa_media"].values[0])
                limite = taxa_ref * fator

                st.markdown(f"""
                ### 📊 Resultado:
                - **Taxa média em {data_user.strftime('%m/%Y')}:** `{taxa_ref:.2f}%`
                - **Limite com tolerância de {tolerancia_pct:.2f}%:** `{limite:.2f}%`
                - **Taxa contratada informada:** `{taxa_user:.2f}%`
                """)

                if taxa_user > limite:
                    st.error("🚨 Possível indício de juros abusivos.")
                else:
                    st.success("✅ Dentro do padrão de mercado.")

        st.markdown(f"""
        <a href="{linkedin_url}" target="_blank">
            <button style="padding: 8px 16px; font-size: 16px; background-color: #0077b5; color: white; border: none; border-radius: 4px;">
                Solicite um cálculo completo via LinkedIn 
            </button>
        </a>
    """, unsafe_allow_html=True)


    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar o arquivo: {e}")