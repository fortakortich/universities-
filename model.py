import pandas as pd
import joblib
import traceback

# --- Функция подбора (Вариант 1) ---
def recommend_universities_v1(user_input, df_original, model, le_major, le_language, n_recommendations=10):
    """
    Реализует Вариант 1: использует предсказание для пользователя как "ворота".
    Показывает N университетов из df_original, где can_admit == 1,
    если предсказание для профиля пользователя == 1.
    """
    if df_original.empty or model is None or le_major is None or le_language is None:
        print("Ошибка: Не хватает данных или компонентов модели для рекомендации.")
        return []

    try:
        # --- 1. Подготовка данных пользователя для модели ---
        model_input_data = {
            'gpa': user_input.get('gpa'),
            'ielts': user_input.get('ielts'),
            'sat': user_input.get('sat'),
            'budget': user_input.get('budget'),
            'major': user_input.get('major'),
            'language': user_input.get('language'),
            'avg_temp': user_input.get('avg_temp')
        }
        input_df = pd.DataFrame([model_input_data])

        if not all(col in input_df.columns for col in ['major', 'language']):
            print("Ошибка: Отсутствуют колонки 'major' или 'language' во входных данных для модели.")
            return []
        if input_df['major'].iloc[0] is None or input_df['language'].iloc[0] is None:
            print("Ошибка: Значения 'major' или 'language' не должны быть None.")
            return []

        # Преобразование категориальных признаков пользователя
        try:
            input_df['major'] = le_major.transform([input_df['major'].iloc[0]])
            input_df['language'] = le_language.transform([input_df['language'].iloc[0]])
        except ValueError as e:
            # Ошибка, если введено значение, которого не было при обучении энкодера
            print(f"Ошибка преобразования категориальных признаков: {e}. Возможно, выбрано значение, не известное модели.")
            traceback.print_exc()
            return [] # Возвращаем пустой список при такой ошибке

        # Порядок признаков для модели (должен совпадать с обучением!)
        model_feature_order = ['gpa', 'ielts', 'sat', 'budget', 'major', 'language', 'avg_temp']
        try:
            input_df_ordered = input_df[model_feature_order]
        except KeyError as e:
            print(f"Ошибка: Не найден признак '{e}', необходимый для модели, во входных данных.")
            return []

        # --- 2. Предсказание для профиля пользователя ---
        prediction_for_user = model.predict(input_df_ordered)[0]
        print(f"Предсказание модели для пользователя: {prediction_for_user}")

        # --- 3. Выборка университетов из базы данных ---
        if prediction_for_user == 1:
            # Используем ТОЧНОЕ имя целевой колонки из вашего датасета
            target_column = 'can_admit'
            if target_column in df_original.columns:
                eligible_unis = df_original[df_original[target_column] == 1].copy()

                if eligible_unis.empty:
                    print(f"Предсказание для пользователя = 1, но нет университетов с '{target_column}'=1 в базе.")
                    return []

                # Используем ТОЧНЫЕ имена колонок из датасета, ожидаемые HTML
                result_cols = ['university_name', 'country', 'qs_rank', 'description']

                # Проверка наличия этих колонок в eligible_unis
                actual_cols = [col for col in result_cols if col in eligible_unis.columns]
                if len(actual_cols) != len(result_cols):
                    missing = set(result_cols) - set(actual_cols)
                    print(f"Предупреждение: Не все колонки ({missing}) найдены для вывода в HTML.")
                    if not actual_cols: return [] # Нечего выводить

                # Возвращаем N случайных строк с нужными колонками
                num_results = min(n_recommendations, len(eligible_unis))
                # Выбираем ТОЛЬКО существующие и нужные колонки перед to_dict
                recommended_list = eligible_unis.sample(n=num_results)[actual_cols].to_dict('records')
                print(f"Рекомендовано {len(recommended_list)} университетов.")
                return recommended_list
            else:
                print(f"Ошибка: Целевая колонка '{target_column}' не найдена в исходном DataFrame.")
                return []
        else:
            print("Предсказание для пользователя = 0, рекомендации не выдаются.")
            return []

    except Exception as e:
        print(f"Ошибка внутри функции recommend_universities_v1: {e}")
        traceback.print_exc()
        return []