import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog, messagebox
import os
import json # Use JSON for storing the context dictionary

class Counter:
    """A simple class to represent a single counter,
    using tkinter's IntVar to automatically update the UI."""
    
    def __init__(self, name="Counter"):
        self.name = name
        # Use an IntVar, a special variable from tkinter
        # that can be linked to UI elements.
        self.value = tk.IntVar()
        self.value.set(0)

    def increment(self):
        """Increase the counter value by 1."""
        self.value.set(self.value.get() + 1)

    def decrement(self):
        """Decrease the counter value by 1."""
        self.value.set(self.value.get() - 1)

    def reset(self):
        """Reset the counter value to 0."""
        self.value.set(0)

    def get_value_var(self):
        """Return the tkinter variable itself, so it can be
        linked to a label's textvariable."""
        return self.value

class CounterApp:
    """Main application class that builds the GUI."""
    
    def __init__(self, root):
        self.root = root
        root.title("Multi-Counter App")
        root.geometry("400x380") # Set initial window size (made it larger)

        # Define the save file
        self.save_file = "counter/counter_data.json"

        # --- New Data Structure ---
        # This dictionary will hold all our contexts
        # e.g., {"Default": [0, 0, 0], "ABC": [10, 5, 3]}
        self.all_contexts_data = {}
        # This string tracks the name of the currently active context
        self.current_context_name = "Default"
        # This string var links to the combobox UI
        self.context_var = tk.StringVar()
        
        # --- Active Counters ---
        # These 3 Counter objects are now our "view"
        # Their values will be loaded from all_contexts_data
        self.active_counters = [
            Counter(name="Counter 1"),
            Counter(name="Counter 2"),
            Counter(name="Counter 3")
        ]

        # Configure styles
        self.style = ttk.Style()
        self.style.configure("TFrame", padding=10)
        self.style.configure("TLabel", padding=5, font=('Helvetica', 12))
        self.style.configure("Header.TLabel", font=('Helvetica', 16, 'bold'))
        self.style.configure("Context.TLabel", font=('Helvetica', 12, 'bold'))
        self.style.configure("TButton", padding=5, font=('Helvetica', 10))
        self.style.configure("Value.TLabel", font=('Helvetica', 14, 'bold'), foreground='#333')

        # Create main frame
        main_frame = ttk.Frame(root, style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # App Title
        title_label = ttk.Label(main_frame, text="Triple Counter", style="Header.TLabel")
        title_label.pack(pady=(0, 10))

        # --- Load all data from file ---
        self.load_all_data()

        # --- New Context UI ---
        context_frame = ttk.Frame(main_frame, style="TFrame")
        context_frame.pack(fill='x', pady=5)
        
        context_label = ttk.Label(context_frame, text="Context:", style="Context.TLabel")
        context_label.pack(side=tk.LEFT, padx=(0, 5))

        # Context Dropdown
        self.context_dropdown = ttk.Combobox(
            context_frame, 
            textvariable=self.context_var, 
            state="readonly", # User can only pick, not type
            width=15
        )
        self.context_dropdown.pack(side=tk.LEFT, expand=True, fill='x')
        self.context_dropdown.bind("<<ComboboxSelected>>", self.on_context_changed)
        
        # Context Buttons Frame
        context_button_frame = ttk.Frame(main_frame, style="TFrame")
        context_button_frame.pack(fill='x', pady=(0, 10))

        self.add_button = ttk.Button(context_button_frame, text="Add New", command=self.add_context)
        self.add_button.pack(side=tk.LEFT, expand=True, padx=2)
        
        self.rename_button = ttk.Button(context_button_frame, text="Rename", command=self.rename_context)
        self.rename_button.pack(side=tk.LEFT, expand=True, padx=2)

        self.delete_button = ttk.Button(context_button_frame, text="Delete", command=self.delete_context)
        self.delete_button.pack(side=tk.LEFT, expand=True, padx=2)
        
        # --- SET UI VALUES AFTER CREATION ---
        self.context_var.set(self.current_context_name)
        self.update_dropdown_values()
        
        # --- Counter UI ---
        # Create the UI for each of the 3 active counters
        for counter in self.active_counters:
            self.create_counter_ui(main_frame, counter)

        # --- Load initial values ---
        self.update_ui_for_context()

        # Add a separator
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=10)

        # Frame for bottom buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')

        # Reset All Button
        reset_all_button = ttk.Button(button_frame, text="Reset All", command=self.reset_all)
        reset_all_button.pack(side=tk.LEFT, expand=True, padx=5)

        # Save Button
        save_button = ttk.Button(button_frame, text="Save Now", command=self.save_all_data)
        save_button.pack(side=tk.LEFT, expand=True, padx=5)
        
        # --- Set save on close ---
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_counter_ui(self, parent_frame, counter):
        """Helper function to create the UI elements for a single counter. (Unchanged)"""
        counter_frame = ttk.Frame(parent_frame, padding=5)
        counter_frame.pack(fill=tk.X)
        name_label = ttk.Label(counter_frame, text=counter.name, style="TLabel")
        name_label.pack(side=tk.LEFT, expand=True)
        dec_button = ttk.Button(counter_frame, text="-", command=counter.decrement, style="TButton")
        dec_button.pack(side=tk.LEFT, padx=5)
        value_label = ttk.Label(
            counter_frame, 
            textvariable=counter.get_value_var(), 
            style="Value.TLabel",
            width=3,
            anchor=tk.CENTER
        )
        value_label.pack(side=tk.LEFT, padx=5)
        inc_button = ttk.Button(counter_frame, text="+", command=counter.increment, style="TButton")
        inc_button.pack(side=tk.LEFT, padx=5)
        reset_button = ttk.Button(counter_frame, text="Reset", command=counter.reset, style="TButton")
        reset_button.pack(side=tk.LEFT, padx=5)

    def load_all_data(self):
        """Loads all contexts from the JSON save file."""
        if not os.path.exists(self.save_file):
            print("Save file not found. Starting with 'Default' context.")
            self.all_contexts_data = {"Default": [0, 0, 0]}
            self.current_context_name = "Default"
        else:
            try:
                with open(self.save_file, 'r') as f:
                    data = json.load(f)
                    self.all_contexts_data = data.get("contexts", {"Default": [0, 0, 0]})
                    self.current_context_name = data.get("__last_active__", "Default")
                    # Ensure last active context actually exists
                    if self.current_context_name not in self.all_contexts_data:
                        self.current_context_name = "Default"
            except (json.JSONDecodeError, Exception) as e:
                print(f"Error reading save file: {e}. Starting with default.")
                self.all_contexts_data = {"Default": [0, 0, 0]}
                self.current_context_name = "Default"

    def save_all_data(self):
        """Saves all contexts to the JSON file."""
        # First, save the current UI values into our data dictionary
        self.save_current_context_to_memory()
        
        data_to_save = {
            "__last_active__": self.current_context_name,
            "contexts": self.all_contexts_data
        }
        
        try:
            with open(self.save_file, 'w') as f:
                json.dump(data_to_save, f, indent=4)
            print("All contexts saved.")
        except IOError as e:
            print(f"Error saving contexts: {e}")

    def save_current_context_to_memory(self):
        """Saves the 3 active counter values into the all_contexts_data dict."""
        current_values = [c.value.get() for c in self.active_counters]
        self.all_contexts_data[self.current_context_name] = current_values
    
    def update_ui_for_context(self):
        """Loads values from all_contexts_data into the 3 active counters."""
        values = self.all_contexts_data.get(self.current_context_name, [0, 0, 0])
        for i, counter in enumerate(self.active_counters):
            counter.value.set(values[i])
            
    def update_dropdown_values(self):
        """Refreshes the list of options in the combobox."""
        self.context_dropdown['values'] = list(self.all_contexts_data.keys())

    def on_context_changed(self, event=None):
        """Fires when the user selects a new context from the dropdown."""
        new_context_name = self.context_var.get()
        if new_context_name == self.current_context_name:
            return # No change
            
        # 1. Save the values from the old context
        self.save_current_context_to_memory()
        
        # 2. Set the new context name
        self.current_context_name = new_context_name
        
        # 3. Load the values for the new context
        self.update_ui_for_context()
        print(f"Switched to context: {self.current_context_name}")

    def add_context(self):
        """Asks user for a new context name and adds it."""
        new_name = simpledialog.askstring("New Context", "Enter new context name:")
        if not new_name:
            return # User cancelled
        
        if new_name in self.all_contexts_data:
            messagebox.showwarning("Error", "A context with this name already exists.")
        else:
            self.all_contexts_data[new_name] = [0, 0, 0] # Add with default values
            self.update_dropdown_values()
            # Automatically switch to the new context
            self.context_var.set(new_name)
            self.on_context_changed()

    def rename_context(self):
        """Renames the currently active context."""
        old_name = self.current_context_name
        if old_name == "Default":
            messagebox.showwarning("Error", "Cannot rename the 'Default' context.")
            return

        new_name = simpledialog.askstring("Rename Context", "Enter new name:", initialvalue=old_name)
        if not new_name or new_name == old_name:
            return # User cancelled or no change
        
        if new_name in self.all_contexts_data:
            messagebox.showwarning("Error", "A context with this name already exists.")
        else:
            # Pop old data, insert with new key
            data = self.all_contexts_data.pop(old_name)
            self.all_contexts_data[new_name] = data
            # Update UI
            self.current_context_name = new_name
            self.context_var.set(new_name)
            self.update_dropdown_values()
            print(f"Renamed '{old_name}' to '{new_name}'.")

    def delete_context(self):
        """Deletes the currently active context."""
        name_to_delete = self.current_context_name
        if name_to_delete == "Default":
            messagebox.showwarning("Error", "Cannot delete the 'Default' context.")
            return
        
        if messagebox.askyesno("Delete Context", f"Are you sure you want to delete '{name_to_delete}'? This cannot be undone."):
            self.all_contexts_data.pop(name_to_delete)
            # Switch to 'Default' context
            self.context_var.set("Default")
            self.on_context_changed()
            self.update_dropdown_values()
            print(f"Deleted context: {name_to_delete}")

    def reset_all(self):
        """Resets all counters in the *current* context to 0."""
        for counter in self.active_counters:
            counter.reset()

    def on_closing(self):
        """Called when the user closes the window."""
        print("Saving all contexts on close...")
        self.save_all_data()
        self.root.destroy() # This actually closes the window

def main():
    # Standard setup for a tkinter application
    root = tk.Tk()
    app = CounterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()