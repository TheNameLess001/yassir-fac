import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
from datetime import datetime
import os

# --- CONFIGURATION CHARTE GRAPHIQUE (NOUVEAU LOGO VIOLET) ---
# Remplace ce code HEX par le violet exact si nécessaire (ex: #5E17EB, #4B0082...)
YASSIR_PURPLE = "#6f42c1"  
YASSIR_BLACK = "#000000"
YASSIR_GRAY = "#F8F9FA"
LOGO_PATH = "logo.png"  # Assurez-vous que votre fichier logo est dans le même dossier

# --- SETUP PAGE ---
st.set_page_config(page_title="Générateur Factures Yassir", page_icon="🟣", layout="wide")

# Injection CSS pour le thème Violet
st.markdown(f"""
    <style>
    .main {{ background-color: {YASSIR_GRAY}; }}
    h1, h2, h3 {{ color: {YASSIR_PURPLE} !important; font-family: 'Arial', sans-serif; font-weight: 700; }}
    .stButton>button {{
        background-color: {YASSIR_PURPLE}; color: white; border: none; padding: 10px 20px;
        font-weight: bold; border-radius: 8px; width: 100%; transition: 0.3s;
    }}
    .stButton>button:hover {{ background-color: #5a32a3; color: white; }}
    .stSidebar {{ background-color: #FFFFFF; border-right: 2px solid {YASSIR_PURPLE}; }}
    .metric-box {{ border: 1px solid {YASSIR_PURPLE}; border-radius: 5px; padding: 10px; text-align: center; }}
    </style>
""", unsafe_allow_html=True)

