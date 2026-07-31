import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from fpdf import FPDF
import base64, io, time
from supabase import create_client, Client

# ============ IAs OPCIONAIS ============
try:
    import google.generativeai as genai
    GEMINI = True
except ImportError:
    GEMINI = False

try:
    import openai
    OPENAI = True
except ImportError:
    OPENAI = False

# ============ SENDGRID OPCIONAL ============
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

st.set_page_config(page_title="FinBot", page_icon="🤖", layout="wide")

# Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# SendGrid
SENDGRID_API_KEY = st.secrets.get("SENDGRID_API_KEY", "")
FROM_EMAIL = st.secrets.get("FROM_EMAIL", "")
SEND_NOTIFICATIONS = SENDGRID_AVAILABLE and bool(SENDGRID_API_KEY)

def send_email(to_email, subject, body):
    if not SEND_NOTIFICATIONS or not st.session_state.get("email_enabled", True):
        return
    try:
        message = Mail(from_email=FROM_EMAIL, to_emails=to_email, subject=subject, html_content=body)
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
    except Exception as e:
        error_msg = str(e)
        if "rate limit" in error_msg.lower():
            st.toast("⚠️ Cota de emails excedida. Tente novamente mais tarde.", icon="📧")
        else:
            st.error(f"Erro ao enviar email: {e}")

# ============ TRADUÇÕES ============
T = {
  "pt": {
    "title": "FinBot", "subtitle": "Seu assistente financeiro inteligente",
    "income": "Receitas", "expenses": "Despesas", "balance": "Saldo",
    "transactions": "transações", "positive": "Disponível", "negative": "Negativo",
    "new_transaction": "Nova transação", "type": "Tipo", "type_income": "Receita", "type_expense": "Despesa",
    "description": "Descrição", "desc_placeholder": "Ex: Salário, Aluguel, Ifood...",
    "amount": "Valor", "date": "Data", "category": "Categoria",
    "categories": ["Salário","Alimentação","Transporte","Moradia","Lazer","Saúde","Educação","Investimento","Outros"],
    "add_button": "Adicionar transação", "delete": "Excluir", "no_transactions": "Nenhuma transação ainda",
    "tab_dashboard": "Painel", "tab_add": "Adicionar", "tab_history": "Histórico",
    "tab_budgets": "Orçamentos", "tab_goals": "Metas", "tab_insights": "Insights",
    "tab_export": "Exportar", "tab_reminders": "Lembretes",
    "no_expenses": "Nenhuma despesa registrada", "summary": "Resumo", "of_income_spent": "da receita gasta",
    "on_track": "Sob controle", "watch_out": "Atenção", "over_budget": "Estourado",
    "total_transactions": "Total de transações", "largest_expense": "Maior despesa",
    "top_category": "Categoria principal", "average_expense": "Despesa média",
    "daily_average": "Média diária (30d)", "trend": "Tendência (7d)", "no_data": "Sem dados",
    "footer": "FinBot", "choose_language": "Idioma", "portuguese": "Português", "english": "English",
    "currency": "R$", "fill_all": "Preencha todos os campos",
    "budget_title": "Definir Orçamentos", "set_budget": "Definir limite",
    "current_spending": "Gasto atual", "remaining": "Restante", "clear_budgets": "Limpar orçamentos",
    "goal_title": "Metas Financeiras", "goal_amount": "Valor da meta", "goal_deadline": "Prazo final",
    "goal_current": "Economizado", "goal_progress": "Progresso", "goal_set": "Definir meta", "goal_reset": "Limpar meta",
    "insights_title": "Análise Inteligente",
    "export_title": "Exportar PDF", "export_pdf_pt": "Baixar PDF (PT)", "export_pdf_en": "Baixar PDF (EN)",
    "chat_title": "Consultor IA", "chat_placeholder": "Digite sua dúvida...",
    "login_title": "Entrar no FinBot", "login_user": "Email", "login_pass": "Senha",
    "login_btn": "Entrar", "login_error": "Email ou senha inválidos.",
    "register_btn": "Criar conta", "register_success": "Conta criada! Verifique seu email.",
    "username_taken": "Email já cadastrado.", "logout": "Sair",
    "chat_suggestions": ["Como economizar?","Onde investir?","Dicas para orçamento","Metas financeiras"],
    "monthly_comparison": "Comparativo Mensal", "forecast": "Previsão", "annual_summary": "Resumo Anual",
    "alert_budget": "⚠️ Orçamento estourado!",
    "reminder_title": "Lembretes", "reminder_desc": "Cadastre contas a pagar.",
    "reminder_description": "Descrição", "reminder_amount": "Valor", "reminder_due_date": "Vencimento",
    "reminder_add": "Adicionar", "reminder_delete": "Excluir",
    "reminder_paid": "Pago", "reminder_pending": "Pendente", "reminder_overdue": "Vencido!",
    "no_reminders": "Nenhum lembrete.", "clear_reminders": "Limpar todos",
    "send_resume": "Enviar resumo por email",
    "email_toggle": "Ativar emails automáticos"
  },
  "en": {
    "title": "FinBot", "subtitle": "Your intelligent financial assistant",
    "income": "Income", "expenses": "Expenses", "balance": "Balance",
    "transactions": "transactions", "positive": "Available", "negative": "Overdrawn",
    "new_transaction": "New transaction", "type": "Type", "type_income": "Income", "type_expense": "Expense",
    "description": "Description", "desc_placeholder": "e.g., Salary, Rent, Food...",
    "amount": "Amount", "date": "Date", "category": "Category",
    "categories": ["Salary","Food","Transport","Housing","Leisure","Health","Education","Investment","Other"],
    "add_button": "Add transaction", "delete": "Delete", "no_transactions": "No transactions yet",
    "tab_dashboard": "Dashboard", "tab_add": "Add", "tab_history": "History",
    "tab_budgets": "Budgets", "tab_goals": "Goals", "tab_insights": "Insights",
    "tab_export": "Export", "tab_reminders": "Reminders",
    "no_expenses": "No expenses recorded", "summary": "Summary", "of_income_spent": "of income spent",
    "on_track": "On track", "watch_out": "Watch out", "over_budget": "Over budget",
    "total_transactions": "Total transactions", "largest_expense": "Largest expense",
    "top_category": "Top category", "average_expense": "Average expense",
    "daily_average": "Daily average (30d)", "trend": "Trend (7d)", "no_data": "No data",
    "footer": "FinBot", "choose_language": "Language", "portuguese": "Português", "english": "English",
    "currency": "$", "fill_all": "Please fill all fields",
    "budget_title": "Set Budgets", "set_budget": "Set limit",
    "current_spending": "Current spending", "remaining": "Remaining", "clear_budgets": "Clear budgets",
    "goal_title": "Financial Goals", "goal_amount": "Goal amount", "goal_deadline": "Deadline",
    "goal_current": "Saved", "goal_progress": "Progress", "goal_set": "Set goal", "goal_reset": "Clear goal",
    "insights_title": "Smart Insights",
    "export_title": "Export PDF", "export_pdf_pt": "Download PDF (PT)", "export_pdf_en": "Download PDF (EN)",
    "chat_title": "AI Advisor", "chat_placeholder": "Type your question...",
    "login_title": "Login to FinBot", "login_user": "Email", "login_pass": "Password",
    "login_btn": "Login", "login_error": "Invalid email or password.",
    "register_btn": "Sign up", "register_success": "Account created! Check your email.",
    "username_taken": "Email already registered.", "logout": "Logout",
    "chat_suggestions": ["How to save?","Where to invest?","Budget tips","Financial goals"],
    "monthly_comparison": "Monthly Comparison", "forecast": "Forecast", "annual_summary": "Annual Summary",
    "alert_budget": "⚠️ Budget exceeded!",
    "reminder_title": "Reminders", "reminder_desc": "Add bills to pay.",
    "reminder_description": "Description", "reminder_amount": "Amount", "reminder_due_date": "Due date",
    "reminder_add": "Add", "reminder_delete": "Delete",
    "reminder_paid": "Paid", "reminder_pending": "Pending", "reminder_overdue": "Overdue!",
    "no_reminders": "No reminders.", "clear_reminders": "Clear all",
    "send_resume": "Send summary by email",
    "email_toggle": "Enable automatic emails"
  }
}

