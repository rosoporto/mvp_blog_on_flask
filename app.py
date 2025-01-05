from flask import Flask, render_template, abort
import os
import markdown
from slugify import slugify, Slugify, UniqueSlugify


app = Flask(__name__)
custom_slugify = Slugify(to_lower=True)
custom_slugify.separator = '_'

# Путь к папке с статьями
CONTENTS_DIR = 'contents'

def get_articles():
    """Получаем список статей из папки contents."""
    articles = []
    for filename in os.listdir(CONTENTS_DIR):
        if filename.endswith('.md'):
            name = filename[:-3]  # Убираем расширение .md
            title = get_article_content(filename, header=True)  # Получаем заголовок
            slug = custom_slugify(title)  # Генерируем slug на основе заголовка
            articles.append({'name': name, 'filename': filename, 'title': title, 'slug': slug})
    articles =sorted(articles, key=lambda x: x['filename'])
    return articles

def get_article_content(filename, header=None):
    """Читаем содержимое статьи из файла и извлекаем заголовок, описание и тело."""
    with open(os.path.join(CONTENTS_DIR, filename), 'r', encoding='utf-8') as file:
        content = file.read()
        
        # Разделяем метаданные и тело статьи
        parts = content.split('---')
        metadata = parts[0].strip()
        body = parts[1].strip()
        
        # Извлекаем заголовок
        lines = metadata.split('\n')
        title = lines[0].replace('#', '').strip()  # Убираем символ # и лишние пробелы
        if header:
            return title
        
        # Извлекаем описание и картику
        description, image_url = None, None
        for line in lines[1:]:
            if line.startswith('description:'):
                description = line.replace('description:', '').strip()
            
            if line.startswith('image:'):
                image_url = line.replace('image:', '').strip()
            
        # Если описание не найдено, берем первые несколько слов из тела статьи
        if not description:
            words = body.split()
            description = ' '.join(words[:10])  # Берем первые 10 слов
        
        # Если картинка не найдена, используем заглушку        
        if not image_url:            
            image_url = 'https://via.placeholder.com/150'  # Заглушка            
 
        # Преобразуем Markdown в HTML
        body_html = markdown.markdown(body)
        return title, description, image_url, body_html

@app.route('/')
def index():
    articles = get_articles()
    return render_template('index.html', articles=articles)

@app.route('/article/<slug>')
def article(slug):
    # Ищем статью по slug
    articles = get_articles()
    article_data = next((article for article in articles if article['slug'] == slug), None)
    if not article_data:
        abort(404)  # Если статья не найдена, возвращаем 404
    title, description, image_url, content = get_article_content(article_data['filename'])
    return render_template('article.html', title=title, description=description, image_url=image_url, content=content)

if __name__ == '__main__':
    app.run(debug=True)