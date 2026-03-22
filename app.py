import streamlit as st
import pandas as pd
import numpy as np

# Configuração da Página
st.set_page_config(page_title="Calculadora de Estatística Agrupada", layout="wide")

st.title("📊 Estatística Descritiva: Dados Agrupados")
st.markdown("""
Esta ferramenta calcula medidas de tendência central e dispersão para dados organizados em **classes (intervalos)**.
""")

# --- ESTADO DA SESSÃO ---
# Inicializa a lista de dados se não existir
if 'df_dados' not in st.session_state:
    st.session_state.df_dados = pd.DataFrame(columns=['Limite Inferior', 'Limite Superior', 'Frequência'])

# --- SIDEBAR: ENTRADA DE DADOS ---
with st.sidebar:
    st.header("Entrada de Dados")
    with st.form("add_data", clear_on_submit=True):
        col1, col2 = st.columns(2)
        li = col1.number_input("Limite Inferior", format="%.2f")
        ls = col2.number_input("Limite Superior", format="%.2f")
        fi = st.number_input("Frequência (fi)", min_value=1, step=1)
        
        submitted = st.form_submit_button("Adicionar Classe")
        
        if submitted:
            if ls <= li:
                st.error("O limite superior deve ser maior que o inferior.")
            else:
                novo_dado = pd.DataFrame([[li, ls, fi]], columns=['Limite Inferior', 'Limite Superior', 'Frequência'])
                st.session_state.df_dados = pd.concat([st.session_state.df_dados, novo_dado], ignore_index=True)

    if st.button("Limpar Tudo"):
        st.session_state.df_dados = pd.DataFrame(columns=['Limite Inferior', 'Limite Superior', 'Frequência'])
        st.rerun()

# --- CORPO PRINCIPAL ---
if not st.session_state.df_dados.empty:
    df = st.session_state.df_dados.copy()
    
    # 1. Cálculos de Base
    df['Ponto Médio (xi)'] = (df['Limite Inferior'] + df['Limite Superior']) / 2
    df['fi * xi'] = df['Frequência'] * df['Ponto Médio (xi)']
    df['Frequência Acumulada (Fi)'] = df['Frequência'].cumsum()
    
    n = df['Frequência'].sum()
    h = df.iloc[0]['Limite Superior'] - df.iloc[0]['Limite Inferior'] # Amplitude da classe
    
    st.subheader("Tabela de Distribuição")
    st.dataframe(df, use_container_width=True)

    # --- PROCESSAMENTO MATEMÁTICO ---
    
    # MÉDIA: Σ(fi * xi) / n
    media = df['fi * xi'].sum() / n
    
    # MEDIANA: Li + [((n/2) - Fant) / fi] * h
    me_pos = n / 2
    idx_mediana = df[df['Frequência Acumulada (Fi)'] >= me_pos].index[0]
    classe_mediana = df.iloc[idx_mediana]
    fant = df.iloc[idx_mediana-1]['Frequência Acumulada (Fi)'] if idx_mediana > 0 else 0
    mediana = classe_mediana['Limite Inferior'] + ((me_pos - fant) / classe_mediana['Frequência']) * h
    
    # MODA (Czuber): Li + [(fi - fi_ant) / ((fi - fi_ant) + (fi - fi_post))] * h
    idx_moda = df['Frequência'].idxmax()
    classe_moda = df.iloc[idx_moda]
    fi_atual = classe_moda['Frequência']
    fi_ant = df.iloc[idx_moda-1]['Frequência'] if idx_moda > 0 else 0
    fi_post = df.iloc[idx_moda+1]['Frequência'] if idx_moda < len(df)-1 else 0
    
    # Prevenção de divisão por zero se todas as frequências forem iguais
    denominador_moda = (fi_atual - fi_ant) + (fi_atual - fi_post)
    moda = classe_moda['Limite Inferior'] + ((fi_atual - fi_ant) / denominador_moda) * h if denominador_moda != 0 else classe_moda['Ponto Médio (xi)']

    # VARIÂNCIA: Σ [fi * (xi - media)²] / (n - 1)
    df['fi * (xi-media)^2'] = df['Frequência'] * ((df['Ponto Médio (xi)'] - media)**2)
    variancia = df['fi * (xi-media)^2'].sum() / (n - 1)
    desvio_padrao = np.sqrt(variancia)
    erro_padrao = desvio_padrao / np.sqrt(n)

    # --- EXIBIÇÃO DOS RESULTADOS ---
    st.divider()
    st.subheader("Resultados Estatísticos")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Média (x̄)", f"{media:.4f}")
    m2.metric("Mediana (Md)", f"{mediana:.4f}")
    m3.metric("Moda (Mo)", f"{moda:.4f}")
    
    d1, d2, d3 = st.columns(3)
    d1.metric("Variância (s²)", f"{variancia:.4f}")
    d2.metric("Desvio Padrão (s)", f"{desvio_padrao:.4f}")
    d3.metric("Erro Padrão", f"{erro_padrao:.4f}")

    # Visualização opcional
    st.bar_chart(df.set_index('Ponto Médio (xi)')['Frequência'])

else:
    st.info("Aguardando inserção de dados na barra lateral para calcular...")