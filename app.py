import streamlit as st
from database import get_connection, init_db, migrate_database
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import io
import calendar
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="TaskSync - Operations Strategy",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== SESSION STATE INITIALIZATION =====
def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        "notifications": [],
        "saved_filters": {},
        "comments": {},
        "user_name": "Usuário",
        "user_email": None,
        "user_role": "viewer",
        "show_new_wp_form": False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ===== DATABASE INITIALIZATION WITH MIGRATIONS =====
@st.cache_resource
def init_database():
    """Initialize database and run migrations"""
    print("🔄 Inicializando banco de dados...")
    
    # Criar tabelas se não existirem
    init_db()
    
    # Executar migrações para garantir que as colunas existem
    try:
        migrate_database()
        print("✅ Migrações executadas com sucesso")
    except Exception as e:
        print(f"⚠️ Erro nas migrações: {e}")
    
    return get_connection()

# Inicializar banco de dados
conn = init_database()

# ===== DARK MODE ONLY STYLES =====
st.markdown("""
<style>
/* Dark Mode Base */
.stApp {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

/* Modern Cards */
.card-modern {
    background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 1.5rem;
    margin: 1rem 0;
    border: 1px solid rgba(255,255,255,0.18);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.card-modern:hover {
    transform: translateY(-5px);
    box-shadow: 0 20px 35px rgba(0,0,0,0.3);
    border-color: rgba(255,255,255,0.3);
}
.card-modern::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #00d2ff, #3a7bd5, #00d2ff);
}

/* Metric Cards */
.metric-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.1);
    transition: all 0.3s ease;
}
.metric-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}
.metric-value {
    font-size: 2.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #00d2ff, #3a7bd5);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}
.metric-label {
    color: #a0a0a0;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Badges */
.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    margin: 0 0.25rem;
}
.badge-high { background: #ff6b6b; color: white; }
.badge-medium { background: #ffb347; color: white; }
.badge-low { background: #4ecdc4; color: white; }
.badge-todo { background: #3498db; color: white; }
.badge-progress { background: #f39c12; color: white; }
.badge-done { background: #2ecc71; color: white; }
.badge-draft { background: #95a5a6; color: white; }
.badge-review { background: #3498db; color: white; }
.badge-published { background: #2ecc71; color: white; }
.badge-info { background: #3498db; color: white; }

/* Tags */
.tag {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 12px;
    font-size: 0.7rem;
    font-weight: 500;
    margin-right: 0.5rem;
    background: rgba(255,255,255,0.1);
    color: #e0e0e0;
}

/* Countdown */
.countdown-urgent {
    background: rgba(255,68,68,0.2);
    color: #ff8888;
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
    font-weight: bold;
}
.countdown-warning {
    background: rgba(255,180,71,0.2);
    color: #ffb347;
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
}
.countdown-normal {
    background: rgba(46,204,113,0.2);
    color: #2ecc71;
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
}

/* Progress Bar */
.progress-bar {
    background: rgba(255,255,255,0.1);
    border-radius: 10px;
    height: 8px;
    overflow: hidden;
}
.progress-fill {
    background: linear-gradient(90deg, #00d2ff, #3a7bd5);
    height: 100%;
    border-radius: 10px;
    transition: width 0.3s ease;
}

/* Timeline */
.timeline-item {
    border-left: 2px solid #00d2ff;
    padding-left: 1rem;
    margin: 1rem 0;
    position: relative;
}
.timeline-dot {
    position: absolute;
    left: -0.5rem;
    top: 0;
    width: 0.8rem;
    height: 0.8rem;
    border-radius: 50%;
    background: #00d2ff;
}

/* Text Colors */
h1, h2, h3, h4, p, span, label, .stMarkdown {
    color: #e0e0e0;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(135deg, #00d2ff, #3a7bd5);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    transition: all 0.3s ease;
}
.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0,210,255,0.3);
}

hr {
    border-color: rgba(255,255,255,0.1);
}

/* Inputs */
.stTextInput>div>div>input, .stTextArea textarea, .stSelectbox>div>div {
    background-color: rgba(255,255,255,0.08) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# ===== NOTIFICATION SYSTEM =====
def add_notification(message, type="info"):
    st.session_state.notifications.append({
        "message": message,
        "type": type,
        "timestamp": datetime.now()
    })

def show_notifications():
    for notif in st.session_state.notifications[-5:]:
        if notif["type"] == "success":
            st.success(notif["message"])
        elif notif["type"] == "error":
            st.error(notif["message"])
        elif notif["type"] == "warning":
            st.warning(notif["message"])
        else:
            st.info(notif["message"])
    st.session_state.notifications = []

# ===== HELPER FUNCTIONS =====
def days_until(date_value):
    if pd.isna(date_value) or date_value is None:
        return None
    today = datetime.now().date()
    if isinstance(date_value, str):
        try:
            date_value = datetime.strptime(date_value, '%Y-%m-%d').date()
        except:
            return None
    elif hasattr(date_value, 'date'):
        date_value = date_value.date()
    if not isinstance(date_value, date):
        return None
    delta = date_value - today
    return delta.days

def format_countdown(days):
    if days is None:
        return ""
    if days < 0:
        return f"<span class='countdown-urgent'>⏰ Atrasado {abs(days)} dias</span>"
    elif days == 0:
        return "<span class='countdown-urgent'>🔥 Hoje!</span>"
    elif days <= 3:
        return f"<span class='countdown-urgent'>⚠️ {days} dias</span>"
    elif days <= 7:
        return f"<span class='countdown-warning'>📅 {days} dias</span>"
    else:
        return f"<span class='countdown-normal'>🗓️ {days} dias</span>"

def render_tag(tag):
    tag_colors = {
        "urgente": "#FF6B6B", "prioritario": "#FFB347", "planejamento": "#4ECDC4",
        "execução": "#45B7D1", "revisão": "#96CEB4", "manufacturing": "#FF6B6B",
        "supply_chain": "#4ECDC4", "digital_twin": "#45B7D1", "ia_ml": "#96CEB4", "healthcare": "#FFB347"
    }
    color = tag_colors.get(tag.lower(), "#95A5A6")
    return f'<span style="background-color: {color}; padding: 2px 8px; border-radius: 12px; font-size: 0.7rem; margin-right: 5px; color: white;">{tag}</span>'

def get_priority_badge(priority):
    badges = {"Alta": "badge-high", "Média": "badge-medium", "Baixa": "badge-low"}
    return f'<span class="badge {badges.get(priority, "badge-medium")}">{priority}</span>'

def get_status_badge(status):
    badges = {"To Do": "badge-todo", "In Progress": "badge-progress", "Done": "badge-done"}
    return f'<span class="badge {badges.get(status, "badge-todo")}">{status}</span>'

def check_deadlines():
    tasks = get_tasks()
    today = date.today()
    for _, task in tasks.iterrows():
        if task['due_date'] and task['status'] != 'Done':
            days_left = (task['due_date'] - today).days
            if days_left <= 3 and days_left >= 0:
                add_notification(f"⚠️ Tarefa '{task['title']}' vence em {days_left} dias!", "warning")
            elif days_left < 0:
                add_notification(f"❌ Tarefa '{task['title']}' está atrasada!", "error")

def get_realtime_metrics():
    tasks = get_tasks()
    if tasks.empty:
        return {"total": 0, "completed": 0, "in_progress": 0, "todo": 0, "on_track": 0, "delayed": 0, "productivity_rate": 0}
    today = date.today()
    total = len(tasks)
    completed = len(tasks[tasks['status'] == 'Done'])
    in_progress = len(tasks[tasks['status'] == 'In Progress'])
    todo = len(tasks[tasks['status'] == 'To Do'])
    delayed = len(tasks[(tasks['due_date'] < today) & (tasks['status'] != 'Done')]) if 'due_date' in tasks.columns else 0
    return {"total": total, "completed": completed, "in_progress": in_progress, "todo": todo,
            "on_track": total - delayed, "delayed": delayed, "productivity_rate": (completed / total * 100) if total > 0 else 0}

def export_to_excel(data, filename):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        data.to_excel(writer, sheet_name='Relatório', index=False)
    return st.download_button(label="📥 Exportar para Excel", data=output.getvalue(),
                              file_name=f"{filename}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                              mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

def export_glossary_to_pdf(glossary_df):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, alignment=TA_CENTER, spaceAfter=30)
    elements = []
    elements.append(Paragraph("TaskSync - Glossário de Termos", title_style))
    elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    categories = glossary_df['category'].unique() if 'category' in glossary_df.columns else ['todos']
    for category in categories:
        elements.append(Paragraph(f"<b>{category.upper()}</b>", styles['Heading2']))
        elements.append(Spacer(1, 10))
        category_terms = glossary_df[glossary_df['category'] == category] if 'category' in glossary_df.columns else glossary_df
        for _, row in category_terms.iterrows():
            elements.append(Paragraph(f"<b>{row['term']}</b>", styles['Heading3']))
            elements.append(Paragraph(f"<i>Definição:</i> {row['definition']}", styles['Normal']))
            if row.get('example') and row['example'] != 'N/A':
                elements.append(Paragraph(f"<i>Exemplo:</i> {row['example']}", styles['Normal']))
            elements.append(Spacer(1, 10))
        elements.append(PageBreak())
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

# ===== DATA FUNCTIONS =====
def get_tasks():
    return pd.read_sql_query("SELECT * FROM tasks ORDER BY priority DESC, due_date", conn)

def get_events():
    return pd.read_sql_query("SELECT * FROM events ORDER BY start_date", conn)

def get_companies():
    return pd.read_sql_query("SELECT * FROM target_companies", conn)

def get_advisors():
    return pd.read_sql_query("SELECT * FROM senior_advisors", conn)

def get_glossary():
    return pd.read_sql_query("SELECT * FROM glossary ORDER BY term", conn)

def get_whitepapers():
    return pd.read_sql_query("SELECT * FROM whitepapers ORDER BY created_at DESC", conn)

def get_cases():
    return pd.read_sql_query("SELECT * FROM knowledge_base WHERE type='case_study' ORDER BY created_at DESC", conn)

# ===== WHITEPAPERS FUNCTIONS =====
def get_whitepaper_details(wp_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT id, title, topic, status, progress, author_name, 
               content, document_link, published_date, target_audience, tags, created_at
        FROM whitepapers WHERE id = %s
    """, (wp_id,))
    result = cur.fetchone()
    cur.close()
    if result:
        columns = ['id', 'title', 'topic', 'status', 'progress', 'author_name',
                   'content', 'document_link', 'published_date', 'target_audience', 'tags', 'created_at']
        return dict(zip(columns, result))
    return None

