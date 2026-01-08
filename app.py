import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Yassir Invoice Generator", page_icon="🔴", layout="wide")

# --- STYLE CSS (Charte Yassir : Rouge #E3001B, Fond Blanc/Gris) ---
st.markdown("""
    <style>
    .main { background-color: #FAFAFA; }
    h1, h2, h3 { color: #E3001B !important; font-family: 'Arial', sans-serif; font-weight: 700; }
    .stButton>button {
        background-color: #E3001B; color: white; border: none; padding: 10px 20px;
        font-weight: bold; border-radius: 5px; width: 100%;
    }
    .stButton>button:hover { background-color: #C20017; color: white; }
    .stSidebar { background-color: #FFFFFF; border-right: 1px solid #E3001B; }
    </style>
""", unsafe_allow_html=True)

# --- CLASSE PDF MÈRE (Template Yassir) ---
class PDFTemplate(FPDF):
    def header(self):
        # Logo Texte (simulé)
        self.set_font('Arial', 'B', 24)
        self.set_text_color(227, 0, 27) # Rouge Yassir
        self.cell(50, 10, 'Yassir', 0, 0, 'L')
        
        # Infos Yassir (Header Gauche en dessous du logo)
        self.ln(12)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(0)
        self.cell(0, 5, 'YASSIR MAROC', 0, 1, 'L')
        self.set_font('Arial', '', 8)
        self.cell(0, 5, 'VILLA 269 LOTISSEMENT MANDARONA', 0, 1, 'L')
        self.cell(0, 5, 'SIDI MAAROUF CASABLANCA - Maroc', 0, 1, 'L')
        self.cell(0, 5, 'ICE: 002148105000084', 0, 1, 'L')
        self.ln(10)

    def footer(self):
        self.set_y(-25)
        self.set_font('Arial', '', 7)
        self.set_text_color(100)
        self.multi_cell(0, 4, "YASSIR MAROC SARL au capital de 2,000,000 DH\nVILLA 269 LOTISSEMENT MANDARONA SIDI MAAROUF CASABLANCA - Maroc\nICE N°002148105000084 - RC 413733 - IF 26164744", 0, 'C')
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

# --- FONCTION : FACTURE RÉCAPITULATIVE ---
def generate_summary_pdf(client_info, totals):
    pdf = PDFTemplate()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Infos Facture (Haut Droite)
    pdf.set_y(15)
    pdf.set_x(120)
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(0)
    pdf.cell(80, 8, f"Facture N°: {client_info['ref_facture']}", 0, 1, 'R')
    pdf.set_x(120)
    pdf.set_font('Arial', '', 10)
    pdf.cell(80, 8, f"Date: {datetime.now().strftime('%d/%m/%Y')}", 0, 1, 'R')

    pdf.ln(25)

    # Cadre Client
    pdf.set_fill_color(250, 250, 250)
    pdf.set_draw_color(220, 220, 220)
    pdf.rect(10, pdf.get_y(), 90, 40, 'FD')
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(90, 8, f"   {client_info['name']}", 0, 1, 'L')
    pdf.set_font('Arial', '', 9)
    pdf.cell(90, 6, f"   Adresse: {client_info['address']}", 0, 1, 'L')
    pdf.cell(90, 6, f"   Ville: {client_info['city']}", 0, 1, 'L')
    pdf.cell(90, 6, f"   ICE: {client_info['ice']}", 0, 1, 'L')
    if client_info['rc']:
        pdf.cell(90, 6, f"   RC: {client_info['rc']}", 0, 1, 'L')

    pdf.ln(20)

    # Tableau 1 : Ligne Unique
    pdf.set_fill_color(227, 0, 27)
    pdf.set_text_color(255)
    pdf.set_font('Arial', 'B', 9)
    # Headers
    cols = [60, 40, 40, 50]
    headers = ['Période', 'Ventes TTC', 'Taux Comm.', 'Commission HT']
    for i, h in enumerate(headers):
        pdf.cell(cols[i], 10, h, 1, 0, 'C', 1)
    pdf.ln()
    
    # Data
    pdf.set_text_color(0)
    pdf.set_font('Arial', '', 9)
    pdf.cell(cols[0], 10, f"{client_info['period']}", 1, 0, 'C')
    pdf.cell(cols[1], 10, f"{totals['sales_ttc']:,.2f}", 1, 0, 'C')
    pdf.cell(cols[2], 10, f"{client_info['rate']}%", 1, 0, 'C')
    pdf.cell(cols[3], 10, f"{totals['comm_ht']:,.2f}", 1, 1, 'C')

    pdf.ln(10)

    # Tableau 2 : Totaux (Aligné à droite)
    x_start = 110
    
    def add_total_row(label, value, bold=False, bg=False):
        pdf.set_x(x_start)
        pdf.set_font('Arial', 'B' if bold else '', 9)
        pdf.set_fill_color(240 if bg else 255)
        pdf.cell(50, 8, label, 1, 0, 'L', bg)
        pdf.cell(40, 8, f"{value:,.2f}", 1, 1, 'R', bg)

    add_total_row("Total Commission HT", totals['comm_ht'])
    add_total_row("TVA 20%", totals['tva'])
    add_total_row("Total Facture TTC", totals['invoice_ttc'], bold=True)
    add_total_row("Total du panier", totals['sales_ttc'])
    
    pdf.ln(2)
    pdf.set_x(x_start)
    pdf.set_fill_color(227, 0, 27)
    pdf.set_text_color(255)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(50, 10, "NET À PAYER", 1, 0, 'L', 1)
    pdf.cell(40, 10, f"{totals['net_pay']:,.2f} DH", 1, 1, 'R', 1)

    # Pied de page explicatif
    pdf.ln(20)
    pdf.set_text_color(0)
    pdf.set_font('Arial', 'I', 9)
    pdf.cell(0, 6, f"Arrêté la présente facture à la somme de : {totals['net_pay']:,.2f} Dirhams", 0, 1, 'L')
    pdf.cell(0, 6, "Mode de règlement: Virement bancaire", 0, 1, 'L')

    return pdf.output(dest='S').encode('latin-1')

