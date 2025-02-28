import streamlit as st
import pandas as pd
import openai


    # Configuration de la page
st.set_page_config(
    page_title="Analyse des Comptes Rendus - Parkours",
    page_icon="🚀",
    layout="wide"
)

# Utiliser un lien direct vers l'image hébergée
logo_url= "https://image.noelshack.com/fichiers/2025/09/3/1740586406-logo-parkours.png"
st.markdown(
    f"""
    <div style="display: flex; justify-content: center;">
        <img src="{logo_url}" width="120">
    </div>
    """,
    unsafe_allow_html=True
)

# Bloc de texte explicatif (mode "tuto")
st.markdown("""
    <h1 style='text-align: center; font-size: 60px; color: #06668c;'>RelectIA</h1>
    <h2 style='text-align: center; font-size: 30px; color: #333;'>L'application qui t'aide à relire les comptes rendus trimestriels</h2>
    <br>

    <p style='font-size: 18px; text-align: justify;'>
    Cette application vous permet de :
    </p>

    <ul style='font-size: 18px;'>
        <li><b>Charger</b> un fichier CSV contenant vos comptes rendus trimestriels.</li>
        <li><b>Analyser</b> automatiquement les comptes rendus grâce à l'intelligence artificielle pour obtenir des suggestions d'amélioration.</li>
    </ul>
    <br>

    <p style='font-size: 22px; color: #06668c;'>Comment utiliser l'application :</p>
    <ol style='font-size: 18px;'>
        <li>Téléchargez votre fichier au format CSV.</li>
        <li>Vérifiez avec l'aperçu que c'est le bon fichier.</li>
        <li>Visualisez les résultats et téléchargez le fichier mis à jour.</li>
        <li>Demandez à Raph la clé de l'API.</li>
    </ol>
    <br>

    <p style='font-size: 16px; color: red;'><b>Note :</b> Votre fichier CSV doit contenir une colonne nommée <code>compte_rendu</code> pour que l'analyse fonctionne correctement.</p>
""", unsafe_allow_html=True)

# Demander la clé API OpenAI à l'utilisateur
# openai_api_key = "la clé la clé" (jamais faire ça ok ?)
# openai.api_key = openai_api_key

# Demander la clé API OpenAI à l'utilisateur
openai_api_key = st.text_input("Clé API OpenAI", type="password")
if not openai_api_key:
    st.info("Veuillez entrer votre clé API OpenAI pour continuer.", icon="🔑")
