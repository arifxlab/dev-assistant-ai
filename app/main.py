import os
from app.analyzer.code_analyzer import CodeAnalyzer


def main():
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "main.py")

    analyzer = CodeAnalyzer(file_path)
    analyzer.load_file()

    print("\nFull Analysis:")

    results = analyzer.full_analysis()

    for r in results:
        print(f"\nFunction: {r['name']}")
        print(f"Length: {r['length']}")
        print(f"Args: {r['args']}")
        print(f"Complexity: {r['complexity']}")
        print(f"Score: {r['score']}/10")

        if not r["issues"]:
            print("Issues: None")
        else:
            print("Issues:")
            for issue in r["issues"]:
                print(f"- {issue['type']} ({issue['severity']})")


if __name__ == "__main__":
    main()