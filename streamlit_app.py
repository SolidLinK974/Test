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
                    
                    #Créer le prompt pour l'IA
                    prompt = f"Le mot étude doit être remplacé par tutorat et le mot Parkours est bien écrit de cette manière car c'est le nom de notre marque (ni Parkour's, ni parcours, etc).\n Un bon compte rendu doit être clair, structuré et rédigé dans un registre soutenu. Voici les principales caractéristiques à prendre en compte pour la rédaction :\n Langue : Le compte rendu doit être rédigé à la deuxième personne du singulier. Utiliser un langage respectueux et soutenu, en évitant les termes familiers ou vagues. Il est important d'être précis tout en restant motivant.\n Style : Chaque compte rendu doit commencer par une observation positive concernant les efforts ou les qualités de l'élève. Il est nécessaire d'identifier les progrès faits au cours de la période concernée, tout en soulignant les points sur lesquels l'élève peut encore s'améliorer. Ces points d'amélioration doivent être formulés de manière constructive, en proposant des pistes pour progresser.\n Syntaxe : Les phrases doivent être bien structurées, débutant par une majuscule et se terminant par une ponctuation adéquate. Le style doit être fluide, avec des transitions claires entre les différentes idées, afin de maintenir la cohérence du compte rendu.\n Motivation : Terminer par une phrase motivante pour encourager l'élève à poursuivre ses efforts et à maintenir la régularité dans son engagement au tutorat.\n Spécificité : Chaque commentaire doit être spécifique, mentionnant des aspects concrets du travail ou du comportement de l'élève, par exemple : 'Tu as fait preuve d'une bonne attitude face aux difficultés en posant régulièrement des questions pertinentes.' Plutôt que des termes généraux, utiliser des exemples qui montrent clairement les actions positives. \n Exemple Observation positive : 'Tu as su montrer un véritable engagement dans ton travail personnel.' \n Améliorations suggérées : 'Pour continuer à progresser, tu devrais essayer de maintenir une concentration constante et de t’éloigner des distractions.' \n Conclusion motivante : 'Continue sur cette voie, tes efforts porteront leurs fruits.':\n\n{compte_rendu}"

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
