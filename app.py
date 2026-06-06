import streamlit as st
from database import (
    init_db, get_vendas, add_venda,
    get_vendedores, add_vendedor
)
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="Dashboard de Vendas",
    page_icon="📊",
    layout="wide"
)

init_db()

st.title("📊 Dashboard de Vendas")

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
        df["valor"] = pd.to_numeric(df["valor"])
        df["margem"] = pd.to_numeric(df["margem"])
        df["margem_valor"] = df["valor"] * df["margem"] / 100

        # ── Métricas ──
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Vendas", len(df))
        with col2:
            st.metric("Valor Total", f"R$ {df['valor'].sum():,.2f}")
        with col3:
            st.metric("Ticket Médio", f"R$ {df['valor'].mean():,.2f}")
        with col4:
            st.metric("Margem Total", f"R$ {df['margem_valor'].sum():,.2f}")

        st.divider()

        # ── Registro de Vendas Recentes ──
        st.subheader("Registro de Vendas Recentes")
        df_display = df[[
            "data", "cliente", "valor", "vendedor",
            "marca_exclusiva", "tipo_produto", "margem"
        ]].copy()
        df_display.columns = [
            "Data", "Nome da Loja", "Valor Total", "Vendedor",
            "Marca Exclusiva", "Genérico/Similar", "Margem (%)"
        ]
        df_display["Marca Exclusiva"] = df_display["Marca Exclusiva"].map(
            {True: "Sim", False: "Não"}
        )
        df_display["Margem (%)"] = df_display["Margem (%)"].apply(
            lambda x: f"{x:.0f}%"
        )
        st.dataframe(df_display, use_container_width=True)

        st.divider()

        # ── Agrupamento por Tipo de Produto ──
        st.subheader("Agrupamento por Tipo de Produto e Margem")

        grupo = df.groupby("tipo_produto").agg(
            valor_total=("valor", "sum"),
            margem_media=("margem", "mean"),
            margem_total=("margem_valor", "sum")
        ).reset_index()

        grupo.columns = [
            "Grupo de Produto", "Valor Total",
            "Margem (%)", "Margem Total"
        ]
        grupo["Margem (%)"] = grupo["Margem (%)"].apply(
            lambda x: f"{x:.2f}%"
        )
        st.dataframe(grupo, use_container_width=True)

        st.divider()

        # ── Gráficos ──
        col1, col2 = st.columns(2)
        with col1:
            fig1 = px.bar(
                df.groupby("vendedor")["valor"].sum().reset_index(),
                x="vendedor", y="valor",
                title="Vendas por Vendedor",
                color="vendedor"
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = px.pie(
                df.groupby("tipo_produto")["valor"].sum().reset_index(),
                values="valor", names="tipo_produto",
                title="Vendas por Tipo de Produto"
            )
            st.plotly_chart(fig2, use_container_width=True)

        # ── Gráfico por Loja ──
        st.subheader("Vendas por Loja")
        fig3 = px.bar(
            df.groupby("cliente")["valor"].sum().reset_index(),
            x="cliente", y="valor",
            title="Vendas por Nome da Loja",
            color="cliente",
            labels={"cliente": "Nome da Loja", "valor": "Valor Total"}
        )
        st.plotly_chart(fig3, use_container_width=True)

# ── ABA LANÇAR VENDA ───────────────────────
elif aba == "➕ Lançar Venda":
    st.header("Lançar Nova Venda")
    vendedores = get_vendedores()

    if not vendedores:
        st.warning("Cadastre um vendedor primeiro!")
    else:
        nomes = [v["nome"] for v in vendedores]

        with st.form("form_venda"):
            col1, col2 = st.columns(2)
            with col1:
                data = st.date_input("Data", value=datetime.today())
                # ← ALTERADO: selectbox com as lojas
                cliente = st.selectbox(
                    "Nome da Loja",
                    ["Xavier", "Campo Largo"]
                )
                vendedor = st.selectbox("Vendedor", nomes)
            with col2:
                valor = st.number_input(
                    "Valor Total (R$)", min_value=0.0, step=0.01
                )
                tipo_produto = st.selectbox(
                    "Tipo de Produto",
                    ["Genérico e Similares", "Marca Exclusiva"]
                )
                marca_exclusiva = tipo_produto == "Marca Exclusiva"
                margem = st.number_input(
                    "Margem (%)", min_value=0.0,
                    max_value=100.0, step=0.5
                )

            submitted = st.form_submit_button("💾 Salvar Venda")
            if submitted:
                if valor > 0:
                    add_venda(
                        str(data), cliente, vendedor,
                        valor, marca_exclusiva,
                        tipo_produto, margem
                    )
                    st.success("✅ Venda registrada com sucesso!")
                    st.rerun()
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

        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            lojas = ["Todas"] + list(df["cliente"].unique())
            loja_filtro = st.selectbox("Filtrar por Loja", lojas)
        with col2:
            vendedores_lista = ["Todos"] + list(df["vendedor"].unique())
            vendedor_filtro = st.selectbox("Filtrar por Vendedor", vendedores_lista)

        if loja_filtro != "Todas":
            df = df[df["cliente"] == loja_filtro]
        if vendedor_filtro != "Todos":
            df = df[df["vendedor"] == vendedor_filtro]

        df_display = df.copy()
        df_display = df_display.rename(columns={"cliente": "Nome da Loja"})
        st.dataframe(df_display, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Baixar CSV",
            csv,
            "vendas.csv",
            "text/csv"
        )

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
                st.rerun()
            else:
                st.error("Digite o nome!")

    st.subheader("Vendedores Cadastrados")
    vendedores = get_vendedores()
    if not vendedores:
        st.info("Nenhum vendedor cadastrado!")
    else:
        for v in vendedores:
            st.write(f"👤 {v['nome']}")
