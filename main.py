import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
from tkcalendar import DateEntry

import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship, sessionmaker

engine = create_engine('mysql+pymysql://root:!andrei2002@localhost:3306/proiect')
Base = sqlalchemy.orm.declarative_base()

#ala bala

class Student(Base):
    __tablename__ = 'studenti'
    idstudent = Column(Integer, primary_key=True)
    nume = Column(String(50))
    prenume = Column(String(50))
    cnp = Column(String(13))  # Assuming the CNP has 13 characters
    anstudiu = Column(Integer)
    facultate = Column(String(50))
    inscrieri = relationship('Inscriere', back_populates='student',  cascade='all, delete-orphan')

class Curs(Base):
    __tablename__ = 'cursuri'
    idcurs = Column(Integer, primary_key=True)
    denumire = Column(String(50))
    anrecomandat = Column(Integer)
    facultaterecomandata = Column(String(50))
    domeniu = Column(String(50))
    semestru = Column(Integer)
    inscrieri = relationship('Inscriere', back_populates='curs',  cascade='all, delete-orphan')

class Inscriere(Base):
    __tablename__ = 'inscrieri'
    idinscriere = Column(Integer, primary_key=True)
    idstudent = Column(Integer, ForeignKey('studenti.idstudent'))
    idcurs = Column(Integer, ForeignKey('cursuri.idcurs'))
    data_inscriere = Column(Date)
    student = relationship('Student', back_populates='inscrieri')
    curs = relationship('Curs', back_populates='inscrieri')

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# GUI
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="PIBD CRUD App", font=("Helvetica", 24))
        label.pack(pady=20)

        label = tk.Label(self, text="Andrei Dobrin 432A", font=("Helvetica", 24))
        label.pack(pady=20)

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        db_buttons = []
        db_names = ['studenti', 'cursuri', 'inscrieri']
        for db_name in db_names:
            button = ttk.Button(button_frame, text=db_name[0].upper()+db_name[1:len(db_name)], command=lambda name=db_name: self.show_crud_interface(name))
            button.pack(side=tk.LEFT, padx=10)
            db_buttons.append(button)

    def show_crud_interface(self, db_name):
        self.controller.show_frame(CrudWindow, db_name)


class CrudApp(ThemedTk):
    def __init__(self):
        super().__init__()

        self.title("PIBD CRUD App")
        self.set_theme("plastik")

        self.state('zoomed')  # Start maximized

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True, padx=10, pady=10, anchor="center")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, CrudWindow):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        confirm = messagebox.askyesno("Exit", "Are you sure you want to exit? Any unsaved changes will be lost.")
        if confirm:
            engine.dispose()
            self.destroy()

    def show_frame(self, cont, *args):
        frame = self.frames[cont]
        frame.tkraise()

        if isinstance(frame, CrudWindow):
            frame.set_db_name(*args)

        if hasattr(frame, 'back_button'):
            frame.back_button.destroy()

        if cont != StartPage:
            back_button = ttk.Button(self, text='Back', command=lambda: self.show_frame(StartPage))
            back_button.pack(side=tk.TOP, anchor="w", padx=10, pady=10)
            frame.back_button = back_button


