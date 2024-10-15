import requests

def get_video_categories(api_key, country_code):
    url = (
        f"https://www.googleapis.com/youtube/v3/videoCategories"
        f"?part=snippet&regionCode={country_code}&key={api_key}"
    )
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return {}

    categories = {}
    data = response.json()
    for item in data.get('items', []):
        category_id = item['id']
        category_name = item['snippet']['title']
        categories[category_id] = category_name

    return categories

# Example usage
api_key = 'AIzaSyAaHjUZfRMNZqErxOwyADOOGJ2WvOTC7FE'
country_code = 'JP'
categories = get_video_categories(api_key, country_code)
print(categories)