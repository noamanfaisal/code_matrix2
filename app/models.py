from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from code_matrix.database.info import Base


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    language = Column(String, nullable=False)
    meta_data = Column(Text)
    branch = Column(String, nullable=False)  # Git branch stored at the project level
    modules = relationship("Module", back_populates="project", cascade="all, delete-orphan")

class Module(Base):
    __tablename__ = "modules"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)
    meta_data = Column(Text)
    project = relationship("Project", back_populates="modules")
    files = relationship("File", back_populates="module", cascade="all, delete-orphan")  # Added files relationship

class Relation(Base):
    __tablename__ = "relations"
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"))  # Source file
    related_file_id = Column(Integer, ForeignKey("files.id"))  # Target file
    relation_type = Column(String, nullable=False)
    meta_data = Column(Text)
    
    # Relationships to the File model
    source_file = relationship("File", foreign_keys=[file_id], back_populates="relations")
    target_file = relationship("File", foreign_keys=[related_file_id], back_populates="related_files")


class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"))
    text = Column(Text, nullable=False)
    path = Column(String, nullable=False)
    chroma_path = Column(String, nullable=True)
    module = relationship("Module", back_populates="files")
    
    # Relationships for classes, imports, and functions
    classes = relationship("Class", back_populates="file", cascade="all, delete-orphan")
    imports = relationship("Import", back_populates="file", cascade="all, delete-orphan")
    functions = relationship("Function", back_populates="file", cascade="all, delete-orphan")
    
    # Relationships for file relations
    relations = relationship(
        "Relation",
        foreign_keys=[Relation.file_id],
        back_populates="source_file",
        cascade="all, delete-orphan"
    )
    related_files = relationship(
        "Relation",
        foreign_keys=[Relation.related_file_id],
        back_populates="target_file",
        cascade="all, delete-orphan"
    )


class Class(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"))
    name = Column(String, nullable=False)  # Class name
    file = relationship("File", back_populates="classes")  # Link back to the File table


class Import(Base):
    __tablename__ = "imports"
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"))
    module_name = Column(String, nullable=False)  # Full module name
    alias = Column(String, nullable=True)  # Optional alias for the import
    file = relationship("File", back_populates="imports")  # Link back to the File table


class Function(Base):
    __tablename__ = "functions"
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"))
    name = Column(String, nullable=False)  # Function name
    file = relationship("File", back_populates="functions")  # Link back to the File table