# ========== FUNÇÕES SUPABASE ==========
def load_transactions(uid):
    r = supabase.table("transactions").select("*").eq("user_id", uid).order("date", desc=True).execute()
    data = r.data or []
    for tx in data:
        if isinstance(tx['date'], str): tx['date'] = datetime.fromisoformat(tx['date'])
    return data

def save_transaction(uid, tx):
    supabase.table("transactions").insert({"user_id": uid, "date": tx['date'].isoformat(), "description": tx['description'], "value": tx['value'], "type": tx['type'], "category": tx['category']}).execute()

def delete_transaction(tid):
    supabase.table("transactions").delete().eq("id", tid).execute()

def load_budgets(uid):
    r = supabase.table("budgets").select("*").eq("user_id", uid).execute()
    return {row['category']: float(row['limit_value']) for row in (r.data or [])}

def save_budget(uid, cat, limit):
    supabase.table("budgets").upsert({"user_id": uid, "category": cat, "limit_value": limit}).execute()

def clear_budgets(uid):
    supabase.table("budgets").delete().eq("user_id", uid).execute()

def load_goal(uid):
    r = supabase.table("goals").select("*").eq("user_id", uid).execute()
    if r.data:
        g = r.data[0]
        return {'amount': float(g['amount']), 'deadline': datetime.strptime(g['deadline'], '%Y-%m-%d').date()}
    return None

def save_goal(uid, amount, deadline):
    supabase.table("goals").upsert({"user_id": uid, "amount": amount, "deadline": deadline.isoformat()}).execute()

def delete_goal(uid):
    supabase.table("goals").delete().eq("user_id", uid).execute()

def load_chat(uid):
    r = supabase.table("chat_history").select("*").eq("user_id", uid).order("created_at", desc=False).execute()
    return [{"role": row['role'], "content": row['content']} for row in (r.data or [])]

def save_chat(uid, role, content):
    supabase.table("chat_history").insert({"user_id": uid, "role": role, "content": content}).execute()

def clear_chat(uid):
    supabase.table("chat_history").delete().eq("user_id", uid).execute()

def load_reminders(uid):
    r = supabase.table("reminders").select("*").eq("user_id", uid).order("due_date", desc=False).execute()
    data = r.data or []
    for rem in data:
        if isinstance(rem['due_date'], str): rem['due_date'] = datetime.fromisoformat(rem['due_date']).date()
    return data

def save_reminder(uid, desc, amount, due):
    supabase.table("reminders").insert({"user_id": uid, "description": desc, "amount": amount, "due_date": due.isoformat(), "paid": False}).execute()

def toggle_reminder(rid, paid):
    supabase.table("reminders").update({"paid": paid}).eq("id", rid).execute()

def delete_reminder(rid):
    supabase.table("reminders").delete().eq("id", rid).execute()

def clear_reminders(uid):
    supabase.table("reminders").delete().eq("user_id", uid).execute()

# ========== ESTADO ==========
if 'lang' not in st.session_state: st.session_state.lang = None
if 'user' not in st.session_state: st.session_state.user = None
if 'chat_model' not in st.session_state: st.session_state.chat_model = "Offline"
if 'show_chat' not in st.session_state: st.session_state.show_chat = False
if 'memory' not in st.session_state: st.session_state.memory = []
if 'budget_emailed_today' not in st.session_state: st.session_state.budget_emailed_today = {}
if 'reminder_email_sent' not in st.session_state: st.session_state.reminder_email_sent = False
if 'email_enabled' not in st.session_state: st.session_state.email_enabled = True

# ========== IDIOMA ==========
if st.session_state.lang is None:
    st.markdown("<style>.stApp{background:#0a0a0a;}</style>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🇧🇷 Português", use_container_width=True): st.session_state.lang = "pt"; st.rerun()
    with c2:
        if st.button("🇺🇸 English", use_container_width=True): st.session_state.lang = "en"; st.rerun()
    st.stop()

def t(key): return T[st.session_state.lang][key]
sym = t("currency")

