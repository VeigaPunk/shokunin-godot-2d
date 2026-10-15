import re

def classify_process(code, error, output, expected_exit, signature, allowed_errors=()):
        lines = output.splitlines()
        def allowed_error(line, allowed):
            stripped = line.strip()
            if stripped == allowed:
                return True
            if allowed.endswith(","):
                return stripped.startswith(allowed) and stripped.count("ERROR:") == 1
            if allowed == "ERROR: chain incomplete":
                return (stripped.startswith("ERROR: chain incomplete collections=")
                        and "scene=SceneB:<Node#" in stripped and "old_alive=false" in stripped
                        and stripped.count("ERROR:") == 1)
            return False

        unrelated_errors = [line for line in lines if "ERROR:" in line
                            and not any(allowed_error(line, allowed) for allowed in allowed_errors)]
        return (code == expected_exit and error is None and signature in output
                and not unrelated_errors and "SCRIPT ERROR:" not in output and "Parse Error:" not in output)
