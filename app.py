import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Générateur Factures Partenaires",
    page_icon="🔴",
    layout="centered"
)

# --- STYLE CSS (Charte Yassir) ---
# On force le rouge Yassir (#E3001B) et un style propre
st.markdown("""
    <style>
    .stApp {
        background-color: #FAFAFA;
    }
    h1, h2, h3 {
        color: #E3001B !important;
        font-family: 'Arial', sans-serif;
    }
    .stButton>button {
        background-color: #E3001B;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #C20017;
        color: white;
    }
    .uploadedFile {
        border: 1px solid #E3001B;
    }
    </style>
""", unsafe_allow_html=True)

# --- CLASSE DE GÉNÉRATION PDF ---
class YassirInvoice(FPDF):
    def header(self):
        # Logo (Simulé par du texte si pas d'image, sinon insérer image)
        self.set_font('Arial', 'B', 24)
        self.set_text_color(227, 0, 27) # Rouge Yassir
        self.cell(0, 10, 'Yassir', 0, 1, 'L')
        
        # Info Yassir (Gauche)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(0, 0, 0)
        self.cell(0, 5, 'YASSIR MAROC', 0, 1, 'L')
        self.set_font('Arial', '', 8)
        self.cell(0, 5, 'VILLA 269 LOTISSEMENT MANDARONA', 0, 1, 'L')
        self.cell(0, 5, 'SIDI MAAROUF CASABLANCA - Maroc', 0, 1, 'L')
        self.cell(0, 5, 'ICE: 002148105000084', 0, 1, 'L')
        self.ln(5)

    def footer(self):
        self.set_y(-25)
        self.set_font('Arial', '', 7)
        self.set_text_color(100, 100, 100)
        self.multi_cell(0, 4, "YASSIR MAROC SARL au capital de 2,000,000 DH\nVILLA 269 LOTISSEMENT MANDARONA SIDI MAAROUF CASABLANCA - Maroc\nICE N°002148105000084 - RC 413733 - IF 26164744", 0, 'C')

def create_pdf(row):
    pdf = YassirInvoice()
    pdf.add_page()
    
    # --- INFO FACTURE (Haut Droite) ---
    pdf.set_xy(120, 10)
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(70, 8, f"Facture N°: {row['Facture_Ref']}", 0, 1, 'R')
    pdf.set_font('Arial', '', 10)
    pdf.cell(70, 8, f"Date: {row['Date']}", 0, 1, 'R')

    pdf.ln(20)

    # --- CLIENT BOX ---
    pdf.set_fill_color(245, 245, 245)
    pdf.rect(10, pdf.get_y(), 90, 35, 'F')
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(90, 8, f"   {row['Client']}", 0, 1, 'L')
    pdf.set_font('Arial', '', 9)
    pdf.cell(90, 6, f"   Adresse: {row['Adresse']}", 0, 1, 'L')
    pdf.cell(90, 6, f"   Ville: {row['Ville']}", 0, 1, 'L')
    pdf.cell(90, 6, f"   ICE: {row['ICE_Client']}", 0, 1, 'L')

    pdf.ln(15)

    # --- TABLEAU DÉTAILS ---
    # Header Tableau
    pdf.set_fill_color(227, 0, 27) # Rouge
    pdf.set_text_color(255, 255, 255) # Blanc
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(60, 10, 'Période', 1, 0, 'C', 1)
    pdf.cell(40, 10, 'Ventes TTC', 1, 0, 'C', 1)
    pdf.cell(40, 10, 'Taux Comm.', 1, 0, 'C', 1)
    pdf.cell(50, 10, 'Commission HT', 1, 1, 'C', 1)

    # Contenu Tableau
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 9)
    
    # Calculs (Logique : Commission calculée sur le HT estimé ou direct TTC selon paramétrage)
    # Ici on suit la logique de ta facture: Ventes 3885.90 -> Comm HT 453.36 (~11.6%).
    # Supposons que le CSV contient le montant Ventes TTC et le Taux.
    
    ventes_ttc = float(str(row['Ventes_TTC']).replace(',','.'))
    taux = float(str(row['Taux']).replace('%','')) / 100
    
    # Calcul reverse engineering approximatif de la facture modèle (TVA 20% sur la comm)
    # Commission HT = (Ventes TTC / 1.2) * Taux (Si le taux s'applique sur le HT)
    # Ou Commission HT = Ventes TTC * Taux
    # Pour l'exemple, calculons simplement : 
    comm_ht = ventes_ttc / 1.2 * taux 
    
    pdf.cell(60, 10, f"{row['Periode']}", 1, 0, 'C')
    pdf.cell(40, 10, f"{ventes_ttc:,.2f} DH", 1, 0, 'C')
    pdf.cell(40, 10, f"{int(taux*100)}%", 1, 0, 'C')
    pdf.cell(50, 10, f"{comm_ht:,.2f} DH", 1, 1, 'C')

    pdf.ln(10)

    # --- TABLEAU TOTAUX (Bas Droite) ---
    tva = comm_ht * 0.20
    total_facture_ttc = comm_ht + tva
    net_a_payer = ventes_ttc - total_facture_ttc

    x_start = 110
    pdf.set_x(x_start)
    pdf.cell(50, 8, "Total Commission HT", 1, 0, 'L')
    pdf.cell(40, 8, f"{comm_ht:,.2f}", 1, 1, 'R')

    pdf.set_x(x_start)
    pdf.cell(50, 8, "TVA 20%", 1, 0, 'L')
    pdf.cell(40, 8, f"{tva:,.2f}", 1, 1, 'R')
    
    pdf.set_x(x_start)
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(50, 8, "Total Facture TTC", 1, 0, 'L')
    pdf.cell(40, 8, f"{total_facture_ttc:,.2f}", 1, 1, 'R')
    
    pdf.set_x(x_start)
    pdf.set_font('Arial', '', 9)
    pdf.cell(50, 8, "Total du panier (Ventes)", 1, 0, 'L')
    pdf.cell(40, 8, f"{ventes_ttc:,.2f}", 1, 1, 'R')

    pdf.set_x(x_start)
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(50, 10, "NET À PAYER", 1, 0, 'L', 1)
    pdf.cell(40, 10, f"{net_a_payer:,.2f} DH", 1, 1, 'R', 1)

    # --- EN TOUTES LETTRES (Simulé pour l'exemple) ---
    pdf.ln(15)
    pdf.set_font('Arial', 'I', 9)
    pdf.cell(0, 5, f"Arrêté la présente facture à la somme de : {net_a_payer:,.2f} Dirhams", 0, 1, 'L')
    pdf.cell(0, 5, "Mode de règlement: Virement bancaire", 0, 1, 'L')

    return pdf.output(dest='S').encode('latin-1')

