import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from fpdf import FPDF
import base64
import io
import sqlite3
import json

# Tentar importar APIs de IA (opcionais)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

st.set_page_config(page_title="FinBot", page_icon="🤖", layout="wide")

# ============ TRADUÇÕES COMPLETAS ============
TEXT = {
    "pt": {
        "title": "FinBot", "subtitle": "Seu assistente financeiro inteligente",
        "income": "Receitas", "expenses": "Despesas", "balance": "Saldo",
        "transactions": "transações", "positive": "Disponível", "negative": "Negativo",
        "new_transaction": "Nova transação", "type": "Tipo",
        "type_income": "Receita", "type_expense": "Despesa",
        "description": "Descrição", "desc_placeholder": "Ex: Salário, Aluguel, Ifood...",
        "amount": "Valor", "date": "Data", "category": "Categoria",
        "categories": ["Salário", "Alimentação", "Transporte", "Moradia", "Lazer", "Saúde", "Educação", "Investimento", "Outros"],
        "add_button": "Adicionar transação", "delete": "Excluir",
        "recent_activity": "Atividade recente", "no_transactions": "Nenhuma transação ainda",
        "tab_dashboard": "Painel", "tab_add": "Adicionar", "tab_history": "Histórico",
        "tab_budgets": "Orçamentos", "tab_goals": "Metas", "tab_insights": "Insights",
        "tab_export": "Exportar",
        "spending_breakdown": "Para onde vai seu dinheiro",
        "no_expenses": "Nenhuma despesa registrada",
        "summary": "Resumo do período", "of_income_spent": "da receita gasta",
        "on_track": "Você está no controle", "watch_out": "Fique atento",
        "over_budget": "Orçamento estourado", "total_transactions": "Total de transações",
        "largest_expense": "Maior despesa", "top_category": "Categoria principal",
        "average_expense": "Despesa média", "daily_average": "Média diária (30 dias)",
        "trend": "Tendência (7 dias)", "no_data": "Sem dados suficientes",
        "add_to_see": "Adicione transações para visualizar", "footer": "FinBot",
        "choose_language": "Escolha o idioma", "portuguese": "Português", "english": "English",
        "currency_symbol": "R$", "fill_all": "Preencha todos os campos",
        "budget_title": "Definir Orçamentos", "budget_desc": "Estabeleça limites de gastos por categoria.",
        "set_budget": "Definir limite", "current_spending": "Gasto atual", "remaining": "Restante",
        "exceeded": "Estourado!", "save_budgets": "Salvar orçamentos",
        "goal_title": "Metas Financeiras", "goal_desc": "Defina um objetivo de economia e acompanhe seu progresso.",
        "goal_amount": "Valor da meta", "goal_deadline": "Prazo final", "goal_current": "Economizado até agora",
        "goal_progress": "Progresso", "goal_set": "Definir meta", "goal_reset": "Limpar meta",
        "insights_title": "Análise Inteligente", "insights_desc": "Recomendações baseadas nos seus hábitos financeiros.",
        "insight_top_category": "Sua maior categoria de gasto é",
        "insight_spending_increase": "Seus gastos aumentaram",
        "insight_budget_warning": "Você já usou mais de 80% do orçamento de",
        "insight_frequency": "Você teve muitas transações este mês. Que tal revisar os pequenos gastos?",
        "insight_general": "Continue acompanhando seus gastos para manter o controle.",
        "export_title": "Exportar Relatório PDF",
        "export_pdf_pt": "Baixar PDF (Português)", "export_pdf_en": "Baixar PDF (English)",
        "pdf_balance": "Saldo", "pdf_income": "Receitas totais", "pdf_expense": "Despesas totais",
        "pdf_recent_transactions": "Últimas transações", "pdf_generated": "Gerado por FinBot",
        "chat_title": "Consultor IA", "chat_placeholder": "Digite sua dúvida...",
        "login_title": "Entrar no FinBot", "login_user": "Usuário", "login_pass": "Senha",
        "login_btn": "Entrar", "login_error": "Usuário ou senha inválidos.",
        "register_btn": "Criar conta", "register_success": "Conta criada! Faça login.",
        "username_taken": "Nome de usuário já existe.",
        "no_budgets": "Nenhum orçamento definido.",
        "clear_budgets": "Limpar todos os orçamentos",
        "category_select": "Categoria",
        "budget_added": "Limite para {cat} definido!",
        "goal_set_success": "Meta definida!",
        "clear_chat_history": "Limpar histórico do chat",
        "chat_model_label": "Modelo",
        "gemini_key_label": "Chave Gemini",
        "openai_key_label": "Chave OpenAI",
        "logout": "Sair",
    },
    "en": {
        "title": "FinBot", "subtitle": "Your intelligent financial assistant",
        "income": "Income", "expenses": "Expenses", "balance": "Balance",
        "transactions": "transactions", "positive": "Available", "negative": "Overdrawn",
        "new_transaction": "New transaction", "type": "Type",
        "type_income": "Income", "type_expense": "Expense",
        "description": "Description", "desc_placeholder": "e.g., Salary, Rent, Food...",
        "amount": "Amount", "date": "Date", "category": "Category",
        "categories": ["Salary", "Food", "Transport", "Housing", "Leisure", "Health", "Education", "Investment", "Other"],
        "add_button": "Add transaction", "delete": "Delete",
        "recent_activity": "Recent activity", "no_transactions": "No transactions yet",
        "tab_dashboard": "Dashboard", "tab_add": "Add", "tab_history": "History",
        "tab_budgets": "Budgets", "tab_goals": "Goals", "tab_insights": "Insights",
        "tab_export": "Export",
        "spending_breakdown": "Where your money goes",
        "no_expenses": "No expenses recorded",
        "summary": "Period summary", "of_income_spent": "of income spent",
        "on_track": "You're on track", "watch_out": "Keep an eye",
        "over_budget": "Over budget", "total_transactions": "Total transactions",
        "largest_expense": "Largest expense", "top_category": "Top category",
        "average_expense": "Average expense", "daily_average": "Daily average (30d)",
        "trend": "Trend (7 days)", "no_data": "Not enough data",
        "add_to_see": "Add transactions to see", "footer": "FinBot",
        "choose_language": "Choose language", "portuguese": "Português", "english": "English",
        "currency_symbol": "$", "fill_all": "Please fill all fields",
        "budget_title": "Set Budgets", "budget_desc": "Define spending limits per category.",
        "set_budget": "Set limit", "current_spending": "Current spending", "remaining": "Remaining",
        "exceeded": "Exceeded!", "save_budgets": "Save budgets",
        "goal_title": "Financial Goals", "goal_desc": "Set a savings goal and track your progress.",
        "goal_amount": "Goal amount", "goal_deadline": "Deadline", "goal_current": "Saved so far",
        "goal_progress": "Progress", "goal_set": "Set goal", "goal_reset": "Clear goal",
        "insights_title": "Smart Insights", "insights_desc": "Recommendations based on your spending habits.",
        "insight_top_category": "Your top spending category is",
        "insight_spending_increase": "Your spending increased by",
        "insight_budget_warning": "You've used over 80% of the budget for",
        "insight_frequency": "You've had many transactions this month. Consider reviewing small expenses.",
        "insight_general": "Keep tracking your spending to stay in control.",
        "export_title": "Export PDF Report",
        "export_pdf_pt": "Download PDF (Português)", "export_pdf_en": "Download PDF (English)",
        "pdf_balance": "Balance", "pdf_income": "Total Income", "pdf_expense": "Total Expenses",
        "pdf_recent_transactions": "Recent Transactions", "pdf_generated": "Generated by FinBot",
        "chat_title": "AI Advisor", "chat_placeholder": "Type your question...",
        "login_title": "Login to FinBot", "login_user": "User", "login_pass": "Password",
        "login_btn": "Login", "login_error": "Invalid user or password.",
        "register_btn": "Sign up", "register_success": "Account created! Please login.",
        "username_taken": "Username already taken.",
        "no_budgets": "No budgets defined.",
        "clear_budgets": "Clear all budgets",
        "category_select": "Category",
        "budget_added": "Budget for {cat} set!",
        "goal_set_success": "Goal set!",
        "clear_chat_history": "Clear chat history",
        "chat_model_label": "Model",
        "gemini_key_label": "Gemini Key",
        "openai_key_label": "OpenAI Key",
        "logout": "Logout",
    }
}

# ============ BANCO DE DADOS SQLITE ============
DB_FILE = "finbot.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS data (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    conn.commit()
    conn.close()

def save_data(key, value):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("REPLACE INTO data (key, value) VALUES (?, ?)", (key, json.dumps(value)))
    conn.commit()
    conn.close()

def load_data(key, default=None):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT value FROM data WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return default

def save_all():
    save_data("transactions", st.session_state.transactions)
    save_data("budgets", st.session_state.budgets)
    save_data("goal", st.session_state.goal)
    save_data("chat_history", st.session_state.chat_history)

def load_all():
    if 'db_loaded' not in st.session_state:
        init_db()
        st.session_state.transactions = load_data("transactions", [])
        st.session_state.budgets = load_data("budgets", {})
        st.session_state.goal = load_data("goal", None)
        st.session_state.chat_history = load_data("chat_history", [])
        st.session_state.db_loaded = True

# ============ ESTADO DA SESSÃO ============
if 'lang' not in st.session_state:
    st.session_state.lang = None
if 'users' not in st.session_state:
    st.session_state.users = {"admin": "admin"}
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# Carrega dados salvos
load_all()

# Inicializa estado se não existir
if 'chat_model' not in st.session_state:
    st.session_state.chat_model = "Offline"
if 'show_chat' not in st.session_state:
    st.session_state.show_chat = False

