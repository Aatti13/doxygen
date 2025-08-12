# Imports
import os
import subprocess
import shutil
import re


class DoxygenAutomation:
  def __init__(self):
    self.github_url = ""
    self.clone_dir = ""
    self.project_name = ""
    self.input_dir = ""
    self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    self.output_dir = os.path.join(self.root_dir, "docs", "doxygen")
    self.doxyfile_path = os.path.join(self.root_dir, "Doxyfile")

  """
    Function to Get User Input:-
    - Get the GitHub Link
    - Check whether it is a legit GitHub Repo Link
    - Extract Project Name from the Link
    - Point the input directory to the Cloned Repo Link
  """
  def get_user_input(self):
    self.github_url = input("Enter GitHub repo URL: ").strip()
    if not self.github_url.endswith(".git"):
      self.github_url += ".git"

    self.project_name = self.github_url.split("/")[-1].replace(".git", "")
    self.clone_dir = os.path.join(self.root_dir, self.project_name)
    self.input_dir = self.clone_dir


  """
    Function to check whether doxygen is installed
  """
  def check_doxygen(self):
    if shutil.which("doxygen") is None:
      raise EnvironmentError("Doxygen is not installed or not in PATH.")

  """
    Function to clone the GitHub Repository
    - Use Subprocess to run the shell command 'git clone <repo-link>'
  """
  def clone_repo(self):
    if os.path.exists(self.clone_dir):
      print(f" Repo '{self.project_name}' already exists locally. Skipping clone.")
    else:
      print(f"Cloning {self.github_url}...")
      subprocess.run(["git", "clone", self.github_url, self.clone_dir], check=True)
      print("Repo cloned.")

  """
    Function to Make the Required Directories
    - (Here): ./docs/doxygen/docs
  """
  def prepare_directories(self):
    os.makedirs(self.output_dir, exist_ok=True)
    print(f"Ensured output directory exists: {self.output_dir}")

  """
    Function to Create or Update Already Created DoxyFile
    - Here: Part of parent Directory: Doxyfile
  """
  def create_or_update_doxyfile(self):
    self.prepare_directories()

    if not os.path.exists(self.doxyfile_path):
      subprocess.run(["doxygen", "-g", self.doxyfile_path], check=True)

    with open(self.doxyfile_path, "r") as file:
      config = file.read()

    # Doxyfile metadata
    replacements = {
      "PROJECT_NAME": f'PROJECT_NAME           = "{self.project_name}"',
      "OUTPUT_DIRECTORY": f"OUTPUT_DIRECTORY       = {self.output_dir}",
      "INPUT": f"INPUT                  = {self.input_dir}",
      "RECURSIVE": "RECURSIVE              = YES",
      "GENERATE_LATEX": "GENERATE_LATEX         = NO",
      "EXTRACT_ALL": "EXTRACT_ALL            = YES"
    }


    """
    Sometimes while using regular filepaths \s; \n are treated as escape sequences
    Therefore: .//a//b... or .\\a\\b\\... are treated as actual backslashes
    """
    for key, new_value in replacements.items():
      config = re.sub(
        rf"^{key}\s*=.*",
        lambda m: new_value.replace("\\", "\\\\"),
        config,
        flags=re.MULTILINE
      )

    # Write into the doxyfile
    with open(self.doxyfile_path, "w") as file:
      file.write(config)

    print(f"Doxyfile updated. INPUT now points to: {self.input_dir}")

  """
  Function to Generate Docs for GitHub Repo
  """
  def generate_docs(self):
    print("Generating documentation...")
    subprocess.run(["doxygen", self.doxyfile_path], check=True)
    print(f"Documentation generated in: {os.path.join(self.output_dir, 'html', 'index.html')}")

  """
  Calling all functions
  """
  def run(self):
    self.get_user_input()
    self.check_doxygen()
    self.clone_repo()
    self.create_or_update_doxyfile()
    self.generate_docs()


# Driver Code
if __name__ == "__main__":
  DoxygenAutomation().run()