def update_whitepaper_details(wp_id, updates):
    cur = conn.cursor()
    set_clause = ", ".join([f"{key}=%s" for key in updates.keys()])
    values = list(updates.values()) + [wp_id]
    cur.execute(f"UPDATE whitepapers SET {set_clause} WHERE id=%s", values)
    conn.commit()
    cur.close()

def delete_whitepaper(wp_id):
    cur = conn.cursor()
    cur.execute("DELETE FROM whitepapers WHERE id=%s", (wp_id,))
    conn.commit()
    cur.close()

def get_whitepaper_comments(wp_id):
    if f"wp_comments_{wp_id}" not in st.session_state:
        st.session_state[f"wp_comments_{wp_id}"] = []
    return st.session_state[f"wp_comments_{wp_id}"]

def add_whitepaper_comment(wp_id, comment_text, user_name):
    if comment_text.strip():
        st.session_state[f"wp_comments_{wp_id}"].append({
            "user": user_name,
            "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "text": comment_text.strip()
        })
        return True
    return False

def show_whitepaper_modal(wp_id, wp_title):
    wp = get_whitepaper_details(wp_id)
    if not wp:
        return
    
    st.markdown(f"## 📄 {wp['title']}")
    status_colors = {"draft": "badge-draft", "review": "badge-review", "published": "badge-published"}
    status_color = status_colors.get(wp['status'], "badge-draft")
    
    st.markdown(f"""
    <div style="margin-bottom: 1rem;">
        <span class="badge {status_color}">{wp['status'].upper()}</span>
        <span class="badge badge-info">Progresso: {wp['progress']}%</span>
    </div>
    <div class="progress-bar"><div class="progress-fill" style="width: {wp['progress']}%;"></div></div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📝 Conteúdo", "✏️ Editar", "💬 Comentários"])
    
    with tab1:
        st.markdown("### 📋 Informações Gerais")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Tópico:** {wp['topic'] or 'N/A'}")
            st.markdown(f"**Autor:** {wp['author_name'] or 'N/A'}")
        with col2:
            st.markdown(f"**Data de publicação:** {wp['published_date'] or 'Não publicado'}")
            st.markdown(f"**Criado em:** {wp['created_at'].strftime('%d/%m/%Y') if wp['created_at'] else 'N/A'}")
        
        if wp['content']:
            st.markdown("### 📄 Conteúdo")
            st.markdown(f'<div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px;">{wp["content"]}</div>', unsafe_allow_html=True)
        if wp['target_audience']:
            st.markdown("### 👥 Público-alvo")
            st.write(wp['target_audience'])
        if wp['tags']:
            st.markdown("### 🏷️ Tags")
            tags_html = ''.join([render_tag(tag.strip()) for tag in wp['tags'].split(',') if tag.strip()])
            st.markdown(tags_html, unsafe_allow_html=True)
        if wp['document_link']:
            st.markdown(f"### 🔗 Link para documento")
            st.markdown(f'<a href="{wp["document_link"]}" target="_blank">{wp["document_link"]}</a>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### ✏️ Editar Whitepaper")
        col1, col2 = st.columns(2)
        with col1:
            new_title = st.text_input("Título", value=wp['title'], key=f"edit_wp_title_{wp_id}")
            new_topic = st.text_input("Tópico", value=wp['topic'] or "", key=f"edit_wp_topic_{wp_id}")
            new_author = st.text_input("Autor", value=wp['author_name'] or "", key=f"edit_wp_author_{wp_id}")
            new_status = st.selectbox("Status", ["draft", "review", "published"],
                                     index=["draft", "review", "published"].index(wp['status']) if wp['status'] in ["draft", "review", "published"] else 0,
                                     key=f"edit_wp_status_{wp_id}")
        with col2:
            new_progress = st.slider("Progresso (%)", 0, 100, wp['progress'] or 0, key=f"edit_wp_progress_{wp_id}")
            new_published_date = st.date_input("Data de publicação", 
                                              value=wp['published_date'] if wp['published_date'] else date.today(),
                                              key=f"edit_wp_date_{wp_id}")
            new_target_audience = st.text_input("Público-alvo", value=wp['target_audience'] or "", key=f"edit_wp_audience_{wp_id}")
            new_tags = st.text_input("Tags", value=wp['tags'] or "", key=f"edit_wp_tags_{wp_id}")
        
        new_content = st.text_area("Conteúdo", value=wp['content'] or "", height=200, key=f"edit_wp_content_{wp_id}")
        new_document_link = st.text_input("Link do documento", value=wp['document_link'] or "", key=f"edit_wp_link_{wp_id}")
        
        if st.button("💾 Salvar alterações", key=f"save_wp_{wp_id}", use_container_width=True):
            updates = {
                "title": new_title, "topic": new_topic,
                "status": new_status, "progress": new_progress, "author_name": new_author,
                "content": new_content, "document_link": new_document_link,
                "published_date": new_published_date, "target_audience": new_target_audience,
                "tags": new_tags
            }
            update_whitepaper_details(wp_id, updates)
            add_notification(f"✅ Whitepaper '{new_title}' atualizado!", "success")
            st.rerun()
    
    with tab3:
        st.markdown("### 💬 Comentários")
        comments = get_whitepaper_comments(wp_id)
        if comments:
            for idx, comment in enumerate(reversed(comments)):
                st.markdown(f"**{comment['user']}** - *{comment['date']}*")
                st.markdown(comment['text'])
                if st.button("🗑️", key=f"delete_wp_comment_{wp_id}_{idx}"):
                    del st.session_state[f"wp_comments_{wp_id}"][len(comments) - 1 - idx]
                    st.rerun()
                st.markdown("---")
        else:
            st.info("Nenhum comentário ainda.")
        
        new_comment = st.text_area("Escreva seu comentário...", height=100, key=f"new_wp_comment_{wp_id}")
        if st.button("📤 Enviar", key=f"submit_wp_comment_{wp_id}"):
            if add_whitepaper_comment(wp_id, new_comment, st.session_state.user_name):
                add_notification("✅ Comentário adicionado!", "success")
                st.rerun()
    
    if st.button("🔙 Fechar", key=f"close_wp_modal_{wp_id}"):
        st.session_state[f"show_wp_details_{wp_id}"] = False
        st.rerun()

# ===== COMMENTS SYSTEM =====
def init_comments(task_id):
    if f"comments_{task_id}" not in st.session_state:
        st.session_state[f"comments_{task_id}"] = []

def add_comment(task_id, comment_text, user_name):
    if comment_text.strip():
        st.session_state[f"comments_{task_id}"].append({
            "user": user_name,
            "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "text": comment_text.strip()
        })
        return True
    return False

def get_comments(task_id):
    return st.session_state.get(f"comments_{task_id}", [])

def delete_comment(task_id, comment_index):
    if f"comments_{task_id}" in st.session_state:
        if 0 <= comment_index < len(st.session_state[f"comments_{task_id}"]):
            del st.session_state[f"comments_{task_id}"][comment_index]
            return True
    return False

def get_task_details(task_id):
    cur = conn.cursor()
    cur.execute("""SELECT id, title, description, category, subcategory, priority, status, 
                   owner_name, due_date, target_companies, document_link, tags, notes,
                   created_at, start_date, completed_date, estimated_hours, actual_hours
                   FROM tasks WHERE id = %s""", (task_id,))
    result = cur.fetchone()
    cur.close()
    if result:
        columns = ['id', 'title', 'description', 'category', 'subcategory', 'priority', 'status',
                   'owner_name', 'due_date', 'target_companies', 'document_link', 'tags', 'notes',
                   'created_at', 'start_date', 'completed_date', 'estimated_hours', 'actual_hours']
        return dict(zip(columns, result))
    return None

def update_task_details(task_id, updates):
    cur = conn.cursor()
    set_clause = ", ".join([f"{key}=%s" for key in updates.keys()])
    values = list(updates.values()) + [task_id]
    cur.execute(f"UPDATE tasks SET {set_clause} WHERE id=%s", values)
    conn.commit()
    cur.close()

def show_task_modal(task_id, task_title):
    task = get_task_details(task_id)
    if not task:
        return
    init_comments(task_id)
    st.markdown(f"## 📋 {task['title']}")
    tab1, tab2, tab3 = st.tabs(["📝 Detalhes", "💬 Comentários", "📊 Progresso"])
    
    with tab1:
        st.markdown("### Informações da Tarefa")
        col1, col2 = st.columns(2)
        with col1:
            new_title = st.text_input("Título", value=task['title'], key=f"edit_title_{task_id}")
            new_description = st.text_area("Descrição", value=task['description'] or "", height=150, key=f"edit_desc_{task_id}")
            new_category = st.selectbox("Categoria", ["challenge", "next_step", "tool", "whitepaper", "initiative"],
                                       index=["challenge", "next_step", "tool", "whitepaper", "initiative"].index(task['category']) if task['category'] in ["challenge", "next_step", "tool", "whitepaper", "initiative"] else 0,
                                       key=f"edit_cat_{task_id}")
        with col2:
            new_priority = st.selectbox("Prioridade", ["Alta", "Média", "Baixa"],
                                       index=["Alta", "Média", "Baixa"].index(task['priority']) if task['priority'] in ["Alta", "Média", "Baixa"] else 0,
                                       key=f"edit_priority_{task_id}")
            new_owner = st.text_input("Responsável", value=task['owner_name'] or "", key=f"edit_owner_{task_id}")
            new_due_date = st.date_input("Data limite", value=task['due_date'] if task['due_date'] else date.today(), key=f"edit_due_{task_id}")
            new_tags = st.text_input("Tags", value=task['tags'] or "", key=f"edit_tags_{task_id}")
        
        new_notes = st.text_area("Notas", value=task['notes'] or "", height=100, key=f"edit_notes_{task_id}")
        new_document_link = st.text_input("Link do documento", value=task['document_link'] or "", key=f"edit_link_{task_id}")
        
        if st.button("💾 Salvar", key=f"save_task_{task_id}"):
            updates = {"title": new_title, "description": new_description, "category": new_category,
                      "priority": new_priority, "owner_name": new_owner, "due_date": new_due_date,
                      "tags": new_tags, "notes": new_notes, "document_link": new_document_link}
            update_task_details(task_id, updates)
            add_notification(f"✅ Tarefa atualizada!", "success")
            st.rerun()
    
    with tab2:
        st.markdown("### 💬 Comentários")
        comments = get_comments(task_id)
        if comments:
            for idx, comment in enumerate(reversed(comments)):
                st.markdown(f"**{comment['user']}** - *{comment['date']}*")
                st.markdown(comment['text'])
                if st.button("🗑️", key=f"delete_comment_{task_id}_{idx}"):
                    delete_comment(task_id, len(comments) - 1 - idx)
                    st.rerun()
                st.markdown("---")
        else:
            st.info("Nenhum comentário ainda.")
        
        new_comment = st.text_area("Escreva seu comentário...", height=100, key=f"new_comment_{task_id}")
        if st.button("📤 Enviar", key=f"submit_comment_{task_id}"):
            if add_comment(task_id, new_comment, st.session_state.user_name):
                add_notification("✅ Comentário adicionado!", "success")
                st.rerun()
    
    with tab3:
        st.markdown("### 📊 Progresso")
        status_options = ["To Do", "In Progress", "Done"]
        current_status_index = status_options.index(task['status']) if task['status'] in status_options else 0
        new_status = st.selectbox("Status", status_options, index=current_status_index, key=f"status_{task_id}")
        if new_status != task['status']:
            if st.button("🔄 Atualizar Status"):
                updates = {"status": new_status}
                if new_status == "In Progress" and not task['start_date']:
                    updates["start_date"] = date.today()
                if new_status == "Done" and not task['completed_date']:
                    updates["completed_date"] = date.today()
                update_task_details(task_id, updates)
                add_notification(f"✅ Status atualizado!", "success")
                st.rerun()
    
    if st.button("🔙 Fechar", key=f"close_modal_{task_id}"):
        st.session_state[f"show_details_{task_id}"] = False
        st.rerun()

# ===== VISUALIZATION FUNCTIONS =====
def show_progress_charts(tasks_df):
    if tasks_df.empty:
        st.info("Nenhuma tarefa para exibir")
        return
    status_counts = tasks_df['status'].value_counts()
    fig_pie = px.pie(values=status_counts.values, names=status_counts.index, title="Distribuição por Status")
    fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
    if 'category' in tasks_df.columns:
        category_counts = tasks_df['category'].value_counts()
        fig_bar = px.bar(x=category_counts.index, y=category_counts.values, title="Iniciativas por Categoria")
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_pie, use_container_width=True)
        with col2:
            st.plotly_chart(fig_bar, use_container_width=True)

def show_timeline(tasks_df):
    if tasks_df.empty or 'due_date' not in tasks_df.columns:
        return
    timeline_data = tasks_df[tasks_df['due_date'].notna()].copy()
    if timeline_data.empty:
        return
    timeline_data['start'] = pd.to_datetime(timeline_data['created_at'] if 'created_at' in timeline_data.columns else datetime.now())
    timeline_data['end'] = pd.to_datetime(timeline_data['due_date'])
    fig = px.timeline(timeline_data, x_start="start", x_end="end", y="title", color="priority")
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
    st.plotly_chart(fig, use_container_width=True)

def show_upcoming_deadlines():
    tasks = get_tasks()
    today = date.today()
    upcoming = tasks[(tasks['status'] != 'Done') & (tasks['due_date'].notna())].copy()
    if upcoming.empty:
        st.info("🎉 Nenhum prazo próximo!")
        return
    upcoming['days_left'] = upcoming['due_date'].apply(lambda x: (x - today).days if pd.notna(x) else None)
    upcoming = upcoming.sort_values('days_left').head(10)
    for _, task in upcoming.iterrows():
        days = task['days_left']
        if days <= 0:
            st.error(f"❌ **{task['title']}** - Atrasado!")
        elif days <= 3:
            st.warning(f"⚠️ **{task['title']}** - Vence em {days} dias")
        else:
            st.info(f"📅 **{task['title']}** - Vence em {days} dias")

def show_calendar_view(events_df):
    if events_df.empty:
        st.info("Nenhum evento para exibir")
        return
    today = datetime.now().date()
    cal = calendar.monthcalendar(today.year, today.month)
    events_df['start_date_dt'] = pd.to_datetime(events_df['start_date'], errors='coerce')
    event_days = set()
    for _, event in events_df.iterrows():
        if pd.notna(event['start_date_dt']):
            event_days.add(event['start_date_dt'].day)
    st.markdown(f"### 📅 {today.strftime('%B %Y')}")
    cols = st.columns(7)
    for i, day in enumerate(['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']):
        with cols[i]:
            st.markdown(f"**{day}**")
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    st.write("")
                elif day in event_days:
                    st.markdown(f"<div style='background: #ffb347; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; font-weight: bold;'>{day}</div>", unsafe_allow_html=True)
                elif day == today.day:
                    st.markdown(f"<div style='background: #00d2ff; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; font-weight: bold;'>{day}</div>", unsafe_allow_html=True)
                else:
                    st.write(day)

# ===== SIDEBAR =====
with st.sidebar:
    st.markdown("## 🎯 TaskSync")
    st.markdown("Operations Strategy")
    st.markdown("---")
    
    menu = st.radio("Navegação", ["📊 Dashboard", "📋 Kanban", "📅 Eventos", "📚 Knowledge Base", "🏢 Empresas Target", "👥 Senior Advisors"])
    st.markdown("---")
    st.caption("TaskSync v3.0 | Raíssa Azevedo - 2026")

# ===== MAIN CONTENT =====
st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <h1>🎯 TaskSync - Operations Strategy</h1>
    <p>Gestão de desafios, próximos passos, ferramentas e conhecimento em operações</p>
</div>
""", unsafe_allow_html=True)

