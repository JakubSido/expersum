import re
import shutil
from nbconvert import MarkdownExporter
from nbconvert.preprocessors import ExecutePreprocessor
import nbformat
import os
from traitlets.config import Config
from nbconvert.preprocessors import TagRemovePreprocessor

def generate_from_all_templates(template_folder, result_folder):
    for template in os.listdir(template_folder):
        template_path = os.path.join(template_folder, template)
        generate_readme_from_template(result_folder, template_path)

def generate_readme_from_template(result_folder, template_path):
    file_name = os.path.basename(template_path)
    file_name_no_ext = os.path.splitext(file_name)[0]
    python_script = os.path.join(result_folder, file_name)

    if not os.path.exists(python_script):  # due to results in template repository
        shutil.copy(template_path, python_script)

    os.system(f"python -m jupytext --to notebook {python_script}")

    # Define paths
    notebook_filename = python_script.replace(".py", ".ipynb")

    output_markdown_file = os.path.join(result_folder, file_name.replace(".py", ".md"))
    # exporter = MarkdownExporter(template_file="templates/custom.tpl")
    exporter = MarkdownExporter()

    # Setup config
    c = Config()

    # Configure tag removal - be sure to tag your cells to remove  using the
    # words remove_cell to remove cells. You can also modify the code to use
    # a different tag word
    c.TagRemovePreprocessor.remove_cell_tags = ("remove_cell",)
    c.TagRemovePreprocessor.remove_all_outputs_tags = ("remove_output",)
    c.TagRemovePreprocessor.remove_input_tags = ("remove_input",)
    c.TagRemovePreprocessor.enabled = True
    exporter.register_preprocessor(TagRemovePreprocessor(config=c), True)

    # Load the notebook
    with open(notebook_filename, encoding="utf8") as f:
        nb = nbformat.read(f, as_version=4)

    # Execute all cells in the notebook
    ep = ExecutePreprocessor(timeout=600, kernel_name="python3")
    ep.preprocess(nb, {"metadata": {"path": result_folder}})

    # Modify the `resources` dictionary to specify the output folder for images
    resources = {"output_files_dir": f"img_{file_name_no_ext}", "metadata": {"path": result_folder}}

    # Export the notebook to markdown, with image outputs saved in `output_folder`
    body, resources = exporter.from_notebook_node(nb, resources=resources)
    body = re.sub(r"```python[\s\S]*?```", "", body)

    # Save the markdown file in the output folder
    with open(output_markdown_file, "w") as f:
        f.write(body)

    # Save all additional outputs (images) in the output folder
    for filename, data in resources.get("outputs", {}).items():
        output_path = os.path.join(result_folder, filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "wb") as img_file:
            img_file.write(data)

    print(f"Markdown and image outputs saved to folder: {result_folder}")

