import subprocess
import sys


def run_check(command, description, allow_fail=False):
    print(f"\n[+] Ejecutando: {description}...")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        if allow_fail:
            print(f"⚠️  {description} reportó advertencias (no bloqueante).")
            return
        print(f"\n❌ Error en el paso: {description}.")
        sys.exit(1)
    print(f"✓ {description} completado con éxito.")


def main():
    print("==========================================")
    print(" INICIANDO COMPROBACIÓN PREVIA A COMPILAR ")
    print("==========================================")

    run_check("flake8 src/ --max-line-length=120", "Flake8", allow_fail=True)
    run_check("mypy src/ --ignore-missing-imports", "Mypy", allow_fail=True)
    run_check("pytest -q", "Pytest")

    print("\n==========================================")
    print(" 🎉 LISTO PARA COMPILAR")
    print("==========================================")


if __name__ == "__main__":
    main()
