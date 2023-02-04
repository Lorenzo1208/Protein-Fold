import streamlit as st
from stmol import showmol
import py3Dmol
import requests
import biotite.structure.io as bsio

st.sidebar.title('🧪 ESMFold')
st.sidebar.write("[*ESMFold*](https://esmatlas.com/about) est un prédicteur de la structure d'une séquence unique de protéines basé sur le modèle de langage ESM-2. Pour plus d'informations, lisez l'[article de recherche](https://www.biorxiv.org/content/10.1101/2022.07.20.500902v2) et l'[article d'actualité](https://www.nature.com/articles/d41586-022-03539-1).")

# stmol
def render_mol(pdb):
    pdbview = py3Dmol.view()
    pdbview.addModel(pdb,'pdb')
    pdbview.setStyle({'cartoon':{'color':'spectrum'}})
    pdbview.setBackgroundColor('white')#('0xeeeeee')
    pdbview.zoomTo()
    pdbview.zoom(2, 800)
    pdbview.spin(True)
    showmol(pdbview, height = 500,width=800)

# Entrée de la séquence de la protéine
DEFAULT_SEQ = "MGSSHHHHHHSSGLVPRGSHMRGPNPTAASLEASAGPFTVRSFTVSRPSGYGAGTVYYPTNAGGTVGAIAIVPGYTARQSSIKWWGPRLASHGFVVITIDTNSTLDQPSSRSSQQMAALRQVASLNGTSSSPIYGKVDTARMGVMGWSMGGGGSLISAANNPSLKAAAPQAPWDSSTNFSSVTVPTLIFACENDSIAPVNSSALPIYDSMSRNAKQFLEINGGSHSCANSGNSNQALIGKKGVAWMKRFMDNDTRYSTFACENPNSTRVSDFRTANCSLEDPAANKARKEAELAAATAEQ"
txt = st.sidebar.text_area('Ajouter la séquence', DEFAULT_SEQ, height=500)

# ESMfold
def update(sequence=txt):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    response = requests.post('https://api.esmatlas.com/foldSequence/v1/pdb/', headers=headers, data=sequence)
    name = sequence[:3] + sequence[-3:]
    pdb_string = response.content.decode('utf-8')

    with open('predicted.pdb', 'w') as f:
        f.write(pdb_string)

    struct = bsio.load_structure('predicted.pdb', extra_fields=["b_factor"])
    b_value = round(struct.b_factor.mean(), 4)

    # Afficher la structure de la protéine
    st.subheader('Visualisation de la structure prédite des protéines')
    render_mol(pdb_string)

    # plDDT est stockée dans le champ du facteur B.
    st.subheader('plDDT')
    st.write('plDDT est une estimation par résidu de la confiance dans la prédiction sur une échelle de 0 à 100.')
    st.info(f'plDDT: {b_value}')

    st.download_button(
        label="Download PDB",
        data=pdb_string,
        file_name='predicted.pdb',
        mime='text/plain',
    )

predict = st.sidebar.button('Prédire', on_click=update)

if not predict:
    st.warning('👈 Entrer la séquences de la protéine !')

import pandas as pd
import requests
import streamlit as st

def load_fasta(url):
    response = requests.get(url)
    data = response.text.split('\n')
    data = [x for x in data if x]
    records = []
    header = ''
    sequence = ''
    for line in data:
        if line.startswith('>'):
            if header:
                records.append((header, sequence))
                header = ''
                sequence = ''
            header = line[1:]
        else:
            sequence += line
    records.append((header, sequence))
    df = pd.DataFrame(records, columns=['header', 'sequence'])
    df = df[df['sequence'].str.len() < 100]
    return df

df = load_fasta('https://raw.githubusercontent.com/soedinglab/MMseqs2/master/examples/QUERY.fasta')
df['sequence'].rename('Exemple de séquences de protéines', inplace=True)

st.write('## Exemple de séquences de protéines ⚗️')
st.write(df['sequence'])
st.write("[Atlas des protéines]https://esmatlas.com/explore?at=2.0929007530212402%2C1.1427013874053955%2C0.05168796671072847")
