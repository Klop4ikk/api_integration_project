# client_advanced.py - Улучшенный клиент с графиками
import requests
import json
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

BASE_URL = "http://127.0.0.1:5000/api"

class BookAPIClient:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def get_all_books(self):
        """Получить все книги"""
        response = requests.get(f"{self.base_url}/books")
        return response.json()
    
    def add_book(self, title, author, year=None):
        """Добавить новую книгу"""
        data = {"title": title, "author": author}
        if year:
            data["year"] = year
        
        response = requests.post(f"{self.base_url}/books", json=data)
        return response.json()
    
    def get_statistics(self):
        """Получить статистику"""
        books = self.get_all_books()["books"]
        
        if not books:
            return {"total": 0, "message": "Нет книг в библиотеке"}
        
        # Создаем DataFrame для анализа
        df = pd.DataFrame(books)
        
        stats = {
            "total_books": len(books),
            "authors_count": df['author'].nunique() if 'author' in df.columns else 0,
            "oldest_year": int(df['year'].min()) if 'year' in df.columns and pd.notna(df['year'].min()) else None,
            "newest_year": int(df['year'].max()) if 'year' in df.columns and pd.notna(df['year'].max()) else None,
            "books_per_author": {}
        }
        
        # Книги по авторам
        if 'author' in df.columns:
            author_counts = df['author'].value_counts()
            stats["books_per_author"] = author_counts.to_dict()
        
        return stats
    
    def display_books_table(self):
        """Вывести таблицу с книгами"""
        result = self.get_all_books()
        books = result.get("books", [])
        
        print("\n" + "="*60)
        print(f"{'БИБЛИОТЕКА КНИГ':^60}")
        print("="*60)
        print(f"{'ID':<5} {'НАЗВАНИЕ':<30} {'АВТОР':<20} {'ГОД':<6}")
        print("-"*60)
        
        for book in books:
            book_id = book.get('id', '')
            title = book.get('title', '')[:28] + '..' if len(book.get('title', '')) > 28 else book.get('title', '')
            author = book.get('author', '')[:18] + '..' if len(book.get('author', '')) > 18 else book.get('author', '')
            year = book.get('year', '')
            
            print(f"{book_id:<5} {title:<30} {author:<20} {year:<6}")
        
        print("="*60)
        print(f"Всего книг: {result.get('count', 0)}")
    
    def create_chart(self):
        """Создать график распределения книг по годам"""
        books = self.get_all_books()["books"]
        
        if not books:
            print("Нет данных для графика")
            return
        
        df = pd.DataFrame(books)
        
        if 'year' in df.columns and df['year'].notna().any():
            plt.figure(figsize=(10, 6))
            
            # Гистограмма по годам
            years = df['year'].dropna().astype(int)
            plt.hist(years, bins=20, edgecolor='black', alpha=0.7)
            plt.title('Распределение книг по годам издания')
            plt.xlabel('Год издания')
            plt.ylabel('Количество книг')
            plt.grid(True, alpha=0.3)
            
            plt.savefig('books_chart.png')
            print("График сохранен как 'books_chart.png'")
        else:
            print("Нет данных о годах издания для создания графика")

def main():
    client = BookAPIClient(BASE_URL)
    
    print("📚 ПРОДВИНУТЫЙ КЛИЕНТ ДЛЯ API КНИГ")
    print("="*50)
    
    while True:
        print("\nМЕНЮ:")
        print("1. Показать все книги")
        print("2. Добавить книгу")
        print("3. Получить статистику")
        print("4. Создать график")
        print("5. Проверить статус API")
        print("6. Выйти")
        
        choice = input("\nВыберите действие (1-6): ")
        
        if choice == '1':
            client.display_books_table()
        
        elif choice == '2':
            print("\nДобавление новой книги:")
            title = input("Название: ")
            author = input("Автор: ")
            year = input("Год издания (опционально): ")
            
            if year and year.isdigit():
                result = client.add_book(title, author, int(year))
            else:
                result = client.add_book(title, author)
            
            print("\nРезультат:", json.dumps(result, ensure_ascii=False, indent=2))
        
        elif choice == '3':
            stats = client.get_statistics()
            print("\nСТАТИСТИКА БИБЛИОТЕКИ:")
            print(json.dumps(stats, ensure_ascii=False, indent=2))
        
        elif choice == '4':
            print("Создание графика...")
            client.create_chart()
        
        elif choice == '5':
            try:
                response = requests.get(f"{BASE_URL}/status")
                print("\nСтатус API:")
                print(json.dumps(response.json(), ensure_ascii=False, indent=2))
            except:
                print("❌ API недоступен")
        
        elif choice == '6':
            print("Выход...")
            break
        
        else:
            print("Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main()