else:
    # Créer un client OpenAI
    openai.api_key = openai_api_key

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
        #st.header("Poser une question sur le fichier CSV chargé")
        #csv_question = st.text_area("Posez une question concernant les données du fichier CSV :", disabled=uploaded_file is None)
        #if csv_question:
        #    try:
        #        document = df.to_csv(index=False)
        #        messages = [
        #            {
        #                "role": "user",
        #                "content": f"Voici un document CSV :\n{document}\n\n---\n\n{csv_question}",
        #            }
        #        ]

        #        stream = openai.ChatCompletion.create(
        #            model="gpt-4-turbo",
        #            messages=messages,
        #            stream=True,
        #        )

        #        response_content = ""
        #        for chunk in stream:
        #            if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
        #                response_content += chunk.choices[0].delta.content
        #        st.write(response_content)

        #    except Exception as e:
        #        st.error(f"Erreur lors de l'appel à l'API : {e}")

        # Bouton pour analyser les comptes rendus avec l'IA
        if st.button("Analyser les comptes rendus avec l'IA"):
            st.write("Analyse en cours...")

            suggestions = []
            corrections = []

            if 'compte_rendu' not in df.columns:
                st.error("La colonne 'compte_rendu' est absente du fichier CSV. Assurez-vous que le fichier est correctement formaté.")
            else:
                for index, row in df.iterrows():
                    compte_rendu = row['compte_rendu']

                     # 1. Génération de la suggestion
                    prompt_suggestion = f"""
                    
Critères de suggestion pour l'évaluation des compte-rendus :

Corrections de Fautes :
Orthographe/Conjugaison : Identifier et corriger les fautes d'orthographe et de conjugaison spécifiques.
Phrases mal Formulées : Corriger les phrases grammaticalement incorrectes ou mal formulées pour améliorer la clarté (ex. "ce qui lui pose de plus de difficultés" devrait être "ce qui lui pose le plus de difficultés").

Langage Approprié :
Inapproprié ou Grossier : Remplacer tout langage inapproprié ou grossier par des termes plus respectueux (ex. remplacer "idiot" par "distrait").

Contenu des Compte-Rendus :
Progression Académique : Mentionner uniquement la progression académique lorsque les améliorations des notes ou de la moyenne sont explicitement évoquées.
Longueur du Texte : Signaler si le texte est en-dessous de 80 mots ou au-dessus de 140 mots.
Termes Académiques Spécifiques : Identifier l'utilisation des termes "étude", "études", "semestre" et dire s’ils sont utilisés dans le compte rendu.
Chaque suggestion sera formulée de manière claire et concise, en évitant les répétitions inutiles, et en fournissant des explications lorsque des termes académiques spécifiques sont utilisés de manière inappropriée. Les retours seront uniformisés et organisés de manière à faciliter la lecture et la compréhension.

{compte_rendu}
"""

                    try:
                        # Préparer le message pour l'API
                        messages = [
                        {"role": "user", "content": prompt_suggestion}
                        ]

                        # Envoyer le prompt à l'API OpenAI
                        response = openai.chat.completions.create(
                        model="gpt-4-turbo",
                        messages=messages
                        )

                        # Extraire la réponse du contenu
                        suggestion = response.choices[0].message.content.strip()

                        # Ajouter la suggestion à la liste des suggestions
                        suggestions.append(suggestion)

                    except Exception as e:
                        st.error(f"Erreur lors de l'appel à l'API pour l'entrée {index + 1} : {e}")
                        suggestions.append("Erreur lors de l'analyse")

                        # 2. Génération de la correction complète en se basant sur la suggestion
                    prompt_correction = f"""
Proposez une réécriture/une amélioration, du compte rendu en respectant les critères de la suggestion.

Suggestion :
{suggestion}

Compte rendu original :
{compte_rendu}
"""

                    try:
                        # Préparer le message pour l'API
                        messages_corr = [
                        {"role": "user", "content": prompt_correction}
                        ]

                        # Envoyer le prompt à l'API OpenAI
                        response_corr = openai.chat.completions.create(
                        model="gpt-4-turbo",
                        messages=messages_corr
                        )

                        # Extraire la réponse du contenu
                        correction = response_corr.choices[0].message.content.strip()

                        # Ajouter la suggestion à la liste des suggestions
                        corrections.append(correction)

                    except Exception as e:
                        st.error(f"Erreur lors de l'appel à l'API pour l'entrée {index + 1} : {e}")
                        corrections.append("Erreur lors de l'analyse")


            # Vérifier si le nombre de suggestions correspond au nombre de lignes dans le dataframe
            if len(suggestions) != len(df) or len(corrections) != len(df):
                st.error(f"Nombre de suggestions ({len(suggestions)}) ou nombre de corrections ({len(corrections)}) ne correspond pas au nombre de lignes ({len(df)}) dans le fichier.")
            else:
                df['Suggestions'] = suggestions
                df['Corrections'] = corrections

            # Afficher le dataframe avec les deux colonnes
            st.write("Comptes rendus avec suggestions et corrections :")
            st.dataframe(df)

            # Option de téléchargement du fichier mis à jour
            csv = df.to_csv(index=False)
            st.download_button(label="Télécharger les suggestions et corrections", data=csv, file_name='comptes_rendus_avec_suggestions_et_corrections.csv', mime='text/csv')
