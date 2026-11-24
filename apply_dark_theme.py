from pathlib import Path
import re
import shutil

FILES = ["books.py", "students.py", "issue_return.py", "reports.py"]

def patch_file(path):
    source = path.read_text(encoding="utf-8")

    if "from ui_theme import apply_treeview_theme" not in source:
        # database import ke baad common style import add karna
        match = re.search(r"(?m)^from database import connect_db\s*$", source)
        if not match:
            raise RuntimeError(f"{path.name}: database import line nahi mili.")
        source = (
            source[:match.end()]
            + "\nfrom ui_theme import apply_treeview_theme"
            + source[match.end():]
        )

    # Har Treeview create hone se pehle style apply karna
    if "apply_treeview_theme(" not in source:
        source, count = re.subn(
            r"(?m)^([ \t]*)tree\s*=\s*ttk\.Treeview\(",
            lambda m: f"{m.group(1)}apply_treeview_theme(page)\n"
                      f"{m.group(1)}tree = ttk.Treeview(",
            source
        )
        if count == 0:
            raise RuntimeError(f"{path.name}: ttk.Treeview creation nahi mili.")

    backup = path.with_suffix(path.suffix + ".backup")
    if not backup.exists():
        shutil.copy2(path, backup)

    path.write_text(source, encoding="utf-8")
    print(f"Updated: {path.name} (backup: {backup.name})")


def main():
    folder = Path(__file__).resolve().parent
    missing = [name for name in FILES if not (folder / name).exists()]
    if missing:
        print("Ye files isi folder mein nahi mili:", ", ".join(missing))
        print("Script ko project ke main folder mein rakho aur dobara run karo.")
        return

    for name in FILES:
        patch_file(folder / name)

    print("\nDark table theme apply ho gayi.")
    print("Ab project run karo: python main.py")


if __name__ == "__main__":
    main()
