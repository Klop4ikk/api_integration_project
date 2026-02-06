# client.py
import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

def print_response(response):
    """Красиво печатает ответ от сервера"""
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    print("-" * 50)

def main():
    print("=== Тестирование API книг ===\n")
    
    # 1. Получаем все книги
    print("1. GET /api/books")
    response = requests.get(f"{BASE_URL}/books")
    print_response(response)
    
    # 2. Получаем книгу с ID=1
    print("2. GET /api/books/1")
    response = requests.get(f"{BASE_URL}/books/1")
    print_response(response)
    
    # 3. Пытаемся получить несуществующую книгу
    print("3. GET /api/books/999 (несуществующая)")
    response = requests.get(f"{BASE_URL}/books/999")
    print_response(response)
    
    # 4. Добавляем новую книгу
    print("4. POST /api/books")
    new_book = {"title": "Преступление и наказание", "author": "Федор Достоевский"}
    response = requests.post(f"{BASE_URL}/books", json=new_book)
    print_response(response)
    
    # 5. Снова получаем все книги
    print("5. GET /api/books (обновленный список)")
    response = requests.get(f"{BASE_URL}/books")
    print_response(response)
    
    # 6. Плохой запрос
    print("6. POST /api/books (плохой запрос)")
    bad_data = {"wrong": "data"}
    response = requests.post(f"{BASE_URL}/books", json=bad_data)
    print_response(response)

if __name__ == "__main__":
    main()