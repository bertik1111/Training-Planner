import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog

trainings = []
data_file = "trainings.json"

def load_data(filename=None):
    global trainings
    if filename is None:
        filename = data_file
    
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
                if isinstance(loaded_data, list):
                    trainings = loaded_data
                    statusbar.config(text=f"📂 Загружено {len(trainings)} тренировок")
                else:
                    trainings = []
                    messagebox.showwarning("Предупреждение", "Файл имеет неверный формат")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
            trainings = []
    else:
        trainings = []

def save_data(filename=None):
    global trainings
    if filename is None:
        filename = data_file
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(trainings, f, ensure_ascii=False, indent=2, sort_keys=True)
        statusbar.config(text=f"💾 Данные сохранены в {filename}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")

def add_training():
    global trainings
    date = date_entry.get().strip()
    training_type = type_entry.get().strip()
    duration = duration_entry.get().strip()
    
    if not date or not training_type or not duration:
        messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля!")
        return
    
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Ошибка", "Неверный формат даты!\nИспользуйте формат: ГГГГ-ММ-ДД\nНапример: 2024-12-25")
        return
    
    if training_type == "Выберите тип":
        messagebox.showerror("Ошибка", "Пожалуйста, выберите тип тренировки!")
        return
    
    try:
        duration_min = float(duration)
        if duration_min <= 0:
            raise ValueError
        if duration_min > 1440:
            messagebox.showerror("Ошибка", "Длительность не может превышать 1440 минут (24 часа)!")
            return
    except ValueError:
        messagebox.showerror("Ошибка", "Длительность должна быть положительным числом!\nНапример: 30, 45.5, 60")
        return
    
    trainings.append({
        "date": date,
        "type": training_type,
        "duration": duration_min
    })
    
    duration_entry.delete(0, tk.END)
    type_entry.set("Выберите тип")
    
    refresh_table()
    save_data()
    statusbar.config(text=f"✅ Тренировка добавлена: {date}, {training_type}, {duration_min} мин")

def delete_training():
    global trainings
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Предупреждение", "Пожалуйста, выберите тренировку для удаления!")
        return
    
    if not messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить выбранную тренировку?"):
        return
    
    item = tree.item(selected[0])
    values = item['values']
    
    for i, training in enumerate(trainings):
        if (training['date'] == values[0] and 
            training['type'] == values[1] and 
            training['duration'] == float(values[2])):
            del trainings[i]
            break
    
    refresh_table()
    save_data()
    statusbar.config(text=f"🗑 Тренировка удалена: {values[0]}, {values[1]}")

def refresh_table():
    for item in tree.get_children():
        tree.delete(item)
    
    filter_type = filter_type_var.get()
    filter_date = filter_date_entry.get().strip()
    
    filtered = trainings.copy()
    
    if filter_type and filter_type != "Все":
        filtered = [t for t in filtered if t['type'] == filter_type]
    
    if filter_date:
        try:
            datetime.strptime(filter_date, "%Y-%m-%d")
            filtered = [t for t in filtered if t['date'] == filter_date]
        except ValueError:
            if filter_date:
                messagebox.showwarning("Предупреждение", 
                                     f"Неверный формат даты фильтра: {filter_date}\nИспользуйте ГГГГ-ММ-ДД")
    
    for training in filtered:
        tree.insert("", "end", values=(
            training['date'],
            training['type'],
            training['duration']
        ))
    
    total_count = len(trainings)
    filtered_count = len(filtered)
    if filtered_count == total_count:
        statusbar.config(text=f"📊 Всего тренировок: {total_count}")
    else:
        statusbar.config(text=f"📊 Показано: {filtered_count} из {total_count} тренировок")

def reset_filters():
    filter_type_var.set("Все")
    filter_date_entry.delete(0, tk.END)
    refresh_table()

def load_data_dialog():
    filename = filedialog.askopenfilename(
        title="Выберите JSON файл",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )
    if filename:
        load_data(filename)
        refresh_table()

def show_statistics():
    if not trainings:
        messagebox.showinfo("Статистика", "Нет добавленных тренировок")
        return
    
    total_trainings = len(trainings)
    total_duration = sum(t['duration'] for t in trainings)
    
    type_stats = {}
    for t in trainings:
        type_stats[t['type']] = type_stats.get(t['type'], 0) + 1
    
    most_common_type = max(type_stats.items(), key=lambda x: x[1]) if type_stats else ("Нет", 0)
    
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

def show_about():
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

root = tk.Tk()
root.title("Training Planner - План тренировок")
root.geometry("900x600")
root.resizable(True, True)

menubar = tk.Menu(root)
root.config(menu=menubar)

