from code_matrix.app.extract_code import get_code_files
from code_matrix.app.extract_information import extract_code_details
# extract code files
code_files = get_code_files("code/mk_source_code/web")
for code_file in code_files:

    details = extract_code_details('/home/noaman/code/muslimkids/code_matrix/'+code_file['path'])
    print('file_name =%s'%code_file['path'])
    print(details)
