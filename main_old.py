import re
import json
from pathlib import Path


class WordWizard:
    def __init__(self, file_name: str):
        self.file_name = file_name  # przechowujemy nazwę pliku tekstowego.
        self.file_path = Path(file_name)  # tworzymy obiekt ścieżki do pliku
        self.text = self._load_text()  # wczytujemy zawartość pliku tekstowego

    def _load_text(self) -> str:
        try:
            return self.file_path.read_text(encoding='utf-8')  # odczytujemy zawartość pliku jako tekst
        except FileNotFoundError:
            print(f"Plik '{self.file_name}' nie został znaleziony.")  # wiadomośc wyświetlana jeśli dany plik nie istnieje
            return ""

    def count_words(self) -> int:
        words = re.findall(r'\b[a-zA-ZąęółńśćżźĄĘÓŁŃŚĆŻŹ]+\b', self.text)  # znajdujemy wszystkie słowa w tekście
        return len(words)  # zwracamy liczbę słów

    def count_numbers(self) -> int:
        numbers = re.findall(r'\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b', self.text)  # znajdujemy liczby w różnych formatach
        return len(numbers)  # zwracamy liczbę liczb

    def words_starting_with_capital(self) -> list[str]:
        return re.findall(r'\b[A-Z]\w*\b', self.text)  # znajdujemy słowa rozpoczynające się wielką literą

    def words_with_sequences(self, sequences: list[list[str]]) -> dict[str, list[str]]:
        results = {}  # tworzymy pusty słownik na wyniki
        for sequence in sequences:
            # tworzymy dynamiczny wzorzec regularny na podstawie sekwencji liter
            pattern = r'\b\w*?' + r'.*?'.join(map(re.escape, sequence)) + r'\w*?\b'
            results["".join(sequence)] = re.findall(pattern, self.text, re.IGNORECASE)  # wyszukujemy pasujące słowa
        return results

    def unique_sorted_words(self) -> list[str]:
        words = re.findall(r'\b[a-zA-ZąęółńśćżźĄĘÓŁŃŚĆŻŹ]+\b', self.text) # znajdujemy wszystkie słowa
        return sorted(set(words), key=str.lower)  # usuwamy duplikaty i sortujemy alfabetycznie

    def word_frequency(self) -> dict[str, int]:
        # znajdujemy słowa, liczby i znaki interpunkcyjne
        pattern = re.findall(r'\b[\w\d]+\b|\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|[^\w\s]', self.text)
        frequency_dict = {}  # tworzymy pusty słownik na częstotliwości
        for item in pattern:
            frequency_dict[item] = frequency_dict.get(item, 0) + 1  # zliczamy wystąpienia każdego elementu
        return dict(
            sorted(frequency_dict.items(), key=lambda x: x[1], reverse=True))  # sortujemy słownik malejąco po wartości

    def save_results_to_json(self, output_file: Path, sequences_results: dict):
        data = {
            "Liczba wszystkich słów": self.count_words(),
            "Ilość wszystkich liczb": self.count_numbers(),
            "Lista słów rozpoczynających się od wielkiej litery": len(self.words_starting_with_capital()),
            "Lista pasujących sekwencji": sequences_results,
            "Posortowana lista słów": self.unique_sorted_words(),
            "Słownik": self.word_frequency()
        }

        output_file.parent.mkdir(parents=True, exist_ok=True)  # tworzymy folder na wyniki, jeśli jeszcze nie istnieje
        with output_file.open('w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)  # zapisujemy dane do pliku JSON


def main():
    print('''Witaj w programie WordWizard!

WordWizard analizuje tekst z podanego przez Ciebie pliku pod kątem liczby słów, liczb, 
słów zaczynających się wielką literą, dopasowania do określonych sekwencji liter, 
a następnie generuje szczegółowe statystyki i zapisuje je w pliku JSON.
''')
    results_folder = Path("wyniki")  # folder na wyniki analizy

    while True:
        file_path_input = input('Podaj ścieżkę do pliku tekstowego lub wpisz "koniec", aby zakończyć działanie programu: ')

        if file_path_input.lower() == 'koniec':  # sprawdzamy, czy użytkownik chce zakończyć program
            print("Zamykanie programu WordWizard.")
            break

        file_path = Path(file_path_input)  # tworzymy obiekt ścieżki na podstawie podanego wejścia
        if not file_path.exists():  # sprawdzamy, czy plik istnieje
            print(f"Plik '{file_path_input}' nie istnieje. Spróbuj ponownie.")
            continue

        # wczytanie sekwencji liter z pliku sekwencje.json
        try:
            with open("sekwencje.json", "r", encoding="utf-8") as f:
                sequences = json.load(f)["sequences"]  # wczytujemy listę sekwencji liter
        except FileNotFoundError:
            print("Nie znaleziono pliku 'sekwencje.json'. Upewnij się, że plik istnieje w katalogu.")
            continue
        except json.JSONDecodeError:
            print("Plik 'sekwencje.json' zawiera błędy i nie można go wczytać.")
            continue

        # tworzymy obiekt WordWizard i wykonujemy analizę tekstu
        wizard = WordWizard(str(file_path))
        sequences_results = wizard.words_with_sequences(sequences)  # szukamy słów zawierających sekwencje

        # zapisujemy wyniki analizy do pliku JSON w folderze wyniki
        output_file = results_folder / (file_path.stem + "_wyniki.json")
        wizard.save_results_to_json(output_file, sequences_results)

        print(f"Analiza pliku '{file_path_input}' zakończona. Wyniki zapisano do '{output_file}'.")


if __name__ == "__main__":
    main()  # wywołujemy główną funkcję programu