show_notifications()
check_deadlines()

# ===== DASHBOARD =====
if menu == "📊 Dashboard":
    st.header("📊 Dashboard Estratégico")
    tasks = get_tasks()
    events = get_events()
    companies = get_companies()
    advisors = get_advisors()
    metrics = get_realtime_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{metrics["total"]}</div><div class="metric-label">Total Iniciativas</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{metrics["productivity_rate"]:.1f}%</div><div class="metric-label">Taxa de Conclusão</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{metrics["delayed"]}</div><div class="metric-label">Atrasadas</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(events)}</div><div class="metric-label">Eventos</div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    show_progress_charts(tasks)
    st.subheader("⏰ Linha do Tempo")
    show_timeline(tasks)
    st.subheader("⚠️ Prazos Próximos")
    show_upcoming_deadlines()

# ===== KANBAN =====
elif menu == "📋 Kanban":
    st.header("📋 Kanban - Iniciativas")
    
    with st.expander("➕ Nova Iniciativa", expanded=False):
        with st.form("new_task"):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Título *")
                category = st.selectbox("Categoria", ["challenge", "next_step", "tool", "whitepaper", "initiative"])
                priority = st.selectbox("Prioridade", ["Alta", "Média", "Baixa"])
            with col2:
                owner_name = st.text_input("Responsável")
                due_date = st.date_input("Data limite", value=None)
                tags = st.text_input("Tags")
            description = st.text_area("Descrição")
            if st.form_submit_button("Salvar") and title:
                cur = conn.cursor()
                cur.execute("""INSERT INTO tasks (title, description, category, priority, status, owner_name, due_date, tags)
                               VALUES (%s, %s, %s, %s, 'To Do', %s, %s, %s)""",
                           (title, description, category, priority, owner_name, due_date, tags))
                conn.commit()
                add_notification(f"✅ Iniciativa '{title}' criada!", "success")
                st.rerun()
    
    tasks = get_tasks()
    if tasks.empty:
        st.info("Nenhuma tarefa cadastrada.")
    else:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 📝 To Do")
            todo_tasks = tasks[tasks['status'] == 'To Do']
            for _, row in todo_tasks.iterrows():
                st.markdown(f"""
                <div class="card-modern">
                    <h4>{row['title']}</h4>
                    <div>{get_priority_badge(row['priority'])} {get_status_badge(row['status'])}</div>
                    <p><strong>Responsável:</strong> {row['owner_name'] or 'N/A'}</p>
                    <p><strong>Data:</strong> {row['due_date'] or 'N/A'} {format_countdown(days_until(row['due_date']))}</p>
                    <p><small>{row['description'][:100] if row['description'] else 'Sem descrição'}...</small></p>
                </div>
                """, unsafe_allow_html=True)
                
                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    if st.button("→ Iniciar", key=f"start_{row['id']}"):
                        cur = conn.cursor()
                        cur.execute("UPDATE tasks SET status='In Progress', start_date=%s WHERE id=%s", (date.today(), row['id']))
                        conn.commit()
                        st.rerun()
                with col_b:
                    if st.button("📋", key=f"details_{row['id']}"):
                        st.session_state[f"show_details_{row['id']}"] = True
                        st.rerun()
                with col_c:
                    if st.button("✏️", key=f"edit_{row['id']}"):
                        st.session_state[f"editing_{row['id']}"] = True
                with col_d:
                    if st.button("🗑️", key=f"delete_{row['id']}"):
                        cur = conn.cursor()
                        cur.execute("DELETE FROM tasks WHERE id=%s", (row['id'],))
                        conn.commit()
                        st.rerun()
                
                if st.session_state.get(f"show_details_{row['id']}", False):
                    with st.expander(f"📋 Detalhes - {row['title']}", expanded=True):
                        show_task_modal(row['id'], row['title'])
                
                if st.session_state.get(f"editing_{row['id']}", False):
                    with st.form(f"edit_form_{row['id']}"):
                        new_title = st.text_input("Título", value=row['title'])
                        new_desc = st.text_area("Descrição", value=row['description'] or "")
                        new_priority = st.selectbox("Prioridade", ["Alta", "Média", "Baixa"], index=["Alta", "Média", "Baixa"].index(row['priority']))
                        if st.form_submit_button("💾 Salvar"):
                            cur = conn.cursor()
                            cur.execute("UPDATE tasks SET title=%s, description=%s, priority=%s WHERE id=%s",
                                       (new_title, new_desc, new_priority, row['id']))
                            conn.commit()
                            st.session_state[f"editing_{row['id']}"] = False
                            st.rerun()
        
        with col2:
            st.markdown("### 🔄 In Progress")
            ip_tasks = tasks[tasks['status'] == 'In Progress']
            for _, row in ip_tasks.iterrows():
                st.markdown(f"""
                <div class="card-modern">
                    <h4>{row['title']}</h4>
                    <div>{get_priority_badge(row['priority'])} {get_status_badge(row['status'])}</div>
                    <p><strong>Responsável:</strong> {row['owner_name'] or 'N/A'}</p>
                </div>
                """, unsafe_allow_html=True)
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("✅ Concluir", key=f"done_{row['id']}"):
                        cur = conn.cursor()
                        cur.execute("UPDATE tasks SET status='Done', completed_date=%s WHERE id=%s", (date.today(), row['id']))
                        conn.commit()
                        st.rerun()
                with col_b:
                    if st.button("← Voltar", key=f"back_{row['id']}"):
                        cur = conn.cursor()
                        cur.execute("UPDATE tasks SET status='To Do' WHERE id=%s", (row['id'],))
                        conn.commit()
                        st.rerun()
        
        with col3:
            st.markdown("### ✅ Done")
            done_tasks = tasks[tasks['status'] == 'Done']
            for _, row in done_tasks.iterrows():
                st.markdown(f"""
                <div class="card-modern">
                    <h4>✓ {row['title']}</h4>
                    <p>Concluído em: {row['completed_date'] or 'N/A'}</p>
                </div>
                """, unsafe_allow_html=True)

