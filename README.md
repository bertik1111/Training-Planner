import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog

class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner - План тренировок")
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        
        # Данные тренировок
        self.trainings = []
        self.data_file = "trainings.json"
        
        # Загрузка данных при запуске
        self.load_data()
        
        # Создание интерфейса
        self.create_menu()
        self.create_widgets()
        
        # Обновление таблицы
        self.refresh_table()
    
    def create_menu(self):
        """Создание меню приложения"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Сохранить в JSON", command=self.save_data)
        file_menu.add_command(label="Загрузить из JSON", command=self.load_data_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Меню Помощь
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)
    
    def create_widgets(self):
        # Основной контейнер
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill="both", expand=True)
        
        # ===== Рамка для ввода данных =====
        input_frame = ttk.LabelFrame(main_container, text="Добавление новой тренировки", padding="10")
        input_frame.pack(fill="x", pady=(0, 10))
        
        # Дата
        ttk.Label(input_frame, text="Дата:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.date_entry = ttk.Entry(input_frame, width=15, font=("Arial", 10))
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Подсказка для даты
        ttk.Label(input_frame, text="(ГГГГ-ММ-ДД)", foreground="gray").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        
        # Тип тренировки
        ttk.Label(input_frame, text="Тип тренировки:", font=("Arial", 10, "bold")).grid(row=0, column=3, padx=5, pady=5, sticky="e")
        self.type_entry = ttk.Combobox(input_frame, values=["Бег", "Плавание", "Велосипед", "Силовая", "Йога", "Футбол", "Теннис"], 
                                        width=15, font=("Arial", 10))
        self.type_entry.grid(row=0, column=4, padx=5, pady=5)
        self.type_entry.set("Выберите тип")
        
        # Длительность
        ttk.Label(input_frame, text="Длительность (мин):", font=("Arial", 10, "bold")).grid(row=0, column=5, padx=5, pady=5, sticky="e")
        self.duration_entry = ttk.Entry(input_frame, width=10, font=("Arial", 10))
        self.duration_entry.grid(row=0, column=6, padx=5, pady=5)
        
        # Кнопка добавления
        self.add_button = ttk.Button(input_frame, text="➕ Добавить тренировку", command=self.add_training)
        self.add_button.grid(row=0, column=7, padx=10, pady=5)
        
        # ===== Рамка для фильтрации =====
        filter_frame = ttk.LabelFrame(main_container, text="Фильтрация тренировок", padding="10")
        filter_frame.pack(fill="x", pady=(0, 10))
        
        # Фильтр по типу
        ttk.Label(filter_frame, text="Тип тренировки:", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.filter_type = ttk.Combobox(filter_frame, values=["Все", "Бег", "Плавание", "Велосипед", "Силовая", "Йога", "Футбол", "Теннис"], 
                                         width=15, font=("Arial", 10))
        self.filter_type.grid(row=0, column=1, padx=5, pady=5)
        self.filter_type.set("Все")
        
        # Фильтр по дате
        ttk.Label(filter_frame, text="Дата:", font=("Arial", 10)).grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.filter_date = ttk.Entry(filter_frame, width=15, font=("Arial", 10))
        self.filter_date.grid(row=0, column=3, padx=5, pady=5)
        ttk.Label(filter_frame, text="(ГГГГ-ММ-ДД)", foreground="gray").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        
        # Кнопки фильтрации
        ttk.Button(filter_frame, text="🔍 Применить фильтры", command=self.refresh_table).grid(row=0, column=5, padx=5, pady=5)
        ttk.Button(filter_frame, text="🔄 Сбросить фильтры", command=self.reset_filters).grid(row=0, column=6, padx=5, pady=5)
        
        # ===== Таблица тренировок =====
        table_frame = ttk.LabelFrame(main_container, text="Список тренировок", padding="10")
        table_frame.pack(fill="both", expand=True)
        
        # Создание таблицы с прокруткой
        columns = ("date", "type", "duration")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Определение заголовков
        self.tree.heading("date", text="📅 Дата")
        self.tree.heading("type", text="🏃 Тип тренировки")
        self.tree.heading("duration", text="⏱ Длительность (мин)")
        
        # Настройка колонок
        self.tree.column("date", width=120, anchor="center")
        self.tree.column("type", width=200, anchor="center")
        self.tree.column("duration", width=150, anchor="center")
        
        # Скроллбары
        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        # Расположение
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # ===== Рамка для кнопок управления =====
        control_frame = ttk.Frame(main_container)
        control_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(control_frame, text="🗑 Удалить выбранную", command=self.delete_training).pack(side="left", padx=5)
        ttk.Button(control_frame, text="💾 Сохранить в JSON", command=self.save_data).pack(side="left", padx=5)
        ttk.Button(control_frame, text="📂 Загрузить из JSON", command=self.load_data_dialog).pack(side="left", padx=5)
        ttk.Button(control_frame, text="📊 Статистика", command=self.show_statistics).pack(side="left", padx=5)
        
        # Статусбар
        self.statusbar = ttk.Label(main_container, text="Готов к работе", relief="sunken", anchor="w")
        self.statusbar.pack(fill="x", pady=(10, 0))
    
    def add_training(self):
        """Добавление новой тренировки с проверкой данных"""
        date = self.date_entry.get().strip()
        training_type = self.type_entry.get().strip()
        duration = self.duration_entry.get().strip()
        
        # Проверка: все ли поля заполнены
        if not date or not training_type or not duration:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля!")
            return
        
        # Проверка даты
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты!\nИспользуйте формат: ГГГГ-ММ-ДД\nНапример: 2024-12-25")
            return
        
        # Проверка типа тренировки
        if training_type == "Выберите тип":
            messagebox.showerror("Ошибка", "Пожалуйста, выберите тип тренировки!")
            return
        
        # Проверка длительности
        try:
            duration_min = float(duration)
            if duration_min <= 0:
                raise ValueError
            if duration_min > 1440:  # Максимум 24 часа
                messagebox.showerror("Ошибка", "Длительность не может превышать 1440 минут (24 часа)!")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Длительность должна быть положительным числом!\nНапример: 30, 45.5, 60")
            return
        
        # Добавление тренировки
        self.trainings.append({
            "date": date,
            "type": training_type,
            "duration": duration_min
        })
        
        # Очистка полей
        self.duration_entry.delete(0, tk.END)
        self.type_entry.set("Выберите тип")
        
        # Обновление таблицы
        self.refresh_table()
        self.save_data()  # Автосохранение
        
        # Обновление статуса
        self.statusbar.config(text=f"✅ Тренировка добавлена: {date}, {training_type}, {duration_min} мин")
    
    def delete_training(self):
        """Удаление выбранной тренировки"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите тренировку для удаления!")
            return
        
        # Подтверждение удаления
        if not messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить выбранную тренировку?"):
            return
        
        # Получение данных выбранной строки
        item = self.tree.item(selected[0])
        values = item['values']
        
        # Поиск и удаление
        for i, training in enumerate(self.trainings):
            if (training['date'] == values[0] and 
                training['type'] == values[1] and 
                training['duration'] == float(values[2])):
                del self.trainings[i]
                break
        
        self.refresh_table()
        self.save_data()
        self.statusbar.config(text=f"🗑 Тренировка удалена: {values[0]}, {values[1]}")
    
    def refresh_table(self):
        """Обновление таблицы с учетом фильтров"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Получение фильтров
        filter_type = self.filter_type.get()
        filter_date = self.filter_date.get().strip()
        
        # Фильтрация данных
        filtered = self.trainings.copy()
        
        # Фильтр по типу
        if filter_type and filter_type != "Все":
            filtered = [t for t in filtered if t['type'] == filter_type]
        
        # Фильтр по дате
        if filter_date:
            try:
                datetime.strptime(filter_date, "%Y-%m-%d")
                filtered = [t for t in filtered if t['date'] == filter_date]
            except ValueError:
                if filter_date:
                    messagebox.showwarning("Предупреждение", 
                                         f"Неверный формат даты фильтра: {filter_date}\nИспользуйте ГГГГ-ММ-ДД")
        
        # Добавление отфильтрованных данных в таблицу
        for training in filtered:
            self.tree.insert("", "end", values=(
                training['date'],
                training['type'],
                training['duration']
            ))
        
        # Обновление статуса
        total_count = len(self.trainings)
        filtered_count = len(filtered)
        if filtered_count == total_count:
            self.statusbar.config(text=f"📊 Всего тренировок: {total_count}")
        else:
            self.statusbar.config(text=f"📊 Показано: {filtered_count} из {total_count} тренировок")
    
    def reset_filters(self):
        """Сброс фильтров"""
        self.filter_type.set("Все")
        self.filter_date.delete(0, tk.END)
        self.refresh_table()
    
    def save_data(self, filename=None):
        """Сохранение данных в JSON"""
        if filename is None:
            filename = self.data_file
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.trainings, f, ensure_ascii=False, indent=2, sort_keys=True)
            self.statusbar.config(text=f"💾 Данные сохранены в {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")
    
    def load_data(self, filename=None):
        """Загрузка данных из JSON"""
        if filename is None:
            filename = self.data_file
        
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    # Валидация загруженных данных
                    if isinstance(loaded_data, list):
                        self.trainings = loaded_data
                        self.statusbar.config(text=f"📂 Загружено {len(self.trainings)} тренировок")
                    else:
                        self.trainings = []
                        messagebox.showwarning("Предупреждение", "Файл имеет неверный формат")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
                self.trainings = []
        else:
            self.trainings = []
    
    def load_data_dialog(self):
        """Загрузка данных через диалоговое окно"""
        filename = filedialog.askopenfilename(
            title="Выберите JSON файл",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.load_data(filename)
            self.refresh_table()
    
    def show_statistics(self):
        """Показ статистики тренировок"""
        if not self.trainings:
            messagebox.showinfo("Статистика", "Нет добавленных тренировок")
            return
        
        # Подсчет статистики
        total_trainings = len(self.trainings)
        total_duration = sum(t['duration'] for t in self.trainings)
        
        # Статистика по типам
        type_stats = {}
        for t in self.trainings:
            type_stats[t['type']] = type_stats.get(t['type'], 0) + 1
        
        # Самый популярный тип
        most_common_type = max(type_stats.items(), key=lambda x: x[1]) if type_stats else ("Нет", 0)
        
        # Формирование сообщения
        stats_text = f"""
📊 СТАТИСТИКА ТРЕНИРОВОК 📊

📌 Всего тренировок: {total_trainings}
⏱ Общая длительность: {total_duration} минут ({total_duration/60:.1f} часов)
⭐ Средняя длительность: {total_duration/total_trainings:.1f} минут

📈 Распределение по типам:
"""
        for t_type, count in sorted(type_stats.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_trainings) * 100
            stats_text += f"   • {t_type}: {count} ({percentage:.1f}%)\n"
        
        stats_text += f"\n🏆 Самый популярный тип: {most_common_type[0]} ({most_common_type[1]} тренировок)"
        
        messagebox.showinfo("Статистика тренировок", stats_text)
    
    def show_about(self):
        """Информация о программе"""
        about_text = """
 Training Planner v1.0
 
 Программа для планирования и учета тренировок
 
 Возможности:
 • Добавление тренировок
 • Фильтрация по типу и дате
 • Сохранение/загрузка в JSON
 • Статистика тренировок
 
 © 2024
        """
        messagebox.showinfo("О программе", about_text)

def main():
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()

if __name__ == "__main__":
    main()
