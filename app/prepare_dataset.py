from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, join
from code_matrix.database.info import engine
from code_matrix.app.models import Project, Module, File, Class, Import, Function
import pandas as pd
import pickle

def prepare_dataset():
    # Create a database session
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    # Query to fetch file details along with related metadata
    file_details_query = (
        session.query(
            File.path.label("codefile"),
            Project.name.label("django_project_name"),
            Project.meta_data.label("project_meta_data"),
            Module.name.label("module_name"),
            Module.path.label("module_path"),
            File.codemod_status.label("django_version"),
            Class.name.label("class_name"),
            Function.name.label("function_name"),
            Import.module_name.label("import_name"),
        )
        .join(Module, File.module_id == Module.id)
        .join(Project, Module.project_id == Project.id)
        .outerjoin(Class, File.id == Class.file_id)
        .outerjoin(Function, File.id == Function.file_id)
        .outerjoin(Import, File.id == Import.file_id)
    ).all()

    # Process the query result into a list of dictionaries for pandas
    data = []
    for counter, row in enumerate(file_details_query):
        data.append({
            "codefile": row.codefile,
            "django_project_name": row.django_project_name,
            "django_version": row.django_version,
            "module_name": row.module_name,
            "module_path": row.module_path,
            "class_name": row.class_name,
            "function_name": row.function_name,
            "import_name": row.import_name,
            "project_meta_data": row.project_meta_data,  # Can be used to extract specific details like version
        })

    # Convert the list of dictionaries into a pandas DataFrame
    file_details_df = pd.DataFrame(data)

    # Close the session
    session.close()
    # Save DataFrame as a pickle file
    file_details_df.to_pickle("file_details.pkl")

# Display the DataFrame for inspection
# import ace_tools as tools; tools.display_dataframe_to_user(name="File Details DataFrame", dataframe=file_details_df)
