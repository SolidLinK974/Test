import streamlit as st
import pandas as pd
import openai

# Demander la clé API OpenAI à l'utilisateur
openai_api_key = st.text_input("Clé API OpenAI", type="password")
if not openai_api_key:
    st.info("Veuillez entrer votre clé API OpenAI pour continuer.", icon="🔑")
else:
    # Créer un client OpenAI
    openai.api_key = openai_api_key

    # Titre de l'application
    st.title("📄 Relecture et Questions sur les Comptes Rendus Trimestriels")

    # Charger le fichier CSV
    uploaded_file = st.file_uploader("Téléchargez un fichier CSV contenant les comptes rendus", type=["csv"])

    if uploaded_file is not None:
        # Lire le fichier avec pandas
        try:
            df = pd.read_csv(uploaded_file, sep=',', encoding='utf-8')
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier CSV : {e}")
            df = None

        # Afficher un message de succès
        st.success("Fichier chargé avec succès ! 🎉")

        # Afficher un aperçu des données
        st.write("Aperçu des données :")
        st.dataframe(df)

        # Poser une question sur le contenu du CSV
        st.header("Poser une question sur le fichier CSV chargé")
        csv_question = st.text_area("Posez une question concernant les données du fichier CSV :", disabled=uploaded_file is None)
        if uploaded_file and csv_question:
            try:
                        # Préparer le message pour l'API
                document = df.to_csv(index=False)
                messages = [
                    {
                        "role": "user",
                        "content": f"Voici un document CSV :\n{document}\n\n---\n\n{csv_question}",
                    }
                ]

                # Envoyer le prompt à l'API OpenAI
                stream = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    stream=True,
                )

                # Afficher la réponse en continu
                response_content = ""
                for chunk in stream:
                    if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].message.content is not None:
                        response_content += chunk.choices[0].delta.content
                
                # Afficher la réponse complète une fois que toute la réponse est accumulée
                st.write(response_content)


            except Exception as e:
                st.error(f"Erreur lors de l'appel à l'API : {e}")

        # Analyser les comptes rendus
        if st.button("Analyser les comptes rendus avec l'IA"):
            st.write("Analyse en cours...")

            # Ajouter une colonne pour les suggestions IA
            suggestions = []

            if 'compte_rendu' not in df.columns:
                st.error("La colonne 'compte_rendu' est absente du fichier CSV. Assurez-vous que le fichier est correctement formaté.")
            else:
                for index, row in df.iterrows():
                    compte_rendu = row['compte_rendu']  # Assurez-vous que la colonne s'appelle bien "compte_rendu"
                prompt = f"Réécrit le texte suivant ci-besoin afin d'améliorer l'orthographe, la clarté et la pertinence. Il faudrait aussi que le mot étude soit toujours remplacé par le mot tutorat. Voilà l'exemple d'un bon compte rendu Réécrit le texte suivant ci-besoin afin d'améliorer l'orthographe, la clarté et la pertinence. Il faudrait aussi que le mot étude soit toujours remplacé par le mot tutorat. Voilà l'exemple d'un bon compte rendu : Alexandre s’est rapidement approprié les sessions de tutorat pour en tirer le maximum ; il participe avec entrain aux différents temps de travail (rituels de mise au travail, tableau des devoirs, etc.). Durant ce trimestre, nous avons particulièrement insisté sur les mathématiques et plus spécifiquement sur les chapitres de géométrie pour lesquels il rencontre davantage de difficultés. Nous avons également utilement réalisé un certain nombre de dictées, exercice pour lequel nous sommes en train de surmonter ses réticences ! Globalement, le tutorat a l’air de profiter à Alexandre, nous l’encourageons à maintenir cet état d’esprit positif !. Encore un autre exemple :Césaréa a rejoint le tutorat en cours de trimestre. Depuis le début de l’année, nous avons relevé des problèmes d’organisation sur lesquels nous allons essayer de la faire progresser cette année : oubli de matériel fréquent, devoirs notés imparfaitement, etc. Si Césaréa est parfois agitée en début d’étude, elle arrive dans la plupart des cas à se recentrer sur ses devoirs et sollicite  le tuteur dès qu’elle en ressent le besoin. C’est une bonne chose ! Nous allons également continuer d’accorder une attention particulière aux mathématiques pour lesquelles elle rencontre davantage de difficultés. N'hésites pas à faire des paragraphes si tu sens que c'est nécessaire. On peut également vérifier que le prénom est le bon et qu'il n'y a pas de copié collé entre chaque ligne de différents comptes rendus :\n\n{compte_rendu}"

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

            # Ajouter les suggestions au dataframe
            while len(suggestions) < len(df):
                suggestions.append("Pas de suggestion disponible")
            if len(suggestions) < len(df):
                suggestions += ["Pas de suggestion disponible"] * (len(df) - len(suggestions))
            df['Suggestions'] = suggestions

            # Afficher les résultats avec les suggestions
            st.write("Comptes rendus avec suggestions :")
            st.dataframe(df)

            # Ajouter une option pour télécharger le fichier mis à jour
            csv = df.to_csv(index=False)
            st.download_button(label="Télécharger les suggestions", data=csv, file_name='comptes_rendus_avec_suggestions.csv', mime='text/csv')