class CrudWindow(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db_name = None

        self.title_label = tk.Label(self, text="", font=("Helvetica", 16))
        self.title_label.pack(pady=10)
        self.entry_widgets = []
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        self.create_button = ttk.Button(button_frame, text='Create', command=self.create)
        self.create_button.pack(side=tk.LEFT, padx=10)

        self.read_button = ttk.Button(button_frame, text='Read', command=self.read)
        self.read_button.pack(side=tk.LEFT, padx=10)

        self.update_button = ttk.Button(button_frame, text='Update', command=self.update)
        self.update_button.pack(side=tk.LEFT, padx=10)

        self.delete_button = ttk.Button(button_frame, text='Delete', command=self.delete)
        self.delete_button.pack(side=tk.LEFT, padx=10)

        self.tree = ttk.Treeview(self)
        self.tree.pack(pady=10)
        self.bind("WM_DELETE_WINDOW", self.event_delete)

    def set_db_name(self, db_name):
        self.db_name = db_name
        self.title_label.config(text=f"Table: {db_name.capitalize()}")
        self.update_tree_columns()
        self.show_data()

    def update_tree_columns(self):
        columns = []
        column_properties = []

        if self.db_name == 'studenti':
            columns = ['#1', '#2', '#3', '#4', '#5', '#6']
            column_properties = [
                ('#1', 'ID', 'center', 100),
                ('#2', 'Name', 'center', 150),
                ('#3', 'Prenume', 'center', 150),
                ('#4', 'CNP', 'center', 150),
                ('#5', 'An Studiu', 'center', 100),
                ('#6', 'Facultate', 'center', 150)
            ]
        elif self.db_name == 'cursuri':
            columns = ['#1', '#2', '#3', '#4', '#5', '#6']
            column_properties = [
                ('#1', 'ID', 'center', 100),
                ('#2', 'Denumire', 'center', 150),
                ('#3', 'An Recomandat', 'center', 100),
                ('#4', 'Facultate Recomandata', 'center', 150),
                ('#5', 'Domeniu', 'center', 150),
                ('#6', 'Semestru', 'center', 100)
            ]
        elif self.db_name == 'inscrieri':
            columns = ['#1', '#2', '#3', '#4']
            column_properties = [
                ('#1', 'ID', 'center', 100),
                ('#2', 'ID Student', 'center', 100),
                ('#3', 'ID Curs', 'center', 100),
                ('#4', 'Data Inscriere', 'center', 150)
            ]

        self.tree["columns"] = columns
        self.tree["show"] = "headings"

        for col_id, col_text, col_anchor, col_width in column_properties:
            self.tree.heading(col_id, text=col_text)
            self.tree.column(col_id, anchor=col_anchor)
            self.tree.column(col_id, width=col_width, stretch=True)

    def show_input_dialog(self, existing_data=None):
        global dropdown_values_student
        dialog = tk.Toplevel(self)
        dialog.title(f'Add {self.db_name.capitalize()}')
        dialog.geometry('800x600')

        label_names = []
        dropdown_values_student = []
        dropdown_values_curs = []

        dropdown_values_student = [str(student.idstudent) + '. ' + student.nume + ' ' + student.prenume for student
                                   in session.query(Student).all()]
        dropdown_values_curs = [str(curs.idcurs) + '. ' + curs.denumire for curs in session.query(Curs).all()]

        if self.db_name == 'studenti':
            label_names = ['Name', 'Prenume', 'CNP', 'An Studiu', 'Facultate']
        elif self.db_name == 'cursuri':
            label_names = ['Denumire', 'An Recomandat', 'Facultate Recomandata', 'Domeniu', 'Semestru']
        elif self.db_name == 'inscrieri':
            label_names = ['Inscrieri']

        entry_vars = []

        for i, label_name in enumerate(label_names):
            label = tk.Label(dialog, text=f'{label_name}:')
            label.pack(pady=5)

            if label_name == 'Data Inscriere':
                entry_var = tk.StringVar()
                entry = DateEntry(dialog, textvariable=entry_var, date_pattern='yyyy-mm-dd')
                entry.pack(pady=5)
            elif label_name == 'Student':
                entry_var = tk.StringVar()
                entry = ttk.Combobox(dialog, textvariable=entry_var, values=dropdown_values_student)
                entry.pack(pady=5)
                if dropdown_values_student:
                    entry.set(dropdown_values_student[0])
            elif label_name == 'Curs':
                entry_var = tk.StringVar()
                entry = ttk.Combobox(dialog, textvariable=entry_var, values=dropdown_values_curs)
                entry.pack(pady=5)
                if dropdown_values_curs:
                    entry.set(dropdown_values_curs[0])
            elif label_name == 'Inscrieri':
                entry_var = tk.StringVar()
                entry = ttk.Combobox(dialog, textvariable=entry_var, values=dropdown_values_student)
                entry.pack(pady=5)
                if dropdown_values_student:
                    entry.set(dropdown_values_student[0])
                entry_var2 = tk.StringVar()
                entry2 = ttk.Combobox(dialog, textvariable=entry_var2, values=dropdown_values_curs)
                entry2.pack(pady=5)

                if dropdown_values_curs:
                    entry2.set(dropdown_values_curs[0])


                entry_var3 = tk.StringVar()
                entry3 = DateEntry(dialog, textvariable=entry_var3, date_pattern='yyyy-mm-dd')
                entry3.pack(pady=5)

                ok_button = ttk.Button(dialog, text='OK', command=lambda: dialog.destroy())
                ok_button.pack(pady=10)

                dialog.wait_window(dialog)

                return [entry_var.get(), entry_var2.get(), entry_var3.get()]
            else:
                entry_var = tk.StringVar()
                entry = tk.Entry(dialog, textvariable=entry_var)
                entry.pack(pady=5)

            entry_vars.append(entry_var)

            if existing_data is not None:
                entry_var.set(existing_data[label_name])

        ok_button = ttk.Button(dialog, text='OK', command=lambda: dialog.destroy())
        ok_button.pack(pady=10)

        dialog.wait_window(dialog)

        return [entry_var.get() for entry_var in entry_vars]

    def create(self):
        data = self.show_input_dialog()
        if data is not None:
            if self.db_name == 'studenti':
                # validate data
                if not data[0].isalpha():
                    messagebox.showerror("Error", "Name must contain only letters")
                    return
                if not data[1].isalpha():
                    messagebox.showerror("Error", "Prenume must contain only letters")
                    return
                if len(data[2]) != 13:
                    messagebox.showerror("Error", "CNP must have 13 characters")
                    return
                if not data[3].isnumeric():
                    messagebox.showerror("Error", "An studiu must be a number")
                    return
                if not data[4].isalpha():
                    messagebox.showerror("Error", "Facultate must contain only letters")
                    return

                nume, prenume, cnp, anstudiu, facultate = data
                new_student = Student(nume=nume, prenume=prenume, cnp=cnp, anstudiu=anstudiu, facultate=facultate)
                session.add(new_student)
                session.commit()
                self.show_data()

            elif self.db_name == 'cursuri':
                # validate data
                if not data[0].isalpha():
                    messagebox.showerror("Error", "Denumire must contain only letters")
                    return
                if not data[1].isnumeric():
                    messagebox.showerror("Error", "An recomandat must be a number")
                    return
                if not data[4].isnumeric():
                    messagebox.showerror("Error", "Semestru must be a number")
                    return

                denumire, anrecomandat, facultaterecomandata, domeniu, semestru = data
                new_curs = Curs(denumire=denumire, anrecomandat=anrecomandat,
                                facultaterecomandata=facultaterecomandata, domeniu=domeniu, semestru=semestru)
                session.add(new_curs)
                session.commit()
                self.show_data()

            elif self.db_name == 'inscrieri':
                data_student= data[0].split('.')[0]
                data_curs=data[1].split('.')[0]
                # validate data
                if not data_student.isnumeric() or not data_curs.isnumeric():
                    messagebox.showerror("Error", "ID Student and ID Curs must be numbers")
                    return
                if session.query(Student).get(data_student) is None:
                    messagebox.showerror("Error", "ID Student does not exist")
                    return
                if session.query(Curs).get(data_curs) is None:
                    messagebox.showerror("Error", "ID Curs does not exist")
                    return
                idstudent, idcurs, data_inscriere = data_student, data_curs,data[2]
                new_inscriere = Inscriere(idstudent=idstudent, idcurs=idcurs, data_inscriere=data_inscriere)
                session.add(new_inscriere)
                session.commit()
                self.show_data()
    def read(self):
        self.show_data()

    def validate_input_data(self, input_data):
        if self.db_name == 'studenti':
            # Validare pentru tabelul 'studenti'
            if not input_data[0].isalpha():
                messagebox.showerror("Error", "Name must contain only letters")
                return False
            if not input_data[1].isalpha():
                messagebox.showerror("Error", "Prenume must contain only letters")
                return False
            if len(input_data[2]) != 13:
                messagebox.showerror("Error", "CNP must have 13 characters")
                return False
            if not input_data[3].isnumeric():
                messagebox.showerror("Error", "An studiu must be a number")
                return False
            if not input_data[4].isalpha():
                messagebox.showerror("Error", "Facultate must contain only letters")
                return False

        elif self.db_name == 'cursuri':
            # Validare pentru tabelul 'cursuri'
            if not input_data[0].isalpha():
                messagebox.showerror("Error", "Denumire must contain only letters")
                return False
            if not input_data[1].isnumeric():
                messagebox.showerror("Error", "An recomandat must be a number")
                return False
            if not input_data[4].isnumeric():
                messagebox.showerror("Error", "Semestru must be a number")
                return False

        elif self.db_name == 'inscrieri':
            # Validare pentru tabelul 'inscrieri'
            if not input_data[0].isnumeric() or not input_data[1].isnumeric():
                messagebox.showerror("Error", "ID Student and ID Curs must be numbers")
                return
            if session.query(Student).get(input_data[0]) is None:
                messagebox.showerror("Error", "ID Student does not exist")
                return
            if session.query(Curs).get(input_data[1]) is None:
                messagebox.showerror("Error", "ID Curs does not exist")
                return
        return True

    def update(self):
        selected_ids = self.get_selected_item_ids()
        if selected_ids:
            # Obține datele existente
            existing_data = self.get_existing_data(selected_ids[0])

            # Afișează dialogul cu datele existente completate
            data = self.show_input_dialog(existing_data)
            print(data)
            if self.db_name == 'inscrieri':
	            data=data[0].split('.')[0],data[1].split('.')[0],data[2]

            if data is not None:
                # Validare date introduse
                if not self.validate_input_data(data):
                    return
                if self.db_name == 'studenti':
                    for item_id in selected_ids:
                        student = session.get(Student, item_id)
                        if student:
                            student.nume, student.prenume, student.cnp, student.anstudiu, student.facultate = data
                            session.commit()
                    self.show_data()

                elif self.db_name == 'cursuri':
                    for item_id in selected_ids:
                        curs = session.query(Curs).get(item_id)
                        if curs:
                            curs.denumire, curs.anrecomandat, curs.facultaterecomandata, curs.domeniu, curs.semestru = data
                            session.commit()
                    self.show_data()

                elif self.db_name == 'inscrieri':
                    print(data, selected_ids)
                    for item_id in selected_ids:
                        print(item_id)
                        inscriere = session.query(Inscriere).get(item_id)
                        if inscriere:
                            inscriere.idstudent, inscriere.idcurs, inscriere.data_inscriere = data
                            session.commit()
                    self.show_data()


    def get_existing_data(self, item_id):
        if self.db_name == 'studenti':
            student = session.query(Student).get(item_id)
            return {'Name': student.nume, 'Prenume': student.prenume, 'CNP': student.cnp,
                    'An Studiu': student.anstudiu, 'Facultate': student.facultate} if student else None
        elif self.db_name == 'cursuri':
            curs = session.query(Curs).get(item_id)
            return {'Denumire': curs.denumire, 'An Recomandat': curs.anrecomandat,
                    'Facultate Recomandata': curs.facultaterecomandata, 'Domeniu': curs.domeniu,
                    'Semestru': curs.semestru} if curs else None
        elif self.db_name == 'inscrieri':
            inscriere = session.query(Inscriere).get(item_id)
            return {'ID Student': inscriere.idstudent, 'ID Curs': inscriere.idcurs,
                    'Data Inscriere': inscriere.data_inscriere} if inscriere else None

    def delete(self):
        selected_ids = self.get_selected_item_ids()
        if selected_ids:
            confirm = messagebox.askyesno("Delete", "Are you sure you want to delete the selected items?")
            if confirm:
                for item_id in selected_ids:
                    if self.db_name == 'studenti':
                        student = session.query(Student).get(item_id)
                        if student:
                            session.delete(student)

                    elif self.db_name == 'cursuri':
                        curs = session.query(Curs).get(item_id)
                        if curs:
                            session.delete(curs)

                    elif self.db_name == 'inscrieri':
                        inscriere = session.query(Inscriere).get(item_id)
                        if inscriere:
                            session.delete(inscriere)

                session.commit()
                self.show_data()

    def get_selected_item_ids(self):
        selected_items = self.tree.selection()
        if selected_items:
            item_ids = [int(self.tree.item(item)['values'][0]) for item in selected_items]
            return item_ids
        return None

    def show_data(self):
        # Clear existing rows
        self.tree.delete(*self.tree.get_children())

        if self.db_name == 'studenti':
            students = session.query(Student).all()
            for student in students:
                self.tree.insert("", 'end', values=(student.idstudent, student.nume, student.prenume, student.cnp,
                                                    student.anstudiu, student.facultate))
        elif self.db_name == 'cursuri':
            cursuri = session.query(Curs).all()
            for curs in cursuri:
                self.tree.insert("", 'end', values=(curs.idcurs, curs.denumire, curs.anrecomandat,
                                                    curs.facultaterecomandata, curs.domeniu, curs.semestru))
        elif self.db_name == 'inscrieri':
            inscrieri = session.query(Inscriere).all()
            for inscriere in inscrieri:
                self.tree.insert("", 'end', values=(inscriere.idinscriere, inscriere.idstudent, inscriere.idcurs,
                                                    inscriere.data_inscriere))


app = CrudApp()
app.mainloop()