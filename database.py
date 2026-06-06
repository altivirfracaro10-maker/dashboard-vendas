import streamlit as st
from supabase import create_client, Client

def get_client() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

def init_db():
    supabase = get_client()
    # Testa a conexão
    try:
        supabase.table("vendas").select("id").limit(1).execute()
    except Exception as e:
        st.error(f"Erro ao conectar ao Supabase: {e}")

def get_vendas():
    supabase = get_client()
    try:
        response = supabase.table("vendas").select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"Erro ao buscar vendas: {e}")
        return []

def add_venda(vendedor, produto, valor, data):
    supabase = get_client()
    try:
        supabase.table("vendas").insert({
            "vendedor": vendedor,
            "produto": produto,
            "valor": valor,
            "data": data
        }).execute()
    except Exception as e:
        st.error(f"Erro ao adicionar venda: {e}")

def get_vendedores():
    supabase = get_client()
    try:
        response = supabase.table("vendedores").select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"Erro ao buscar vendedores: {e}")
        return []

def add_vendedor(nome):
    supabase = get_client()
    try:
        supabase.table("vendedores").insert({
            "nome": nome
        }).execute()
    except Exception as e:
        st.error(f"Erro ao adicionar vendedor: {e}")
