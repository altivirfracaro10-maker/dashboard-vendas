import streamlit as st
from database import (
    init_db, get_vendas, add_venda,
    get_vendedores, add_vendedor
)
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Vendas",
    page_icon="📊",
    layout="wide"
)

# Inicializa o banco
init_db()

st.title("📊 Dashboard de Vendas")

# Menu lateral
aba = st.sidebar.radio(
    "Menu",
    ["📊 Dashboard", "➕ Lançar Venda",
     "📋 Histórico", "👥 Vendedores"]
)

# ── ABA DASHBOARD ──────────────────────────
if aba == "📊 Dashboard":
    st.header("Resumo de Vendas")
    vendas = get_vendas()
    if not vendas:
        st.info("Nenhuma venda registrada ainda!")
    else:
        df = pd.DataFrame(vendas)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Vendas", len(df))
        with col2:
            total = df["valor"].sum()
            st.metric("Valor Total", f"R$ {total:,.2f}")
        with col3:
            media = df["valor"].mean()
            st.metric("Ticket Médio", f"R$ {media:,.2f}")
        fig = px.bar(
            df.groupby("vendedor")["valor"]
              .sum().reset_index(),
            x="vendedor", y="valor",
            title="Vendas por Vendedor",
            color="vendedor"
        )
        st.plotly_chart(fig, use_container_width=True)

# ── ABA LANÇAR VENDA ───────────────────────
elif aba == "➕ Lançar Venda":
    st.header("Lançar Nova Venda")
    vendedores = get_vendedores()
    if not vendedores:
        st.warning("Cadastre um vendedor primeiro!")
    else:
        nomes = [v["nome"] for v in vendedores]
        with st.form("form_venda"):
            vendedor = st.selectbox("Vendedor", nomes)
            produto  = st.text_input("Produto")
            valor    = st.number_input(
                "Valor (R$)", min_value=0.0, step=0.01
            )
            data = st.date_input(
                "Data", value=datetime.today()
            )
            submitted = st.form_submit_button("Salvar")
            if submitted:
                if produto and valor > 0:
                    add_venda(vendedor, produto,
                              valor, str(data))
                    st.success("✅ Venda registrada!")
                else:
                    st.error("Preencha todos os campos!")

# ── ABA HISTÓRICO ──────────────────────────
elif aba == "📋 Histórico":
    st.header("Histórico de Vendas")
    vendas = get_vendas()
    if not vendas:
        st.info("Nenhuma venda registrada ainda!")
    else:
        df = pd.DataFrame(vendas)
        st.dataframe(df, use_container_width=True)

# ── ABA VENDEDORES ─────────────────────────
elif aba == "👥 Vendedores":
    st.header("Gerenciar Vendedores")
    with st.form("form_vendedor"):
        nome = st.text_input("Nome do Vendedor")
        submitted = st.form_submit_button("Cadastrar")
        if submitted:
            if nome:
                add_vendedor(nome)
                st.success(f"✅ {nome} cadastrado!")
            else:
                st.error("Digite o nome!")
    st.subheader("Vendedores Cadastrados")
    vendedores = get_vendedores()
    if not vendedores:
        st.info("Nenhum vendedor cadastrado!")
    else:
        for v in vendedores:
            st.write(f"👤 {v['nome']}")
