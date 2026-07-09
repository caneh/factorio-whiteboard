import os
import time
from glob import glob
from collections import namedtuple

import mkdocs_gen_files  # pip install mkdocs-gen-files


def process_lua():
    """
    For each .lua files in the ./lua/ folder
    Create a markdown file in docs/lua_scripts/{script_name}.md
    """
    start_time = time.time()
    files = glob("./lua/*.lua")
    nav = mkdocs_gen_files.Nav()
    nav["Overview"] = "index.md"
    for path in files:
        print(f"Processing {path}")
        basename = os.path.basename(path)
        with open(path) as f:
            contents = f.read()
        script_name = basename.split(".lua")[0]
        filename = f"lua_scripts/{script_name}.md"
        with mkdocs_gen_files.open(filename, "w") as f:
            print(f'```lua title="{path}"\n', file=f)
            print(contents, file=f)
            print(f"\n```\n", file=f)
        mkdocs_gen_files.set_edit_path(filename, path)
        nav[script_name] = f"{script_name}.md"
    # gen-files only adds pages to the build, it doesn't add them to the nav;
    # mkdocs-literate-nav reads this SUMMARY.md to build the sidebar for this folder
    with mkdocs_gen_files.open("lua_scripts/SUMMARY.md", "w") as f:
        f.writelines(nav.build_literate_nav())
    print("Processed %s scripts in %0.3fs" % (len(files), time.time() - start_time))


def process_blueprints():
    """
    For each blueprint file anywhere under ./blueprints/ (searched recursively,
    since blueprints are organized into category subfolders)
    It will create a markdown file in docs/blueprints/{relative_path}.md
    """
    start_time = time.time()
    # non-blueprint tooling files that sometimes live alongside blueprints
    skip_extensions = {".py", ".bat", ".json", ".md"}
    files = [
        file
        for file in glob("./blueprints/**/*", recursive=True)
        if os.path.isfile(file)
        and os.path.splitext(file)[1].lower() not in skip_extensions
    ]
    nav = mkdocs_gen_files.Nav()
    nav["Overview"] = "index.md"
    for path in files:
        print(f"Processing {path}")
        # normalize to forward slashes: mkdocs_gen_files paths are URL-like,
        # but os.path.relpath uses the host OS separator (e.g. "\" on Windows)
        relpath = os.path.relpath(path, "./blueprints").replace(os.sep, "/")
        display_path = path.replace(os.sep, "/")
        basename = os.path.basename(path)
        with open(path) as f:
            contents = f.read().strip()
        filename = f"blueprints/{relpath}.md"
        with mkdocs_gen_files.open(f"blueprints/{relpath}.txt", "w") as f:
            print(contents, file=f)
        with mkdocs_gen_files.open(filename, "w") as f:
            print(f'```txt title="{display_path}"\n', file=f)
            # print(contents, file=f)
            print(f"\n```\n", file=f)
            # container and script for client-side blueprint string processing
            print(
                f"""<div id="blueprintContainer">Processing blueprint string ...</div>
                <script>
                if (typeof processBlueprint === "undefined") {{ 
                    window.addEventListener('load', (event) => {{
                        processBlueprint(`{basename}`, document.getElementById("blueprintContainer"));
                    }});
                }} else {{ 
                    processBlueprint(`{basename}`, document.getElementById("blueprintContainer")); 
                }}
                </script>""".replace(
                    "    ", ""
                ),  # replace whitespace to avoid markdown treating it as code block
                file=f,
            )
        mkdocs_gen_files.set_edit_path(filename, path)
        nav[tuple(relpath.split("/"))] = f"{relpath}.md"
    # gen-files only adds pages to the build, it doesn't add them to the nav;
    # mkdocs-literate-nav reads this SUMMARY.md to build the sidebar for this folder
    with mkdocs_gen_files.open("blueprints/SUMMARY.md", "w") as f:
        f.writelines(nav.build_literate_nav())
    print("Processed %s blueprints in %0.3fs" % (len(files), time.time() - start_time))


process_lua()
process_blueprints()