# --- MOTEUR PDF (FPDF) ---
class PDFTemplate(FPDF):
    def header(self):
        # 1. LOGO (Importation auto si présent)
        if os.path.exists(LOGO_PATH):
            self.image(LOGO_PATH, 10, 8, 30)
            self.ln(25)
        else:
            # Fallback Texte Violet si pas d'image
            self.set_font('Arial', 'B', 24)
            # Conversion Hex -> RGB pour FPDF
            r, g, b = tuple(int(YASSIR_PURPLE.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            self.set_text_color(r, g, b)
            self.cell(50, 10, 'Yassir', 0, 1, 'L')
            self.ln(5)
        
        # 2. INFOS YASSIR (Fixes)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(0)
        self.cell(0, 5, 'YASSIR MAROC', 0, 1, 'L')
        self.set_font('Arial', '', 8)
        self.cell(0, 5, 'VILLA 269 LOTISSEMENT MANDARONA', 0, 1, 'L')
        self.cell(0, 5, 'SIDI MAAROUF CASABLANCA - Maroc', 0, 1, 'L')
        self.cell(0, 5, 'ICE: 002148105000084', 0, 1, 'L')
        
        # Ligne de séparation Violette
        r, g, b = tuple(int(YASSIR_PURPLE.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        self.set_draw_color(r, g, b)
        self.set_line_width(0.5)
        self.line(10, self.get_y()+5, 200, self.get_y()+5)
        self.ln(10)

    def footer(self):
        self.set_y(-25)
        self.set_font('Arial', '', 7)
        self.set_text_color(100)
        # Footer légal identique à l'exemple
        self.multi_cell(0, 4, "YASSIR MAROC SARL au capital de 2,000,000 DH\nVILLA 269 LOTISSEMENT MANDARONA SIDI MAAROUF CASABLANCA - Maroc\nICE N°002148105000084 - RC 413733 - IF 26164744", 0, 'C')
        
        # Numéro de page en violet
        r, g, b = tuple(int(YASSIR_PURPLE.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        self.set_text_color(r, g, b)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

# --- FONCTION GENERATION FACTURE ---
def generate_invoice_pdf(client_data, totals):
    pdf = PDFTemplate()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Couleur Violette RGB
    r, g, b = tuple(int(YASSIR_PURPLE.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

    # --- EN-TÊTE FACTURE ---
    pdf.set_y(20)
    pdf.set_x(120)
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(r, g, b)
    pdf.cell(80, 8, "FACTURE COMMISSION", 0, 1, 'R')
    
    pdf.set_x(120)
    pdf.set_text_color(0)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(80, 6, f"N°: {client_data['ref']}", 0, 1, 'R')
    
    pdf.set_x(120)
    pdf.set_font('Arial', '', 10)
    pdf.cell(80, 6, f"Date: {datetime.now().strftime('%d/%m/%Y')}", 0, 1, 'R')

    pdf.ln(15)

    # --- ZONE CLIENT (Modifiable via Sidebar) ---
    start_y = pdf.get_y()
    
    # Fond gris clair
    pdf.set_fill_color(248, 248, 248)
    pdf.set_draw_color(220, 220, 220)
    pdf.rect(10, start_y, 90, 40, 'F')
    
    # Barre verticale violette (Marque du nouveau design)
    pdf.set_fill_color(r, g, b)
    pdf.rect(10, start_y, 2, 40, 'F')
    
    pdf.set_xy(15, start_y + 5)
    pdf.set_font('Arial', 'B', 10)
    pdf.set_text_color(0)
    pdf.cell(80, 5, f"{client_data['name']}", 0, 1, 'L')
    
    pdf.set_font('Arial', '', 9)
    pdf.set_x(15)
    pdf.cell(80, 5, f"{client_data['address']}", 0, 1, 'L')
    pdf.set_x(15)
    pdf.cell(80, 5, f"{client_data['city']}", 0, 1, 'L')
    pdf.set_x(15)
    pdf.cell(80, 5, f"ICE: {client_data['ice']}", 0, 1, 'L')
    if client_data['rc']:
        pdf.set_x(15)
        pdf.cell(80, 5, f"RC: {client_data['rc']}", 0, 1, 'L')

    pdf.ln(25)

    # --- TABLEAU PRINCIPAL ---
    # En-tête Violet
    pdf.set_fill_color(r, g, b)
    pdf.set_text_color(255)
    pdf.set_font('Arial', 'B', 9)
    
    cols = [60, 40, 40, 50]
    headers = ['Période', 'Ventes TTC', 'Taux Comm.', 'Commission HT']
    
    for i, h in enumerate(headers):
        pdf.cell(cols[i], 10, h, 0, 0, 'C', 1)
    pdf.ln()
    
    # Données
    pdf.set_text_color(0)
    pdf.set_font('Arial', '', 9)
    pdf.set_fill_color(255)
    
    # Une seule ligne récapitulative (comme l'exemple O'Tacos)
    pdf.cell(cols[0], 10, f"{client_data['period']}", 'B', 0, 'C')
    pdf.cell(cols[1], 10, f"{totals['sales']:,.2f}", 'B', 0, 'C')
    pdf.cell(cols[2], 10, f"{client_data['rate']}%", 'B', 0, 'C')
    pdf.cell(cols[3], 10, f"{totals['comm_ht']:,.2f}", 'B', 1, 'C')

    pdf.ln(10)

    # --- TOTAUX (Alignés à droite) ---
    x_start = 110
    
    def add_total_line(label, value, bg_color=False, is_bold=False):
        pdf.set_x(x_start)
        pdf.set_font('Arial', 'B' if is_bold else '', 9)
        if bg_color:
            pdf.set_fill_color(r, g, b)
            pdf.set_text_color(255)
            pdf.cell(50, 9, label, 0, 0, 'L', 1)
            pdf.cell(40, 9, f"{value:,.2f} DH", 0, 1, 'R', 1)
        else:
            pdf.set_text_color(0)
            pdf.cell(50, 7, label, 1, 0, 'L')
            pdf.cell(40, 7, f"{value:,.2f}", 1, 1, 'R')

    add_total_line("Total Commission HT", totals['comm_ht'])
    add_total_line("TVA 20%", totals['tva'])
    add_total_line("Total Facture TTC", totals['invoice_ttc'], is_bold=True)
    add_total_line("Total du panier", totals['sales'])
    
    pdf.ln(2)
    # Net à Payer en Violet
    add_total_line("NET À PAYER", totals['net_pay'], bg_color=True, is_bold=True)

    # --- PIED DE PAGE EXPLICATIF ---
    pdf.ln(15)
    pdf.set_text_color(0)
    pdf.set_font('Arial', 'I', 9)
    pdf.cell(0, 6, f"Arrêté la présente facture à la somme de : {totals['net_pay']:,.2f} Dirhams", 0, 1, 'L')
    pdf.cell(0, 6, "Mode de règlement: Virement bancaire", 0, 1, 'L')

    return pdf.output(dest='S').encode('latin-1')

# --- FONCTION ANNEXE DÉTAILLÉE ---
def generate_detail_pdf(client_data, df_detail, mapping):
    pdf = PDFTemplate()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    r, g, b = tuple(int(YASSIR_PURPLE.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

    # Titre
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(r, g, b)
    pdf.cell(0, 10, f"DÉTAIL DES COMMANDES", 0, 1, 'C')
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(0)
    pdf.cell(0, 8, f"Période : {client_data['period']}", 0, 1, 'C')
    pdf.ln(10)

    # Header Tableau
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font('Arial', 'B', 8)
    
    cols = ['Date', 'ID Commande', 'Montant', 'Statut']
    w = [40, 60, 40, 50]
    
    for i, c in enumerate(cols):
        pdf.cell(w[i], 8, c, 1, 0, 'C', 1)
    pdf.ln()

    # Body
    pdf.set_font('Arial', '', 8)
    for _, row in df_detail.iterrows():
        # Extraction sécurisée via le mapping
        d = str(row[mapping['date']])[:10]
        i = str(row[mapping['id']])
        # Nettoyage montant
        try:
            m_raw = str(row[mapping['amount']]).replace(',','.').replace('MAD','').strip()
            m = float(m_raw)
            m_str = f"{m:,.2f}"
        except:
            m_str = "0.00"
            
        s = str(row[mapping['status']]) if mapping['status'] != 'Aucun' else '-'

        pdf.cell(w[0], 7, d, 1, 0, 'C')
        pdf.cell(w[1], 7, i, 1, 0, 'C')
        pdf.cell(w[2], 7, m_str, 1, 0, 'R')
        pdf.cell(w[3], 7, s, 1, 1, 'C')

    return pdf.output(dest='S').encode('latin-1')


# ==========================================
# INTERFACE STREAMLIT
# ==========================================

# --- SIDEBAR : INFOS CLIENT ---
st.sidebar.image(LOGO_PATH) if os.path.exists(LOGO_PATH) else st.sidebar.title("🟣 Yassir")
st.sidebar.markdown("### 📝 Infos Partenaire (Client)")
st.sidebar.info("Remplissez ici les infos qui apparaîtront sur la facture.")

c_name = st.sidebar.text_input("Nom / Raison Sociale", "BLUE TACOS")
c_addr = st.sidebar.text_input("Adresse", "BD MOHAMMED VI")
c_city = st.sidebar.text_input("Ville", "CASABLANCA")
c_ice = st.sidebar.text_input("ICE Client", "003...")
c_rc = st.sidebar.text_input("RC Client", "")

st.sidebar.markdown("### 📅 Période & Facturation")
c_period = st.sidebar.text_input("Période concernée", "NOVEMBRE 2025")
c_ref = st.sidebar.text_input("Numéro Facture", f"F-{datetime.now().strftime('%Y%m')}-001")
c_rate = st.sidebar.number_input("Taux de Commission (%)", value=14.0, step=0.5)

# --- ZONE PRINCIPALE ---
st.title("Générateur de Factures Partenaires")
st.markdown("Importez le fichier CSV (`Detail_Commandes...`) pour générer automatiquement : \n1. **La Facture** (Format O'Tacos)\n2. **Le Détail** des opérations.")

uploaded_file = st.file_uploader("📂 Déposez votre fichier CSV ici", type=['csv'])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, sep=None, engine='python')
        st.success(f"✅ Fichier chargé : {len(df)} commandes.")
        
        with st.expander("👀 Voir les premières lignes du fichier"):
            st.dataframe(df.head())

        st.markdown("### 🔗 Configuration des Colonnes")
        st.caption("Sélectionnez les colonnes correspondantes dans votre fichier CSV.")
        
        cols = df.columns.tolist()
        c1, c2, c3, c4 = st.columns(4)
        
        # Selectbox intelligentes
        col_date = c1.selectbox("Date", cols, index=0)
        col_id = c2.selectbox("ID Commande", cols, index=1 if len(cols)>1 else 0)
        col_amt = c3.selectbox("Montant (TTC)", cols, index=2 if len(cols)>2 else 0)
        col_stat = c4.selectbox("Statut (Optionnel)", ["Aucun"] + cols)

        # --- CALCULS ---
        # Nettoyage de la colonne montant
        try:
            clean_series = df[col_amt].astype(str).str.replace('MAD','').str.replace(' ','').str.replace(',','.')
            df['clean_amount'] = pd.to_numeric(clean_series, errors='coerce').fillna(0)
            
            total_sales = df['clean_amount'].sum()
            comm_ht = total_sales * (c_rate / 100)
            tva = comm_ht * 0.20
            invoice_ttc = comm_ht + tva
            net_pay = total_sales - invoice_ttc
            
            # Données structurées pour PDF
            totals = {
                'sales': total_sales,
                'comm_ht': comm_ht,
                'tva': tva,
                'invoice_ttc': invoice_ttc,
                'net_pay': net_pay
            }
            client_data = {
                'name': c_name, 'address': c_addr, 'city': c_city, 
                'ice': c_ice, 'rc': c_rc, 'period': c_period, 
                'ref': c_ref, 'rate': c_rate
            }
            mapping = {
                'date': col_date, 'id': col_id, 'amount': col_amt, 'status': col_stat
            }

            # Affichage des métriques
            st.markdown("---")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Ventes Totales", f"{total_sales:,.2f}")
            m2.metric("Commission HT", f"{comm_ht:,.2f}")
            m3.metric("Facture Yassir (TTC)", f"{invoice_ttc:,.2f}")
            m4.metric("Net à Verser Partenaire", f"{net_pay:,.2f}", delta_color="normal")

            # --- BOUTONS GENERATION ---
            st.markdown("### 🖨️ Édition des Documents")
            
            col_btn1, col_btn2 = st.columns(2)
            
            # PDF 1
            pdf_inv = generate_invoice_pdf(client_data, totals)
            b64_inv = base64.b64encode(pdf_inv).decode()
            href_inv = f'<a href="data:application/octet-stream;base64,{b64_inv}" download="Facture_{c_ref}.pdf"><button style="background-color:{YASSIR_PURPLE};color:white;border:none;padding:12px;border-radius:8px;width:100%;font-weight:bold;cursor:pointer;">📥 Télécharger la Facture (PDF)</button></a>'
            col_btn1.markdown(href_inv, unsafe_allow_html=True)
            
            # PDF 2
            pdf_det = generate_detail_pdf(client_data, df, mapping)
            b64_det = base64.b64encode(pdf_det).decode()
            href_det = f'<a href="data:application/octet-stream;base64,{b64_det}" download="Detail_Commandes_{c_period}.pdf"><button style="background-color:#6c757d;color:white;border:none;padding:12px;border-radius:8px;width:100%;font-weight:bold;cursor:pointer;">📑 Télécharger le Détail (PDF)</button></a>'
            col_btn2.markdown(href_det, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Erreur de calcul sur les montants : {e}")
            
    except Exception as e:
        st.error(f"Erreur de lecture du fichier : {e}")

else:
    st.info("👋 En attente d'un fichier CSV pour commencer...")
