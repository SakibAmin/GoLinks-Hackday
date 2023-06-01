import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/repositories')
def repository_stats():

    #Inputs 
    username = request.args.get('username')
    if not username:
        return jsonify({'error':'No Username Was Given'}), 400 #Error if no Username is Entered 
    forked = request.args.get('forked', default = 'true') == 'true'


    #Github API Request
    response = requests.get(f'https://api.github.com/users/{username}/repos')
    if response.status_code == 200: #If Code is 200 request is good
        repositories = response.json()
    elif response.status_code == 404: #If User doesnt Exist
        return jsonify({'error': 'User doesnt Exist'}), 404
    else: #Any other Error
        return jsonify({'error': 'Something Went Wrong'}), 500

    #If forked is set to false 
    if not forked:
        repositories = [repo for repo in repositories if not repo['fork']]
    
    #Total Count
    total_count = len(repositories)

    #Total Stargazers
    total_stargazers = sum(repo['stargazers_count'] for repo in repositories)

    #Total Forks
    total_forks = sum(repo['forks_count'] for repo in repositories)
    #Average Size of Repo
    total_size_bytes  = sum(repo['size'] for repo in repositories) / total_count
    if total_size_bytes < 1024:
        average_size = f'{total_size_bytes} B'
    elif total_size_bytes < 1024**2:
        average_size = f'{total_size_bytes/ 1024} KB'
    elif total_size_bytes < 1024**3:
        average_size = f"{total_size_bytes / (1024**2)} MB"
    else:
        average_size = f"{total_size_bytes / (1024**3)} GB"

    #List of Langauges 
    languages = {}
    for repo in repositories:
        language = repo['language']
        if language:
            languages[language] = languages.get(language, 0) + 1
    sorted_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)

    #Statistics 
    response_data = {
        'total_count': total_count,
        'total_stargazers': total_stargazers,
        'total_forks': total_forks,
        'average_size': average_size,
        'languages': sorted_languages
    }

    return jsonify(response_data)


if __name__ == '__main__':
    app.run()

#Test
#curl -X GET "http://localhost:5000/repositories?username=seantomburke"
#curl -X GET "http://localhost:5000/repositories?username=seantomburke&forked=false"

#Error Testing
#curl -X GET "http://localhost:5000/repositories"
#curl -X GET "http://localhost:5000/repositories?username=fsdihuwf9a"
