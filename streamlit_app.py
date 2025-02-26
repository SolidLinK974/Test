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
        <li><b>Interroger</b> le contenu du CSV pour poser des questions spécifiques.</li>
    </ul>
    <br>

    <p style='font-size: 22px; color: #06668c;'>Comment utiliser l'application :</p>
    <ol style='font-size: 18px;'>
        <li>Téléchargez votre fichier au format CSV.</li>
        <li>Vérifier avec l'aperçu que c'est le bon fichier.</li>
        <li>Visualisez les résultats et téléchargez le fichier mis à jour.</li>
    </ol>
    <br>

    <p style='font-size: 16px; color: red;'><b>Note :</b> Votre fichier CSV doit contenir une colonne nommée <code>compte_rendu</code> pour que l'analyse fonctionne correctement.</p>
""", unsafe_allow_html=True)

# Demander la clé API OpenAI à l'utilisateur
openai_api_key = "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"
openai.api_key = openai_api_key

# Définir directement la clé API OpenAI
#openai.api_key = "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"  # Remplacez par votre clé API

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
        #            model="gpt-3.5-turbo",
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
                        # Préparer le message pour l'API
                        messages = [
                        {"role": "user", "content": prompt}
                        ]

                        # Envoyer le prompt à l'API OpenAI
                        response = openai.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=messages
                        )

                        # Extraire la réponse du contenu
                        response_content = response.choices[0].message.content.strip()

                        # Ajouter la suggestion à la liste des suggestions
                        suggestions.append(response_content)

                    except Exception as e:
                        st.error(f"Erreur lors de l'appel à l'API pour l'entrée {index + 1} : {e}")
                        suggestions.append("Erreur lors de l'analyse")


            # Vérifier si le nombre de suggestions correspond au nombre de lignes dans le dataframe
            if len(suggestions) != len(df):
                st.error(f"Nombre de suggestions ({len(suggestions)}) ne correspond pas au nombre de lignes ({len(df)}) dans le fichier.")
            else:
                df['Suggestions'] = suggestions

            # Afficher les résultats avec les suggestions
            st.write("Comptes rendus avec suggestions :")
            st.dataframe(df)

            # Ajouter une option pour télécharger le fichier mis à jour
            csv = df.to_csv(index=False)
            st.download_button(label="Télécharger les suggestions", data=csv, file_name='comptes_rendus_avec_suggestions.csv', mime='text/csv')
