"""
Some utils functions
"""
import os
import shutil
import sys
import pandas as pd

"""
Manually update this dict to add new characters that need to be escaped in LaTeX, or to change the way they are escaped.
For mathematical characters, the value should be the LaTeX code to produce the character, wrapped in $...$ if necessary.
"""
CHAR_CORRESPONDANCE = {
    "¹": "\\textsuperscript{1}",
    "²": "\\textsuperscript{2}",
    "³": "\\textsuperscript{3}",
    "⁴": "\\textsuperscript{4}",
    "⁵": "\\textsuperscript{5}",
    "⁶": "\\textsuperscript{6}",
    "⁷": "\\textsuperscript{7}",
    "⁸": "\\textsuperscript{8}",
    "⁹": "\\textsuperscript{9}",
    "⁰": "\\textsuperscript{0}",
    "&": "\\&", "%": "\\%", "#": "\\#", "_": "\\_",
    "~": "\\textasciitilde{}", "^": "\\textasciicircum{}",
    "∫": "$\\int$", "∑": "$\\sum$", "∏": "$\\prod$",
    "α": "$\\alpha$", "Α": "$\\Alpha$",
    "β": "$\\beta$", "Β": "$\\Beta$",
    "γ": "$\\gamma$", "Γ": "$\\Gamma$",
    "δ": "$\\delta$", "Δ": "$\\Delta$",
    "ε": "$\\epsilon$", "Ε": "$\\Epsilon$",
    "ζ": "$\\zeta$", "Ζ": "$\\Zeta$",
    "η": "$\\eta$", "Η": "$\\Eta$",
    "θ": "$\\theta$", "Θ": "$\\Theta$",
    "ι": "$\\iota$", "Ι": "$\\Iota$",
    "κ": "$\\kappa$", "Κ": "$\\Kappa$",
    "λ": "$\\lambda$", "Λ": "$\\Lambda$",
    "μ": "$\\mu$", "Μ": "$\\Mu$",
    "ν": "$\\nu$", "Ν": "$\\Nu$",
    "ξ": "$\\xi$", "Ξ": "$\\Xi$",
    "ο": "$o$", "Ο": "$O$",
    "π": "$\\pi$", "Π": "$\\Pi$",
    "ρ": "$\\rho$", "Ρ": "$\\Rho$",
    "σ": "$\\sigma$", "Σ": "$\\Sigma$",
    "τ": "$\\tau$", "Τ": "$\\Tau$",
    "υ": "$\\upsilon$", "Υ": "$\\Upsilon$",
    "φ": "$\\phi$", "Φ": "$\\Phi$",
    "χ": "$\\chi$", "Χ": "$\\Chi$",
    "ψ": "$\\psi$", "Ψ": "$\\Psi$",
    "ω": "$\\omega$", "Ω": "$\\Omega$",
}

def get_path(path:str):
    """
    Get the path from template for given string.
        - Replace `$root` by the execution path (directory of __main__)
        - Replace `$pwd` by current execution directory

    :param path: Template path to be updated
    """
    main = sys.modules.get('__main__')
    if main is not None and hasattr(main, "__file__"):
        root = os.path.dirname(os.path.abspath(main.__file__))
    else:
        root = os.getcwd()
    return path.replace("$rootDir", root).replace("$pwd", os.getcwd())

def copy_into(src, dest):
    """
    Copy file into directory

    :param src: Template path of file to be copied
    :param dest: Path to its destination
    """
    src_path = get_path(src)
    dest_path = get_path(dest)
    shutil.copy(src_path, dest_path)

def create_unexisting_dir(path:str):
    """
    Create a directory on disk, if it does not exist

    :param path: Path to the directory to be created
    :type path: str
    """
    if not os.path.exists(path):
        os.makedirs(path)

def export_df(df:pd.DataFrame, output_dir:str, name:str):
    """
    Save a dataframe as a CSV file.

    :param df: Dataframe to be saved
    :type df: pd.DataFrame
    :param output_dir: Path to directory
    :type output_dir: str
    :param name: Name of the CSV file
    :type name: str
    """
    dest_path = os.path.join(output_dir, name)
    df.to_csv(dest_path, index=False)

def texify(string:str):
    """
    Escape special characters for LaTeX

    :param string: String to be escaped
    :type string: str
    """
    # print(f"Texifying string: {string}")
    for char, replacement in CHAR_CORRESPONDANCE.items():
        string = string.replace(char, replacement)
    string = string.replace("$$", "")  # Remove double dollar signs to prevent issues in LaTeX

    # print(f"Texified string: {string}")
    return string
