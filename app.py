import streamlit as st
import pandas as pd
import numpy as np

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Estatística UNDB - Dados Agrupados", layout="wide")

st.title("📊 Estatística Descritiva: Dados Agrupados")

# --- ESTADO DA SESSÃO ---
if 'df_dados' not in st.session_state:
    st.session_state.df_dados = pd.DataFrame(columns=['Intervalo', 'Li', 'Ls', 'fi'])

# --- SIDEBAR: ENTRADA DE DADOS ---
with st.sidebar:
    st.header("📥 Entrada de Dados")
    with st.form("add_data", clear_on_submit=True):
        st.write("Configurar Intervalo:")
        c_esq, c_dir = st.columns(2)
        s_esq = c_esq.selectbox("Início", options=["[ (Fechado)", "] (Aberto)"])
        s_dir = c_dir.selectbox("Fim", options=["[ (Fechado)", "] (Aberto)"])
        
        col1, col2 = st.columns(2)
        li = col1.number_input("Limite Inferior", format="%.2f")
        ls = col2.number_input("Limite Superior", format="%.2f")
        fi = st.number_input("Frequência Absoluta (fi)", min_value=1, step=1)
        
        if st.form_submit_button("Adicionar Classe"):
            if ls <= li:
                st.error("O limite superior deve ser maior que o inferior.")
            else:
                # CORREÇÃO DO BUG DE FECHADO (Simbologia Apostila pág. 11)
                is_fechado_esq = "[" in s_esq
                is_fechado_dir = "[" in s_dir
                
                if is_fechado_esq and is_fechado_dir:
                    simbolo = "|-|" # Fechado nos dois lados
                elif is_fechado_esq and not is_fechado_dir:
                    simbolo = "├"   # Fechado à esquerda, aberto à direita
                else:
                    simbolo = "—"   # Caso genérico
                
                txt_int = f"{li:.2f} {simbolo} {ls:.2f}"
                novo = pd.DataFrame([[txt_int, li, ls, fi]], columns=['Intervalo', 'Li', 'Ls', 'fi'])
                st.session_state.df_dados = pd.concat([st.session_state.df_dados, novo], ignore_index=True)

    if st.button("🗑️ Limpar Tudo"):
        st.session_state.df_dados = pd.DataFrame(columns=['Intervalo', 'Li', 'Ls', 'fi'])
        st.rerun()

# --- PROCESSAMENTO E CÁLCULOS ---
if not st.session_state.df_dados.empty:
    df = st.session_state.df_dados.copy()
    
    n = df['fi'].sum()
    df['xi'] = (df['Li'] + df['Ls']) / 2 
    df['Fac'] = df['fi'].cumsum() 
    df['fr (%)'] = (df['fi'] / n) * 100 
    df['fi_xi'] = df['fi'] * df['xi'] 
    
    # Amplitude (h) baseada na primeira classe
    h = df.iloc[0]['Ls'] - df.iloc[0]['Li']

    # MÉDIA (pág. 14)
    media = df['fi_xi'].sum() / n
    
    # MEDIANA (pág. 18)
    pos_me = n / 2
    idx_me = df[df['Fac'] >= pos_me].index[0]
    fant = df.iloc[idx_me-1]['Fac'] if idx_me > 0 else 0
    mediana = df.iloc[idx_me]['Li'] + (((pos_me - fant) * h) / df.iloc[idx_me]['fi'])
    
    # MODA (Fórmula de Czuber - pág. 20)
    idx_mo = df['fi'].idxmax()
    f_mo = df.iloc[idx_mo]['fi']
    f_ant = df.iloc[idx_mo-1]['fi'] if idx_mo > 0 else 0
    f_pos = df.iloc[idx_mo+1]['fi'] if idx_mo < len(df)-1 else 0
    delta1 = f_mo - f_ant 
    delta2 = f_mo - f_pos 
    moda = df.iloc[idx_mo]['Li'] + (delta1 * h) / (delta1 + delta2) if (delta1 + delta2) != 0 else df.iloc[idx_mo]['xi']

    # VARIÂNCIA AMOSTRAL (S² - pág. 23)
    if n > 1:
        df['xi2_fi'] = (df['xi']**2) * df['fi']
        soma_xi_fi = df['fi_xi'].sum()
        soma_xi2_fi = df['xi2_fi'].sum()
        variancia = (1/(n-1)) * (soma_xi2_fi - (soma_xi_fi**2 / n))
        desvio = np.sqrt(variancia)
        erro = desvio / np.sqrt(n)
    else:
        variancia = desvio = erro = 0.0

    # --- EXIBIÇÃO ---
    st.subheader("📋 Tabela de Distribuição de Frequências")
    df_view = df[['Intervalo', 'fi', 'xi', 'Fac', 'fr (%)']].copy()
    df_view.rename(columns={'fi': 'fi', 'xi': 'xi (Ponto Médio)', 'Fac': 'Fac (Acumulada)', 'fr (%)': 'fr (%) (Relativa)'}, inplace=True)
    df_view['fr (%) (Relativa)'] = df_view['fr (%) (Relativa)'].map("{:.2f}%".format)
    st.table(df_view)

    st.subheader("📊 Resultados Estatísticos")
    c1, c2, c3 = st.columns(3)
    c1.metric("Média (x̄)", f"{media:.4f}")
    c2.metric("Mediana (Md)", f"{mediana:.4f}")
    c3.metric("Moda (Mo)", f"{moda:.4f}")
    
    c4, c5, c6 = st.columns(3)
    c4.metric("Variância (s²)", f"{variancia:.4f}")
    c5.metric("Desvio Padrão (s)", f"{desvio:.4f}")
    c6.metric("Erro Padrão", f"{erro:.4f}")
    
    if n <= 1:
        st.warning("Variância e Desvio Padrão requerem n > 1.")

else:
    st.info("ℹ️ Adicione as classes na barra lateral para iniciar os cálculos.")

# --- SEÇÃO DE FÓRMULAS OCULTA ---
st.divider()
with st.expander("📝 Mostrar Fórmulas e Memorial de Cálculo"):
    st.subheader("📚 Referências Matemáticas")
    f_col1, f_col2 = st.columns(2)
    
    with f_col1:
        st.markdown("**1. Média Aritmética**")
        st.latex(r"\bar{x} = \frac{\sum (x_i \cdot f_i)}{n}")
        st.markdown("**2. Mediana**")
        st.latex(r"Md = l_{Md} + \frac{(\frac{n}{2} - FAC_{ant}) \cdot h}{F_{Md}}")
        st.markdown("**3. Moda (Fórmula de Czuber)**")
        st.latex(r"Mo = l_{Mo} + \frac{\Delta_1 \cdot h}{\Delta_1 + \Delta_2}")

    with f_col2:
        st.markdown("**4. Variância Amostral (S²)**")
        st.latex(r"S^2 = \frac{1}{n-1} \left[ \sum x_i^2 f_i - \frac{(\sum x_i f_i)^2}{n} \right]")
        st.markdown("**5. Desvio Padrão**")
        st.latex(r"S = \sqrt{S^2}")
        st.markdown("**6. Erro Padrão**")
        st.latex(r"EP = \frac{S}{\sqrt{n}}")