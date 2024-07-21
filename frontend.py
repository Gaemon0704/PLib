from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from PIL import ImageTk, Image
import os
import backend
import ttkbootstrap as ttk
from ttkbootstrap.constants import*

# Function to handle the "Add Image" button click event
selected_image = None

def add_image():
    global selected_image
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
    if file_path:
        selected_image = Image.open(file_path)
        # Resize the image to fit in the preview area
        selected_image = selected_image.resize((100, 160), Image.LANCZOS)
        # Create a Tkinter PhotoImage from the selected image
        image_preview = ImageTk.PhotoImage(selected_image)
        # Update the image preview label
        label_image.configure(image=image_preview)
        label_image.image = image_preview

def get_selected_rows():
    selected_rows = []
    for index in tree.selection():
        values = tree.item(index)["values"]
        selected_rows.append(values[0])
    return selected_rows

def get_selected_row(event):
    try:
        global selected_tuple
        index = tree.focus()
        selected_tuple = tree.item(index)["values"]
        e1.delete(0, END)
        e1.insert(END, selected_tuple[1])
        e2.delete(0, END)
        e2.insert(END, selected_tuple[2])
        e3.delete(0, END)
        e3.insert(END, selected_tuple[3])
        e4.delete(0, END)
        e4.insert(END, selected_tuple[4])
        e5.delete(0, END)
        e5.insert(END, selected_tuple[5])

        book_id = selected_tuple[0]  # Get the id from row
        # Fetch the availability from the database based on the ID
        availability = backend.get_availability(book_id)
        # Check the availability value and set checkbox accordingly
        if availability == "Available":
            availability_var.set("Available")
        else:
            availability_var.set("Unavailable")
        
        # Enables update and delete buttons
        b4.configure(state="enabled")
        b5.configure(state="enabled")
        
        # Display the corresponding image
        selected_image_id = selected_tuple[0]
        image_path = os.path.join("images", str(selected_image_id) + ".png")
        if os.path.exists(image_path):
            selected_image = Image.open(image_path)
            # Resize the image to fit in the preview area
            selected_image = selected_image.resize((100, 160), Image.LANCZOS)
            # Create a Tkinter PhotoImage from the selected image
            image_preview = ImageTk.PhotoImage(selected_image)
            # Update the image preview label
            label_image.configure(image=image_preview)
            label_image.image = image_preview
        else:
            # If the image doesn't exist, clear the label_image
            label_image.configure(image="")
            label_image.image = None
    except IndexError:
        pass


def view_command():
    tree.delete(*tree.get_children())
    clear_command()
    rows = backend.view()
    for row in rows:
        book_id = row[0]  # Get the ID from the row
        # Fetch the availability from the database based on the ID
        availability = backend.get_availability(book_id)
        # Check the availability value and set the font color accordingly
        if availability == "Available":
            tree.insert("", END, values=row, tags=("available",))
        else:
            tree.insert("", END, values=row, tags=("unavailable",))

    # Reset the heading text for all columns
    for col in sort_order:
        sort_order[col] = ""
        tree.heading(col, text=col)    
    

def search_command():
    tree.delete(*tree.get_children())
    rows = backend.search(title_text.get(), author_text.get(), year_text.get(), isbn_text.get(), genre_text.get())
    for row in rows:
        book_id = row[0]  # Get the ID from the row
        # Fetch the availability from the database based on the ID
        availability = backend.get_availability(book_id)
        # Check the availability value and set the font color accordingly
        if availability == "Available":
            tree.insert("", END, values=row, tags=("available",))
        else:
            tree.insert("", END, values=row, tags=("unavailable",))

def add_command():
    backend.insert(title_text.get(), author_text.get(), year_text.get(), isbn_text.get(), genre_text.get(), availability_var.get())
        # Get the ID of the last inserted row
    rows = backend.view()
    last_row = rows[-1]
    last_row_id = last_row[0]

    # Set the image file name as the ID of the current entry
    image_file_name = str(last_row_id) + ".png"

    # Check if an image is selected
    if selected_image:
        # Check if the folder exists, create it if it doesn't
        if not os.path.exists("images"):
            os.makedirs("images")

        # Save the image file in the folder
        image_path = os.path.join("images", image_file_name)
        selected_image.save(image_path)
        messagebox.showinfo("Success", "Entry added and image saved.")
    else:
        messagebox.showinfo("Success", "Entry added.")
        
    view_command()
    

