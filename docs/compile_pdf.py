#!/usr/bin/env python3
"""
Script de compilation du rapport LaTeX en PDF.
Utilisation : python compile_rapport.py
Prerequis : pdflatex installe (texlive, miktex...)
"""

import subprocess
import sys
import os

def compile_pdf(tex_file, runs=2):
    if not os.path.exists(tex_file):
        print(f"Erreur : fichier '{tex_file}' introuvable.")
        sys.exit(1)

    base = os.path.splitext(tex_file)[0]

    for i in range(runs):
        print(f"Compilation ({i+1}/{runs})...")
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", tex_file],
            capture_output=True,
        )
        stdout = result.stdout.decode("utf-8", errors="replace")
        stderr = result.stderr.decode("utf-8", errors="replace")

        errors = [l for l in stdout.split("\n") if l.startswith("! ")]
        if errors:
            print("ERREURS DETECTEES :")
            for e in errors[:10]:
                print(f"  {e}")
        if stderr.strip():
            print(f"  Stderr: {stderr[:200]}")

        # Bibliographie : traitement de references.bib par biber
        print("Biber (bibliographie/webographie)...")
        result = subprocess.run(
            ["biber", base],
            capture_output=True,
        )
        stdout = result.stdout.decode("utf-8", errors="replace")
        stderr = result.stderr.decode("utf-8", errors="replace")
        if result.returncode != 0:
            print(f"  Biber : code de retour {result.returncode}")
            print(f"  {stderr[:500]}")

    # Nettoyer fichiers temporaires (apres toutes les compilations)
    for ext in [".aux", ".log", ".out", ".lof", ".lot", ".bcf", ".run.xml", ".bbl", ".blg"]:
        tmp = base + ext
        if os.path.exists(tmp):
            os.remove(tmp)

    pdf_file = base + ".pdf"
    if os.path.exists(pdf_file):
        size = os.path.getsize(pdf_file) / 1024
        print(f"OK : {pdf_file} genere ({size:.0f} Ko)")
        return True
    else:
        print("Erreur : le PDF n'a pas ete genere.")
        return False

if __name__ == "__main__":
    tex_file = sys.argv[1] if len(sys.argv) > 1 else "documentation.tex"
    compile_pdf(tex_file, runs=2)