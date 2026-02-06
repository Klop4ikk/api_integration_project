# server.py - ВЕРСИЯ С CORS
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  # <-- Добавьте этот импорт
import json
import os

app = Flask(__name__)
CORS(app) 

# Файл для хранения данных (вместо памяти)
DATA_FILE = 'books_data.json'

def load_books():
    """Загружает книги из файла"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return [
        {"id": 1, "title": "Война и мир", "author": "Лев Толстой", "year": 1869},
        {"id": 2, "title": "Мастер и Маргарита", "author": "Михаил Булгаков", "year": 1967},
        {"id": 3, "title": "Преступление и наказание", "author": "Федор Достоевский", "year": 1866}
    ]

def save_books(books):
    """Сохраняет книги в файл"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(books, f, ensure_ascii=False, indent=2)

# Загружаем начальные данные
books = load_books()

# Главная страница с красивым интерфейсом
@app.route('/')
def index():
    return render_template('index.html')

# API Endpoints остаются те же, но с улучшениями

@app.route('/api/books', methods=['GET'])
def get_books():
    """Возвращает весь список книг с возможностью фильтрации"""
    # Поддержка параметров запроса
    author = request.args.get('author')
    search = request.args.get('search')
    
    filtered_books = books
    
    if author:
        filtered_books = [b for b in filtered_books if author.lower() in b.get('author', '').lower()]
    
    if search:
        filtered_books = [b for b in filtered_books if 
                         search.lower() in b.get('title', '').lower() or 
                         search.lower() in b.get('author', '').lower()]
    
    return jsonify({
        "count": len(filtered_books),
        "books": filtered_books
    })

@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """Возвращает одну книгу по её ID"""
    for book in books:
        if book['id'] == book_id:
            return jsonify(book)
    return jsonify({
        "error": "Книга не найдена",
        "message": f"Книга с ID {book_id} не существует"
    }), 404

@app.route('/api/books', methods=['POST'])
def add_book():
    """Добавляет новую книгу"""
    if not request.is_json:
        return jsonify({"error": "Требуется JSON данные"}), 400
    
    data = request.get_json()
    
    # Валидация данных
    required_fields = ['title', 'author']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return jsonify({
            "error": "Не все обязательные поля указаны",
            "missing": missing_fields
        }), 400
    
    # Проверяем, не существует ли уже такая книга
    existing_book = next((b for b in books if 
                         b['title'].lower() == data['title'].lower() and 
                         b['author'].lower() == data['author'].lower()), None)
    
    if existing_book:
        return jsonify({
            "error": "Книга уже существует",
            "existing_book": existing_book
        }), 409
    
    # Создаем новую книгу
    new_id = max([book['id'] for book in books]) + 1 if books else 1
    new_book = {
        "id": new_id,
        "title": data['title'],
        "author": data['author'],
        "year": data.get('year'),
        "created_at": "2024-01-01"  # Можно добавить datetime.now()
    }
    
    books.append(new_book)
    save_books(books)  # Сохраняем в файл
    
    return jsonify({
        "message": "Книга успешно добавлена",
        "book": new_book
    }), 201

@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """Обновляет информацию о книге"""
    if not request.is_json:
        return jsonify({"error": "Требуется JSON данные"}), 400
    
    data = request.get_json()
    
    for i, book in enumerate(books):
        if book['id'] == book_id:
            # Обновляем только переданные поля
            for key, value in data.items():
                if key != 'id':  # ID не меняем
                    books[i][key] = value
            
            save_books(books)  # Сохраняем изменения
            return jsonify({
                "message": "Книга обновлена",
                "book": books[i]
            })
    
    return jsonify({"error": "Книга не найдена"}), 404

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """Удаляет книгу"""
    for i, book in enumerate(books):
        if book['id'] == book_id:
            deleted_book = books.pop(i)
            save_books(books)  # Сохраняем изменения
            return jsonify({
                "message": "Книга удалена",
                "deleted_book": deleted_book
            })
    
    return jsonify({"error": "Книга не найдена"}), 404

@app.route('/api/status', methods=['GET'])
def api_status():
    """Возвращает статус API"""
    return jsonify({
        "status": "online",
        "version": "1.0.0",
        "total_books": len(books),
        "endpoints": {
            "GET /api/books": "Получить все книги",
            "GET /api/books/{id}": "Получить книгу по ID",
            "POST /api/books": "Добавить книгу",
            "PUT /api/books/{id}": "Обновить книгу",
            "DELETE /api/books/{id}": "Удалить книгу",
            "GET /api/status": "Статус API"
        }
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Ресурс не найден",
        "available_endpoints": [
            "/api/books",
            "/api/books/{id}",
            "/api/status"
        ]
    }), 404

if __name__ == '__main__':
    # Создаем папку templates если ее нет
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    app.run(host='0.0.0.0', port=5000, debug=True)