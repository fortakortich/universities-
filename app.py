from flask import Flask, render_template, request
import pandas as pd
import joblib # Для загрузки модели и энкодеров
import traceback # Для отладки
# Импортируем функцию из файла model.py
from model import recommend_universities_v1

app = Flask(__name__)

# --- Загрузка данных и ML-компонентов при старте ---
try:
    # Укажите правильные пути к вашим файлам
    df_universities = pd.read_csv('universities_dataset.csv')
    model = joblib.load('model.pkl')
    le_major = joblib.load('le_major.pkl')
    le_language = joblib.load('le_language.pkl')

    # Используем ТОЧНЫЕ имена колонок из вашего датасета
    majors = sorted(df_universities['major'].astype(str).unique())
    languages = sorted(df_universities['language'].astype(str).unique())

    print("Датасет, модель и энкодеры успешно загружены.")
    RESOURCES_LOADED = True
except FileNotFoundError as e:
     print(f"Критическая ошибка: Не найден файл {e.filename}. Проверьте пути.")
     RESOURCES_LOADED = False
     df_universities, model, le_major, le_language, majors, languages = pd.DataFrame(), None, None, None, [], []
except KeyError as e:
     print(f"Критическая ошибка: Не найдена колонка {e} в CSV файле при загрузке majors/languages.")
     RESOURCES_LOADED = False
     df_universities, model, le_major, le_language, majors, languages = pd.DataFrame(), None, None, None, [], []
except Exception as e:
    print(f"Критическая ошибка при загрузке ресурсов: {e}")
    traceback.print_exc()
    RESOURCES_LOADED = False
    df_universities, model, le_major, le_language, majors, languages = pd.DataFrame(), None, None, None, [], []
# --- Конец блока загрузки ---


@app.route('/', methods=['GET', 'POST'])
def index():
    universities_results = []
    error_message = None
    user_input_data = {} # Для сохранения введенных данных

    if not RESOURCES_LOADED:
        error_message = "Ошибка сервера: Не удалось загрузить необходимые данные или модель. Пожалуйста, попробуйте позже."
    elif request.method == 'POST':
        try:
            # --- 1. Считывание данных из формы ---
            user_input_data = {
                'gpa': float(request.form.get('gpa', 0)),
                'ielts': float(request.form.get('ielts', 0)),
                'sat': int(request.form.get('sat', 0)),
                'budget': int(request.form.get('budget', 0)),
                'major': request.form.get('major'),
                'language': request.form.get('language'),
                'avg_temp': float(20 if request.form.get('avg_temp') == 'тёплый'
                                  else 10 if request.form.get('avg_temp') == 'умеренный'
                                  else 0)
            }

            # --- 2. Валидация ввода ---
            if not user_input_data['major'] or not user_input_data['language']:
                error_message = "Пожалуйста, выберите специальность и язык обучения."
            elif user_input_data['gpa'] < 0 or user_input_data['ielts'] < 0 or user_input_data['sat'] < 0 or user_input_data['budget'] < 0:
                 error_message = "Числовые значения (GPA, IELTS, SAT, Бюджет) не могут быть отрицательными."
            else:
                # --- 3. Вызов функции подбора из model.py ---
                universities_results = recommend_universities_v1(
                    user_input_data,
                    df_universities, # Оригинальный DataFrame
                    model,
                    le_major,
                    le_language
                )
                if not universities_results and error_message is None:
                     error_message = "По вашему профилю рекомендации не найдены (возможно, предсказание модели было отрицательным или нет подходящих вузов в базе)."

        except ValueError:
            error_message = "Пожалуйста, проверьте правильность ввода числовых полей (GPA, IELTS, SAT, Бюджет)."
        except Exception as e:
            print(f"Непредвиденная ошибка в роуте /: {e}")
            traceback.print_exc()
            error_message = "Произошла внутренняя ошибка сервера при обработке вашего запроса."

    # Передаем переменные в шаблон (имя 'universities' используется в HTML)
    return render_template('index.html',
                           universities=universities_results,
                           majors=majors,
                           languages=languages,
                           error=error_message)

if __name__ == '__main__':
    app.run(debug=True)