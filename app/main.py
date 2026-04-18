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

    print("\nLong functions:")
    long_funcs = analyzer.find_long_functions(max_lines=5)

    if not long_funcs:
        print("None")
    else:
        for f in long_funcs:
            print(f"- {f['name']} ({f['length']} lines)")

    print("\nFunctions with too many arguments:")

    many_args = analyzer.find_functions_with_many_args(max_args=2)

    if not many_args:
        print("None")
    else:
        for f in many_args:
            print(f"- {f['name']} ({f['args']} args)")


if __name__ == "__main__":
    main()