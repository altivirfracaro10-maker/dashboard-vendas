import streamlit as st
from supabase import create_client, Client

def get_client() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

def init_db():
    supabase = get_client()
    try:
        supabase.table("vendas").select("id").limit(1).execute()
    except Exception as e:
        st.error(f"Erro ao conectar ao Supabase: {e}")

def get_vendas():
    supabase = get_client()
    try:
        response = supabase.table("vendas").select("*").order("data", desc=True).execute()
        return response.data
    except Exception as e:
        st.error(f"Erro ao buscar vendas: {e}")
        return []

def add_venda(data, cliente, vendedor, valor, marca_exclusiva, tipo_produto, margem):
    supabase = get_client()
    try:
        supabase.table("vendas").insert({
            "data": data,
            "cliente": cliente,
            "vendedor": vendedor,
            "valor": valor,
            "marca_exclusiva": marca_exclusiva,
            "tipo_produto": tipo_produto,
            "margem": margem
        }).execute()
    except Exception as e:
        st.error(f"Erro ao adicionar venda: {e}")

def delete_venda(id):
    supabase = get_client()
    try:
        supabase.table("vendas").delete().eq("id", id).execute()
    except Exception as e:
        st.error(f"Erro ao excluir venda: {e}")

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