# --- FONCTION : PDF DÉTAILLÉ ---
def generate_detail_pdf(client_info, df_detail, col_mapping):
    pdf = PDFTemplate()
    pdf.alias_nb_pages()
    pdf.add_page()

    # Titre
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f"DÉTAIL DES OPÉRATIONS - {client_info['period']}", 0, 1, 'C')
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 10, f"Partenaire: {client_info['name']}", 0, 1, 'C')
    pdf.ln(10)

    # Table Header
    pdf.set_fill_color(200, 200, 200)
    pdf.set_font('Arial', 'B', 8)
    
    # On définit les colonnes qu'on veut afficher
    display_cols = ['Date', 'ID Commande', 'Montant Commande', 'Statut']
    # Largeurs
    w = [40, 50, 50, 40]

    for i, h in enumerate(display_cols):
        pdf.cell(w[i], 8, h, 1, 0, 'C', 1)
    pdf.ln()

    # Table Body
    pdf.set_font('Arial', '', 8)
    pdf.set_fill_color(255)

    # On itère sur le dataframe
    # col_mapping = {'date': 'nom_col_csv', 'id': '...', 'amount': '...'}
    
    count = 0
    total_page = 0
    
    for _, row in df_detail.iterrows():
        date_val = str(row[col_mapping['date']])
        id_val = str(row[col_mapping['id']])
        amount_val = float(str(row[col_mapping['amount']]).replace(',','').replace('MAD','').strip())
        status_val = str(row[col_mapping['status']]) if col_mapping['status'] != 'Aucun' else '-'

        pdf.cell(w[0], 7, date_val[:10], 1, 0, 'C')
        pdf.cell(w[1], 7, id_val, 1, 0, 'C')
        pdf.cell(w[2], 7, f"{amount_val:,.2f}", 1, 0, 'R')
        pdf.cell(w[3], 7, status_val, 1, 1, 'C')
        
        count += 1
        # Saut de page si nécessaire
        if pdf.get_y() > 260:
            pdf.add_page()
            # Répéter header
            pdf.set_font('Arial', 'B', 8)
            pdf.set_fill_color(200)
            for i, h in enumerate(display_cols):
                pdf.cell(w[i], 8, h, 1, 0, 'C', 1)
            pdf.ln()
            pdf.set_font('Arial', '', 8)

    return pdf.output(dest='S').encode('latin-1')

# --- INTERFACE PRINCIPALE ---

st.sidebar.title("⚙️ Paramètres Facture")
st.sidebar.markdown("---")
st.sidebar.subheader("1. Infos Client (Partenaire)")

c_name = st.sidebar.text_input("Nom / Raison Sociale", "BLUE TACOS")
c_addr = st.sidebar.text_input("Adresse", "BD MOHAMMED VI")
c_city = st.sidebar.text_input("Ville", "CASABLANCA")
c_ice = st.sidebar.text_input("ICE", "003...")
c_rc = st.sidebar.text_input("RC (Optionnel)")