# ========== LOGIN / REGISTRO ==========
if not st.session_state.user:
    st.markdown("<style>.stApp{background:#0a0a0a;} .login-box{max-width:420px;margin:8% auto;padding:2.5rem 2rem;background:#1c1c1e;border-radius:20px;box-shadow:0 10px 30px rgba(0,0,0,0.5);} h2{color:#f5f5f7;text-align:center;margin-bottom:1.5rem;} .stTextInput>div>div>input{background:#2c2c2e;border:1px solid #3a3a3c;color:#f5f5f7;border-radius:10px;padding:0.75rem 1rem;} .stButton>button{background:#667eea;color:white;border:none;border-radius:10px;padding:0.8rem;font-weight:600;width:100%;transition:background 0.2s;} .stButton>button:hover{background:#5a6fd6;}</style>", unsafe_allow_html=True)
    with st.container():
        st.markdown(f'<div class="login-box"><h2>🤖 {t("login_title")}</h2>', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Login", "Registrar"])
        with tab1:
            with st.form("login_form"):
                email = st.text_input(t("login_user"))
                pwd = st.text_input(t("login_pass"), type="password")
                if st.form_submit_button(t("login_btn")):
                    if not email or not pwd: st.error(t("fill_all"))
                    elif "@" not in email: st.error("Email inválido.")
                    elif len(pwd) < 6: st.error("Senha deve ter pelo menos 6 caracteres.")
                    else:
                        try:
                            auth = supabase.auth.sign_in_with_password({"email": email, "password": pwd})
                            st.session_state.user = auth.user
                            st.rerun()
                        except Exception as e: st.error(f"Erro: {str(e)}")
        with tab2:
            with st.form("register_form"):
                new_email = st.text_input(t("login_user"), key="reg_email")
                new_pwd = st.text_input(t("login_pass"), type="password", key="reg_pwd")
                if st.form_submit_button(t("register_btn")):
                    if not new_email or not new_pwd: st.error(t("fill_all"))
                    elif "@" not in new_email or "." not in new_email.split("@")[-1]: st.error("Email inválido.")
                    elif len(new_pwd) < 6: st.error("Senha deve ter pelo menos 6 caracteres.")
                    else:
                        try:
                            supabase.auth.sign_up({"email": new_email, "password": new_pwd})
                            st.success(t("register_success"))
                        except Exception as e:
                            error_msg = str(e)
                            if "already registered" in error_msg.lower(): st.warning(t("username_taken"))
                            else: st.error(f"Erro: {error_msg}")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ========== DADOS DO USUÁRIO ==========
uid = st.session_state.user.id
user_email = st.session_state.user.email
transactions = load_transactions(uid)
budgets = load_budgets(uid)
goal = load_goal(uid)
chat_history = load_chat(uid)
reminders = load_reminders(uid)

income_total = sum(tx['value'] for tx in transactions if tx['type'] == 'income')
expense_total = sum(tx['value'] for tx in transactions if tx['type'] == 'expense')
balance = income_total - expense_total

# ========== NOTIFICAÇÕES AUTOMÁTICAS (CONTROLADAS) ==========
if reminders and SEND_NOTIFICATIONS and st.session_state.email_enabled:
    overdue = [r for r in reminders if r['due_date'] < datetime.now().date() and not r['paid']]
    if overdue and not st.session_state.reminder_email_sent:
        items = "".join(f"<li>{r['description']}: {sym} {r['amount']:.2f} (vencido em {r['due_date'].strftime('%d/%m/%Y')})</li>" for r in overdue)
        body = f"<h3>🔔 Contas vencidas</h3><p>Você tem {len(overdue)} contas em atraso:</p><ul>{items}</ul>"
        send_email(user_email, "Contas vencidas - FinBot", body)
        st.session_state.reminder_email_sent = True

# ========== CSS ==========
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
*{{font-family:'Inter',sans-serif}}
header, footer, #MainMenu {{display:none!important}}
.stApp{{background:#0a0a0a}}
.block-container{{padding:2rem 3rem;max-width:1200px}}
.logo-area{{display:flex;align-items:center;gap:0.75rem;margin-bottom:2rem}}
.robot-logo{{font-size:36px}}
h1{{font-weight:700!important;color:#f5f5f7!important;font-size:2rem!important}}
.subtitle{{color:#86868b;font-size:0.9rem}}
@keyframes fadeInUp{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:translateY(0)}}}}
@keyframes slideInRight{{from{{transform:translateX(100px);opacity:0}}to{{transform:translateX(0);opacity:1}}}}
@keyframes pulse{{0%{{transform:scale(1)}}50%{{transform:scale(1.05)}}100%{{transform:scale(1)}}}}
.animate-in{{animation:fadeInUp 0.5s ease forwards}}
.metric-card{{
  background:linear-gradient(135deg,#1c1c1e 0%,#2c2c2e 100%);
  padding:1.8rem 1.5rem;border-radius:24px;box-shadow:0 8px 24px rgba(0,0,0,0.3);
  animation:fadeInUp 0.5s ease;transition:transform 0.2s;position:relative;overflow:hidden;
}}
.metric-card:hover{{transform:translateY(-4px)}}
.metric-card::before{{content:'';position:absolute;top:-30px;right:-30px;width:80px;height:80px;border-radius:50%;opacity:0.1}}
.metric-card.income::before{{background:#30d158}}
.metric-card.expense::before{{background:#ff453a}}
.metric-card.balance::before{{background:#667eea}}
.metric-icon{{font-size:2rem;margin-bottom:0.5rem}}
.metric-label{{text-transform:uppercase;letter-spacing:1px;font-size:0.75rem;font-weight:500;color:#86868b;margin-bottom:0.4rem}}
.metric-value{{font-size:2rem;font-weight:700;color:#f5f5f7;line-height:1.2}}
.metric-sub{{color:#6d6d72;font-size:0.8rem;margin-top:0.3rem}}
.alert-budget{{animation:pulse 1s infinite;background:#ff453a!important;color:white!important}}
.card-title{{color:#f5f5f7;font-size:1rem;font-weight:600;margin-bottom:1.5rem}}
.tx-row{{display:flex;align-items:center;justify-content:space-between;padding:0.85rem 0;border-bottom:1px solid #2c2c2e}}
.tx-img{{width:42px;height:42px;border-radius:12px;background:#2c2c2e;display:flex;align-items:center;justify-content:center;font-size:1.5rem;flex-shrink:0}}
.tx-name{{color:#f5f5f7;font-weight:500}}
.tx-cat{{color:#86868b;font-size:0.78rem}}
.tx-amount{{font-weight:550;text-align:right}}
.tx-amount.income{{color:#30d158}}
.tx-amount.expense{{color:#ff453a}}
.tx-date{{color:#6d6d72;font-size:0.72rem;text-align:right}}
.stButton>button{{
  background:#f5f5f7;color:#0a0a0a;border:none;border-radius:14px;
  padding:0.8rem 1.8rem;font-size:0.9rem;font-weight:550;width:100%;cursor:pointer;transition:all 0.2s;
}}
.stButton>button:hover{{background:#e5e5ea;transform:scale(1.02)}}
input, select, .stDateInput>div>input{{background:#2c2c2e!important;border:1px solid #3a3a3c!important;color:#f5f5f7!important;border-radius:12px!important;padding:0.7rem 0.9rem!important;font-size:0.88rem!important}}
.stSelectbox>div{{color:#f5f5f7!important}}
div[data-baseweb="select"] svg{{color:#f5f5f7!important}}
.stTabs [data-baseweb="tab-list"]{{border-bottom:1px solid #2c2c2e;gap:0}}
.stTabs [data-baseweb="tab"]{{padding:0.7rem 1.5rem;font-size:0.9rem;color:#86868b;background:transparent;border:none}}
.stTabs [aria-selected="true"]{{color:#f5f5f7;border-bottom:2px solid #667eea}}
.budget-card{{background:#1c1c1e;padding:1.5rem;border-radius:16px;margin-bottom:1rem;box-shadow:0 2px 12px rgba(0,0,0,0.2)}}
.budget-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem}}
.budget-category{{font-weight:600;color:#f5f5f7;font-size:1rem}}
.progress-bar-container{{width:100%;height:8px;background:#2c2c2e;border-radius:4px;overflow:hidden;margin-top:0.5rem}}
.progress-bar-fill{{height:100%;border-radius:4px;transition:width 0.6s ease}}

/* Chat */
.chat-fab{{
  position:fixed;bottom:30px;right:30px;width:60px;height:60px;border-radius:30px;
  background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
  box-shadow:0 8px 30px rgba(102,126,234,0.5);display:flex;align-items:center;justify-content:center;
  cursor:pointer;z-index:9999;border:none;transition:all 0.3s;
}}
.chat-fab:hover{{transform:scale(1.08)}}
.chat-popup{{
  position:fixed;bottom:100px;right:30px;width:380px;height:550px;
  background:#1c1c1e;border-radius:24px;box-shadow:0 25px 70px rgba(0,0,0,0.6);
  z-index:9998;display:none;flex-direction:column;overflow:hidden;border:1px solid #2c2c2e;
  animation:slideInRight 0.3s ease;
}}
.chat-header{{padding:1rem 1.2rem;background:#2c2c2e;display:flex;justify-content:space-between;align-items:center;color:#f5f5f7;font-weight:600}}
.chat-body{{flex:1;overflow-y:auto;padding:1rem;display:flex;flex-direction:column;gap:0.8rem}}
.message-bubble{{max-width:85%;padding:0.7rem 1rem;border-radius:18px;font-size:0.85rem;line-height:1.5}}
.user-msg{{align-self:flex-end;background:#667eea;color:white;border-bottom-right-radius:6px}}
.bot-msg{{align-self:flex-start;background:#2c2c2e;color:#f5f5f7;border-bottom-left-radius:6px}}
.chat-suggestions{{display:flex;flex-wrap:wrap;gap:0.5rem;padding:0.5rem 1rem 0}}
.chat-suggestion{{background:#2c2c2e;color:#f5f5f7;border:1px solid #3a3a3c;border-radius:20px;padding:0.4rem 1rem;font-size:0.8rem;cursor:pointer}}
.chat-suggestion:hover{{background:#3a3a3c}}
.chat-input-container{{padding:0.8rem;background:#2c2c2e;display:flex;gap:0.5rem}}
.chat-input-container input{{flex:1;background:#3a3a3c;border:none;border-radius:25px;padding:0.6rem 1.2rem;color:white;font-size:0.85rem;outline:none}}
.chat-input-container button{{background:#667eea;border:none;border-radius:50%;width:38px;height:38px;color:white;font-size:1.2rem;cursor:pointer}}

/* Lembretes */
.reminder-card{{background:#1c1c1e;padding:1rem;border-radius:12px;margin-bottom:0.5rem;display:flex;align-items:center;justify-content:space-between}}
.reminder-overdue{{border-left:4px solid #ff453a}}
.reminder-pending{{border-left:4px solid #ff9f0a}}
.reminder-paid{{border-left:4px solid #30d158;opacity:0.7}}
[data-testid="stSidebar"]{{background:#1c1c1e}}
[data-testid="stSidebar"] h3{{color:#f5f5f7}}
</style>
""".replace("{{{{","{").replace("}}}}","}"), unsafe_allow_html=True)

# ========== FUNÇÕES AUX ==========
def insights():
    if not transactions: return []
    df = pd.DataFrame(transactions); df['date'] = pd.to_datetime(df['date'])
    exp = df[df['type'] == 'expense']
    if exp.empty: return [t("no_expenses")]
    ins = []
    top = exp.groupby('category')['value'].sum().idxmax()
    ins.append(f"Sua maior categoria de gasto é **{top}**.")
    now = datetime.now()
    this = exp[exp['date'].dt.month == now.month]['value'].sum()
    prev = exp[exp['date'].dt.month == (now.month-1 if now.month>1 else 12)]['value'].sum()
    if prev > 0 and this > prev:
        ins.append(f"Gastos aumentaram **{((this-prev)/prev)*100:.1f}%** em relação ao mês anterior.")
    for cat, lim in budgets.items():
        spent = exp[exp['category'] == cat]['value'].sum()
        if lim > 0 and spent > lim*0.8:
            ins.append(f"Você já usou mais de 80% do orçamento de **{cat}**.")
    if len(exp) > 10: ins.append("Muitas transações este mês. Revise pequenos gastos.")
    return ins[:5]

def export_pdf(lang):
    if not transactions: return None
    s = T[lang]["currency"]
    pdf = FPDF(); pdf.add_page()
    pdf.set_font("Arial",'B',16)
    pdf.cell(0,10,txt="FinBot - Relatório Financeiro" if lang=="pt" else "FinBot - Financial Report",ln=True,align='C')
    pdf.ln(5); pdf.set_font("Arial",'',10)
    pdf.cell(0,8,txt=f"{T[lang]['pdf_balance']}: {s} {balance:,.2f}",ln=True)
    pdf.cell(0,8,txt=f"{T[lang]['pdf_income']}: {s} {income_total:,.2f}",ln=True)
    pdf.cell(0,8,txt=f"{T[lang]['pdf_expense']}: {s} {expense_total:,.2f}",ln=True)
    pdf.ln(5); pdf.set_font("Arial",'B',12)
    pdf.cell(0,10,txt=T[lang]["pdf_recent_transactions"],ln=True)
    pdf.set_font("Arial",'',9)
    for tx in sorted(transactions, key=lambda x: x['date'], reverse=True)[:20]:
        ds = tx['date'].strftime('%d/%m/%Y') if lang=="pt" else tx['date'].strftime('%Y-%m-%d')
        tipo = "Receita" if tx['type']=='income' else "Despesa" if lang=="pt" else "Income" if tx['type']=='income' else "Expense"
        pdf.cell(30,6,txt=ds,border=1)
        pdf.cell(50,6,txt=tx['description'][:25],border=1)
        pdf.cell(30,6,txt=tipo,border=1)
        pdf.cell(30,6,txt=tx['category'][:15],border=1)
        pdf.cell(30,6,txt=f"{tx['value']:.2f}",border=1)
        pdf.ln()
    pdf.ln(10); pdf.set_font("Arial",'',8)
    pdf.cell(0,10,txt=T[lang]["pdf_generated"],ln=True,align='C')
    b64 = base64.b64encode(pdf.output(dest='S').encode('latin-1')).decode()
    return f'<a href="data:application/pdf;base64,{b64}" download="finbot_{lang}.pdf" style="color:#f5f5f7;text-decoration:none;background:#2c2c2e;padding:0.5rem 1rem;border-radius:8px;">📥 {T[lang]["export_pdf_pt"] if lang=="pt" else T[lang]["export_pdf_en"]}</a>'

def stream_response(prompt, model, key):
    """Generator para streaming do chat."""
    if model == "Offline" or not key:
        df = pd.DataFrame(transactions) if transactions else pd.DataFrame()
        exp = df[df['type']=='expense'] if not df.empty else pd.DataFrame()
        p = prompt.lower()
        if any(w in p for w in ["saldo","balance"]): text = f"Saldo: {sym} {balance:,.2f}. " + ("Positivo!" if balance>=0 else "Negativo!")
        elif any(w in p for w in ["gasto","despesa","spent"]):
            if exp.empty: text = "Sem despesas."
            else: text = f"Total gasto: {sym} {exp['value'].sum():,.2f}. Maior: {exp.groupby('category')['value'].sum().idxmax()}."
        elif any(w in p for w in ["economizar","save"]):
            if exp.empty: text = "Registre despesas."
            else: text = f"Reduza gastos com {exp.groupby('category')['value'].sum().idxmax()}."
        elif any(w in p for w in ["investir","invest"]): text = "Invista em renda fixa (Tesouro Direto, CDB). Mantenha reserva de emergência."
        elif any(w in p for w in ["orçamento","budget"]):
            if not budgets: text = "Defina orçamentos na aba Orçamentos."
            else:
                msg = "Orçamentos:\n"
                for cat, lim in budgets.items():
                    spent = exp[exp['category']==cat]['value'].sum() if not exp.empty else 0
                    msg += f"- {cat}: {sym} {spent:,.2f} de {sym} {lim:,.2f} ({(spent/lim)*100:.0f}%)\n" if lim>0 else f"- {cat}: sem limite\n"
                text = msg
        elif any(w in p for w in ["meta","goal"]):
            if not goal: text = "Nenhuma meta definida."
            else:
                saved = balance if balance>0 else 0
                prog = min(saved/goal['amount']*100,100) if goal['amount']>0 else 0
                days = max((goal['deadline']-datetime.now().date()).days,0)
                text = f"Meta: {sym} {goal['amount']:,.2f}. Progresso: {prog:.1f}%. {days} dias restantes."
        else: text = "Pergunte sobre saldo, gastos, economia, investimentos, orçamentos ou metas!"
        for i in range(len(text)):
            yield text[:i+1]
            time.sleep(0.02)
        return

    mem = st.session_state.memory[-5:]
    ctx = "".join(f"{m['role']}: {m['content']}\n" for m in mem) + f"User: {prompt}\nAssistant:"
    if model == "Gemini" and key and GEMINI:
        genai.configure(api_key=key)
        resp = genai.GenerativeModel('gemini-pro').generate_content(ctx).text
    elif model == "ChatGPT" and key and OPENAI:
        openai.api_key = key
        msgs = [{"role":"system","content":"Consultor financeiro amigável."}]
        for m in mem: msgs.append({"role":m['role'],"content":m['content']})
        msgs.append({"role":"user","content":prompt})
        resp = openai.ChatCompletion.create(model="gpt-3.5-turbo",messages=msgs,max_tokens=200).choices[0].message.content
    else: resp = "Modelo não disponível."
    for i in range(len(resp)):
        yield resp[:i+1]
        time.sleep(0.02)

# ========== INTERFACE ==========
col1, col2 = st.columns([4,1])
with col1:
    st.markdown(f'<div class="logo-area"><div class="robot-logo">🤖</div><div><h1>{t("title")}</h1><div class="subtitle">{t("subtitle")}</div></div></div>', unsafe_allow_html=True)
with col2:
    lang = st.selectbox("", ["Português","English"], index=0 if st.session_state.lang=="pt" else 1, label_visibility="collapsed")
    if (lang=="Português" and st.session_state.lang!="pt") or (lang=="English" and st.session_state.lang!="en"):
        st.session_state.lang = "pt" if lang=="Português" else "en"; st.rerun()
    if st.button("🚪", help=t("logout")):
        supabase.auth.sign_out(); st.session_state.user = None; st.rerun()

c1,c2,c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="metric-card income animate-in"><div class="metric-icon">💰</div><div class="metric-label">{t("income")}</div><div class="metric-value">{sym} {income_total:,.2f}</div><div class="metric-sub">{len([tx for tx in transactions if tx["type"]=="income"])} {t("transactions")}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card expense animate-in"><div class="metric-icon">💸</div><div class="metric-label">{t("expenses")}</div><div class="metric-value">{sym} {expense_total:,.2f}</div><div class="metric-sub">{len([tx for tx in transactions if tx["type"]=="expense"])} {t("transactions")}</div></div>', unsafe_allow_html=True)
with c3:
    cor = "#30d158" if balance>=0 else "#ff453a"
    st.markdown(f'<div class="metric-card balance animate-in"><div class="metric-icon">📊</div><div class="metric-label">{t("balance")}</div><div class="metric-value" style="color:{cor}">{sym} {balance:,.2f}</div><div class="metric-sub">{t("positive") if balance>=0 else t("negative")}</div></div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

tabs = st.tabs([t("tab_add"), t("tab_dashboard"), t("tab_budgets"), t("tab_goals"), t("tab_insights"), t("tab_export"), t("tab_reminders"), t("tab_history")])

# ABA ADICIONAR
with tabs[0]:
    col, _ = st.columns([1,1])
    with col:
        st.markdown(f'<p class="card-title">{t("new_transaction")}</p>', unsafe_allow_html=True)
        tipo = st.selectbox(t("type"), [t("type_income"), t("type_expense")])
        code = "income" if tipo==t("type_income") else "expense"
        desc = st.text_input(t("description"), placeholder=t("desc_placeholder"))
        v, d = st.columns(2)
        val = v.number_input(t("amount"), min_value=0.01, value=50.0, step=10.0, format="%.2f")
        date = d.date_input(t("date"), value=datetime.now().date())
        cat = st.selectbox(t("category"), t("categories"))
        if st.button(t("add_button"), use_container_width=True):
            if desc and val>0:
                save_transaction(uid, {'date':datetime.now(),'description':desc,'value':val,'type':code,'category':cat})
                st.success("Adicionado!" if st.session_state.lang=='pt' else "Added!"); st.rerun()
            else: st.warning(t("fill_all"))

# ABA PAINEL
with tabs[1]:
    if transactions:
        df = pd.DataFrame(transactions); df['date'] = pd.to_datetime(df['date'])
        exp = df[df['type']=='expense'].copy()
        if not exp.empty:
            exp['date'] = pd.to_datetime(exp['date'])
            cat_data = exp.groupby('category')['value'].sum().sort_values()
            fig = go.Figure(go.Bar(y=cat_data.index, x=cat_data.values, orientation='h', marker=dict(color='#f5f5f7',cornerradius=6)))
            fig.update_layout(height=300, margin=dict(l=0,r=100,t=20,b=20), template='plotly_dark', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar':False})
        else: st.info(t("no_expenses"))
        # Comparativo mensal
        st.markdown(f'<p class="card-title">{t("monthly_comparison")}</p>', unsafe_allow_html=True)
        df['month'] = df['date'].dt.to_period('M').astype(str)
        inc_m = df[df['type']=='income'].groupby('month')['value'].sum()
        exp_m = df[df['type']=='expense'].groupby('month')['value'].sum()
        meses = sorted(set(list(inc_m.index)+list(exp_m.index)))
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name=t('income'), x=meses, y=[inc_m.get(m,0) for m in meses], marker=dict(color='#30d158')))
        fig2.add_trace(go.Bar(name=t('expenses'), x=meses, y=[exp_m.get(m,0) for m in meses], marker=dict(color='#ff453a')))
        fig2.update_layout(barmode='group', height=300, template='plotly_dark', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar':False})
        # Previsão
        if not exp.empty:
            st.markdown(f'<p class="card-title">{t("forecast")}</p>', unsafe_allow_html=True)
            daily = exp.set_index('date').resample('D')['value'].sum().reset_index()
            daily['num'] = (daily['date']-daily['date'].min()).dt.days
            if len(daily)>1:
                from sklearn.linear_model import LinearRegression
                X = daily['num'].values.reshape(-1,1); y = daily['value'].values
                model = LinearRegression().fit(X,y)
                fut = np.arange(0, daily['num'].max()+30).reshape(-1,1)
                preds = model.predict(fut)
                fig3 = go.Figure()
                fig3.add_trace(go.Scatter(x=daily['date'], y=y, mode='lines+markers', name='Gasto diário', line=dict(color='#ff453a')))
                fig3.add_trace(go.Scatter(x=[daily['date'].min()+timedelta(days=int(d)) for d in fut.flatten()], y=preds, mode='lines', name='Tendência', line=dict(dash='dash',color='#667eea')))
                fig3.update_layout(height=250, template='plotly_dark', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar':False})
        # Resumo anual
        st.markdown(f'<p class="card-title">{t("annual_summary")}</p>', unsafe_allow_html=True)
        y_inc = df[(df['type']=='income')&(df['date'].dt.year==datetime.now().year)]['value'].sum()
        y_exp = df[(df['type']=='expense')&(df['date'].dt.year==datetime.now().year)]['value'].sum()
        y_bal = y_inc - y_exp
        c1,c2,c3 = st.columns(3)
        c1.markdown(f'<div class="metric-card income"><div class="metric-label">Receita Anual</div><div class="metric-value">{sym} {y_inc:,.2f}</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-card expense"><div class="metric-label">Despesa Anual</div><div class="metric-value">{sym} {y_exp:,.2f}</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="metric-card balance"><div class="metric-label">Saldo Anual</div><div class="metric-value" style="color:{"#30d158" if y_bal>=0 else "#ff453a"}">{sym} {y_bal:,.2f}</div></div>', unsafe_allow_html=True)
        # Alertas de orçamento + email controlado
        today_str = datetime.now().date().isoformat()
        for cat, lim in budgets.items():
            spent = exp[exp['category']==cat]['value'].sum() if not exp.empty else 0
            if lim>0 and spent>lim:
                st.markdown(f'<div class="metric-card expense alert-budget"><div class="metric-label">{t("alert_budget")} {cat}</div><div class="metric-value" style="font-size:1.2rem">{sym} {spent:,.2f} / {sym} {lim:,.2f}</div></div>', unsafe_allow_html=True)
                if SEND_NOTIFICATIONS and st.session_state.email_enabled:
                    if today_str not in st.session_state.budget_emailed_today:
                        st.session_state.budget_emailed_today = {today_str: set()}
                    if cat not in st.session_state.budget_emailed_today.get(today_str, set()):
                        body = f"<h3>⚠️ Orçamento estourado!</h3><p>A categoria <b>{cat}</b> ultrapassou o limite de {sym} {lim:,.2f}.</p><p>Gasto atual: {sym} {spent:,.2f}</p>"
                        send_email(user_email, f"Alerta de orçamento - {cat}", body)
                        if today_str not in st.session_state.budget_emailed_today:
                            st.session_state.budget_emailed_today[today_str] = set()
                        st.session_state.budget_emailed_today[today_str].add(cat)
    else: st.info(t("no_data"))

# ABA ORÇAMENTOS
with tabs[2]:
    st.markdown(f'<p class="card-title">{t("budget_title")}</p>', unsafe_allow_html=True)
    cats = [c for c in t("categories") if c not in ["Salário","Salary"]]
    c1,c2,c3 = st.columns([2,2,1])
    sel = c1.selectbox(t("category_select"), cats, key="bcat")
    lim = c2.number_input(f"{t('set_budget')} ({sym})", min_value=0.0, value=500.0, step=50.0, format="%.2f", key="bval")
    if c3.button("➕", key="addb"):
        save_budget(uid, sel, lim)
        st.success(t("budget_added")); st.rerun()
    st.markdown("---")
    if not budgets: st.info(t("no_budgets"))
    else:
        df_exp = pd.DataFrame(transactions) if transactions else pd.DataFrame()
        cur = df_exp[df_exp['type']=='expense'].groupby('category')['value'].sum().to_dict() if not df_exp.empty else {}
        for cat, lim in budgets.items():
            spent = cur.get(cat,0)
            pct = min(spent/lim*100,100) if lim>0 else 100
            cor = "#30d158" if pct<50 else "#ff9f0a" if pct<80 else "#ff453a"
            st.markdown(f'<div class="budget-card animate-in"><div class="budget-header"><span class="budget-category">{cat}</span><span style="color:{cor}">{t("on_track") if pct<50 else t("watch_out") if pct<80 else t("over_budget")}</span></div><div style="color:#86868b">{t("current_spending")}: {sym} {spent:,.2f} | {t("remaining")}: {sym} {lim-spent:,.2f}</div><div class="progress-bar-container"><div class="progress-bar-fill" style="width:{pct}%;background:{cor}"></div></div><div style="text-align:right;font-size:0.8rem;color:#86868b">{pct:.1f}%</div></div>', unsafe_allow_html=True)
        if st.button(t("clear_budgets")):
            clear_budgets(uid); st.rerun()

# ABA METAS
with tabs[3]:
    st.markdown(f'<p class="card-title">{t("goal_title")}</p>', unsafe_allow_html=True)
    c1,c2,c3 = st.columns([2,2,1])
    amt = c1.number_input(f"{t('goal_amount')} ({sym})", min_value=0.0, value=1000.0, step=100.0, format="%.2f", key="gamt")
    dead = c2.date_input(t("goal_deadline"), min_value=datetime.now().date(), key="gdead")
    if c3.button(t("goal_set"), key="setg"):
        save_goal(uid, amt, dead); st.success(t("goal_set_success")); st.rerun()
    if goal:
        saved = balance if balance>0 else 0
        prog = min(saved/goal['amount']*100,100) if goal['amount']>0 else 100
        days = max((goal['deadline']-datetime.now().date()).days,0)
        cor = "#30d158" if prog>=100 else "#ff9f0a" if prog>50 else "#ff453a"
        st.markdown(f'<div class="budget-card animate-in"><div class="budget-header"><span class="budget-category">{t("goal_progress")}</span><span style="color:{cor}">{prog:.1f}%</span></div><div style="color:#86868b">{t("goal_current")}: {sym} {saved:,.2f} / {sym} {goal["amount"]:,.2f}</div><div style="color:#86868b">Prazo: {goal["deadline"].strftime("%d/%m/%Y")} ({days} dias restantes)</div><div class="progress-bar-container"><div class="progress-bar-fill" style="width:{prog}%;background:{cor}"></div></div></div>', unsafe_allow_html=True)
        if st.button(t("goal_reset")): delete_goal(uid); st.rerun()

# ABA INSIGHTS
with tabs[4]:
    st.markdown(f'<p class="card-title">{t("insights_title")}</p>', unsafe_allow_html=True)
    ins = insights()
    if ins:
        for i in ins: st.markdown(f'<div class="budget-card animate-in" style="padding:1rem"><div style="color:#f5f5f7">{i}</div></div>', unsafe_allow_html=True)
    else: st.info(t("no_data"))

# ABA EXPORTAR
with tabs[5]:
    st.markdown(f'<p class="card-title">{t("export_title")}</p>', unsafe_allow_html=True)
    if transactions:
        c1,c2 = st.columns(2)
        c1.markdown(export_pdf("pt"), unsafe_allow_html=True)
        c2.markdown(export_pdf("en"), unsafe_allow_html=True)
    else: st.warning(t("no_transactions"))

# ABA LEMBRETES
with tabs[6]:
    st.markdown(f'<p class="card-title">{t("reminder_title")}</p>', unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns([3,2,2,1])
    desc = c1.text_input(t("reminder_description"), key="rdesc")
    amt_r = c2.number_input(t("reminder_amount"), min_value=0.01, value=50.0, step=10.0, format="%.2f", key="ramt")
    due_r = c3.date_input(t("reminder_due_date"), value=datetime.now().date(), key="rdue")
    if c4.button("➕", key="addr"):
        save_reminder(uid, desc, amt_r, due_r); st.rerun()
    st.markdown("---")
    if reminders:
        for rem in reminders:
            due = rem['due_date']; paid = rem['paid']
            days = (due - datetime.now().date()).days
            if paid: cls, emoji = "reminder-paid", "✅"
            elif days<0: cls, emoji = "reminder-overdue", "🔴"
            else: cls, emoji = "reminder-pending", "🟡"
            c1,c2 = st.columns([10,1])
            with c1:
                st.markdown(f'<div class="reminder-card {cls}"><div><span style="font-weight:500">{rem["description"]}</span><br><span style="color:#86868b;font-size:0.8rem">{t("reminder_amount")}: {sym} {rem["amount"]:.2f} | {t("date")}: {due.strftime("%d/%m/%Y")} ({days} dias)</span></div><div><span style="font-size:1.2rem">{emoji}</span></div></div>', unsafe_allow_html=True)
            with c2:
                if st.button("✓" if not paid else "↩", key=f"pay_{rem['id']}"):
                    toggle_reminder(rem['id'], not paid); st.rerun()
                if st.button("🗑️", key=f"delr_{rem['id']}"):
                    delete_reminder(rem['id']); st.rerun()
        if st.button(t("clear_reminders")): clear_reminders(uid); st.rerun()
    else: st.info(t("no_reminders"))

# Notificação toast
if reminders:
    ovd = [r for r in reminders if r['due_date']<datetime.now().date() and not r['paid']]
    if ovd: st.toast(f"⚠️ Você tem {len(ovd)} contas vencidas!", icon="🔔")

# ABA HISTÓRICO
with tabs[7]:
    if transactions:
        for tx in sorted(transactions, key=lambda x: x['date'], reverse=True):
            cls = "income" if tx['type']=='income' else "expense"
            sign = "+" if tx['type']=='income' else "-"
            ds = tx['date'].strftime('%d/%m/%Y %H:%M') if st.session_state.lang=='pt' else tx['date'].strftime('%b %d, %H:%M')
            icons = {"Salary":"💰","Food":"🍔","Transport":"🚌","Housing":"🏠","Leisure":"🎮","Health":"💊","Education":"📚","Investment":"📈","Other":"📦","Salário":"💰","Alimentação":"🍕","Transporte":"🚗","Moradia":"🏡","Lazer":"🎬","Saúde":"🩺","Educação":"🎓","Investimento":"💹","Outros":"📌"}
            img = icons.get(tx['category'],"💲")
            ci, cd = st.columns([10,1])
            with ci:
                st.markdown(f'<div class="tx-row"><div class="tx-left"><div class="tx-img">{img}</div><div><div class="tx-name">{tx["description"]}</div><div class="tx-cat">{tx["category"]}</div></div></div><div><div class="tx-amount {cls}">{sign}{sym} {tx["value"]:,.2f}</div><div class="tx-date">{ds}</div></div></div>', unsafe_allow_html=True)
            with cd:
                if st.button("🗑️", key=f"del_{tx['id']}"): delete_transaction(tx['id']); st.rerun()
    else: st.info(t("no_transactions"))

# ========== CHAT COM STREAMING ==========
st.markdown('<button class="chat-fab" id="chatFab"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/><circle cx="9" cy="10" r="1.5" fill="white"/><circle cx="15" cy="10" r="1.5" fill="white"/></svg></button>', unsafe_allow_html=True)
st.markdown("""
<script>
const fab = document.getElementById('chatFab');
const popup = document.getElementById('chatPopup');
fab.addEventListener('click', () => {
    if (popup.style.display === 'flex') { popup.style.display = 'none'; }
    else { popup.style.display = 'flex'; }
});
</script>
""", unsafe_allow_html=True)

disp = 'flex' if st.session_state.show_chat else 'none'
st.markdown(f'<div class="chat-popup" id="chatPopup" style="display:{disp}">', unsafe_allow_html=True)
st.markdown(f'<div class="chat-header"><span>{t("chat_title")}</span><span style="cursor:pointer" onclick="document.getElementById(\'chatPopup\').style.display=\'none\'">✕</span></div>', unsafe_allow_html=True)
st.markdown('<div class="chat-body">', unsafe_allow_html=True)

for msg in chat_history:
    cls = "user-msg" if msg["role"]=="user" else "bot-msg"
    st.markdown(f'<div class="message-bubble {cls}">{msg["content"]}</div>', unsafe_allow_html=True)

st.markdown('<div class="chat-suggestions">', unsafe_allow_html=True)
for sug in t("chat_suggestions"):
    if st.button(sug, key=f"sug_{sug}"):
        st.session_state.memory.append({"role":"user","content":sug})
        save_chat(uid, "user", sug)
        with st.spinner(""):
            full_resp = ""
            placeholder = st.empty()
            for chunk in stream_response(sug, st.session_state.chat_model, st.session_state.get("gkey","") or st.session_state.get("okey","")):
                full_resp = chunk
                placeholder.markdown(f'<div class="message-bubble bot-msg">{chunk}</div>', unsafe_allow_html=True)
            st.session_state.memory.append({"role":"assistant","content":full_resp})
            save_chat(uid, "assistant", full_resp)
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
with st.form(key="cform", clear_on_submit=True):
    c1,c2 = st.columns([5,1])
    inp = c1.text_input("", placeholder=t("chat_placeholder"), label_visibility="collapsed", key="cinp")
    if c2.form_submit_button("➤") and inp:
        st.session_state.memory.append({"role":"user","content":inp})
        save_chat(uid, "user", inp)
        with st.spinner(""):
            full_resp = ""
            placeholder = st.empty()
            for chunk in stream_response(inp, st.session_state.chat_model, st.session_state.get("gkey","") or st.session_state.get("okey","")):
                full_resp = chunk
                placeholder.markdown(f'<div class="message-bubble bot-msg">{chunk}</div>', unsafe_allow_html=True)
            st.session_state.memory.append({"role":"assistant","content":full_resp})
            save_chat(uid, "assistant", full_resp)
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Configuração do Chat")
    st.session_state.chat_model = st.selectbox("Modelo", ["Offline","Gemini","ChatGPT"], index=0)
    if st.session_state.chat_model == "Gemini": st.session_state.gkey = st.text_input("Chave Gemini", type="password")
    elif st.session_state.chat_model == "ChatGPT": st.session_state.okey = st.text_input("Chave OpenAI", type="password")
    if st.button("Limpar histórico"): clear_chat(uid); st.session_state.memory = []; st.rerun()
    st.markdown("---")
    st.markdown("### Notificações")
    st.session_state.email_enabled = st.toggle(t("email_toggle"), value=st.session_state.email_enabled)
    if st.button(t("send_resume")):
        if SEND_NOTIFICATIONS:
            body = f"<h2>FinBot - Resumo Financeiro</h2><p>Saldo: {sym} {balance:,.2f}</p><p>Receitas: {sym} {income_total:,.2f}</p><p>Despesas: {sym} {expense_total:,.2f}</p>"
            if goal:
                saved = balance if balance>0 else 0
                prog = min(saved/goal['amount']*100,100) if goal['amount']>0 else 0
                body += f"<p>Meta: {sym} {goal['amount']:,.2f} ({prog:.1f}%)</p>"
            send_email(user_email, "Resumo Financeiro - FinBot", body)
            st.success("Email enviado!")
        else:
            st.error("SendGrid não configurado.")

st.markdown(f'<div style="text-align:center;color:#6d6d72;font-size:0.7rem;padding:2rem 0 1rem 0">{t("footer")}</div>', unsafe_allow_html=True)