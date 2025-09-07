import subprocess
import sys

def run_command(command):
    """Run Python script with subprocess."""
    try:
        subprocess.run(["python"] + command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running command: {e}")

def main():
    while True:
        print("\n=== RailOptima CLI Menu ===")
        print("1. Run schedule optimization")
        print("2. Validate schedule")
        print("3. Visualize schedule")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ")

        if choice == "1":
            dataset = input("Enter dataset file (default: trains.csv): ") or "trains.csv"
            run_command(["optimizer_schedule.py", dataset])
        elif choice == "2":
            run_command(["validate_schedule.py"])
        elif choice == "3":
            run_command(["visualize_schedule.py"])
        elif choice == "4":
            print("👋 Exiting RailOptima. Goodbye!")
            sys.exit(0)
        else:
            print("⚠️ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