st.sidebar.subheader("2. Période & Commission")
c_period = st.sidebar.text_input("Période (ex: NOVEMBRE 2025)", "NOVEMBRE 2025")
c_ref = st.sidebar.text_input("Réf. Facture", f"F-{datetime.now().strftime('%m%Y')}-001")
c_rate = st.sidebar.number_input("Taux de Commission (%)", value=14.0, step=0.5)

# --- ZONE PRINCIPALE ---
st.title("Générateur de Factures & Détails")
st.write("Upload ton fichier CSV contenant le détail des commandes.")

uploaded_file = st.file_uploader("📂 Glisse ton fichier CSV ici", type=['csv'])

if uploaded_file:
    # Lecture CSV
    try:
        df = pd.read_csv(uploaded_file, sep=None, engine='python') # Auto-detect separator
        st.success(f"Fichier chargé : {len(df)} lignes détectées.")
        st.dataframe(df.head(3))
        
        st.markdown("### 🔗 Mapping des colonnes")
        st.info("Indique quelle colonne du CSV correspond à quelle donnée.")
        
        cols = df.columns.tolist()
        
        c1, c2, c3, c4 = st.columns(4)
        col_date = c1.selectbox("Colonne DATE", cols, index=0)
        col_id = c2.selectbox("Colonne ID COMMANDE", cols, index=1 if len(cols)>1 else 0)
        col_amount = c3.selectbox("Colonne MONTANT TOTAL", cols, index=2 if len(cols)>2 else 0)
        col_status = c4.selectbox("Colonne STATUT (Optionnel)", ["Aucun"] + cols)

        # Calculs
        # Nettoyage montant
        try:
            df['clean_amount'] = df[col_amount].astype(str).str.replace('MAD','').str.replace(' ','').str.replace(',','.').astype(float)
            
            # Filtrage optionnel (si statut = Livrée uniquement ?)
            # Pour l'instant on prend tout, ou on peut ajouter un filtre
            
            total_sales = df['clean_amount'].sum()
            comm_ht = total_sales * (c_rate / 100)
            tva = comm_ht * 0.20
            invoice_ttc = comm_ht + tva
            net_pay = total_sales - invoice_ttc
            
            totals = {
                'sales_ttc': total_sales,
                'comm_ht': comm_ht,
                'tva': tva,
                'invoice_ttc': invoice_ttc,
                'net_pay': net_pay
            }
            
            client_info = {
                'name': c_name, 'address': c_addr, 'city': c_city, 'ice': c_ice, 'rc': c_rc,
                'period': c_period, 'ref_facture': c_ref, 'rate': c_rate
            }
            
            col_mapping = {
                'date': col_date, 'id': col_id, 'amount': col_amount, 'status': col_status
            }

            st.markdown("---")
            st.subheader("📊 Aperçu des chiffres")
            k1, k2, k3 = st.columns(3)
            k1.metric("Ventes Totales", f"{total_sales:,.2f} DH")
            k2.metric("Commission Yassir (HT)", f"{comm_ht:,.2f} DH")
            k3.metric("Net à Payer Partenaire", f"{net_pay:,.2f} DH")
            
            st.markdown("### 📥 Téléchargements")
            
            # Génération
            if st.button("Générer les documents PDF"):
                # PDF 1 : Facture
                pdf_summary = generate_summary_pdf(client_info, totals)
                b64_summary = base64.b64encode(pdf_summary).decode()
                
                # PDF 2 : Détail
                pdf_detail = generate_detail_pdf(client_info, df, col_mapping)
                b64_detail = base64.b64encode(pdf_detail).decode()
                
                col_d1, col_d2 = st.columns(2)
                
                href_summary = f'<a href="data:application/octet-stream;base64,{b64_summary}" download="Facture_{c_ref}.pdf" style="text-decoration:none;"><button style="background-color:#E3001B;color:white;border:none;padding:10px;border-radius:5px;width:100%;font-weight:bold;">📄 Télécharger la Facture</button></a>'
                col_d1.markdown(href_summary, unsafe_allow_html=True)
                
                href_detail = f'<a href="data:application/octet-stream;base64,{b64_detail}" download="Detail_{c_ref}.pdf" style="text-decoration:none;"><button style="background-color:#333;color:white;border:none;padding:10px;border-radius:5px;width:100%;font-weight:bold;">📑 Télécharger le Détail</button></a>'
                col_d2.markdown(href_detail, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Erreur lors du calcul des montants. Vérifiez le format de la colonne montant. ({e})")

    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier : {e}")

else:
    st.info("En attente de fichier CSV...")
