import os
from app.analyzer.code_analyzer import CodeAnalyzer


def main():
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "main.py")

    analyzer = CodeAnalyzer(file_path)
    analyzer.load_file()

    print("Functions found:")
    for func in analyzer.get_functions():
        print(f"- {func.name}")


if __name__ == "__main__":
    main()