# ===== EVENTOS =====
elif menu == "📅 Eventos":
    st.header("📅 Eventos do Setor")
    
    with st.expander("➕ Novo Evento", expanded=False):
        with st.form("new_event"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Nome do evento *")
                event_type = st.selectbox("Tipo", ["conference", "webinar", "workshop"])
            with col2:
                start_date = st.date_input("Data início")
                location = st.text_input("Local")
            description = st.text_area("Descrição")
            if st.form_submit_button("Salvar") and name:
                cur = conn.cursor()
                cur.execute("""INSERT INTO events (name, description, event_type, start_date, location)
                               VALUES (%s, %s, %s, %s, %s)""",
                           (name, description, event_type, start_date, location))
                conn.commit()
                st.rerun()
    
    events = get_events()
    search_events = st.text_input("🔍 Buscar eventos", placeholder="Nome, tipo, local ou descrição...", key="search_events")
    if search_events:
        events = events[
            events['name'].str.contains(search_events, case=False, na=False) |
            events['event_type'].str.contains(search_events, case=False, na=False) |
            events['location'].str.contains(search_events, case=False, na=False) |
            events['description'].str.contains(search_events, case=False, na=False)
        ]

    with st.expander("📅 Visualização em Calendário", expanded=False):
        show_calendar_view(events)
    
    if events.empty:
        st.info("Nenhum evento encontrado.")
    else:
        for _, row in events.iterrows():
            st.markdown(f"""
            <div class="card-modern">
                <h4>{row['name']}</h4>
                <p><strong>Data:</strong> {row['start_date']} | <strong>Local:</strong> {row['location'] or 'N/A'}</p>
                <p>{row['description']}</p>
            </div>
            """, unsafe_allow_html=True)

# ===== KNOWLEDGE BASE =====
elif menu == "📚 Knowledge Base":
    st.header("📚 Knowledge Base")
    
    tab1, tab2, tab3 = st.tabs(["📄 Whitepapers", "📖 Glossário", "📊 Case Studies"])
    
    # TAB 1: WHITEPAPERS
    with tab1:
        st.subheader("Whitepapers e Documentos Técnicos")
        
        col_search, col_filter, col_stats = st.columns([2, 1, 1])
        with col_search:
            search_wp = st.text_input("🔍 Buscar whitepapers", placeholder="Título, tópico, autor...", key="search_wp")
        with col_filter:
            status_filter = st.selectbox("Status", ["Todos", "draft", "review", "published"], key="filter_wp_status")
        with col_stats:
            wps_all = get_whitepapers()
            st.metric("Total", len(wps_all), help="Total de whitepapers cadastrados")
        
        col_add, col_export = st.columns(2)
        with col_add:
            if st.button("➕ Novo Whitepaper", use_container_width=True):
                st.session_state.show_new_wp_form = True
        with col_export:
            if st.button("📥 Exportar Lista", use_container_width=True):
                wps_export = get_whitepapers()
                if not wps_export.empty:
                    export_to_excel(wps_export, "whitepapers_list")
        
        if st.session_state.get("show_new_wp_form", False):
            with st.expander("📝 Criar Novo Whitepaper", expanded=True):
                with st.form("new_wp_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        title = st.text_input("Título *")
                        topic = st.text_input("Tópico/Área")
                        author = st.text_input("Autor(es)")
                        status = st.selectbox("Status", ["draft", "review", "published"])
                    with col2:
                        progress = st.slider("Progresso (%)", 0, 100, 0)
                        target_audience = st.text_input("Público-alvo")
                        tags = st.text_input("Tags")
                    content = st.text_area("Conteúdo", height=200)
                    document_link = st.text_input("Link para documento")
                    
                    if st.form_submit_button("✅ Criar Whitepaper") and title:
                        cur = conn.cursor()
                        cur.execute("""
                            INSERT INTO whitepapers (title, topic, status, progress, author_name, 
                                                   content, document_link, target_audience, tags)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (title, topic, status, progress, author, content, document_link, target_audience, tags))
                        conn.commit()
                        add_notification(f"✅ Whitepaper '{title}' criado!", "success")
                        st.session_state.show_new_wp_form = False
                        st.rerun()
        
        wps = get_whitepapers()
        if not wps.empty:
            if search_wp:
                wps = wps[
                    wps['title'].str.contains(search_wp, case=False, na=False) |
                    wps['topic'].str.contains(search_wp, case=False, na=False) |
                    wps['author_name'].str.contains(search_wp, case=False, na=False)
                ]
            if status_filter != "Todos":
                wps = wps[wps['status'] == status_filter]
        
        if wps.empty:
            st.info("📭 Nenhum whitepaper encontrado.")
        else:
            for _, row in wps.iterrows():
                status_colors = {"draft": "🟡 Rascunho", "review": "🔵 Em revisão", "published": "🟢 Publicado"}
                status_display = status_colors.get(row['status'], row['status'])
                progress_color = "#22c55e" if row['progress'] >= 80 else "#f59e0b" if row['progress'] >= 50 else "#ef4444"
                
                st.markdown(f"""
                <div class="card-modern">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div style="flex: 1;">
                            <h4>{row['title']}</h4>
                            <div style="margin-bottom: 0.5rem;">
                                <span class="badge badge-info">{row['topic'] or 'Sem tópico'}</span>
                                <span class="badge badge-info">📝 {row['author_name'] or 'Autor não informado'}</span>
                            </div>
                            <div style="margin-top: 0.5rem;">
                                <div style="display: flex; align-items: center; gap: 0.5rem;">
                                    <span>Progresso:</span>
                                    <div style="flex: 1; background: rgba(255,255,255,0.1); border-radius: 10px; height: 6px;">
                                        <div style="width: {row['progress']}%; background: {progress_color}; height: 100%; border-radius: 10px;"></div>
                                    </div>
                                    <span>{row['progress']}%</span>
                                </div>
                            </div>
                            <div style="margin-top: 0.5rem;">
                                <span class="badge badge-info">{status_display}</span>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if st.button("📖 Ler", key=f"read_wp_{row['id']}"):
                        st.session_state[f"show_wp_details_{row['id']}"] = True
                        st.rerun()
                with col2:
                    if st.button("✏️ Editar", key=f"edit_wp_{row['id']}"):
                        st.session_state[f"editing_wp_{row['id']}"] = True
                with col3:
                    if st.button("📥 Exportar", key=f"export_wp_{row['id']}"):
                        wp_data = pd.DataFrame([{"Título": row['title'], "Tópico": row['topic'], "Autor": row['author_name'], "Status": row['status']}])
                        export_to_excel(wp_data, f"whitepaper_{row['id']}")
                with col4:
                    if st.button("🗑️ Excluir", key=f"delete_wp_{row['id']}"):
                        delete_whitepaper(row['id'])
                        add_notification(f"✅ Whitepaper excluído!", "success")
                        st.rerun()
                
                if st.session_state.get(f"editing_wp_{row['id']}", False):
                    with st.form(f"edit_wp_form_{row['id']}"):
                        new_title = st.text_input("Título", value=row['title'])
                        new_topic = st.text_input("Tópico", value=row['topic'] or "")
                        new_author = st.text_input("Autor", value=row['author_name'] or "")
                        new_status = st.selectbox("Status", ["draft", "review", "published"], index=["draft", "review", "published"].index(row['status']))
                        new_progress = st.slider("Progresso", 0, 100, row['progress'] or 0)
                        if st.form_submit_button("💾 Salvar"):
                            updates = {"title": new_title, "topic": new_topic, "author_name": new_author,
                                      "status": new_status, "progress": new_progress}
                            update_whitepaper_details(row['id'], updates)
                            st.session_state[f"editing_wp_{row['id']}"] = False
                            st.rerun()
                
                if st.session_state.get(f"show_wp_details_{row['id']}", False):
                    with st.expander(f"📖 {row['title']} - Detalhes", expanded=True):
                        show_whitepaper_modal(row['id'], row['title'])
                
                st.markdown("---")
    
    # TAB 2: GLOSSÁRIO
    with tab2:
        st.subheader("Glossário")
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("📄 Exportar PDF", use_container_width=True):
                glossary_df = get_glossary()
                if not glossary_df.empty:
                    pdf_buffer = export_glossary_to_pdf(glossary_df)
                    st.download_button(label="📥 Baixar PDF", data=pdf_buffer, file_name=f"glossario_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf")
        
        with col1:
            search_term = st.text_input("🔍 Buscar no glossário", placeholder="Termo, definição, categoria ou exemplo...", key="search_glossary")
        
        with st.expander("➕ Novo Termo", expanded=False):
            with st.form("new_term"):
                term = st.text_input("Termo *")
                definition = st.text_area("Definição *")
                category = st.selectbox("Categoria", ["technical", "business", "acronym"])
                example = st.text_input("Exemplo")
                if st.form_submit_button("Salvar") and term and definition:
                    cur = conn.cursor()
                    cur.execute("INSERT INTO glossary (term, definition, category, example) VALUES (%s, %s, %s, %s)",
                               (term, definition, category, example))
                    conn.commit()
                    st.rerun()
        
        glossary = get_glossary()
        if search_term:
            glossary = glossary[
                glossary['term'].str.contains(search_term, case=False, na=False) |
                glossary['definition'].str.contains(search_term, case=False, na=False) |
                glossary['category'].str.contains(search_term, case=False, na=False) |
                glossary['example'].str.contains(search_term, case=False, na=False)
            ]
        
        for _, row in glossary.iterrows():
            st.markdown(f"""
            <div class="card-modern">
                <h4>{row['term']}</h4>
                <p><em>{row['definition']}</em></p>
                <p><strong>Categoria:</strong> {row['category']} | <strong>Exemplo:</strong> {row['example'] or 'N/A'}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # TAB 3: CASE STUDIES
    with tab3:
        st.subheader("Case Studies")
        with st.expander("➕ Novo Case Study", expanded=False):
            with st.form("new_case"):
                title = st.text_input("Título *")
                category = st.selectbox("Categoria", ["manufacturing", "supply_chain", "digital_twin", "ia_ml", "healthcare"])
                summary = st.text_area("Resumo *")
                author = st.text_input("Autor")
                if st.form_submit_button("Salvar") and title and summary:
                    cur = conn.cursor()
                    cur.execute("""INSERT INTO knowledge_base (title, type, category, summary, author)
                                   VALUES (%s, 'case_study', %s, %s, %s)""",
                               (title, category, summary, author))
                    conn.commit()
                    st.rerun()

        search_cases = st.text_input("🔍 Buscar case studies", placeholder="Título, categoria, autor ou resumo...", key="search_cases")
        cases = get_cases()
        if search_cases:
            cases = cases[
                cases['title'].str.contains(search_cases, case=False, na=False) |
                cases['category'].str.contains(search_cases, case=False, na=False) |
                cases['author'].str.contains(search_cases, case=False, na=False) |
                cases['summary'].str.contains(search_cases, case=False, na=False)
            ]
        if cases.empty:
            st.info("Nenhum case study encontrado.")
        else:
            for _, row in cases.iterrows():
                st.markdown(f"""
                <div class="card-modern">
                    <h4>{row['title']}</h4>
                    <p><strong>Categoria:</strong> {row['category']} | <strong>Autor:</strong> {row['author'] or 'N/A'}</p>
                    <p>{row['summary']}</p>
                </div>
                """, unsafe_allow_html=True)

# ===== EMPRESAS TARGET =====
elif menu == "🏢 Empresas Target":
    st.header("🏢 Empresas Target")
    
    with st.expander("➕ Nova Empresa", expanded=False):
        with st.form("new_company"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Nome da empresa *")
                industry = st.selectbox("Indústria", ["manufacturing", "healthcare", "b2b", "tech"])
            with col2:
                status = st.selectbox("Status", ["prospect", "contacted", "meeting", "proposal"])
                contact_person = st.text_input("Contato")
            notes = st.text_area("Observações")
            if st.form_submit_button("Salvar") and name:
                cur = conn.cursor()
                cur.execute("""INSERT INTO target_companies (name, industry, status, contact_person, notes)
                               VALUES (%s, %s, %s, %s, %s)""",
                           (name, industry, status, contact_person, notes))
                conn.commit()
                st.rerun()
    
    search_company = st.text_input("🔍 Buscar empresas", placeholder="Nome, indústria, status ou contato...", key="search_company")
    companies = get_companies()
    if search_company:
        companies = companies[
            companies['name'].str.contains(search_company, case=False, na=False) |
            companies['industry'].str.contains(search_company, case=False, na=False) |
            companies['status'].str.contains(search_company, case=False, na=False) |
            companies['contact_person'].str.contains(search_company, case=False, na=False) |
            companies['notes'].str.contains(search_company, case=False, na=False)
        ]
    if companies.empty:
        st.info("Nenhuma empresa encontrada.")
    else:
        for _, row in companies.iterrows():
            st.markdown(f"""
            <div class="card-modern">
                <h4>{row['name']}</h4>
                <p><strong>Indústria:</strong> {row['industry']} | <strong>Status:</strong> {row['status']}</p>
                <p><strong>Contato:</strong> {row['contact_person'] or 'N/A'}</p>
                <p><em>{row['notes']}</em></p>
            </div>
            """, unsafe_allow_html=True)

# ===== SENIOR ADVISORS =====
elif menu == "👥 Senior Advisors":
    st.header("👥 Senior Advisors")
    
    with st.expander("➕ Novo Advisor", expanded=False):
        with st.form("new_advisor"):
            name = st.text_input("Nome *")
            expertise = st.text_input("Expertise")
            company = st.text_input("Empresa")
            linkedin = st.text_input("LinkedIn")
            notes = st.text_area("Notas")
            if st.form_submit_button("Salvar") and name:
                cur = conn.cursor()
                cur.execute("""INSERT INTO senior_advisors (name, expertise, company, linkedin, notes)
                               VALUES (%s, %s, %s, %s, %s)""",
                           (name, expertise, company, linkedin, notes))
                conn.commit()
                st.rerun()
    
    search_advisor = st.text_input("🔍 Buscar advisors", placeholder="Nome, expertise, empresa ou notas...", key="search_advisor")
    advisors = get_advisors()
    if search_advisor:
        advisors = advisors[
            advisors['name'].str.contains(search_advisor, case=False, na=False) |
            advisors['expertise'].str.contains(search_advisor, case=False, na=False) |
            advisors['company'].str.contains(search_advisor, case=False, na=False) |
            advisors['notes'].str.contains(search_advisor, case=False, na=False)
        ]
    if advisors.empty:
        st.info("Nenhum senior advisor encontrado.")
    else:
        for _, row in advisors.iterrows():
            st.markdown(f"""
            <div class="card-modern">
                <h4>{row['name']}</h4>
                <p><strong>Expertise:</strong> {row['expertise']} | <strong>Empresa:</strong> {row['company'] or 'N/A'}</p>
                <p><strong>LinkedIn:</strong> <a href="{row['linkedin']}" target="_blank">{row['linkedin']}</a></p>
                <p><em>{row['notes']}</em></p>
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")
st.caption("TaskSync v3.0 - Operations Strategy | Raíssa Azevedo - 2026")