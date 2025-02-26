import streamlit as st
import pandas as pd
import openai

# Configuration de la page
st.set_page_config(
    page_title="Analyse des Comptes Rendus - Parkours",
    page_icon="🚀",
    layout="wide"
)

# Utiliser un lien direct vers l'image hébergée sur Google Drive
# Pour obtenir le lien direct, remplacez YOUR_FILE_ID par l'ID de votre fichier dans Google Drive
logo_url = "https://drive.google.com/uc?export=view&id=1rClnpVF-pxDnUlnr80tChKX8BBBt4vJ5"
st.image(logo_url, width=120)

# Bloc de texte explicatif (mode "tuto")
st.markdown("""
# Bienvenue sur l'application d'analyse des comptes rendus Parkours

Cette application vous permet de :
- **Charger** un fichier CSV contenant vos comptes rendus trimestriels.
- **Analyser** automatiquement les comptes rendus grâce à l'intelligence artificielle pour obtenir des suggestions d'amélioration.
- **Interroger** le contenu du CSV pour poser des questions spécifiques.

**Comment utiliser l'application :**
1. Téléchargez votre fichier CSV.
2. Posez une question sur le contenu du CSV ou cliquez sur *Analyser les comptes rendus avec l'IA* pour obtenir des suggestions personnalisées.
3. Visualisez les résultats et téléchargez le fichier mis à jour.

**Note :** Votre fichier CSV doit contenir une colonne nommée `compte_rendu` pour que l'analyse fonctionne correctement.
""", unsafe_allow_html=True)

# Définir directement la clé API OpenAI
openai.api_key = "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"  # Remplacez par votre clé API

# Charger le fichier CSV
uploaded_file = st.file_uploader("Téléchargez un fichier CSV contenant les comptes rendus", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, sep=',', encoding='utf-8')
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier CSV : {e}")
        df = None

    if df is not None:
        st.success("Fichier chargé avec succès ! 🎉")
        st.write("### Aperçu des données :")
        st.dataframe(df)

        # Section pour poser une question sur le contenu du CSV
        st.header("Poser une question sur le fichier CSV chargé")
        csv_question = st.text_area("Posez une question concernant les données du fichier CSV :", disabled=uploaded_file is None)
        if csv_question:
            try:
                document = df.to_csv(index=False)
                messages = [
                    {
                        "role": "user",
                        "content": f"Voici un document CSV :\n{document}\n\n---\n\n{csv_question}",
                    }
                ]

                stream = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    stream=True,
                )

                response_content = ""
                for chunk in stream:
                    if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
                        response_content += chunk.choices[0].delta.content
                st.write(response_content)

            except Exception as e:
                st.error(f"Erreur lors de l'appel à l'API : {e}")

        # Bouton pour analyser les comptes rendus avec l'IA
        if st.button("Analyser les comptes rendus avec l'IA"):
            st.write("Analyse en cours...")

            suggestions = []

            if 'compte_rendu' not in df.columns:
                st.error("La colonne 'compte_rendu' est absente du fichier CSV. Assurez-vous que le fichier est correctement formaté.")
            else:
                for index, row in df.iterrows():
                    compte_rendu = row['compte_rendu']

                    prompt = f"""
Le mot "étude" doit être remplacé par "tutorat" et le mot "Parkours" est bien écrit de cette manière car c'est le nom de notre marque (ni Parkour's, ni parcours, etc.).

Un bon compte rendu doit être clair, structuré et rédigé dans un registre soutenu. Voici les principales caractéristiques à prendre en compte pour la rédaction :

1. **Langue** : Le compte rendu doit être rédigé à la deuxième personne du singulier. Utilise un langage respectueux et soutenu, en évitant les termes familiers ou vagues. Il est important d'être précis tout en restant motivant.

2. **Style** : Chaque compte rendu doit commencer par une observation positive concernant les efforts ou les qualités de l'élève. Il est nécessaire d'identifier les progrès faits au cours de la période concernée, tout en soulignant les points sur lesquels l'élève peut encore s'améliorer. Ces points d'amélioration doivent être formulés de manière constructive, en proposant des pistes pour progresser.

3. **Syntaxe** : Les phrases doivent être bien structurées, débutant par une majuscule et se terminant par une ponctuation adéquate. Le style doit être fluide, avec des transitions claires entre les différentes idées, afin de maintenir la cohérence du compte rendu.

4. **Motivation** : Termine par une phrase motivante pour encourager l'élève à poursuivre ses efforts et à maintenir la régularité dans son engagement au tutorat.

5. **Spécificité** : Chaque commentaire doit être spécifique, mentionnant des aspects concrets du travail ou du comportement de l'élève, par exemple : "Tu as fait preuve d'une bonne attitude face aux difficultés en posant régulièrement des questions pertinentes." Il est préférable d'utiliser des exemples concrets plutôt que des termes généraux.

{compte_rendu}
"""

                    try:
                        messages = [{"role": "user", "content": prompt}]
                        response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=messages
                        )
                        response_content = response.choices[0].message.content.strip()
                        suggestions.append(response_content)
                    except Exception as e:
                        st.error(f"Erreur lors de l'appel à l'API pour l'entrée {index + 1} : {e}")
                        suggestions.append("Erreur lors de l'analyse")

                if len(suggestions) != len(df):
                    st.error(f"Nombre de suggestions ({len(suggestions)}) ne correspond pas au nombre de lignes ({len(df)}) dans le fichier.")
                else:
                    df['Suggestions'] = suggestions

                st.write("### Comptes rendus avec suggestions :")
                st.dataframe(df)

                csv_data = df.to_csv(index=False)
                st.download_button(label="Télécharger les suggestions", data=csv_data, file_name='comptes_rendus_avec_suggestions.csv', mime='text/csv')