file_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Файл", menu=file_menu)
file_menu.add_command(label="Сохранить в JSON", command=save_data)
file_menu.add_command(label="Загрузить из JSON", command=load_data_dialog)
file_menu.add_separator()
file_menu.add_command(label="Выход", command=root.quit)

help_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Помощь", menu=help_menu)
help_menu.add_command(label="О программе", command=show_about)

main_container = ttk.Frame(root, padding="10")
main_container.pack(fill="both", expand=True)

input_frame = ttk.LabelFrame(main_container, text="Добавление новой тренировки", padding="10")
input_frame.pack(fill="x", pady=(0, 10))

ttk.Label(input_frame, text="Дата:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="e")
date_entry = ttk.Entry(input_frame, width=15, font=("Arial", 10))
date_entry.grid(row=0, column=1, padx=5, pady=5)
date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
ttk.Label(input_frame, text="(ГГГГ-ММ-ДД)", foreground="gray").grid(row=0, column=2, padx=5, pady=5, sticky="w")

ttk.Label(input_frame, text="Тип тренировки:", font=("Arial", 10, "bold")).grid(row=0, column=3, padx=5, pady=5, sticky="e")
type_entry = ttk.Combobox(input_frame, values=["Бег", "Плавание", "Велосипед", "Силовая", "Йога", "Футбол", "Теннис"], 
                                    width=15, font=("Arial", 10))
type_entry.grid(row=0, column=4, padx=5, pady=5)
type_entry.set("Выберите тип")

ttk.Label(input_frame, text="Длительность (мин):", font=("Arial", 10, "bold")).grid(row=0, column=5, padx=5, pady=5, sticky="e")
duration_entry = ttk.Entry(input_frame, width=10, font=("Arial", 10))
duration_entry.grid(row=0, column=6, padx=5, pady=5)

ttk.Button(input_frame, text="➕ Добавить тренировку", command=add_training).grid(row=0, column=7, padx=10, pady=5)

filter_frame = ttk.LabelFrame(main_container, text="Фильтрация тренировок", padding="10")
filter_frame.pack(fill="x", pady=(0, 10))

ttk.Label(filter_frame, text="Тип тренировки:", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
filter_type_var = tk.StringVar(value="Все")
filter_type = ttk.Combobox(filter_frame, textvariable=filter_type_var, 
                           values=["Все", "Бег", "Плавание", "Велосипед", "Силовая", "Йога", "Футбол", "Теннис"], 
                           width=15, font=("Arial", 10))
filter_type.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(filter_frame, text="Дата:", font=("Arial", 10)).grid(row=0, column=2, padx=5, pady=5, sticky="e")
filter_date_entry = ttk.Entry(filter_frame, width=15, font=("Arial", 10))
filter_date_entry.grid(row=0, column=3, padx=5, pady=5)
ttk.Label(filter_frame, text="(ГГГГ-ММ-ДД)", foreground="gray").grid(row=0, column=4, padx=5, pady=5, sticky="w")

ttk.Button(filter_frame, text="🔍 Применить фильтры", command=refresh_table).grid(row=0, column=5, padx=5, pady=5)
ttk.Button(filter_frame, text="🔄 Сбросить фильтры", command=reset_filters).grid(row=0, column=6, padx=5, pady=5)

table_frame = ttk.LabelFrame(main_container, text="Список тренировок", padding="10")
table_frame.pack(fill="both", expand=True)

columns = ("date", "type", "duration")
tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

tree.heading("date", text="📅 Дата")
tree.heading("type", text="🏃 Тип тренировки")
tree.heading("duration", text="⏱ Длительность (мин)")

tree.column("date", width=120, anchor="center")
tree.column("type", width=200, anchor="center")
tree.column("duration", width=150, anchor="center")

scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
scroll_x = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

tree.grid(row=0, column=0, sticky="nsew")
scroll_y.grid(row=0, column=1, sticky="ns")
scroll_x.grid(row=1, column=0, sticky="ew")

table_frame.grid_rowconfigure(0, weight=1)
table_frame.grid_columnconfigure(0, weight=1)

control_frame = ttk.Frame(main_container)
control_frame.pack(fill="x", pady=(10, 0))

ttk.Button(control_frame, text="🗑 Удалить выбранную", command=delete_training).pack(side="left", padx=5)
ttk.Button(control_frame, text="💾 Сохранить в JSON", command=save_data).pack(side="left", padx=5)
ttk.Button(control_frame, text="📂 Загрузить из JSON", command=load_data_dialog).pack(side="left", padx=5)
ttk.Button(control_frame, text="📊 Статистика", command=show_statistics).pack(side="left", padx=5)

statusbar = ttk.Label(main_container, text="Готов к работе", relief="sunken", anchor="w")
statusbar.pack(fill="x", pady=(10, 0))

load_data()

refresh_table()

root.mainloop()