def delete_command():
    selected_rows = get_selected_rows()
    delprompt = messagebox.askokcancel("Confirmation", "Deleting will delete all selected entries.")
    if delprompt is True:
        messagebox.showinfo("Success", "Deleted successfully.")
        for row_id in selected_rows:
            # Get the ID of the row to be deleted
            row_id = int(row_id)
            # Delete the corresponding image file
            image_file_name = str(row_id) + ".png"
            image_path = os.path.join("images", image_file_name)
            if os.path.exists(image_path):
                os.remove(image_path)
            # Delete the row from the database
            backend.delete(row_id)
            b5.configure(state="disabled")
    view_command()

def update_command():
    selected_rows = get_selected_rows()
    if len(selected_rows) != 1:
        messagebox.showwarning("Warning", "Please select a single row to update.")
        return

    selected_row_id = selected_rows[0]
    backend.update(selected_row_id, title_text.get(), author_text.get(), year_text.get(), isbn_text.get(), genre_text.get(), availability_var.get())

    # Update the image file if an image is selected
    if selected_image:
        image_file_name = str(selected_row_id) + ".png"
        image_path = os.path.join("images", image_file_name)
        if os.path.exists(image_path):
            os.remove(image_path)  # Remove the existing image file

        # Save the new image file in the folder
        selected_image.save(image_path)
        messagebox.showinfo("Success", "Entry updated and image replaced.")
    else:
        messagebox.showinfo("Success", "Entry updated.")
    b4.configure(state="disabled")
    view_command()

def sort_column(column):
    current_sort = sort_order.get(column, "")
    new_sort = ""
    if current_sort == "":
        new_sort = "asc"
    elif current_sort == "asc":
        new_sort = "desc"
    elif current_sort == "desc":
        new_sort = "asc"
    sort_order[column] = new_sort
    sort_text = column

    # Reset the heading text for all columns
    for col, text in sort_order.items():
        if col != column:
            sort_order[col] = ""
            tree.heading(col, text=col)
        else:
            if text == "asc":
                sort_text += " ▲"
            elif text == "desc":
                sort_text += " ▼"

    # Sort all rows in the tree
    rows = tree.get_children("")
    sorted_rows = sorted(rows, key=lambda x: tree.set(x, column).lower(), reverse=(new_sort == "desc"))
    for index, row in enumerate(sorted_rows):
        tree.move(row, "", index)

    # Update the heading text with the new sort order and indicator
    tree.heading(column, text=sort_text)

def clear_command():
    e1.delete(0, END)
    e2.delete(0, END)
    e3.delete(0, END)
    e4.delete(0, END)
    e5.delete(0, END)
    availability_var.set("Unavailable")
    b5.configure(state="disabled")
    b4.configure(state="disabled")

    global selected_image
    selected_image = None
    label_image.configure(image=None)
    label_image.image = None

def input_check():
    if e1.get() or e2.get() or e3.get() or e4.get() or e5.get():
        b3.configure(state="normal")
    else:
        b3.configure(state="disabled")
    window.after(100, input_check)


window = ttk.Window(themename="newtheme")
window.wm_title("Book Library Management")
window.minsize(716, 446)

# Frames
image_frame = ttk.Frame(window, width=105, height=165)
image_frame.grid(row=1, column=0, columnspan=4, rowspan=4, padx=(20, 10), pady=5, sticky="w")

# Labels
label_image = ttk.Label(window)
label_image.grid(row=1, column=0, columnspan=4, rowspan=4, padx=(20,10), pady=5, sticky="w")

l1 = ttk.Label(window, text="Title")
l1.grid(row=0, column=0, padx=10, pady=5, sticky="e")

l2 = ttk.Label(window, text="Author")
l2.grid(row=1, column=0, padx=10, pady=5, sticky="e")

l3 = ttk.Label(window, text="Year")
l3.grid(row=2, column=0, padx=10, pady=5, sticky="e")

l4 = ttk.Label(window, text="ISBN")
l4.grid(row=3, column=0, padx=10, pady=5, sticky="e")

l5 = ttk.Label(window, text="Genre")
l5.grid(row=4, column=0, padx=10, pady=5, sticky="e")


# Input fields
title_text = StringVar()
e1 = ttk.Entry(window, textvariable=title_text)
e1.grid(row=0, column=1, padx=10, pady=5, sticky="we")

