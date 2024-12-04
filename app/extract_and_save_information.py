import ast
import jedi
import os
from sqlalchemy.orm import Session
from code_matrix.app.models import Project, Module, File, Class, Import, Function
from sqlalchemy.orm import sessionmaker
from code_matrix.database.info import engine
import pickle
web_path = 'web.5'
def extract_file_details(file_path):
    """
    Extracts imports, classes, and functions from a Python file.

    Args:
        file_path (str): Path to the Python file.

    Returns:
        dict: Extracted information containing:
              - imports (list of dicts): Module and alias information.
              - classes (list): Class names.
              - functions (list): Function names.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        file_code = f.read()

    # Extract imports using AST
    tree = ast.parse(file_code)
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append({"module_name": alias.name, "alias": alias.asname})
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imports.append({"module_name": f"{module}.{alias.name}", "alias": alias.asname})

    # Extract classes and functions using Jedi
    script = jedi.Script(file_code)
    names = script.get_names(all_scopes=True)
    classes = [name.name for name in names if name.type == "class"]
    functions = [name.name for name in names if name.type == "function"]

    return {
        "imports": imports,
        "classes": classes,
        "functions": functions,
        "code":file_code
    }

def get_code_files(folder_path, extensions=(".py")):
    """
    Recursively collect all files with allowed extensions and extract imports, classes, and functions.

    Args:
        folder_path (str): Path to the folder to scan for files.
        extensions (tuple): Allowed file extensions (default: ".py").

    Returns:
        list: A list of dictionaries containing file path and extracted details.
    """
    
    code_files_details = []  # List to store file paths and extracted details
    counter = 0
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(extensions):
                file_path = os.path.join(root, file)
                print(f"Processing file {counter}: {file_path}")

                counter = counter + 1
                try:
                    # Extract file details
                    
                    extracted_details = extract_file_details(file_path)
                    extracted_details["path"] = file_path  # Add file path to the result
                    code_files_details.append(extracted_details)
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")
    
    return code_files_details

def get_all_files_information(folder_path = f"code/mk_source_code/{web_path}"):

    # Call the function
    # import pdb;pdb.set_trace()
    code_and_extracted_information = get_code_files(folder_path)
    return code_and_extracted_information

def save_to_pickle(data_to_save, file_name):

    # Save to a pickle file
    with open(file_name, "wb") as file:  # Open file in write-binary mode
        pickle.dump(data_to_save, file)

def load_from_pickle(file_name):
    # Load from a pickle file
    with open(file_name, "rb") as file:  # Open file in read-binary mode
        loaded_data = pickle.load(file)
        return loaded_data
    
def get_module_info(file_path, apps_root):
    """
    Extracts the module name and module path from the given file path.

    Args:
        file_path (str): Full path of the file.
        apps_root (str): Root directory of the apps folder.

    Returns:
        tuple: (module_name, module_path)
    """
    # Ensure the apps_root ends with a slash for consistent handling
    # import pdb;pdb.set_trace()
    apps_root = os.path.join(apps_root, "")
    
    if apps_root not in file_path:
        raise ValueError(f"File path {file_path} is not within the apps root {apps_root}")
    
    # Extract the part of the path after the apps directory
    relative_path = file_path.split(apps_root, 1)[1]
    
    # Module name is the first component after "apps"
    parts = relative_path.split(os.sep)
    module_name = parts[0]
    
    # Module path is the full path up to the module directory
    module_path = os.path.join(apps_root, module_name)

    return module_name, module_path

def save_all_information(folder_path = f"code/mk_source_code/{web_path}"):

    
    data = get_all_files_information()
    # saving data to pickle for later use
    
    save_to_pickle(data, f'{web_path}.pickle')
    # data = load_from_pickle("1.pickle")
    # Create a database session
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    # Add a project
    
    project = add_project(session, "Muslimkids.Django5", branch="web-production2", 
                          meta_data="django.5.codemod")
    for item in data:
        try:
            module_name, module_path = get_module_info(item['path'],                                        
            f'code/mk_source_code/{web_path}/apps')
            # saving module
            
        except ValueError as ve:
            module_name = 'global_app'
            module_path = f'code/mk_source_code/{web_path}'
        # adding module for that entry
        module = add_module(session, project.id, module_name, module_path)
        # print(item['path'])
        # print(module_name)

        # adding file for that module
        code_file = add_file(session, module.id, item['path'], item['code'])
        # # adding import
        add_imports(session, code_file.id, item['imports'])
        # # addin classes and functions
        add_classes_and_functions(session, code_file.id, item['classes'], item['functions'])

def add_project(session: Session, project_name: str, branch: str,meta_data: str, language: str = "Python"):
    """
    Add a new project to the database.

    Args:
        session (Session): SQLAlchemy session.
        project_name (str): Name of the project.
        branch (str): Git branch.
        language (str): Programming language (default: "Python").

    Returns:
        Project: The created or existing project instance.
    """
    project = session.query(Project).filter_by(name=project_name).first()
    if not project:
        project = Project(name=project_name, branch=branch, language=language, meta_data=meta_data)
        session.add(project)
        session.commit()
    return project

def add_module(session: Session, project_id: int, module_name: str, module_path: str):
    """
    Add a new module to the database.

    Args:
        session (Session): SQLAlchemy session.
        project_id (int): ID of the project the module belongs to.
        module_name (str): Name of the module.
        module_path (str): Path to the module.

    Returns:
        Module: The created or existing module instance.
    """
    module = session.query(Module).filter_by(name=module_name, project_id=project_id).first()
    if not module:
        module = Module(project_id=project_id, name=module_name, path=module_path, meta_data="{}")
        session.add(module)
        session.commit()
    return module

def add_file(session: Session, module_id: int, file_path: str, file_text: str):
    """
    Add a new file to the database.

    Args:
        session (Session): SQLAlchemy session.
        module_id (int): ID of the module the file belongs to.
        file_path (str): Path to the file.
        file_text (str): File content.

    Returns:
        File: The created or existing file instance.
    """
    file_entry = session.query(File).filter_by(path=file_path, module_id=module_id).first()
    if not file_entry:
        file_entry = File(module_id=module_id, path=file_path, text=file_text, chroma_path=None)
        session.add(file_entry)
        session.commit()
    return file_entry

def add_classes_and_functions(session: Session, file_id: int, classes: list, functions: list):
    """
    Add classes and functions to the database.

    Args:
        session (Session): SQLAlchemy session.
        file_id (int): ID of the file the classes and functions belong to.
        classes (list): List of class names.
        functions (list): List of function names.
    """
    # Add classes
    for class_name in classes:
        existing_class = session.query(Class).filter_by(file_id=file_id, name=class_name).first()
        if not existing_class:
            new_class = Class(file_id=file_id, name=class_name)
            session.add(new_class)

    # Add functions
    for function_name in functions:
        existing_function = session.query(Function).filter_by(file_id=file_id, name=function_name).first()
        if not existing_function:
            new_function = Function(file_id=file_id, name=function_name)
            session.add(new_function)

    session.commit()

def add_imports(session: Session, file_id: int, imports: list):
    """
    Add imports to the database.

    Args:
        session (Session): SQLAlchemy session.
        file_id (int): ID of the file the imports belong to.
        imports (list): List of dictionaries containing module_name and alias.
    """
    for imp in imports:
        existing_import = session.query(Import).filter_by(
            file_id=file_id, module_name=imp["module_name"], alias=imp["alias"]
        ).first()
        if not existing_import:
            new_import = Import(
                file_id=file_id, module_name=imp["module_name"], alias=imp["alias"]
            )
            session.add(new_import)

    session.commit()