# --- INTERFACE UTILISATEUR ---

st.title("🔴 Générateur de Factures Partenaires")
st.write("Importez votre fichier CSV pour générer les factures PDF au format Yassir.")

# 1. Exemple de CSV
data_exemple = {
    'Facture_Ref': ['267-11-2025YAS'],
    'Date': ['30/11/2025'],
    'Client': ['LISABEL SARL (O TACOS)'],
    'Adresse': ['12 RUE SARIA BEN ZOUNAIM'],
    'Ville': ['CASABLANCA'],
    'ICE_Client': ['003655960000063'],
    'Periode': ['NOVEMBRE 2025'],
    'Ventes_TTC': [3885.90],
    'Taux': [14]
}
df_exemple = pd.DataFrame(data_exemple)

with st.expander("ℹ️ Format du fichier CSV attendu"):
    st.write("Votre fichier doit contenir ces colonnes exactes :")
    st.dataframe(df_exemple)
    csv_model = df_exemple.to_csv(index=False).encode('utf-8')
    st.download_button("Télécharger un modèle CSV", csv_model, "modele_facture.csv", "text/csv")

# 2. Upload
uploaded_file = st.file_uploader("Choisissez votre fichier CSV", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success(f"{len(df)} factures détectées.")
        
        # Aperçu
        st.dataframe(df.head())

        if st.button("Générer les Factures PDF"):
            progress_bar = st.progress(0)
            
            for index, row in df.iterrows():
                try:
                    pdf_bytes = create_pdf(row)
                    b64 = base64.b64encode(pdf_bytes).decode()
                    href = f'<a href="data:application/octet-stream;base64,{b64}" download="Facture_{row["Client"]}.pdf">📥 Télécharger Facture : {row["Client"]}</a>'
                    st.markdown(href, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Erreur sur la ligne {index}: {e}")
                
                progress_bar.progress((index + 1) / len(df))
            
            st.success("Traitement terminé !")

    except Exception as e:
        st.error(f"Erreur de lecture du fichier : {e}")
