"""
🤖 FINBOT - Assistente Financeiro Pessoal
Seu primeiro sistema financeiro com IA!
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================
st.set_page_config(
    page_title="FinBot - Assistente Financeiro",
    page_icon="💰",
    layout="wide"
)

# ============================================
# BANCO DE Dstreamlit run app.pyADOS SIMPLES (depois migra pra SQLite)
# ============================================
if 'transactions' not in st.session_state:
    st.session_state.transactions = []

# ============================================
# INTERFACE
# ============================================
st.title("🤖 FinBot - Seu Assistente Financeiro")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("💰 Saldo Atual")
    
    # Calcula saldo
    entradas = sum(t['value'] for t in st.session_state.transactions if t['type'] == 'Entrada')
    saidas = sum(t['value'] for t in st.session_state.transactions if t['type'] == 'Saída')
    saldo = entradas - saidas
    
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Entradas", f"R$ {entradas:,.2f}")
    with col2:
        st.metric("Saídas", f"R$ {saidas:,.2f}")
    
    st.markdown("---")
    st.caption("💡 Adicione transações abaixo!")

# Área principal
tab1, tab2 = st.tabs(["📝 Adicionar", "📊 Dashboard"])

with tab1:
    st.subheader("📝 Nova Transação")
    
    col1, col2 = st.columns(2)
    
    with col1:
        description = st.text_input("Descrição", placeholder="Ex: Salário, Ifood, Uber...")
        value = st.number_input("Valor (R$)", min_value=0.01, value=50.00, step=10.0)
    
    with col2:
        trans_type = st.selectbox("Tipo", ["Entrada", "Saída"])
        
        # Categorias inteligentes
        categories = ["Salário", "Alimentação", "Transporte", "Moradia", 
                     "Lazer", "Saúde", "Educação", "Investimento", "Outros"]
        category = st.selectbox("Categoria", categories)
    
    if st.button("✅ Adicionar Transação", use_container_width=True):
        transaction = {
            'date': datetime.now(),
            'description': description,
            'value': value,
            'type': trans_type,
            'category': category
        }
        st.session_state.transactions.append(transaction)
        st.success(f"✅ {trans_type} de R$ {value:,.2f} adicionada!")
        st.balloons()

with tab2:
    st.subheader("📊 Seus Gastos")
    
    if st.session_state.transactions:
        df = pd.DataFrame(st.session_state.transactions)
        
        # Gráfico de gastos por categoria
        saidas_df = df[df['type'] == 'Saída']
        if not saidas_df.empty:
            gastos_por_categoria = saidas_df.groupby('category')['value'].sum()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Por Categoria")
                st.bar_chart(gastos_por_categoria)
            
            with col2:
                st.subheader("📋 Últimas Transações")
                st.dataframe(
                    df.tail(10)[['date', 'description', 'type', 'value', 'category']],
                    use_container_width=True
                )
    else:
        st.info("Nenhuma transação ainda. Adicione na aba 'Adicionar'!")

# Rodapé
st.markdown("---")
st.caption("🚀 FinBot v1.0 - Seu assistente financeiro pessoal")