author_text = StringVar()
e2 = ttk.Entry(window, textvariable=author_text)
e2.grid(row=1, column=1, padx=10, pady=5, sticky="we")

year_text = StringVar()
e3 = ttk.Entry(window, textvariable=year_text)
e3.grid(row=2, column=1, padx=10, pady=5, sticky="we")

isbn_text = StringVar()
e4 = ttk.Entry(window, textvariable=isbn_text)
e4.grid(row=3, column=1, padx=10, pady=5, sticky="we")

genre_text = StringVar()  
e5 = ttk.Entry(window, textvariable=genre_text)  
e5.grid(row=4, column=1, padx=10, pady=5, sticky="we")


# Buttons
b1 = ttk.Button(window, bootstyle="info", text="View all", width=14, command=view_command)
b2 = ttk.Button(window, text="Search entry", width=14, command=search_command)
b3 = ttk.Button(window, text="Add entry", width=14, command=add_command)
b4 = ttk.Button(window, bootstyle="secondary", state="disabled", text="Update selected", width=14, command=update_command)
b5 = ttk.Button(window, bootstyle="danger", state="disabled", text="Delete selected", width=14, command=delete_command)
add_image_button = ttk.Button(window, bootstyle="success", text="Add Image", width=12, command=add_image)


b1.grid(row=0, column=2, padx=10, pady=5)
b2.grid(row=1, column=2, padx=10, pady=5)
b3.grid(row=2, column=2, padx=10, pady=5)
b4.grid(row=3, column=2, padx=10, pady=5)
b5.grid(row=4, column=2, padx=10, pady=5)
add_image_button.grid(row=5, column=0, padx=(20,10), pady=5, sticky="w")
input_check()

# Treeview table
tree = ttk.Treeview(window, columns=("ID", "Title", "Author", "Year", "ISBN", "Genre"), show="headings", selectmode="extended")
tree.heading("ID", text="ID", anchor="center", command=lambda: sort_column("ID"))
tree.heading("Title", text="Title", anchor="center", command=lambda: sort_column("Title"))
tree.heading("Author", text="Author", anchor="center", command=lambda: sort_column("Author"))
tree.heading("Year", text="Year", anchor="center", command=lambda: sort_column("Year"))
tree.heading("ISBN", text="ISBN", anchor="center", command=lambda: sort_column("ISBN"))
tree.heading("Genre", text="Genre", anchor="center", command=lambda: sort_column("Genre"))
tree.column("ID", width=30, anchor="center")
tree.column("Title", width=150, anchor="center")
tree.column("Author", width=150, anchor="center")
tree.column("Year", width=80, anchor="center")
tree.column("ISBN", width=120, anchor="center")
tree.column("Genre", width=150, anchor="center")
tree.tag_configure("available", foreground="#017e50")  # Set the font color for available rows to green
tree.tag_configure("unavailable", foreground="#ff4646")  # Set the font color for unavailable rows to red
tree.grid(row=6, column=0, columnspan=3, padx=10, pady=5, sticky="nsew")

# Center-align all values inside the treeview table
for column in ("ID", "Title", "Author", "Year", "ISBN", "Genre"):
    tree.heading(column, anchor="center")
    tree.column(column, anchor="center")

sb1 = ttk.Scrollbar(window, orient="vertical", command=tree.yview)
sb1.grid(row=6, column=3, sticky="ns")
tree.configure(yscrollcommand=sb1.set)

tree.bind("<<TreeviewSelect>>", get_selected_row)

# Dictionary to keep track of the sort order for each column
sort_order = {"ID": "", "Title": "", "Author": "", "Year": "", "ISBN": "", "Genre": ""}

# Clear button
clear_button = ttk.Button(window, bootstyle="warning", text="Clear", width=12, command=clear_command)
clear_button.grid(row=5, column=1, padx=10, pady=5, sticky="w")

# Availability checkbox
availability_var = StringVar(value="Available")
availability_checkbox = ttk.Checkbutton(window,bootstyle="success", text="Available", variable=availability_var, onvalue="Available", offvalue="Unavailable")
availability_checkbox.grid(row=5, column=2, padx=10, pady=5, sticky="w")

# Configure resizing behavior
window.grid_rowconfigure(6, weight=1)
window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(1, weight=1)
window.grid_columnconfigure(2, weight=1)

# Initial view of all entries
view_command()

window.mainloop()
