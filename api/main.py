from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Stocker temporairement les résultats de recherche de chaque utilisateur
user_search_results = {}

# Route pour rechercher des clips YouTube d'un artiste avec pagination
@app.route('/recherche', methods=['GET'])
def recherche_videos():
    titre = request.args.get('titre')
    page_token = request.args.get('pageToken', '')  # pour la pagination

    # URL de l'API YouTube
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'part': 'snippet',
        'q': titre,
        'type': 'video',
        'maxResults': 10,
        'key': YOUTUBE_API_KEY,
        'pageToken': page_token
    }

    # Appel API
    response = requests.get(url, params=params)
    data = response.json()

    # Gestion des erreurs
    if response.status_code != 200:
        return jsonify({"error": "Erreur lors de l'appel de l'API YouTube"}), 500

    # Extraction des vidéos
    videos = []
    for item in data.get('items', []):
        video_id = item['id']['videoId']
        videos.append({
            'title': item['snippet']['title'],
            'videoId': video_id,
            'url': f"https://www.youtube.com/watch?v={video_id}"
        })

    # Stocker les résultats pour cet utilisateur (identifié par l'adresse IP)
    user_ip = request.remote_addr
    user_search_results[user_ip] = videos

    # Ajout des informations pour la pagination
    result = {
        'videos': videos,
        'nextPageToken': data.get('nextPageToken'),
        'prevPageToken': data.get('prevPageToken')
    }
    
    return jsonify(result)

# Nouvelle route pour récupérer l'URL d'une vidéo sélectionnée par son numéro
@app.route('/videos', methods=['GET'])
def video_by_index():
    video_index = request.args.get('watch')
    
    # Vérifier que le paramètre 'watch' est bien un nombre
    if not video_index.isdigit():
        return jsonify({"error": "Veuillez entrer un numéro valide pour sélectionner une vidéo"}), 400
    
    video_index = int(video_index) - 1  # Convertir en index (1 pour la première vidéo)
    user_ip = request.remote_addr

    # Vérifier si l'utilisateur a des résultats stockés
    if user_ip not in user_search_results or video_index >= len(user_search_results[user_ip]):
        return jsonify({"error": "Aucun résultat de recherche trouvé pour cet utilisateur ou index invalide"}), 404

    # Renvoyer l'URL de la vidéo sélectionnée
    selected_video = user_search_results[user_ip][video_index]
    return jsonify({"url": selected_video['url'], "title": selected_video['title']})

# Exécuter l'application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
  
