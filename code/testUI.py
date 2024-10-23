import tkinter as tk


# File for a test UI
def submit_query():
    query = query_entry.get()
    key = key_entry.get()
    # Execute query and decryption


root = tk.Tk()
root.title("Query Interface")

query_entry = tk.Entry(root)
query_entry.pack()
key_entry = tk.Entry(root)
key_entry.pack()

submit_button = tk.Button(root, text="Submit", command=submit_query)
submit_button.pack()

root.mainloop()
