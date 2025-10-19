import os
from python_minifier import minify


def minify_project(project_name: str, output_dir: str, source_dir: str, strip_comments: bool):
    """
    Minifies a Python project using python_minifier.

    Args:
        project_name (str): The name of the project to minify.
        output_dir (str): The directory where the minified files will be saved.
        source_dir (str): The directory containing the source files to minify.
        strip_comments (bool): Removes comments, docstrings and strips them.

    Returns:
        str: The absolute path to the minified project's output directory.
    """
    # Resolve absolute paths
    output_dir = os.path.abspath(f"{output_dir}/{project_name}")
    source_dir = os.path.abspath(source_dir)

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Traverse the source directory to find Python files
    for root, dirs, files in os.walk(source_dir):
        print(f"Minifying Current Directory: {root}")
        print(f"Next Subdirectories: {dirs}")
        print(f"Files: {files}")
        print("-" * 40)
        for file in files:
            if file.endswith(".py"):
                # Define the input and output file paths
                input_file = os.path.join(root, file)
                relative_path = os.path.relpath(root, source_dir)
                target_dir = os.path.join(output_dir, relative_path)
                os.makedirs(target_dir, exist_ok=True)
                output_file = os.path.join(target_dir, file)

                # Read the source file
                with open(input_file, 'r') as f:
                    code = f.read()

                # Minify the code
                minified_code = minify(
                    code,
                    remove_literal_statements=strip_comments,  # Removes docstrings
                    remove_annotations=True, # Removes annotations
                )

                # Write the minified code to the output file
                with open(output_file, 'w') as f:
                    f.write(minified_code)

    return output_dir