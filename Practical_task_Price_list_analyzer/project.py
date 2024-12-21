import os
import csv


class PriceMachine:
    def __init__(self):
        self.data = []

    def load_prices(self, folder_path='.'):
        """
            Сканирует указанный каталог. Ищет файлы со словом price в названии.
            В файле ищет столбцы с названием товара, ценой и весом.
            Допустимые названия для столбца с товаром:
                товар
                название
                наименование
                продукт

            Допустимые названия для столбца с ценой:
                розница
                цена

            Допустимые названия для столбца с весом (в кг.):
                вес
                масса
                фасовка
        """
        counter = 0  # Счётчик загруженных товаров
        for filename in os.listdir(folder_path):
            if 'price' in filename:
                file_path = os.path.join(folder_path, filename)  # Создание полного пути к файлу
                with open(file_path, newline='', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')  # Создание объекта для чтения CSV
                    headers = next(reader)  # Читает первую строку файла (заголовок) и сохраняет её в переменную
                    price_index, weight_index, product_index = self._search_product_price_weight(headers)

                    for row in reader:
                        if price_index is not None and weight_index is not None and product_index is not None:
                            try:
                                price = float(row[price_index])
                                weight = float(row[weight_index])
                                product = row[product_index]
                                if weight > 0:
                                    price_per_kg = price / weight
                                    self.data.append({
                                        'product': product,
                                        'price': price,
                                        'weight': weight,
                                        'file': filename,
                                        'price_per_kg': price_per_kg
                                    })
                                    counter += 1  # Увеличиваем счётчик
                            except (ValueError, IndexError):
                                continue
        return counter  # Возвращаем количество загруженных товаров

    def _search_product_price_weight(self, headers):
        """Возвращает номера столбцов"""

        product_names = ['товар', 'название', 'наименование', 'продукт']
        price_names = ['цена', 'розница']
        weight_names = ['вес', 'масса', 'фасовка']

        product_index = next((i for i, header in enumerate(headers) if header.lower() in product_names), None)
        price_index = next((i for i, header in enumerate(headers) if header.lower() in price_names), None)
        weight_index = next((i for i, header in enumerate(headers) if header.lower() in weight_names), None)

        return price_index, weight_index, product_index

    def export_to_html(self, file_name='output.html'):
        result = '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Позиции продуктов</title>
            </head>
            <body>
                <table border="1">
                    <tr>
                        <th>Номер</th>
                        <th>Название</th>
                        <th>Цена</th>
                        <th>Фасовка</th>
                        <th>Файл</th>
                        <th>Цена за кг.</th>
                    </tr>
        '''
        for idx, item in enumerate(self.data, start=1):
            result += f'''
                    <tr>
                        <td>{idx}</td>
                        <td>{item['product']}</td>
                        <td>{item['price']}</td>
                        <td>{item['weight']}</td>
                        <td>{item['file']}</td>
                        <td>{item['price_per_kg']:.2f}</td>
                    </tr>
            '''
        result += '''
                </table>
            </body>
            </html>
        '''
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(result)

    def find_text(self, text):
        result = [item for item in self.data if text.lower() in item['product'].lower()]
        return sorted(result, key=lambda x: x['price_per_kg'])


if __name__ == '__main__':
    pm = PriceMachine()
    count = pm.load_prices()
    print(f"Загружено товаров: {count}")

    while True:
        user_input = input("Введите название товара для поиска (или 'exit' для выхода): ")
        if user_input.lower() == 'exit':
            print("Работа программы завершена.")
            break
        results = pm.find_text(user_input)
        if results:
            print(f"\nНайдено {len(results)} позиций:\n")
            print(f"{'№':<2} {'Наименование':<25} {'Цена':<8} {'Вес':<3} {'Файл':<12} {'Цена за кг.':<7}")
            for indx, item in enumerate(results, start=1):
                print(f"{indx:<2} {item['product']:<25} {item['price']:<8.2f} "
                      f"{item['weight']:<3.0f} {item['file']:<12} {item['price_per_kg']:.2f}")
        else:
            print("Товар не найден.")

    pm.export_to_html()
    print("Данные экспортированы в output.html.")
