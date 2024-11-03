#!/usr/bin/env python3

# author : Cheshami@gmail.com

import tkinter as tk
from tkinter import simpledialog, messagebox
import json

class TreeNode:
    def __init__(self, id, data, parent=None):
        self.id = id
        self.data = data
        self.parent = parent
        self.left = None
        self.right = None

class BinaryTree:
    def __init__(self):
        self.root = None
        self.nodes = {}
        self.next_id = 0

    def insert(self, data, parent_id=None):
        new_node = TreeNode(self.next_id, data)
        self.nodes[self.next_id] = new_node
        self.next_id += 1

        if parent_id is None:
            if self.root is None:
                self.root = new_node
            else:
                return False  # Root already exists
        else:
            if parent_id in self.nodes:
                parent_node = self.nodes[parent_id]
                if parent_node.left is None:
                    parent_node.left = new_node
                elif parent_node.right is None:
                    parent_node.right = new_node
                else:
                    return False  # Parent has two children
                new_node.parent = parent_node
            else:
                return False  # Parent not found
        return True

    def to_dict(self):
        def node_to_dict(node):
            if node is None:
                return None
            return {
                'id': node.id,
                'data': node.data,
                'left': node_to_dict(node.left),
                'right': node_to_dict(node.right)
            }
        return node_to_dict(self.root)

    def from_dict(self, data):
        if data is None:
            return None
        node = TreeNode(data['id'], data['data'])
        node.left = self.from_dict(data['left'])
        node.right = self.from_dict(data['right'])
        return node

    def save_to_file(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f)

    def load_from_file(self, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
            self.root = self.from_dict(data)
            self.nodes = {node.id: node for node in self._flatten_tree(self.root)}
            self.next_id = max(self.nodes.keys()) + 1 if self.nodes else 0

    def _flatten_tree(self, node):
        if node is None:
            return []
        return [node] + self._flatten_tree(node.left) + self._flatten_tree(node.right)
    
    def search_by_name(self, name):
        def search_node(node):
            if node is None:
                return None
            if node.data['name'] == name:
                return node
            left_result = search_node(node.left)
            if left_result:
                return left_result
            return search_node(node.right)

        return search_node(self.root)

class App:
    def __init__(self, master):
        self.master = master
        self.tree = BinaryTree()
        self.is_saved = True  # Track if the tree is saved
        self.canvas = tk.Canvas(master, width=1000, height=800)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.menu = tk.Menu(master)
        master.config(menu=self.menu)
        self.file_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New Tree", command=self.create_new_tree)
        self.file_menu.add_command(label="Save", command=self.save_tree)
        self.file_menu.add_command(label="Load", command=self.load_tree)
        self.file_menu.add_command(label="Search", command=self.search_node)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.on_exit)

        master.protocol("WM_DELETE_WINDOW", self.on_exit)

    def on_canvas_click(self, event):
        clicked_node = self.get_clicked_node(event.x, event.y)
        if clicked_node:
            self.show_node_info(clicked_node)

    def get_clicked_node(self, x, y):
        for node in self.tree.nodes.values():
            if abs(node.x - x) < 30 and abs(node.y - y) < 30:
                return node
        return None

    def show_node_info(self, node):
        # Create a new window for editing and adding child
        self.edit_add_window(node)

    def edit_add_window(self, node):
        window = tk.Toplevel(self.master)
        window.title("Edit/Add Node")

        tk.Label(window, text=f"Node ID: {node.id}").pack()
        tk.Label(window, text=f"Name: {node.data['name']}").pack()
        tk.Label(window, text=f"Wallet Number: {node.data['wallet_number']}").pack()

        edit_button = tk.Button(window, text="Edit Node", command=lambda: self.edit_node(node, window))
        edit_button.pack()

        add_child_button = tk.Button(window, text="Add Child Node", command=lambda: self.add_child(node, window))
        add_child_button.pack()

        close_button = tk.Button(window, text="Close", command=window.destroy)
        close_button.pack()

    def edit_node(self, node, window):
        name = simpledialog.askstring("Edit Name", "Enter new name:", initialvalue=node.data['name'])
        wallet_number = simpledialog.askstring("Edit Wallet Number", "Enter new wallet number:", initialvalue=node.data['wallet_number'])

        if name and wallet_number:
            node.data = {
                'name': name,
                'wallet_number': wallet_number,
                'position': node.data['position'],
                'parent': node.data['parent']
            }

        self.draw_tree()
        self.is_saved = False  # Mark tree as unsaved
        window.destroy()

    def add_child(self, parent_node, window):
        position = 'L'
        name = simpledialog.askstring("Input", "Enter name:")
        wallet_number = simpledialog.askstring("Input", "Enter wallet number:")

        data = {
            'name': name,
            'wallet_number': wallet_number,
            'position': position,
            'parent': parent_node.id
        }

        if position == 'L':
            if not self.tree.insert(data, parent_node.id):
                position = 'R'
        elif position == 'R':
            if not self.tree.insert(data, parent_node.id):
                messagebox.showwarning("Warning", "Cannot add right child.")

        self.draw_tree()
        self.is_saved = False  # Mark tree as unsaved
        window.destroy()
    
    def create_new_tree(self):
        if self.tree.root is not None:
            messagebox.showwarning("Warning", "Tree already exists. Please load a new tree.")
            return

        name = simpledialog.askstring("Input", "Enter name:")
        wallet_number = simpledialog.askstring("Input", "Enter wallet number:")

        data = {
            'name': name,
            'wallet_number': wallet_number,
            'position': 'root',
            'parent': None
        }
        self.tree.insert(data)
        self.draw_tree()
        self.is_saved = False  # Mark tree as unsaved

    def save_tree(self):
        filename = simpledialog.askstring("Save Tree", "Enter filename:")
        if filename:
            self.tree.save_to_file(filename)
            self.is_saved = True  # Mark tree as saved

    def load_tree(self):
        filename = simpledialog.askstring("Load Tree", "Enter filename:")
        if filename:
            self.tree.load_from_file(filename)
            self.draw_tree()
            self.is_saved = True  # Mark tree as saved
    
    def search_node(self):
        name = simpledialog.askstring("Search Node", "Enter the name to search:")
        if name:
            result_node = self.tree.search_by_name(name)
            if result_node:
                messagebox.showinfo("Search Result", f"Node found: ID={result_node.id}, Name={result_node.data['name']}, Wallet Number={result_node.data['wallet_number']}")
            else:
                messagebox.showinfo("Search Result", "Node not found.")

    def on_exit(self):
        if not self.is_saved:
            if messagebox.askyesno("Exit", "The tree is unsaved. Do you want to save it before exiting?"):
                self.save_tree()
        self.master.destroy()

    def draw_tree(self):
        self.canvas.delete("all")
        self._draw_node(self.tree.root, 500, 20, 200)

    def _draw_node(self, node, x, y, offset):
        if node is not None:
            node.x, node.y = x, y  # Store coordinates for click detection
            self.canvas.create_text(x, y, text=f"{node.id}")
            if node.left:
                self.canvas.create_line(x, y + 10, x - offset, y + 50)
                self._draw_node(node.left, x - offset, y + 60, offset // 2)
            if node.right:
                self.canvas.create_line(x, y + 10, x + offset, y + 50)
                self._draw_node(node.right, x + offset, y + 60, offset // 2)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Network")
    app = App(root)
    root.mainloop()
