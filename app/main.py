from colorama import Fore, init
init(autoreset=True)
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
        if r["score"] <= 5:
            print(Fore.RED + f"Score: {r['score']}/10")
        elif r["score"] <= 7:
            print(Fore.YELLOW + f"Score: {r['score']}/10")
        else:
            print(Fore.GREEN + f"Score: {r['score']}/10")

        if not r["issues"]:
            print("Issues: None")
        else:
            print("Issues:")
            for issue in r["issues"]:
                if issue["severity"] == "High":
                    print(Fore.RED + f"- {issue['type']} (High)")
                else:
                    print(Fore.YELLOW + f"- {issue['type']} (Medium)")

    print("\nWorst Functions:")
    worst = analyzer.get_worst_functions()
    for r in worst:
        print(f"- {r['name']} (Score: {r['score']}/10)")

    print("\nProblematic Functions:")
    problematic = analyzer.get_problematic_functions()

    if not problematic:
        print("None 🎉")
    else:
        for r in problematic:
            print(f"\n- {r['name']} (Score: {r['score']}/10)")
            for issue in r["issues"]:
                print(f"  → {issue['type']} ({issue['severity']})")

    print("\nCritical Functions:")
    critical = analyzer.get_critical_functions()

    if not critical:
        print("None 🚀")
    else:
        for r in critical:
            print(f"\n- {r['name']} (Score: {r['score']}/10)")
            for issue in r["issues"]:
                print(f"  🔥 {issue['type']}")


if __name__ == "__main__":
    main()