# ============ TELA DE ESCOLHA DE IDIOMA ============
if st.session_state.lang is None:
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        * { font-family: 'Inter', sans-serif; }
        .stApp { background: #0a0a0a; }
        .welcome-container {
            display: flex; flex-direction: column; align-items: center;
            justify-content: center; min-height: 70vh; color: white;
        }
        .robot-logo-large { font-size: 80px; margin-bottom: 1.5rem; }
        .welcome-title { font-size: 2rem; font-weight: 600; margin-bottom: 2rem; }
    </style>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="welcome-container">
        <div class="robot-logo-large">🤖</div>
        <div class="welcome-title">Bem-vindo ao FinBot</div>
        <p style="opacity: 0.7;">Escolha o idioma / Choose language</p>
    </div>
    """, unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🇧🇷 Português", use_container_width=True):
            st.session_state.lang = "pt"
            st.rerun()
    with c2:
        if st.button("🇺🇸 English", use_container_width=True):
            st.session_state.lang = "en"
            st.rerun()
    st.stop()

# ============ TELA DE LOGIN / REGISTRO ============
if not st.session_state.logged_in:
    st.markdown("""
    <style>
        .stApp { background: #0a0a0a; }
        .login-container { max-width: 400px; margin: 10% auto; padding: 2rem; background: #1c1c1e; border-radius: 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.3); }
        h2 { color: #f5f5f7; text-align: center; }
    </style>
    """, unsafe_allow_html=True)
    with st.container():
        st.markdown(f"<h2>🤖 {TEXT[st.session_state.lang]['login_title']}</h2>", unsafe_allow_html=True)
        tab_login, tab_register = st.tabs(["Login", "Registrar"])
        with tab_login:
            user = st.text_input(TEXT[st.session_state.lang]['login_user'])
            password = st.text_input(TEXT[st.session_state.lang]['login_pass'], type="password")
            if st.button(TEXT[st.session_state.lang]['login_btn'], use_container_width=True):
                if st.session_state.users.get(user) == password:
                    st.session_state.logged_in = True
                    st.session_state.current_user = user
                    st.rerun()
                else:
                    st.error(TEXT[st.session_state.lang]['login_error'])
        with tab_register:
            new_user = st.text_input(TEXT[st.session_state.lang]['login_user'], key="reg_user")
            new_pass = st.text_input(TEXT[st.session_state.lang]['login_pass'], type="password", key="reg_pass")
            if st.button(TEXT[st.session_state.lang]['register_btn'], use_container_width=True):
                if new_user in st.session_state.users:
                    st.warning(TEXT[st.session_state.lang]['username_taken'])
                elif new_user and new_pass:
                    st.session_state.users[new_user] = new_pass
                    st.success(TEXT[st.session_state.lang]['register_success'])
                else:
                    st.warning(TEXT[st.session_state.lang]['fill_all'])
    st.stop()

# ============ CSS TEMA ESCURO + CHAT MINIMALISTA ============
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;450;500;600;700&display=swap');
    * {{{{ font-family: 'Inter', sans-serif; }}}}
    header[data-testid="stHeader"] {{{{ display: none !important; }}}}
    div[data-testid="stToolbar"] {{{{ display: none !important; }}}}
    div[data-testid="stDecoration"] {{{{ display: none !important; }}}}
    #MainMenu {{{{ display: none !important; }}}}
    footer {{{{ display: none !important; }}}}
    .stApp {{{{ background: #0a0a0a; }}}}
    .block-container {{{{ padding: 2rem 3rem; max-width: 1200px; }}}}
    
    .logo-area {{{{ display: flex; align-items: center; gap: 0.75rem; margin-bottom: 2rem; }}}}
    .robot-logo {{{{ font-size: 36px; line-height: 1; }}}}
    h1 {{{{ font-weight: 700 !important; color: #f5f5f7 !important; font-size: 2rem !important; }}}}
    .subtitle {{{{ color: #86868b; font-size: 0.9rem; }}}}
    
    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes pulse {{
        0% {{ transform: scale(1); }}
        50% {{ transform: scale(1.02); }}
        100% {{ transform: scale(1); }}
    }}
    @keyframes slideInRight {{
        from {{ transform: translateX(100px); opacity: 0; }}
        to {{ transform: translateX(0); opacity: 1; }}
    }}
    .animate-in {{{{ animation: fadeInUp 0.5s ease forwards; }}}}
    .animate-pulse {{{{ animation: pulse 2s infinite; }}}}
    
    .metric-card {{
        background: linear-gradient(135deg, #1c1c1e 0%, #2c2c2e 100%);
        padding: 1.8rem 1.5rem;
        border-radius: 24px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        animation: fadeInUp 0.5s ease;
        transition: transform 0.2s;
        position: relative;
        overflow: hidden;
    }}
    .metric-card:hover {{
        transform: translateY(-4px);
    }}
    .metric-card::before {{
        content: '';
        position: absolute;
        top: -30px;
        right: -30px;
        width: 80px;
        height: 80px;
        border-radius: 50%;
        opacity: 0.1;
    }}
    .metric-card.income::before {{ background: #30d158; }}
    .metric-card.expense::before {{ background: #ff453a; }}
    .metric-card.balance::before {{ background: #667eea; }}
    .metric-icon {{ font-size: 2rem; margin-bottom: 0.5rem; }}
    .metric-label {{ text-transform: uppercase; letter-spacing: 1px; font-size: 0.75rem; font-weight: 500; color: #86868b; margin-bottom: 0.4rem; }}
    .metric-value {{ font-size: 2rem; font-weight: 700; color: #f5f5f7; line-height: 1.2; }}
    .metric-sub {{ color: #6d6d72; font-size: 0.8rem; margin-top: 0.3rem; }}
    
    .content-card {{
        background: #1c1c1e; padding: 2rem; border-radius: 20px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2); animation: fadeInUp 0.5s ease; transition: transform 0.2s;
    }}
    .content-card:hover {{ transform: translateY(-2px); }}
    .card-title {{ color: #f5f5f7; font-size: 1rem; font-weight: 600; margin-bottom: 1.5rem; }}
    
    .tx-row {{
        display: flex; align-items: center; justify-content: space-between;
        padding: 0.85rem 0; border-bottom: 1px solid #2c2c2e; transition: background 0.2s;
    }}
    .tx-row:hover {{ background: rgba(255,255,255,0.02); }}
    .tx-img {{
        width: 42px; height: 42px; border-radius: 12px; background: #2c2c2e;
        display: flex; align-items: center; justify-content: center; font-size: 1.5rem; flex-shrink: 0;
    }}
    .tx-name {{ color: #f5f5f7; font-weight: 500; }}
    .tx-cat {{ color: #86868b; font-size: 0.78rem; }}
    .tx-amount {{ font-weight: 550; text-align: right; transition: transform 0.2s; }}
    .tx-amount.income {{ color: #30d158; }}
    .tx-amount.expense {{ color: #ff453a; }}
    .tx-date {{ color: #6d6d72; font-size: 0.72rem; text-align: right; }}
    
    .stButton > button {{
        background: #f5f5f7; color: #0a0a0a; border: none; border-radius: 14px;
        padding: 0.8rem 1.8rem; font-size: 0.9rem; font-weight: 550;
        width: 100%; cursor: pointer; transition: all 0.2s;
    }}
    .stButton > button:hover {{ background: #e5e5ea; transform: scale(1.02); box-shadow: 0 6px 20px rgba(0,0,0,0.2); }}
    
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div,
    .stDateInput > div > div > input {{
        background: #2c2c2e; border: 1px solid #3a3a3c; color: #f5f5f7;
        border-radius: 12px; padding: 0.7rem 0.9rem; font-size: 0.88rem; transition: border 0.2s;
    }}
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div:focus,
    .stDateInput > div > div > input:focus {{
        border-color: #667eea; box-shadow: 0 0 0 3px rgba(102,126,234,0.2);
    }}
    .stSelectbox > div {{ color: #f5f5f7; }}
    div[data-baseweb="select"] svg {{ color: #f5f5f7; }}
    
    .stTabs [data-baseweb="tab-list"] {{ border-bottom: 1px solid #2c2c2e; gap: 0; }}
    .stTabs [data-baseweb="tab"] {{
        padding: 0.7rem 1.5rem; font-size: 0.9rem; color: #86868b;
        background: transparent; border: none; transition: color 0.2s;
    }}
    .stTabs [data-baseweb="tab"]:hover {{ color: #f5f5f7; }}
    .stTabs [aria-selected="true"] {{ color: #f5f5f7; border-bottom: 2px solid #667eea; }}
    
    .budget-card {{
        background: #1c1c1e; padding: 1.5rem; border-radius: 16px; margin-bottom: 1rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.2); animation: fadeInUp 0.5s ease; transition: transform 0.2s;
    }}
    .budget-card:hover {{ transform: translateY(-2px); }}
    .budget-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }}
    .budget-category {{ font-weight: 600; color: #f5f5f7; font-size: 1rem; }}
    .progress-bar-container {{
        width: 100%; height: 8px; background: #2c2c2e; border-radius: 4px; overflow: hidden; margin-top: 0.5rem;
    }}
    .progress-bar-fill {{ height: 100%; border-radius: 4px; transition: width 0.6s ease; }}
    
    .chat-fab {{
        position: fixed; bottom: 30px; right: 30px; width: 56px; height: 56px; border-radius: 28px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        box-shadow: 0 8px 25px rgba(102,126,234,0.4); display: flex; align-items: center; justify-content: center;
        font-size: 24px; color: white; cursor: pointer; z-index: 9999; border: none;
        transition: transform 0.3s, box-shadow 0.3s;
    }}
    .chat-fab:hover {{ transform: scale(1.08); box-shadow: 0 12px 30px rgba(102,126,234,0.6); }}
    .chat-popup {{
        position: fixed; bottom: 100px; right: 30px; width: 320px; height: 420px;
        background: #1c1c1e; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        z-index: 9998; display: none; flex-direction: column; overflow: hidden;
        border: 1px solid #2c2c2e; animation: slideInRight 0.3s ease;
    }}
    .chat-header {{
        padding: 0.8rem 1rem; background: #2c2c2e; display: flex;
        justify-content: space-between; align-items: center; color: #f5f5f7; font-weight: 600; font-size: 0.9rem;
    }}
    .chat-body {{ flex: 1; overflow-y: auto; padding: 0.8rem; display: flex; flex-direction: column; gap: 0.6rem; }}
    .message-bubble {{
        max-width: 85%; padding: 0.6rem 0.9rem; border-radius: 16px; font-size: 0.82rem; line-height: 1.4; word-wrap: break-word;
    }}
    .user-msg {{ align-self: flex-end; background: #667eea; color: white; border-bottom-right-radius: 4px; }}
    .bot-msg {{ align-self: flex-start; background: #2c2c2e; color: #f5f5f7; border-bottom-left-radius: 4px; }}
    .chat-input-container {{ padding: 0.6rem; background: #2c2c2e; display: flex; gap: 0.4rem; }}
    .chat-input-container input {{
        flex: 1; background: #3a3a3c; border: none; border-radius: 20px; padding: 0.5rem 0.9rem;
        color: white; font-size: 0.82rem; outline: none;
    }}
    .chat-input-container button {{
        background: #667eea; border: none; border-radius: 50%; width: 32px; height: 32px;
        color: white; font-size: 1rem; cursor: pointer; transition: background 0.2s;
    }}
    .chat-input-container button:hover {{ background: #5a6fd6; }}
    
    [data-testid="stSidebar"] {{ background: #1c1c1e; }}
    [data-testid="stSidebar"] h3 {{ color: #f5f5f7; }}
</style>
""".replace("{{{{", "{").replace("}}}}", "}"), unsafe_allow_html=True)

# ============ FUNÇÕES AUXILIARES ============
def t(key):
    return TEXT[st.session_state.lang][key]

income_total = sum(tx['value'] for tx in st.session_state.transactions if tx['type'] == 'income')
expense_total = sum(tx['value'] for tx in st.session_state.transactions if tx['type'] == 'expense')
balance = income_total - expense_total
sym = t("currency_symbol")

def generate_insights():
    if not st.session_state.transactions:
        return []
    df = pd.DataFrame(st.session_state.transactions)
    expense_df = df[df['type'] == 'expense']
    insights = []
    if expense_df.empty:
        insights.append(t("insight_general"))
        return insights
    top_cat = expense_df.groupby('category')['value'].sum().idxmax()
    insights.append(f"{t('insight_top_category')} **{top_cat}**.")
    now = datetime.now()
    this_month = now.month
    prev_month = this_month - 1 if this_month > 1 else 12
    this_month_exp = expense_df[expense_df['date'].dt.month == this_month]['value'].sum()
    prev_month_exp = expense_df[expense_df['date'].dt.month == prev_month]['value'].sum()
    if prev_month_exp > 0 and this_month_exp > prev_month_exp:
        diff = ((this_month_exp - prev_month_exp) / prev_month_exp) * 100
        insights.append(f"{t('insight_spending_increase')} **{diff:.1f}%**.")
    for cat, limit in st.session_state.budgets.items():
        spent = expense_df[expense_df['category'] == cat]['value'].sum()
        if limit > 0 and spent > limit * 0.8:
            insights.append(f"{t('insight_budget_warning')} **{cat}**.")
    if len(expense_df) > 10:
        insights.append(t("insight_frequency"))
    return insights[:5]

def export_pdf(lang):
    if not st.session_state.transactions:
        return None
    sym_lang = TEXT[lang]["currency_symbol"]
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(0, 10, txt="FinBot - Relatório Financeiro" if lang == "pt" else "FinBot - Financial Report", ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 8, txt=f"{TEXT[lang]['pdf_balance']}: {sym_lang} {balance:,.2f}", ln=True)
    pdf.cell(0, 8, txt=f"{TEXT[lang]['pdf_income']}: {sym_lang} {income_total:,.2f}", ln=True)
    pdf.cell(0, 8, txt=f"{TEXT[lang]['pdf_expense']}: {sym_lang} {expense_total:,.2f}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(0, 10, txt=TEXT[lang]["pdf_recent_transactions"], ln=True)
    pdf.set_font("Arial", size=9)
    col_widths = [30, 50, 30, 30, 30]
    header = [TEXT[lang]["date"], TEXT[lang]["description"], TEXT[lang]["type"], TEXT[lang]["category"], TEXT[lang]["amount"]]
    for i, h in enumerate(header):
        pdf.cell(col_widths[i], 7, txt=h, border=1)
    pdf.ln()
    for tx in sorted(st.session_state.transactions, key=lambda x: x['date'], reverse=True)[:20]:
        date_str = tx['date'].strftime('%d/%m/%Y') if lang == "pt" else tx['date'].strftime('%Y-%m-%d')
        tipo = "Receita" if tx['type'] == 'income' else "Despesa" if lang == "pt" else "Income" if tx['type'] == 'income' else "Expense"
        val_str = f"{tx['value']:.2f}"
        pdf.cell(col_widths[0], 6, txt=date_str, border=1)
        pdf.cell(col_widths[1], 6, txt=tx['description'][:25], border=1)
        pdf.cell(col_widths[2], 6, txt=tipo, border=1)
        pdf.cell(col_widths[3], 6, txt=tx['category'][:15], border=1)
        pdf.cell(col_widths[4], 6, txt=val_str, border=1)
        pdf.ln()
    pdf.ln(10)
    pdf.set_font("Arial", size=8)
    pdf.cell(0, 10, txt=TEXT[lang]["pdf_generated"], ln=True, align='C')
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    b64 = base64.b64encode(pdf_bytes).decode()
    label = TEXT[lang]["export_pdf_pt"] if lang == "pt" else TEXT[lang]["export_pdf_en"]
    return f'<a href="data:application/pdf;base64,{b64}" download="finbot_{lang}.pdf" style="color: #f5f5f7; text-decoration: none; background: #2c2c2e; padding: 0.5rem 1rem; border-radius: 8px;">📥 {label}</a>'

def offline_chat_response(prompt):
    df = pd.DataFrame(st.session_state.transactions) if st.session_state.transactions else pd.DataFrame()
    expense_df = df[df['type'] == 'expense'] if not df.empty else pd.DataFrame()
    context = f"Saldo atual: {sym} {balance:,.2f}. "
    if not expense_df.empty:
        top_cat = expense_df.groupby('category')['value'].sum().idxmax()
        context += f"Maior gasto: {top_cat}. "
    if st.session_state.goal:
        goal = st.session_state.goal
        saved = balance if balance > 0 else 0
        progress = min(saved / goal['amount'] * 100, 100) if goal['amount'] > 0 else 0
        context += f"Meta: {sym} {goal['amount']:,.2f} ({progress:.1f}%). "
    p = prompt.lower()
    if any(w in p for w in ["saldo", "balance", "quanto tenho"]):
        return f"Seu saldo é {sym} {balance:,.2f}. " + ("Positivo!" if balance >= 0 else "Negativo. Cuidado!")
    if any(w in p for w in ["gasto", "despesa", "gastei", "spent"]):
        if expense_df.empty:
            return "Sem despesas registradas."
        top = expense_df.groupby('category')['value'].sum().idxmax()
        total = expense_df['value'].sum()
        return f"Total gasto: {sym} {total:,.2f}. Maior gasto: {top}."
    if any(w in p for w in ["economizar", "save", "poupar"]):
        if expense_df.empty:
            return "Registre despesas para eu sugerir economia."
        top = expense_df.groupby('category')['value'].sum().idxmax()
        return f"Reduza gastos com {top}. Pequenas economias fazem diferença!"
    if any(w in p for w in ["investir", "invest", "renda"]):
        return "Invista em renda fixa (Tesouro Direto, CDB). Mantenha reserva de emergência de 6 meses."
    if any(w in p for w in ["orçamento", "budget"]):
        if not st.session_state.budgets:
            return "Defina orçamentos na aba Orçamentos."
        msg = "Orçamentos:\n"
        for cat, limit in st.session_state.budgets.items():
            spent = expense_df[expense_df['category'] == cat]['value'].sum() if not expense_df.empty else 0
            pct = (spent / limit) * 100 if limit > 0 else 0
            msg += f"- {cat}: {sym} {spent:,.2f} de {sym} {limit:,.2f} ({pct:.0f}%)\n"
        return msg
    if any(w in p for w in ["meta", "goal"]):
        if not st.session_state.goal:
            return "Nenhuma meta definida. Vá em Metas."
        goal = st.session_state.goal
        saved = balance if balance > 0 else 0
        progress = min(saved / goal['amount'] * 100, 100) if goal['amount'] > 0 else 0
        days_left = max((goal['deadline'] - datetime.now().date()).days, 0)
        return f"Meta: {sym} {goal['amount']:,.2f}. Progresso: {progress:.1f}%. {days_left} dias restantes."
    return f"{context}\nPergunte sobre saldo, gastos, economia, investimentos, orçamentos ou metas!"

# ============ INTERFACE PRINCIPAL ============
col_logo, col_controls = st.columns([4, 1])
with col_logo:
    st.markdown(f"""
    <div class="logo-area">
        <div class="robot-logo">🤖</div>
        <div>
            <h1>{t('title')}</h1>
            <div class="subtitle">{t('subtitle')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_controls:
    st.markdown('<div class="top-controls">', unsafe_allow_html=True)
    lang_options = ["Português", "English"]
    new_lang = st.selectbox("", lang_options, index=0 if st.session_state.lang == "pt" else 1, label_visibility="collapsed", key="lang_select")
    if (new_lang == "Português" and st.session_state.lang != "pt"):
        st.session_state.lang = "pt"
        st.rerun()
    elif (new_lang == "English" and st.session_state.lang != "en"):
        st.session_state.lang = "en"
        st.rerun()
    if st.button("🚪", help=t("logout")):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ============ CARDS DE MÉTRICAS ============
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"""
    <div class="metric-card income animate-in">
        <div class="metric-icon">💰</div>
        <div class="metric-label">{t('income')}</div>
        <div class="metric-value">{sym} {income_total:,.2f}</div>
        <div class="metric-sub">{len([tx for tx in st.session_state.transactions if tx['type']=='income'])} {t('transactions')}</div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="metric-card expense animate-in">
        <div class="metric-icon">💸</div>
        <div class="metric-label">{t('expenses')}</div>
        <div class="metric-value">{sym} {expense_total:,.2f}</div>
        <div class="metric-sub">{len([tx for tx in st.session_state.transactions if tx['type']=='expense'])} {t('transactions')}</div>
    </div>
    """, unsafe_allow_html=True)
with c3:
    bal_color = "#30d158" if balance >= 0 else "#ff453a"
    st.markdown(f"""
    <div class="metric-card balance animate-in">
        <div class="metric-icon">📊</div>
        <div class="metric-label">{t('balance')}</div>
        <div class="metric-value" style="color: {bal_color};">{sym} {balance:,.2f}</div>
        <div class="metric-sub">{t('positive') if balance >= 0 else t('negative')}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============ ABAS ============
tab_add, tab_dash, tab_budgets, tab_goals, tab_insights, tab_export, tab_hist = st.tabs([
    t("tab_add"), t("tab_dashboard"), t("tab_budgets"), t("tab_goals"),
    t("tab_insights"), t("tab_export"), t("tab_history")
])

# ---------- ABA ADICIONAR ----------
with tab_add:
    col_form, _ = st.columns([1, 1])
    with col_form:
        st.markdown(f'<p class="card-title">{t("new_transaction")}</p>', unsafe_allow_html=True)
        trans_type_label = st.selectbox(t("type"), [t("type_income"), t("type_expense")])
        type_code = "income" if trans_type_label == t("type_income") else "expense"
        description = st.text_input(t("description"), placeholder=t("desc_placeholder"))
        c_val, c_date = st.columns(2)
        with c_val:
            value = st.number_input(t("amount"), min_value=0.01, value=50.00, step=10.0, format="%.2f")
        with c_date:
            date = st.date_input(t("date"), value=datetime.now().date())
        category = st.selectbox(t("category"), t("categories"))
        if st.button(t("add_button"), use_container_width=True):
            if description and value > 0:
                st.session_state.transactions.append({
                    'date': datetime.combine(date, datetime.min.time()),
                    'description': description,
                    'value': value,
                    'type': type_code,
                    'category': category
                })
                save_all()
                st.success("Adicionado!" if st.session_state.lang == 'pt' else "Added!")
                st.rerun()
            else:
                st.warning(t("fill_all"))

# ---------- ABA PAINEL ----------
with tab_dash:
    if st.session_state.transactions:
        df = pd.DataFrame(st.session_state.transactions)
        expense_df = df[df['type'] == 'expense'].copy()
        if not expense_df.empty:
            cat_data = expense_df.groupby('category')['value'].sum().sort_values(ascending=True)
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                y=cat_data.index, x=cat_data.values, orientation='h',
                marker=dict(color='#f5f5f7', cornerradius=6, line=dict(width=0)),
                text=[f'{sym} {v:,.0f}' for v in cat_data.values],
                textposition='outside', textfont=dict(color='#f5f5f7', family='Inter'),
                hovertemplate='%{y}: ' + sym + ' %{x:,.2f}<extra></extra>'
            ))
            fig_bar.update_layout(
                showlegend=False, height=350, margin=dict(l=0, r=100, t=20, b=20),
                xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                yaxis=dict(showgrid=False), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', template='plotly_dark'
            )
            st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info(t("no_expenses"))

        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown(f'<p class="card-title" style="margin-top:1rem;">{t("summary")}</p>', unsafe_allow_html=True)
            total_tx = len(st.session_state.transactions)
            largest_exp = expense_df.loc[expense_df['value'].idxmax()] if not expense_df.empty else None
            top_cat = cat_data.idxmax() if not expense_df.empty else "-"
            now = datetime.now()
            last30 = now - timedelta(days=30)
            recent_exp = expense_df[expense_df['date'] >= last30] if not expense_df.empty else expense_df
            daily_avg = recent_exp['value'].sum() / 30 if not recent_exp.empty else 0
            st.markdown(f"""
            <div class="summary-grid">
                <div class="summary-item"><div class="value">{total_tx}</div><div class="label">{t('total_transactions')}</div></div>
                <div class="summary-item"><div class="value">{sym} {largest_exp['value'] if largest_exp is not None else 0:,.2f}</div><div class="label">{t('largest_expense')}</div></div>
                <div class="summary-item"><div class="value">{top_cat}</div><div class="label">{t('top_category')}</div></div>
                <div class="summary-item"><div class="value">{sym} {daily_avg:,.2f}</div><div class="label">{t('daily_average')}</div></div>
            </div>
            """, unsafe_allow_html=True)
        with col_right:
            st.markdown(f'<p class="card-title" style="margin-top:1rem;">{t("trend")}</p>', unsafe_allow_html=True)
            if not expense_df.empty:
                expense_df['date_only'] = expense_df['date'].dt.date
                last7 = now - timedelta(days=7)
                trend_df = expense_df[expense_df['date'] >= last7].groupby('date_only')['value'].sum().reset_index()
                if not trend_df.empty:
                    all_dates = pd.date_range(start=last7.date(), end=now.date(), freq='D')
                    trend_df = trend_df.set_index('date_only').reindex(all_dates.date, fill_value=0).reset_index()
                    trend_df.columns = ['date', 'value']
                    fig_line = px.line(trend_df, x='date', y='value', markers=True, color_discrete_sequence=['#667eea'], template='plotly_dark')
                    fig_line.update_traces(line=dict(width=2), marker=dict(size=6))
                    fig_line.update_layout(showlegend=False, height=250, margin=dict(l=0, r=20, t=20, b=20),
                                           xaxis=dict(showgrid=False, tickfont=dict(color='#f5f5f7')),
                                           yaxis=dict(showgrid=False, tickfont=dict(color='#f5f5f7')),
                                           plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_line, use_container_width=True, config={'displayModeBar': False})
                else: st.info(t("no_data"))
            else: st.info(t("no_data"))
    else:
        st.info(t("no_data"))

# ---------- ABA ORÇAMENTOS ----------
with tab_budgets:
    st.markdown(f'<p class="card-title">{t("budget_title")}</p>', unsafe_allow_html=True)
    expense_categories = [cat for cat in t("categories") if cat not in ["Salário", "Salary"]]
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        selected_cat = st.selectbox(t("category_select"), expense_categories, key="budget_cat")
    with col2:
        budget_value = st.number_input(f"{t('set_budget')} ({sym})", min_value=0.0, value=500.0, step=50.0, format="%.2f", key="budget_val")
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕", key="add_budget_btn"):
            st.session_state.budgets[selected_cat] = budget_value
            save_all()
            st.success(t("budget_added").replace("{cat}", selected_cat))
    st.markdown("---")
    if not st.session_state.budgets:
        st.info(t("no_budgets"))
    else:
        df_exp = pd.DataFrame(st.session_state.transactions) if st.session_state.transactions else pd.DataFrame()
        current_spending = {}
        if not df_exp.empty:
            df_exp = df_exp[df_exp['type'] == 'expense']
            current_spending = df_exp.groupby('category')['value'].sum().to_dict()
        for cat, limit in st.session_state.budgets.items():
            spent = current_spending.get(cat, 0)
            percent = min(spent / limit * 100, 100) if limit > 0 else 100
            color = "#30d158" if percent < 50 else "#ff9f0a" if percent < 80 else "#ff453a"
            status = t("on_track") if percent < 50 else t("watch_out") if percent < 80 else t("over_budget")
            st.markdown(f"""
            <div class="budget-card animate-in">
                <div class="budget-header"><span class="budget-category">{cat}</span><span style="color: {color}; font-weight: 600;">{status}</span></div>
                <div style="color: #86868b;">{t('current_spending')}: {sym} {spent:,.2f} | {t('remaining')}: {sym} {limit - spent:,.2f}</div>
                <div class="progress-bar-container"><div class="progress-bar-fill" style="width: {percent}%; background: {color};"></div></div>
                <div style="text-align: right; font-size: 0.8rem; color: #86868b;">{percent:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
    if st.button(t("clear_budgets")):
        st.session_state.budgets = {}
        save_all()
        st.rerun()

# ---------- ABA METAS ----------
with tab_goals:
    st.markdown(f'<p class="card-title">{t("goal_title")}</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        goal_amount = st.number_input(f"{t('goal_amount')} ({sym})", min_value=0.0, value=1000.0, step=100.0, format="%.2f", key="goal_amount_input")
    with col2:
        goal_deadline = st.date_input(t("goal_deadline"), min_value=datetime.now().date(), key="goal_deadline_input")
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(t("goal_set"), key="set_goal_btn"):
            st.session_state.goal = {'amount': goal_amount, 'deadline': goal_deadline}
            save_all()
            st.success(t("goal_set_success"))
    if st.session_state.goal:
        goal = st.session_state.goal
        saved = balance if balance > 0 else 0
        progress = min(saved / goal['amount'] * 100, 100) if goal['amount'] > 0 else 100
        days_left = max((goal['deadline'] - datetime.now().date()).days, 0)
        color = "#30d158" if progress >= 100 else "#ff9f0a" if progress > 50 else "#ff453a"
        st.markdown(f"""
        <div class="budget-card animate-in">
            <div class="budget-header"><span class="budget-category">{t('goal_progress')}</span><span style="color: {color}; font-weight: 600;">{progress:.1f}%</span></div>
            <div style="color: #86868b;">{t('goal_current')}: {sym} {saved:,.2f} / {sym} {goal['amount']:,.2f}</div>
            <div style="color: #86868b;">Prazo: {goal['deadline'].strftime('%d/%m/%Y')} ({days_left} dias restantes)</div>
            <div class="progress-bar-container"><div class="progress-bar-fill" style="width: {progress}%; background: {color};"></div></div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(t("goal_reset")):
            st.session_state.goal = None
            save_all()
            st.rerun()

# ---------- ABA INSIGHTS (CORRIGIDA) ----------
with tab_insights:
    st.markdown(f'<p class="card-title">{t("insights_title")}</p>', unsafe_allow_html=True)
    insights = generate_insights()
    if insights:
        for insight in insights:
            st.markdown(f'<div class="budget-card animate-in" style="padding: 1rem;"><div style="color: #f5f5f7;">{insight}</div></div>', unsafe_allow_html=True)
    else:
        st.info(t("no_data"))

# ---------- ABA EXPORTAR ----------
with tab_export:
    st.markdown(f'<p class="card-title">{t("export_title")}</p>', unsafe_allow_html=True)
    if st.session_state.transactions:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(export_pdf("pt"), unsafe_allow_html=True)
        with col2:
            st.markdown(export_pdf("en"), unsafe_allow_html=True)
    else:
        st.warning(t("no_transactions"))

# ---------- ABA HISTÓRICO ----------
with tab_hist:
    if st.session_state.transactions:
        for idx, tx in enumerate(sorted(st.session_state.transactions, key=lambda x: x['date'], reverse=True)):
            amt_class = "income" if tx['type'] == 'income' else "expense"
            sign = "+" if tx['type'] == 'income' else "-"
            date_str = tx['date'].strftime('%d/%m/%Y %H:%M') if st.session_state.lang == 'pt' else tx['date'].strftime('%b %d, %H:%M')
            cat_images = {
                "Salary": "💰", "Food": "🍔", "Transport": "🚌", "Housing": "🏠",
                "Leisure": "🎮", "Health": "💊", "Education": "📚", "Investment": "📈", "Other": "📦",
                "Salário": "💰", "Alimentação": "🍕", "Transporte": "🚗", "Moradia": "🏡",
                "Lazer": "🎬", "Saúde": "🩺", "Educação": "🎓", "Investimento": "💹", "Outros": "📌"
            }
            img = cat_images.get(tx['category'], "💲")
            col_info, col_del = st.columns([10, 1])
            with col_info:
                st.markdown(f"""
                <div class="tx-row">
                    <div class="tx-left"><div class="tx-img">{img}</div><div><div class="tx-name">{tx['description']}</div><div class="tx-cat">{tx['category']}</div></div></div>
                    <div><div class="tx-amount {amt_class}">{sign}{sym} {tx['value']:,.2f}</div><div class="tx-date">{date_str}</div></div>
                </div>
                """, unsafe_allow_html=True)
            with col_del:
                if st.button("🗑️", key=f"del_{idx}"):
                    st.session_state.transactions.remove(tx)
                    save_all()
                    st.rerun()
    else:
        st.info(t("no_transactions"))

# ============ CHAT FLUTUANTE (MINIMALISTA) ============
st.markdown("""
<button class="chat-fab" id="chatFab">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
    </svg>
</button>
""", unsafe_allow_html=True)

st.markdown("""
<script>
const fab = document.getElementById('chatFab');
const popup = document.getElementById('chatPopup');
fab.addEventListener('click', () => {
    if (popup.style.display === 'flex') {
        popup.style.display = 'none';
    } else {
        popup.style.display = 'flex';
    }
});
</script>
""", unsafe_allow_html=True)

if st.session_state.show_chat:
    st.markdown('<div class="chat-popup" id="chatPopup" style="display: flex;">', unsafe_allow_html=True)
else:
    st.markdown('<div class="chat-popup" id="chatPopup" style="display: none;">', unsafe_allow_html=True)

st.markdown(f'<div class="chat-header"><span>{t("chat_title")}</span><span style="cursor:pointer;" onclick="document.getElementById(\'chatPopup\').style.display=\'none\'">✕</span></div>', unsafe_allow_html=True)
st.markdown('<div class="chat-body">', unsafe_allow_html=True)

for msg in st.session_state.chat_history:
    css_class = "user-msg" if msg["role"] == "user" else "bot-msg"
    st.markdown(f'<div class="message-bubble {css_class}">{msg["content"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
with st.form(key="chat_form", clear_on_submit=True):
    cols = st.columns([5, 1])
    with cols[0]:
        user_input = st.text_input("", placeholder=t("chat_placeholder"), label_visibility="collapsed", key="chat_input")
    with cols[1]:
        submitted = st.form_submit_button("➤")
    if submitted and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        model = st.session_state.chat_model
        api_key = st.session_state.get("gemini_key", "") or st.session_state.get("openai_key", "")
        if model == "Gemini" and api_key and GEMINI_AVAILABLE:
            try:
                response = generate_gemini_response(user_input, api_key)
            except Exception as e:
                response = f"Erro Gemini: {str(e)}"
        elif model == "ChatGPT" and api_key and OPENAI_AVAILABLE:
            try:
                response = generate_openai_response(user_input, api_key)
            except Exception as e:
                response = f"Erro OpenAI: {str(e)}"
        else:
            response = offline_chat_response(user_input)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        save_all()
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Configuração do chat na barra lateral
with st.sidebar:
    st.markdown("### Configuração do Chat")
    st.session_state.chat_model = st.selectbox(t("chat_model_label"), ["Offline", "Gemini", "ChatGPT"], index=0)
    if st.session_state.chat_model == "Gemini":
        st.session_state.gemini_key = st.text_input(t("gemini_key_label"), type="password")
    elif st.session_state.chat_model == "ChatGPT":
        st.session_state.openai_key = st.text_input(t("openai_key_label"), type="password")
    if st.button(t("clear_chat_history")):
        st.session_state.chat_history = []
        save_all()
        st.rerun()

st.markdown(f"""
<div style="text-align: center; color: #6d6d72; font-size: 0.7rem; padding: 2rem 0 1rem 0;">
    {t("footer")}
</div>
""", unsafe_allow_html=True)
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from fpdf import FPDF
import base64
import io
import sqlite3
import json

# Tentar importar APIs de IA (opcionais)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

st.set_page_config(page_title="FinBot", page_icon="🤖", layout="wide")

# ============ TRADUÇÕES COMPLETAS ============
TEXT = {
    "pt": {
        "title": "FinBot", "subtitle": "Seu assistente financeiro inteligente",
        "income": "Receitas", "expenses": "Despesas", "balance": "Saldo",
        "transactions": "transações", "positive": "Disponível", "negative": "Negativo",
        "new_transaction": "Nova transação", "type": "Tipo",
        "type_income": "Receita", "type_expense": "Despesa",
        "description": "Descrição", "desc_placeholder": "Ex: Salário, Aluguel, Ifood...",
        "amount": "Valor", "date": "Data", "category": "Categoria",
        "categories": ["Salário", "Alimentação", "Transporte", "Moradia", "Lazer", "Saúde", "Educação", "Investimento", "Outros"],
        "add_button": "Adicionar transação", "delete": "Excluir",
        "recent_activity": "Atividade recente", "no_transactions": "Nenhuma transação ainda",
        "tab_dashboard": "Painel", "tab_add": "Adicionar", "tab_history": "Histórico",
        "tab_budgets": "Orçamentos", "tab_goals": "Metas", "tab_insights": "Insights",
        "tab_export": "Exportar",
        "spending_breakdown": "Para onde vai seu dinheiro",
        "no_expenses": "Nenhuma despesa registrada",
        "summary": "Resumo do período", "of_income_spent": "da receita gasta",
        "on_track": "Você está no controle", "watch_out": "Fique atento",
        "over_budget": "Orçamento estourado", "total_transactions": "Total de transações",
        "largest_expense": "Maior despesa", "top_category": "Categoria principal",
        "average_expense": "Despesa média", "daily_average": "Média diária (30 dias)",
        "trend": "Tendência (7 dias)", "no_data": "Sem dados suficientes",
        "add_to_see": "Adicione transações para visualizar", "footer": "FinBot",
        "choose_language": "Escolha o idioma", "portuguese": "Português", "english": "English",
        "currency_symbol": "R$", "fill_all": "Preencha todos os campos",
        "budget_title": "Definir Orçamentos", "budget_desc": "Estabeleça limites de gastos por categoria.",
        "set_budget": "Definir limite", "current_spending": "Gasto atual", "remaining": "Restante",
        "exceeded": "Estourado!", "save_budgets": "Salvar orçamentos",
        "goal_title": "Metas Financeiras", "goal_desc": "Defina um objetivo de economia e acompanhe seu progresso.",
        "goal_amount": "Valor da meta", "goal_deadline": "Prazo final", "goal_current": "Economizado até agora",
        "goal_progress": "Progresso", "goal_set": "Definir meta", "goal_reset": "Limpar meta",
        "insights_title": "Análise Inteligente", "insights_desc": "Recomendações baseadas nos seus hábitos financeiros.",
        "insight_top_category": "Sua maior categoria de gasto é",
        "insight_spending_increase": "Seus gastos aumentaram",
        "insight_budget_warning": "Você já usou mais de 80% do orçamento de",
        "insight_frequency": "Você teve muitas transações este mês. Que tal revisar os pequenos gastos?",
        "insight_general": "Continue acompanhando seus gastos para manter o controle.",
        "export_title": "Exportar Relatório PDF",
        "export_pdf_pt": "Baixar PDF (Português)", "export_pdf_en": "Baixar PDF (English)",
        "pdf_balance": "Saldo", "pdf_income": "Receitas totais", "pdf_expense": "Despesas totais",
        "pdf_recent_transactions": "Últimas transações", "pdf_generated": "Gerado por FinBot",
        "chat_title": "Consultor IA", "chat_placeholder": "Digite sua dúvida...",
        "login_title": "Entrar no FinBot", "login_user": "Usuário", "login_pass": "Senha",
        "login_btn": "Entrar", "login_error": "Usuário ou senha inválidos.",
        "register_btn": "Criar conta", "register_success": "Conta criada! Faça login.",
        "username_taken": "Nome de usuário já existe.",
        "no_budgets": "Nenhum orçamento definido.",
        "clear_budgets": "Limpar todos os orçamentos",
        "category_select": "Categoria",
        "budget_added": "Limite para {cat} definido!",
        "goal_set_success": "Meta definida!",
        "clear_chat_history": "Limpar histórico do chat",
        "chat_model_label": "Modelo",
        "gemini_key_label": "Chave Gemini",
        "openai_key_label": "Chave OpenAI",
        "logout": "Sair",
    },
    "en": {
        "title": "FinBot", "subtitle": "Your intelligent financial assistant",
        "income": "Income", "expenses": "Expenses", "balance": "Balance",
        "transactions": "transactions", "positive": "Available", "negative": "Overdrawn",
        "new_transaction": "New transaction", "type": "Type",
        "type_income": "Income", "type_expense": "Expense",
        "description": "Description", "desc_placeholder": "e.g., Salary, Rent, Food...",
        "amount": "Amount", "date": "Date", "category": "Category",
        "categories": ["Salary", "Food", "Transport", "Housing", "Leisure", "Health", "Education", "Investment", "Other"],
        "add_button": "Add transaction", "delete": "Delete",
        "recent_activity": "Recent activity", "no_transactions": "No transactions yet",
        "tab_dashboard": "Dashboard", "tab_add": "Add", "tab_history": "History",
        "tab_budgets": "Budgets", "tab_goals": "Goals", "tab_insights": "Insights",
        "tab_export": "Export",
        "spending_breakdown": "Where your money goes",
        "no_expenses": "No expenses recorded",
        "summary": "Period summary", "of_income_spent": "of income spent",
        "on_track": "You're on track", "watch_out": "Keep an eye",
        "over_budget": "Over budget", "total_transactions": "Total transactions",
        "largest_expense": "Largest expense", "top_category": "Top category",
        "average_expense": "Average expense", "daily_average": "Daily average (30d)",
        "trend": "Trend (7 days)", "no_data": "Not enough data",
        "add_to_see": "Add transactions to see", "footer": "FinBot",
        "choose_language": "Choose language", "portuguese": "Português", "english": "English",
        "currency_symbol": "$", "fill_all": "Please fill all fields",
        "budget_title": "Set Budgets", "budget_desc": "Define spending limits per category.",
        "set_budget": "Set limit", "current_spending": "Current spending", "remaining": "Remaining",
        "exceeded": "Exceeded!", "save_budgets": "Save budgets",
        "goal_title": "Financial Goals", "goal_desc": "Set a savings goal and track your progress.",
        "goal_amount": "Goal amount", "goal_deadline": "Deadline", "goal_current": "Saved so far",
        "goal_progress": "Progress", "goal_set": "Set goal", "goal_reset": "Clear goal",
        "insights_title": "Smart Insights", "insights_desc": "Recommendations based on your spending habits.",
        "insight_top_category": "Your top spending category is",
        "insight_spending_increase": "Your spending increased by",
        "insight_budget_warning": "You've used over 80% of the budget for",
        "insight_frequency": "You've had many transactions this month. Consider reviewing small expenses.",
        "insight_general": "Keep tracking your spending to stay in control.",
        "export_title": "Export PDF Report",
        "export_pdf_pt": "Download PDF (Português)", "export_pdf_en": "Download PDF (English)",
        "pdf_balance": "Balance", "pdf_income": "Total Income", "pdf_expense": "Total Expenses",
        "pdf_recent_transactions": "Recent Transactions", "pdf_generated": "Generated by FinBot",
        "chat_title": "AI Advisor", "chat_placeholder": "Type your question...",
        "login_title": "Login to FinBot", "login_user": "User", "login_pass": "Password",
        "login_btn": "Login", "login_error": "Invalid user or password.",
        "register_btn": "Sign up", "register_success": "Account created! Please login.",
        "username_taken": "Username already taken.",
        "no_budgets": "No budgets defined.",
        "clear_budgets": "Clear all budgets",
        "category_select": "Category",
        "budget_added": "Budget for {cat} set!",
        "goal_set_success": "Goal set!",
        "clear_chat_history": "Clear chat history",
        "chat_model_label": "Model",
        "gemini_key_label": "Gemini Key",
        "openai_key_label": "OpenAI Key",
        "logout": "Logout",
    }
}

# ============ BANCO DE DADOS SQLITE ============
DB_FILE = "finbot.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS data (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    conn.commit()
    conn.close()

def save_data(key, value):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("REPLACE INTO data (key, value) VALUES (?, ?)", (key, json.dumps(value)))
    conn.commit()
    conn.close()

def load_data(key, default=None):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT value FROM data WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return default

def save_all():
    save_data("transactions", st.session_state.transactions)
    save_data("budgets", st.session_state.budgets)
    save_data("goal", st.session_state.goal)
    save_data("chat_history", st.session_state.chat_history)

def load_all():
    if 'db_loaded' not in st.session_state:
        init_db()
        st.session_state.transactions = load_data("transactions", [])
        st.session_state.budgets = load_data("budgets", {})
        st.session_state.goal = load_data("goal", None)
        st.session_state.chat_history = load_data("chat_history", [])
        st.session_state.db_loaded = True

# ============ ESTADO DA SESSÃO ============
if 'lang' not in st.session_state:
    st.session_state.lang = None
if 'users' not in st.session_state:
    st.session_state.users = {"admin": "admin"}
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# Carrega dados salvos
load_all()

# Inicializa estado se não existir
if 'chat_model' not in st.session_state:
    st.session_state.chat_model = "Offline"
if 'show_chat' not in st.session_state:
    st.session_state.show_chat = False

# ============ TELA DE ESCOLHA DE IDIOMA ============
if st.session_state.lang is None:
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        * { font-family: 'Inter', sans-serif; }
        .stApp { background: #0a0a0a; }
        .welcome-container {
            display: flex; flex-direction: column; align-items: center;
            justify-content: center; min-height: 70vh; color: white;
        }
        .robot-logo-large { font-size: 80px; margin-bottom: 1.5rem; }
        .welcome-title { font-size: 2rem; font-weight: 600; margin-bottom: 2rem; }
    </style>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="welcome-container">
        <div class="robot-logo-large">🤖</div>
        <div class="welcome-title">Bem-vindo ao FinBot</div>
        <p style="opacity: 0.7;">Escolha o idioma / Choose language</p>
    </div>
    """, unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🇧🇷 Português", use_container_width=True):
            st.session_state.lang = "pt"
            st.rerun()
    with c2:
        if st.button("🇺🇸 English", use_container_width=True):
            st.session_state.lang = "en"
            st.rerun()
    st.stop()

# ============ TELA DE LOGIN / REGISTRO ============
if not st.session_state.logged_in:
    st.markdown("""
    <style>
        .stApp { background: #0a0a0a; }
        .login-container { max-width: 400px; margin: 10% auto; padding: 2rem; background: #1c1c1e; border-radius: 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.3); }
        h2 { color: #f5f5f7; text-align: center; }
    </style>
    """, unsafe_allow_html=True)
    with st.container():
        st.markdown(f"<h2>🤖 {TEXT[st.session_state.lang]['login_title']}</h2>", unsafe_allow_html=True)
        tab_login, tab_register = st.tabs(["Login", "Registrar"])
        with tab_login:
            user = st.text_input(TEXT[st.session_state.lang]['login_user'])
            password = st.text_input(TEXT[st.session_state.lang]['login_pass'], type="password")
            if st.button(TEXT[st.session_state.lang]['login_btn'], use_container_width=True):
                if st.session_state.users.get(user) == password:
                    st.session_state.logged_in = True
                    st.session_state.current_user = user
                    st.rerun()
                else:
                    st.error(TEXT[st.session_state.lang]['login_error'])
        with tab_register:
            new_user = st.text_input(TEXT[st.session_state.lang]['login_user'], key="reg_user")
            new_pass = st.text_input(TEXT[st.session_state.lang]['login_pass'], type="password", key="reg_pass")
            if st.button(TEXT[st.session_state.lang]['register_btn'], use_container_width=True):
                if new_user in st.session_state.users:
                    st.warning(TEXT[st.session_state.lang]['username_taken'])
                elif new_user and new_pass:
                    st.session_state.users[new_user] = new_pass
                    st.success(TEXT[st.session_state.lang]['register_success'])
                else:
                    st.warning(TEXT[st.session_state.lang]['fill_all'])
    st.stop()

# ============ CSS TEMA ESCURO + CHAT MINIMALISTA ============
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;450;500;600;700&display=swap');
    * {{{{ font-family: 'Inter', sans-serif; }}}}
    header[data-testid="stHeader"] {{{{ display: none !important; }}}}
    div[data-testid="stToolbar"] {{{{ display: none !important; }}}}
    div[data-testid="stDecoration"] {{{{ display: none !important; }}}}
    #MainMenu {{{{ display: none !important; }}}}
    footer {{{{ display: none !important; }}}}
    .stApp {{{{ background: #0a0a0a; }}}}
    .block-container {{{{ padding: 2rem 3rem; max-width: 1200px; }}}}
    
    .logo-area {{{{ display: flex; align-items: center; gap: 0.75rem; margin-bottom: 2rem; }}}}
    .robot-logo {{{{ font-size: 36px; line-height: 1; }}}}
    h1 {{{{ font-weight: 700 !important; color: #f5f5f7 !important; font-size: 2rem !important; }}}}
    .subtitle {{{{ color: #86868b; font-size: 0.9rem; }}}}
    
    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes pulse {{
        0% {{ transform: scale(1); }}
        50% {{ transform: scale(1.02); }}
        100% {{ transform: scale(1); }}
    }}
    @keyframes slideInRight {{
        from {{ transform: translateX(100px); opacity: 0; }}
        to {{ transform: translateX(0); opacity: 1; }}
    }}
    .animate-in {{{{ animation: fadeInUp 0.5s ease forwards; }}}}
    .animate-pulse {{{{ animation: pulse 2s infinite; }}}}
    
    .metric-card {{
        background: linear-gradient(135deg, #1c1c1e 0%, #2c2c2e 100%);
        padding: 1.8rem 1.5rem;
        border-radius: 24px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        animation: fadeInUp 0.5s ease;
        transition: transform 0.2s;
        position: relative;
        overflow: hidden;
    }}
    .metric-card:hover {{
        transform: translateY(-4px);
    }}
    .metric-card::before {{
        content: '';
        position: absolute;
        top: -30px;
        right: -30px;
        width: 80px;
        height: 80px;
        border-radius: 50%;
        opacity: 0.1;
    }}
    .metric-card.income::before {{ background: #30d158; }}
    .metric-card.expense::before {{ background: #ff453a; }}
    .metric-card.balance::before {{ background: #667eea; }}
    .metric-icon {{ font-size: 2rem; margin-bottom: 0.5rem; }}
    .metric-label {{ text-transform: uppercase; letter-spacing: 1px; font-size: 0.75rem; font-weight: 500; color: #86868b; margin-bottom: 0.4rem; }}
    .metric-value {{ font-size: 2rem; font-weight: 700; color: #f5f5f7; line-height: 1.2; }}
    .metric-sub {{ color: #6d6d72; font-size: 0.8rem; margin-top: 0.3rem; }}
    
    .content-card {{
        background: #1c1c1e; padding: 2rem; border-radius: 20px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2); animation: fadeInUp 0.5s ease; transition: transform 0.2s;
    }}
    .content-card:hover {{ transform: translateY(-2px); }}
    .card-title {{ color: #f5f5f7; font-size: 1rem; font-weight: 600; margin-bottom: 1.5rem; }}
    
    .tx-row {{
        display: flex; align-items: center; justify-content: space-between;
        padding: 0.85rem 0; border-bottom: 1px solid #2c2c2e; transition: background 0.2s;
    }}
    .tx-row:hover {{ background: rgba(255,255,255,0.02); }}
    .tx-img {{
        width: 42px; height: 42px; border-radius: 12px; background: #2c2c2e;
        display: flex; align-items: center; justify-content: center; font-size: 1.5rem; flex-shrink: 0;
    }}
    .tx-name {{ color: #f5f5f7; font-weight: 500; }}
    .tx-cat {{ color: #86868b; font-size: 0.78rem; }}
    .tx-amount {{ font-weight: 550; text-align: right; transition: transform 0.2s; }}
    .tx-amount.income {{ color: #30d158; }}
    .tx-amount.expense {{ color: #ff453a; }}
    .tx-date {{ color: #6d6d72; font-size: 0.72rem; text-align: right; }}
    
    .stButton > button {{
        background: #f5f5f7; color: #0a0a0a; border: none; border-radius: 14px;
        padding: 0.8rem 1.8rem; font-size: 0.9rem; font-weight: 550;
        width: 100%; cursor: pointer; transition: all 0.2s;
    }}
    .stButton > button:hover {{ background: #e5e5ea; transform: scale(1.02); box-shadow: 0 6px 20px rgba(0,0,0,0.2); }}
    
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div,
    .stDateInput > div > div > input {{
        background: #2c2c2e; border: 1px solid #3a3a3c; color: #f5f5f7;
        border-radius: 12px; padding: 0.7rem 0.9rem; font-size: 0.88rem; transition: border 0.2s;
    }}
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div:focus,
    .stDateInput > div > div > input:focus {{
        border-color: #667eea; box-shadow: 0 0 0 3px rgba(102,126,234,0.2);
    }}
    .stSelectbox > div {{ color: #f5f5f7; }}
    div[data-baseweb="select"] svg {{ color: #f5f5f7; }}
    
    .stTabs [data-baseweb="tab-list"] {{ border-bottom: 1px solid #2c2c2e; gap: 0; }}
    .stTabs [data-baseweb="tab"] {{
        padding: 0.7rem 1.5rem; font-size: 0.9rem; color: #86868b;
        background: transparent; border: none; transition: color 0.2s;
    }}
    .stTabs [data-baseweb="tab"]:hover {{ color: #f5f5f7; }}
    .stTabs [aria-selected="true"] {{ color: #f5f5f7; border-bottom: 2px solid #667eea; }}
    
    .budget-card {{
        background: #1c1c1e; padding: 1.5rem; border-radius: 16px; margin-bottom: 1rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.2); animation: fadeInUp 0.5s ease; transition: transform 0.2s;
    }}
    .budget-card:hover {{ transform: translateY(-2px); }}
    .budget-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }}
    .budget-category {{ font-weight: 600; color: #f5f5f7; font-size: 1rem; }}
    .progress-bar-container {{
        width: 100%; height: 8px; background: #2c2c2e; border-radius: 4px; overflow: hidden; margin-top: 0.5rem;
    }}
    .progress-bar-fill {{ height: 100%; border-radius: 4px; transition: width 0.6s ease; }}
    
    .chat-fab {{
        position: fixed; bottom: 30px; right: 30px; width: 56px; height: 56px; border-radius: 28px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        box-shadow: 0 8px 25px rgba(102,126,234,0.4); display: flex; align-items: center; justify-content: center;
        font-size: 24px; color: white; cursor: pointer; z-index: 9999; border: none;
        transition: transform 0.3s, box-shadow 0.3s;
    }}
    .chat-fab:hover {{ transform: scale(1.08); box-shadow: 0 12px 30px rgba(102,126,234,0.6); }}
    .chat-popup {{
        position: fixed; bottom: 100px; right: 30px; width: 320px; height: 420px;
        background: #1c1c1e; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        z-index: 9998; display: none; flex-direction: column; overflow: hidden;
        border: 1px solid #2c2c2e; animation: slideInRight 0.3s ease;
    }}
    .chat-header {{
        padding: 0.8rem 1rem; background: #2c2c2e; display: flex;
        justify-content: space-between; align-items: center; color: #f5f5f7; font-weight: 600; font-size: 0.9rem;
    }}
    .chat-body {{ flex: 1; overflow-y: auto; padding: 0.8rem; display: flex; flex-direction: column; gap: 0.6rem; }}
    .message-bubble {{
        max-width: 85%; padding: 0.6rem 0.9rem; border-radius: 16px; font-size: 0.82rem; line-height: 1.4; word-wrap: break-word;
    }}
    .user-msg {{ align-self: flex-end; background: #667eea; color: white; border-bottom-right-radius: 4px; }}
    .bot-msg {{ align-self: flex-start; background: #2c2c2e; color: #f5f5f7; border-bottom-left-radius: 4px; }}
    .chat-input-container {{ padding: 0.6rem; background: #2c2c2e; display: flex; gap: 0.4rem; }}
    .chat-input-container input {{
        flex: 1; background: #3a3a3c; border: none; border-radius: 20px; padding: 0.5rem 0.9rem;
        color: white; font-size: 0.82rem; outline: none;
    }}
    .chat-input-container button {{
        background: #667eea; border: none; border-radius: 50%; width: 32px; height: 32px;
        color: white; font-size: 1rem; cursor: pointer; transition: background 0.2s;
    }}
    .chat-input-container button:hover {{ background: #5a6fd6; }}
    
    [data-testid="stSidebar"] {{ background: #1c1c1e; }}
    [data-testid="stSidebar"] h3 {{ color: #f5f5f7; }}
</style>
""".replace("{{{{", "{").replace("}}}}", "}"), unsafe_allow_html=True)

# ============ FUNÇÕES AUXILIARES ============
def t(key):
    return TEXT[st.session_state.lang][key]

income_total = sum(tx['value'] for tx in st.session_state.transactions if tx['type'] == 'income')
expense_total = sum(tx['value'] for tx in st.session_state.transactions if tx['type'] == 'expense')
balance = income_total - expense_total
sym = t("currency_symbol")

def generate_insights():
    if not st.session_state.transactions:
        return []
    df = pd.DataFrame(st.session_state.transactions)
    expense_df = df[df['type'] == 'expense']
    insights = []
    if expense_df.empty:
        insights.append(t("insight_general"))
        return insights
    top_cat = expense_df.groupby('category')['value'].sum().idxmax()
    insights.append(f"{t('insight_top_category')} **{top_cat}**.")
    now = datetime.now()
    this_month = now.month
    prev_month = this_month - 1 if this_month > 1 else 12
    this_month_exp = expense_df[expense_df['date'].dt.month == this_month]['value'].sum()
    prev_month_exp = expense_df[expense_df['date'].dt.month == prev_month]['value'].sum()
    if prev_month_exp > 0 and this_month_exp > prev_month_exp:
        diff = ((this_month_exp - prev_month_exp) / prev_month_exp) * 100
        insights.append(f"{t('insight_spending_increase')} **{diff:.1f}%**.")
    for cat, limit in st.session_state.budgets.items():
        spent = expense_df[expense_df['category'] == cat]['value'].sum()
        if limit > 0 and spent > limit * 0.8:
            insights.append(f"{t('insight_budget_warning')} **{cat}**.")
    if len(expense_df) > 10:
        insights.append(t("insight_frequency"))
    return insights[:5]

def export_pdf(lang):
    if not st.session_state.transactions:
        return None
    sym_lang = TEXT[lang]["currency_symbol"]
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(0, 10, txt="FinBot - Relatório Financeiro" if lang == "pt" else "FinBot - Financial Report", ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 8, txt=f"{TEXT[lang]['pdf_balance']}: {sym_lang} {balance:,.2f}", ln=True)
    pdf.cell(0, 8, txt=f"{TEXT[lang]['pdf_income']}: {sym_lang} {income_total:,.2f}", ln=True)
    pdf.cell(0, 8, txt=f"{TEXT[lang]['pdf_expense']}: {sym_lang} {expense_total:,.2f}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(0, 10, txt=TEXT[lang]["pdf_recent_transactions"], ln=True)
    pdf.set_font("Arial", size=9)
    col_widths = [30, 50, 30, 30, 30]
    header = [TEXT[lang]["date"], TEXT[lang]["description"], TEXT[lang]["type"], TEXT[lang]["category"], TEXT[lang]["amount"]]
    for i, h in enumerate(header):
        pdf.cell(col_widths[i], 7, txt=h, border=1)
    pdf.ln()
    for tx in sorted(st.session_state.transactions, key=lambda x: x['date'], reverse=True)[:20]:
        date_str = tx['date'].strftime('%d/%m/%Y') if lang == "pt" else tx['date'].strftime('%Y-%m-%d')
        tipo = "Receita" if tx['type'] == 'income' else "Despesa" if lang == "pt" else "Income" if tx['type'] == 'income' else "Expense"
        val_str = f"{tx['value']:.2f}"
        pdf.cell(col_widths[0], 6, txt=date_str, border=1)
        pdf.cell(col_widths[1], 6, txt=tx['description'][:25], border=1)
        pdf.cell(col_widths[2], 6, txt=tipo, border=1)
        pdf.cell(col_widths[3], 6, txt=tx['category'][:15], border=1)
        pdf.cell(col_widths[4], 6, txt=val_str, border=1)
        pdf.ln()
    pdf.ln(10)
    pdf.set_font("Arial", size=8)
    pdf.cell(0, 10, txt=TEXT[lang]["pdf_generated"], ln=True, align='C')
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    b64 = base64.b64encode(pdf_bytes).decode()
    label = TEXT[lang]["export_pdf_pt"] if lang == "pt" else TEXT[lang]["export_pdf_en"]
    return f'<a href="data:application/pdf;base64,{b64}" download="finbot_{lang}.pdf" style="color: #f5f5f7; text-decoration: none; background: #2c2c2e; padding: 0.5rem 1rem; border-radius: 8px;">📥 {label}</a>'

def offline_chat_response(prompt):
    df = pd.DataFrame(st.session_state.transactions) if st.session_state.transactions else pd.DataFrame()
    expense_df = df[df['type'] == 'expense'] if not df.empty else pd.DataFrame()
    context = f"Saldo atual: {sym} {balance:,.2f}. "
    if not expense_df.empty:
        top_cat = expense_df.groupby('category')['value'].sum().idxmax()
        context += f"Maior gasto: {top_cat}. "
    if st.session_state.goal:
        goal = st.session_state.goal
        saved = balance if balance > 0 else 0
        progress = min(saved / goal['amount'] * 100, 100) if goal['amount'] > 0 else 0
        context += f"Meta: {sym} {goal['amount']:,.2f} ({progress:.1f}%). "
    p = prompt.lower()
    if any(w in p for w in ["saldo", "balance", "quanto tenho"]):
        return f"Seu saldo é {sym} {balance:,.2f}. " + ("Positivo!" if balance >= 0 else "Negativo. Cuidado!")
    if any(w in p for w in ["gasto", "despesa", "gastei", "spent"]):
        if expense_df.empty:
            return "Sem despesas registradas."
        top = expense_df.groupby('category')['value'].sum().idxmax()
        total = expense_df['value'].sum()
        return f"Total gasto: {sym} {total:,.2f}. Maior gasto: {top}."
    if any(w in p for w in ["economizar", "save", "poupar"]):
        if expense_df.empty:
            return "Registre despesas para eu sugerir economia."
        top = expense_df.groupby('category')['value'].sum().idxmax()
        return f"Reduza gastos com {top}. Pequenas economias fazem diferença!"
    if any(w in p for w in ["investir", "invest", "renda"]):
        return "Invista em renda fixa (Tesouro Direto, CDB). Mantenha reserva de emergência de 6 meses."
    if any(w in p for w in ["orçamento", "budget"]):
        if not st.session_state.budgets:
            return "Defina orçamentos na aba Orçamentos."
        msg = "Orçamentos:\n"
        for cat, limit in st.session_state.budgets.items():
            spent = expense_df[expense_df['category'] == cat]['value'].sum() if not expense_df.empty else 0
            pct = (spent / limit) * 100 if limit > 0 else 0
            msg += f"- {cat}: {sym} {spent:,.2f} de {sym} {limit:,.2f} ({pct:.0f}%)\n"
        return msg
    if any(w in p for w in ["meta", "goal"]):
        if not st.session_state.goal:
            return "Nenhuma meta definida. Vá em Metas."
        goal = st.session_state.goal
        saved = balance if balance > 0 else 0
        progress = min(saved / goal['amount'] * 100, 100) if goal['amount'] > 0 else 0
        days_left = max((goal['deadline'] - datetime.now().date()).days, 0)
        return f"Meta: {sym} {goal['amount']:,.2f}. Progresso: {progress:.1f}%. {days_left} dias restantes."
    return f"{context}\nPergunte sobre saldo, gastos, economia, investimentos, orçamentos ou metas!"

# ============ INTERFACE PRINCIPAL ============
col_logo, col_controls = st.columns([4, 1])
with col_logo:
    st.markdown(f"""
    <div class="logo-area">
        <div class="robot-logo">🤖</div>
        <div>
            <h1>{t('title')}</h1>
            <div class="subtitle">{t('subtitle')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_controls:
    st.markdown('<div class="top-controls">', unsafe_allow_html=True)
    lang_options = ["Português", "English"]
    new_lang = st.selectbox("", lang_options, index=0 if st.session_state.lang == "pt" else 1, label_visibility="collapsed", key="lang_select")
    if (new_lang == "Português" and st.session_state.lang != "pt"):
        st.session_state.lang = "pt"
        st.rerun()
    elif (new_lang == "English" and st.session_state.lang != "en"):
        st.session_state.lang = "en"
        st.rerun()
    if st.button("🚪", help=t("logout")):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ============ CARDS DE MÉTRICAS ============
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"""
    <div class="metric-card income animate-in">
        <div class="metric-icon">💰</div>
        <div class="metric-label">{t('income')}</div>
        <div class="metric-value">{sym} {income_total:,.2f}</div>
        <div class="metric-sub">{len([tx for tx in st.session_state.transactions if tx['type']=='income'])} {t('transactions')}</div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="metric-card expense animate-in">
        <div class="metric-icon">💸</div>
        <div class="metric-label">{t('expenses')}</div>
        <div class="metric-value">{sym} {expense_total:,.2f}</div>
        <div class="metric-sub">{len([tx for tx in st.session_state.transactions if tx['type']=='expense'])} {t('transactions')}</div>
    </div>
    """, unsafe_allow_html=True)
with c3:
    bal_color = "#30d158" if balance >= 0 else "#ff453a"
    st.markdown(f"""
    <div class="metric-card balance animate-in">
        <div class="metric-icon">📊</div>
        <div class="metric-label">{t('balance')}</div>
        <div class="metric-value" style="color: {bal_color};">{sym} {balance:,.2f}</div>
        <div class="metric-sub">{t('positive') if balance >= 0 else t('negative')}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============ ABAS ============
tab_add, tab_dash, tab_budgets, tab_goals, tab_insights, tab_export, tab_hist = st.tabs([
    t("tab_add"), t("tab_dashboard"), t("tab_budgets"), t("tab_goals"),
    t("tab_insights"), t("tab_export"), t("tab_history")
])

# ---------- ABA ADICIONAR ----------
with tab_add:
    col_form, _ = st.columns([1, 1])
    with col_form:
        st.markdown(f'<p class="card-title">{t("new_transaction")}</p>', unsafe_allow_html=True)
        trans_type_label = st.selectbox(t("type"), [t("type_income"), t("type_expense")])
        type_code = "income" if trans_type_label == t("type_income") else "expense"
        description = st.text_input(t("description"), placeholder=t("desc_placeholder"))
        c_val, c_date = st.columns(2)
        with c_val:
            value = st.number_input(t("amount"), min_value=0.01, value=50.00, step=10.0, format="%.2f")
        with c_date:
            date = st.date_input(t("date"), value=datetime.now().date())
        category = st.selectbox(t("category"), t("categories"))
        if st.button(t("add_button"), use_container_width=True):
            if description and value > 0:
                st.session_state.transactions.append({
                    'date': datetime.combine(date, datetime.min.time()),
                    'description': description,
                    'value': value,
                    'type': type_code,
                    'category': category
                })
                save_all()
                st.success("Adicionado!" if st.session_state.lang == 'pt' else "Added!")
                st.rerun()
            else:
                st.warning(t("fill_all"))

# ---------- ABA PAINEL ----------
with tab_dash:
    if st.session_state.transactions:
        df = pd.DataFrame(st.session_state.transactions)
        expense_df = df[df['type'] == 'expense'].copy()
        if not expense_df.empty:
            cat_data = expense_df.groupby('category')['value'].sum().sort_values(ascending=True)
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                y=cat_data.index, x=cat_data.values, orientation='h',
                marker=dict(color='#f5f5f7', cornerradius=6, line=dict(width=0)),
                text=[f'{sym} {v:,.0f}' for v in cat_data.values],
                textposition='outside', textfont=dict(color='#f5f5f7', family='Inter'),
                hovertemplate='%{y}: ' + sym + ' %{x:,.2f}<extra></extra>'
            ))
            fig_bar.update_layout(
                showlegend=False, height=350, margin=dict(l=0, r=100, t=20, b=20),
                xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                yaxis=dict(showgrid=False), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', template='plotly_dark'
            )
            st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info(t("no_expenses"))

        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown(f'<p class="card-title" style="margin-top:1rem;">{t("summary")}</p>', unsafe_allow_html=True)
            total_tx = len(st.session_state.transactions)
            largest_exp = expense_df.loc[expense_df['value'].idxmax()] if not expense_df.empty else None
            top_cat = cat_data.idxmax() if not expense_df.empty else "-"
            now = datetime.now()
            last30 = now - timedelta(days=30)
            recent_exp = expense_df[expense_df['date'] >= last30] if not expense_df.empty else expense_df
            daily_avg = recent_exp['value'].sum() / 30 if not recent_exp.empty else 0
            st.markdown(f"""
            <div class="summary-grid">
                <div class="summary-item"><div class="value">{total_tx}</div><div class="label">{t('total_transactions')}</div></div>
                <div class="summary-item"><div class="value">{sym} {largest_exp['value'] if largest_exp is not None else 0:,.2f}</div><div class="label">{t('largest_expense')}</div></div>
                <div class="summary-item"><div class="value">{top_cat}</div><div class="label">{t('top_category')}</div></div>
                <div class="summary-item"><div class="value">{sym} {daily_avg:,.2f}</div><div class="label">{t('daily_average')}</div></div>
            </div>
            """, unsafe_allow_html=True)
        with col_right:
            st.markdown(f'<p class="card-title" style="margin-top:1rem;">{t("trend")}</p>', unsafe_allow_html=True)
            if not expense_df.empty:
                expense_df['date_only'] = expense_df['date'].dt.date
                last7 = now - timedelta(days=7)
                trend_df = expense_df[expense_df['date'] >= last7].groupby('date_only')['value'].sum().reset_index()
                if not trend_df.empty:
                    all_dates = pd.date_range(start=last7.date(), end=now.date(), freq='D')
                    trend_df = trend_df.set_index('date_only').reindex(all_dates.date, fill_value=0).reset_index()
                    trend_df.columns = ['date', 'value']
                    fig_line = px.line(trend_df, x='date', y='value', markers=True, color_discrete_sequence=['#667eea'], template='plotly_dark')
                    fig_line.update_traces(line=dict(width=2), marker=dict(size=6))
                    fig_line.update_layout(showlegend=False, height=250, margin=dict(l=0, r=20, t=20, b=20),
                                           xaxis=dict(showgrid=False, tickfont=dict(color='#f5f5f7')),
                                           yaxis=dict(showgrid=False, tickfont=dict(color='#f5f5f7')),
                                           plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_line, use_container_width=True, config={'displayModeBar': False})
                else: st.info(t("no_data"))
            else: st.info(t("no_data"))
    else:
        st.info(t("no_data"))

# ---------- ABA ORÇAMENTOS ----------
with tab_budgets:
    st.markdown(f'<p class="card-title">{t("budget_title")}</p>', unsafe_allow_html=True)
    expense_categories = [cat for cat in t("categories") if cat not in ["Salário", "Salary"]]
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        selected_cat = st.selectbox(t("category_select"), expense_categories, key="budget_cat")
    with col2:
        budget_value = st.number_input(f"{t('set_budget')} ({sym})", min_value=0.0, value=500.0, step=50.0, format="%.2f", key="budget_val")
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕", key="add_budget_btn"):
            st.session_state.budgets[selected_cat] = budget_value
            save_all()
            st.success(t("budget_added").replace("{cat}", selected_cat))
    st.markdown("---")
    if not st.session_state.budgets:
        st.info(t("no_budgets"))
    else:
        df_exp = pd.DataFrame(st.session_state.transactions) if st.session_state.transactions else pd.DataFrame()
        current_spending = {}
        if not df_exp.empty:
            df_exp = df_exp[df_exp['type'] == 'expense']
            current_spending = df_exp.groupby('category')['value'].sum().to_dict()
        for cat, limit in st.session_state.budgets.items():
            spent = current_spending.get(cat, 0)
            percent = min(spent / limit * 100, 100) if limit > 0 else 100
            color = "#30d158" if percent < 50 else "#ff9f0a" if percent < 80 else "#ff453a"
            status = t("on_track") if percent < 50 else t("watch_out") if percent < 80 else t("over_budget")
            st.markdown(f"""
            <div class="budget-card animate-in">
                <div class="budget-header"><span class="budget-category">{cat}</span><span style="color: {color}; font-weight: 600;">{status}</span></div>
                <div style="color: #86868b;">{t('current_spending')}: {sym} {spent:,.2f} | {t('remaining')}: {sym} {limit - spent:,.2f}</div>
                <div class="progress-bar-container"><div class="progress-bar-fill" style="width: {percent}%; background: {color};"></div></div>
                <div style="text-align: right; font-size: 0.8rem; color: #86868b;">{percent:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
    if st.button(t("clear_budgets")):
        st.session_state.budgets = {}
        save_all()
        st.rerun()

# ---------- ABA METAS ----------
with tab_goals:
    st.markdown(f'<p class="card-title">{t("goal_title")}</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        goal_amount = st.number_input(f"{t('goal_amount')} ({sym})", min_value=0.0, value=1000.0, step=100.0, format="%.2f", key="goal_amount_input")
    with col2:
        goal_deadline = st.date_input(t("goal_deadline"), min_value=datetime.now().date(), key="goal_deadline_input")
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(t("goal_set"), key="set_goal_btn"):
            st.session_state.goal = {'amount': goal_amount, 'deadline': goal_deadline}
            save_all()
            st.success(t("goal_set_success"))
    if st.session_state.goal:
        goal = st.session_state.goal
        saved = balance if balance > 0 else 0
        progress = min(saved / goal['amount'] * 100, 100) if goal['amount'] > 0 else 100
        days_left = max((goal['deadline'] - datetime.now().date()).days, 0)
        color = "#30d158" if progress >= 100 else "#ff9f0a" if progress > 50 else "#ff453a"
        st.markdown(f"""
        <div class="budget-card animate-in">
            <div class="budget-header"><span class="budget-category">{t('goal_progress')}</span><span style="color: {color}; font-weight: 600;">{progress:.1f}%</span></div>
            <div style="color: #86868b;">{t('goal_current')}: {sym} {saved:,.2f} / {sym} {goal['amount']:,.2f}</div>
            <div style="color: #86868b;">Prazo: {goal['deadline'].strftime('%d/%m/%Y')} ({days_left} dias restantes)</div>
            <div class="progress-bar-container"><div class="progress-bar-fill" style="width: {progress}%; background: {color};"></div></div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(t("goal_reset")):
            st.session_state.goal = None
            save_all()
            st.rerun()

# ---------- ABA INSIGHTS (CORRIGIDA) ----------
with tab_insights:
    st.markdown(f'<p class="card-title">{t("insights_title")}</p>', unsafe_allow_html=True)
    insights = generate_insights()
    if insights:
        for insight in insights:
            st.markdown(f'<div class="budget-card animate-in" style="padding: 1rem;"><div style="color: #f5f5f7;">{insight}</div></div>', unsafe_allow_html=True)
    else:
        st.info(t("no_data"))

# ---------- ABA EXPORTAR ----------
with tab_export:
    st.markdown(f'<p class="card-title">{t("export_title")}</p>', unsafe_allow_html=True)
    if st.session_state.transactions:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(export_pdf("pt"), unsafe_allow_html=True)
        with col2:
            st.markdown(export_pdf("en"), unsafe_allow_html=True)
    else:
        st.warning(t("no_transactions"))

# ---------- ABA HISTÓRICO ----------
with tab_hist:
    if st.session_state.transactions:
        for idx, tx in enumerate(sorted(st.session_state.transactions, key=lambda x: x['date'], reverse=True)):
            amt_class = "income" if tx['type'] == 'income' else "expense"
            sign = "+" if tx['type'] == 'income' else "-"
            date_str = tx['date'].strftime('%d/%m/%Y %H:%M') if st.session_state.lang == 'pt' else tx['date'].strftime('%b %d, %H:%M')
            cat_images = {
                "Salary": "💰", "Food": "🍔", "Transport": "🚌", "Housing": "🏠",
                "Leisure": "🎮", "Health": "💊", "Education": "📚", "Investment": "📈", "Other": "📦",
                "Salário": "💰", "Alimentação": "🍕", "Transporte": "🚗", "Moradia": "🏡",
                "Lazer": "🎬", "Saúde": "🩺", "Educação": "🎓", "Investimento": "💹", "Outros": "📌"
            }
            img = cat_images.get(tx['category'], "💲")
            col_info, col_del = st.columns([10, 1])
            with col_info:
                st.markdown(f"""
                <div class="tx-row">
                    <div class="tx-left"><div class="tx-img">{img}</div><div><div class="tx-name">{tx['description']}</div><div class="tx-cat">{tx['category']}</div></div></div>
                    <div><div class="tx-amount {amt_class}">{sign}{sym} {tx['value']:,.2f}</div><div class="tx-date">{date_str}</div></div>
                </div>
                """, unsafe_allow_html=True)
            with col_del:
                if st.button("🗑️", key=f"del_{idx}"):
                    st.session_state.transactions.remove(tx)
                    save_all()
                    st.rerun()
    else:
        st.info(t("no_transactions"))

# ============ CHAT FLUTUANTE (MINIMALISTA) ============
st.markdown("""
<button class="chat-fab" id="chatFab">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
    </svg>
</button>
""", unsafe_allow_html=True)

st.markdown("""
<script>
const fab = document.getElementById('chatFab');
const popup = document.getElementById('chatPopup');
fab.addEventListener('click', () => {
    if (popup.style.display === 'flex') {
        popup.style.display = 'none';
    } else {
        popup.style.display = 'flex';
    }
});
</script>
""", unsafe_allow_html=True)

if st.session_state.show_chat:
    st.markdown('<div class="chat-popup" id="chatPopup" style="display: flex;">', unsafe_allow_html=True)
else:
    st.markdown('<div class="chat-popup" id="chatPopup" style="display: none;">', unsafe_allow_html=True)

st.markdown(f'<div class="chat-header"><span>{t("chat_title")}</span><span style="cursor:pointer;" onclick="document.getElementById(\'chatPopup\').style.display=\'none\'">✕</span></div>', unsafe_allow_html=True)
st.markdown('<div class="chat-body">', unsafe_allow_html=True)

for msg in st.session_state.chat_history:
    css_class = "user-msg" if msg["role"] == "user" else "bot-msg"
    st.markdown(f'<div class="message-bubble {css_class}">{msg["content"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
with st.form(key="chat_form", clear_on_submit=True):
    cols = st.columns([5, 1])
    with cols[0]:
        user_input = st.text_input("", placeholder=t("chat_placeholder"), label_visibility="collapsed", key="chat_input")
    with cols[1]:
        submitted = st.form_submit_button("➤")
    if submitted and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        model = st.session_state.chat_model
        api_key = st.session_state.get("gemini_key", "") or st.session_state.get("openai_key", "")
        if model == "Gemini" and api_key and GEMINI_AVAILABLE:
            try:
                response = generate_gemini_response(user_input, api_key)
            except Exception as e:
                response = f"Erro Gemini: {str(e)}"
        elif model == "ChatGPT" and api_key and OPENAI_AVAILABLE:
            try:
                response = generate_openai_response(user_input, api_key)
            except Exception as e:
                response = f"Erro OpenAI: {str(e)}"
        else:
            response = offline_chat_response(user_input)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        save_all()
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Configuração do chat na barra lateral
with st.sidebar:
    st.markdown("### Configuração do Chat")
    st.session_state.chat_model = st.selectbox(t("chat_model_label"), ["Offline", "Gemini", "ChatGPT"], index=0)
    if st.session_state.chat_model == "Gemini":
        st.session_state.gemini_key = st.text_input(t("gemini_key_label"), type="password")
    elif st.session_state.chat_model == "ChatGPT":
        st.session_state.openai_key = st.text_input(t("openai_key_label"), type="password")
    if st.button(t("clear_chat_history")):
        st.session_state.chat_history = []
        save_all()
        st.rerun()

st.markdown(f"""
<div style="text-align: center; color: #6d6d72; font-size: 0.7rem; padding: 2rem 0 1rem 0;">
    {t("footer")}
</div>
""", unsafe_allow_html=True)