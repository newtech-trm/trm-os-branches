import sys
import traceback

def check_import():
    print("--- check_neomodel_import.py execution start ---")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"sys.path: {sys.path}")

    try:
        import neomodel
        print(f"Found neomodel version: {neomodel.__version__}")
    except ImportError:
        print("ERROR: neomodel package is not installed.")
        return
    except AttributeError:
        print("ERROR: neomodel is installed, but __version__ attribute is missing.")
    except Exception as e:
        print(f"ERROR: Could not import neomodel or get version: {e}")
        traceback.print_exc()
        return

    print("\nAttempting to import from neomodel.cardinality...")
    try:
        from neomodel.cardinality import ZeroOrOne
        print("SUCCESS: Successfully imported ZeroOrOne from neomodel.cardinality")
    except ImportError as e:
        print(f"FAIL: ImportError when importing from neomodel.cardinality: {e}")
        traceback.print_exc()
    except ModuleNotFoundError as e:
        print(f"FAIL: ModuleNotFoundError when importing from neomodel.cardinality: {e}")
        traceback.print_exc()
    except Exception as e:
        print(f"FAIL: Other error when importing from neomodel.cardinality: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    output_lines = []
    original_stdout = sys.stdout

    class CaptureOutput:
        def __init__(self):
            self.lines = []
        def write(self, line):
            self.lines.append(line)
            original_stdout.write(line) # Also print to console
        def flush(self):
            original_stdout.flush()

    capture = CaptureOutput()
    sys.stdout = capture

    try:
        check_import()
    finally:
        sys.stdout = original_stdout
        with open("check_neomodel_output.txt", "w", encoding="utf-8") as f:
            for line in capture.lines:
                f.write(line)
        print("\nOutput also written to check_neomodel_output.txt")
