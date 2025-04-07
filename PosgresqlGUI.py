import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional, Dict, List
from PostgresqlManager import PostgreSQLManager
class PostgreSQLGUI:
    """
    Interface graphique pour le gestionnaire de base de données PostgreSQL.
    """
    
    def __init__(self, root: tk.Tk):
        """
        Initialise l'interface graphique.
        
        :param root: Fenêtre principale Tkinter
        """
        self.root = root
        self.root.title("Gestionnaire PostgreSQL")
        self.root.geometry("1000x700")
        
        # Gestionnaire de base de données
        self.db_manager: Optional[PostgreSQLManager] = None
        
        # Variables d'état
        self.connected = False
        self.current_table = ""
        
        # Création de l'interface
        self.create_connection_frame()
        self.create_table_frame()
        self.create_query_frame()
        self.create_results_frame()
        
        # Désactiver les widgets tant qu'on n'est pas connecté
        self.toggle_widgets_state()
    
    def create_connection_frame(self) -> None:
        """
        Crée le cadre pour les paramètres de connexion.
        """
        frame = ttk.LabelFrame(self.root, text="Connexion à PostgreSQL", padding=10)
        frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # Champs de connexion
        ttk.Label(frame, text="Base de données:").grid(row=0, column=0, sticky="e")
        self.db_entry = ttk.Entry(frame)
        self.db_entry.grid(row=0, column=1, sticky="ew", padx=5)
        
        ttk.Label(frame, text="Utilisateur:").grid(row=1, column=0, sticky="e")
        self.user_entry = ttk.Entry(frame)
        self.user_entry.grid(row=1, column=1, sticky="ew", padx=5)
        
        ttk.Label(frame, text="Mot de passe:").grid(row=2, column=0, sticky="e")
        self.pwd_entry = ttk.Entry(frame, show="*")
        self.pwd_entry.grid(row=2, column=1, sticky="ew", padx=5)
        
        ttk.Label(frame, text="Hôte:").grid(row=0, column=2, sticky="e", padx=(10,0))
        self.host_entry = ttk.Entry(frame)
        self.host_entry.insert(0, "localhost")
        self.host_entry.grid(row=0, column=3, sticky="ew", padx=5)
        
        ttk.Label(frame, text="Port:").grid(row=1, column=2, sticky="e", padx=(10,0))
        self.port_entry = ttk.Entry(frame)
        self.port_entry.insert(0, "5432")
        self.port_entry.grid(row=1, column=3, sticky="ew", padx=5)
        
        # Boutons de connexion/déconnexion
        self.connect_btn = ttk.Button(frame, text="Connexion", command=self.connect_db)
        self.connect_btn.grid(row=2, column=3, sticky="e", padx=5)
        
        # Configurer le redimensionnement
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(3, weight=1)
    
    def create_table_frame(self) -> None:
        """
        Crée le cadre pour la gestion des tables.
        """
        frame = ttk.LabelFrame(self.root, text="Gestion des Tables", padding=10)
        frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Liste des tables
        ttk.Label(frame, text="Tables disponibles:").grid(row=0, column=0, sticky="w")
        self.tables_listbox = tk.Listbox(frame, height=10)
        self.tables_listbox.grid(row=1, column=0, sticky="nsew", pady=5)
        self.tables_listbox.bind("<<ListboxSelect>>", self.on_table_select)
        
        # Boutons pour les tables
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, sticky="ew")
        
        self.refresh_tables_btn = ttk.Button(btn_frame, text="Actualiser", command=self.refresh_tables_list)
        self.refresh_tables_btn.pack(side="left", padx=2)
        
        self.create_table_btn = ttk.Button(btn_frame, text="Créer", command=self.show_create_table_dialog)
        self.create_table_btn.pack(side="left", padx=2)
        
        self.drop_table_btn = ttk.Button(btn_frame, text="Supprimer", command=self.drop_table)
        self.drop_table_btn.pack(side="left", padx=2)
        
        # Structure de la table sélectionnée
        ttk.Label(frame, text="Structure de la table:").grid(row=3, column=0, sticky="w", pady=(10,0))
        self.table_structure_tree = ttk.Treeview(frame, columns=("type", "nullable"), show="headings", height=5)
        self.table_structure_tree.heading("#0", text="Colonne")
        self.table_structure_tree.heading("type", text="Type")
        self.table_structure_tree.heading("nullable", text="Nullable")
        self.table_structure_tree.grid(row=4, column=0, sticky="nsew", pady=5)
        
        # Configurer le redimensionnement
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        frame.rowconfigure(4, weight=1)
    
    def create_query_frame(self) -> None:
        """
        Crée le cadre pour l'exécution de requêtes SQL.
        """
        frame = ttk.LabelFrame(self.root, text="Requête SQL", padding=10)
        frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=5)
        
        # Éditeur de requête
        self.query_editor = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=60, height=10)
        self.query_editor.grid(row=0, column=0, sticky="nsew", pady=5)
        
        # Boutons d'exécution
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=1, column=0, sticky="ew")
        
        self.execute_query_btn = ttk.Button(btn_frame, text="Exécuter", command=self.execute_query)
        self.execute_query_btn.pack(side="left", padx=2)
        
        self.clear_query_btn = ttk.Button(btn_frame, text="Effacer", command=self.clear_query)
        self.clear_query_btn.pack(side="left", padx=2)
        
        # Boutons CRUD rapides
        crud_frame = ttk.Frame(frame)
        crud_frame.grid(row=2, column=0, sticky="ew", pady=(10,0))
        
        ttk.Button(crud_frame, text="SELECT * FROM", command=lambda: self.insert_query_prefix("SELECT * FROM ")).pack(side="left", padx=2)
        ttk.Button(crud_frame, text="INSERT INTO", command=lambda: self.insert_query_prefix("INSERT INTO ")).pack(side="left", padx=2)
        ttk.Button(crud_frame, text="UPDATE", command=lambda: self.insert_query_prefix("UPDATE ")).pack(side="left", padx=2)
        ttk.Button(crud_frame, text="DELETE FROM", command=lambda: self.insert_query_prefix("DELETE FROM ")).pack(side="left", padx=2)
        
        # Configurer le redimensionnement
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
    
    def create_results_frame(self) -> None:
        """
        Crée le cadre pour afficher les résultats des requêtes.
        """
        frame = ttk.LabelFrame(self.root, text="Résultats", padding=10)
        frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
        
        # Treeview pour afficher les résultats sous forme de tableau
        self.results_tree = ttk.Treeview(frame)
        self.results_tree.grid(row=0, column=0, sticky="nsew")
        
        # Barre de défilement
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.results_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        # Zone de texte pour les messages (nombre de lignes affectées, etc.)
        self.message_text = tk.Text(frame, height=3, state="disabled")
        self.message_text.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5,0))
        
        # Configurer le redimensionnement
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=1)
    
    def toggle_widgets_state(self) -> None:
        """
        Active ou désactive les widgets en fonction de l'état de connexion.
        """
        state = "normal" if self.connected else "disabled"
        
        # Widgets à activer/désactiver
        widgets = [
            self.refresh_tables_btn,
            self.create_table_btn,
            self.drop_table_btn,
            self.execute_query_btn,
            self.clear_query_btn,
            self.query_editor
        ]
        
        for widget in widgets:
            widget.config(state=state)
        
        # Bouton de connexion/déconnexion
        self.connect_btn.config(
            text="Déconnexion" if self.connected else "Connexion",
            command=self.disconnect_db if self.connected else self.connect_db
        )
    
    def connect_db(self) -> None:
        """
        Établit une connexion à la base de données.
        """
        try:
            dbname = self.db_entry.get()
            user = self.user_entry.get()
            password = self.pwd_entry.get()
            host = self.host_entry.get()
            port = self.port_entry.get()
            
            if not all([dbname, user, password]):
                messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires")
                return
            
            self.db_manager = PostgreSQLManager(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port
            )
            self.db_manager.connect()
            self.connected = True
            self.toggle_widgets_state()
            self.refresh_tables_list()
            self.show_message("Connexion réussie!")
        except Exception as e:
            messagebox.showerror("Erreur de connexion", f"Impossible de se connecter: {str(e)}")
    
    def disconnect_db(self) -> None:
        """
        Ferme la connexion à la base de données.
        """
        if self.db_manager:
            self.db_manager.disconnect()
            self.connected = False
            self.toggle_widgets_state()
            self.tables_listbox.delete(0, tk.END)
            self.clear_results()
            self.show_message("Déconnecté de la base de données.")
        self.db_manager = None
    
    def refresh_tables_list(self) -> None:
        """
        Actualise la liste des tables dans la base de données.
        """
        if not self.db_manager or not self.connected:
            return
        
        try:
            self.tables_listbox.delete(0, tk.END)
            tables = self.db_manager.execute_query(
                "SELECT table_name FROM information_schema.tables WHERE table_schema='public'",
                fetch=True
            )
            for table in tables:
                self.tables_listbox.insert(tk.END, table['table_name'])
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de récupérer les tables: {str(e)}")
    
    def on_table_select(self, event: tk.Event) -> None:
        """
        Gère la sélection d'une table dans la liste.
        """
        if not self.tables_listbox.curselection():
            return
        
        self.current_table = self.tables_listbox.get(self.tables_listbox.curselection())
        self.show_table_structure()
    
    def show_table_structure(self) -> None:
        """
        Affiche la structure de la table sélectionnée.
        """
        if not self.current_table or not self.db_manager:
            return
        
        try:
            # Effacer l'arborescence actuelle
            for item in self.table_structure_tree.get_children():
                self.table_structure_tree.delete(item)
            
            # Récupérer les colonnes de la table
            columns = self.db_manager.get_table_columns(self.current_table)
            
            # Récupérer les détails des colonnes
            query = """
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = %s;
            """
            result = self.db_manager.execute_query(query, (self.current_table,), fetch=True)
            
            # Ajouter les colonnes à l'arborescence
            for row in result:
                self.table_structure_tree.insert("", "end", text=row['column_name'], 
                                              values=(row['data_type'], row['is_nullable']))
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de récupérer la structure de la table: {str(e)}")
    
    def show_create_table_dialog(self) -> None:
        """
        Affiche une boîte de dialogue pour créer une nouvelle table.
        """
        dialog = tk.Toplevel(self.root)
        dialog.title("Créer une nouvelle table")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Nom de la table:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        table_name_entry = ttk.Entry(dialog)
        table_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Cadre pour les colonnes
        columns_frame = ttk.LabelFrame(dialog, text="Colonnes", padding=10)
        columns_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        
        # En-têtes
        ttk.Label(columns_frame, text="Nom").grid(row=0, column=0, padx=5, pady=2)
        ttk.Label(columns_frame, text="Type").grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(columns_frame, text="Nullable").grid(row=0, column=2, padx=5, pady=2)
        
        # Liste des colonnes
        columns_entries = []
        
        def add_column_row() -> None:
            row = len(columns_entries)
            
            # Nom de la colonne
            name_entry = ttk.Entry(columns_frame)
            name_entry.grid(row=row+1, column=0, padx=5, pady=2, sticky="ew")
            
            # Type de la colonne
            type_combobox = ttk.Combobox(columns_frame, values=[
                "SERIAL", "INTEGER", "BIGINT", "VARCHAR(255)", "TEXT", 
                "BOOLEAN", "DATE", "TIMESTAMP", "NUMERIC", "FLOAT"
            ])
            type_combobox.grid(row=row+1, column=1, padx=5, pady=2, sticky="ew")
            type_combobox.set("VARCHAR(255)")
            
            # Nullable
            nullable_var = tk.BooleanVar(value=True)
            nullable_check = ttk.Checkbutton(columns_frame, variable=nullable_var)
            nullable_check.grid(row=row+1, column=2, padx=5, pady=2)
            
            columns_entries.append({
                "name": name_entry,
                "type": type_combobox,
                "nullable": nullable_var
            })
        
        # Bouton pour ajouter des colonnes
        add_col_btn = ttk.Button(columns_frame, text="+ Ajouter une colonne", command=add_column_row)
        add_col_btn.grid(row=100, column=0, columnspan=3, pady=5)
        
        # Ajouter une première colonne par défaut
        add_column_row()
        
        # Boutons de la boîte de dialogue
        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=5)
        
        def create_table() -> None:
            table_name = table_name_entry.get()
            if not table_name:
                messagebox.showerror("Erreur", "Veuillez spécifier un nom de table")
                return
            
            columns_spec = {}
            for col in columns_entries:
                col_name = col["name"].get()
                col_type = col["type"].get()
                
                if not col_name or not col_type:
                    continue  # Ignorer les colonnes vides
                
                # Ajouter NOT NULL si la colonne n'est pas nullable
                if not col["nullable"].get():
                    col_type += " NOT NULL"
                
                columns_spec[col_name] = col_type
            
            if not columns_spec:
                messagebox.showerror("Erreur", "Veuillez ajouter au moins une colonne valide")
                return
            
            try:
                self.db_manager.create_table(table_name, columns_spec)
                self.refresh_tables_list()
                dialog.destroy()
                self.show_message(f"Table '{table_name}' créée avec succès!")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de créer la table: {str(e)}")
        
        ttk.Button(btn_frame, text="Créer", command=create_table).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Annuler", command=dialog.destroy).pack(side="left", padx=5)
        
        # Configurer le redimensionnement
        dialog.columnconfigure(1, weight=1)
        columns_frame.columnconfigure(0, weight=1)
        columns_frame.columnconfigure(1, weight=1)
    
    def drop_table(self) -> None:
        """
        Supprime la table sélectionnée.
        """
        if not self.current_table:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner une table")
            return
        
        if not messagebox.askyesno("Confirmation", f"Êtes-vous sûr de vouloir supprimer la table '{self.current_table}'?"):
            return
        
        try:
            self.db_manager.drop_table(self.current_table)
            self.refresh_tables_list()
            self.current_table = ""
            self.show_message(f"Table '{self.current_table}' supprimée avec succès!")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de supprimer la table: {str(e)}")
    
    def execute_query(self) -> None:
        """
        Exécute la requête SQL saisie dans l'éditeur.
        """
        if not self.db_manager or not self.connected:
            return
        
        query = self.query_editor.get("1.0", tk.END).strip()
        if not query:
            messagebox.showwarning("Avertissement", "Veuillez saisir une requête SQL")
            return
        
        try:
            # Détecter le type de requête
            query_type = query.split()[0].upper()
            
            if query_type in ("SELECT", "SHOW", "DESCRIBE", "EXPLAIN"):
                # Requête qui retourne des résultats
                result = self.db_manager.execute_query(query, fetch=True)
                self.display_results(result)
                self.show_message(f"{len(result)} ligne(s) retournée(s)")
            else:
                # Requête de modification (INSERT, UPDATE, DELETE, etc.)
                affected = self.db_manager.execute_query(query)
                self.clear_results()
                self.show_message(f"Requête exécutée avec succès. {affected} ligne(s) affectée(s)" if affected else "Requête exécutée avec succès.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'exécution de la requête: {str(e)}")
    
    def display_results(self, results: List[Dict]) -> None:
        """
        Affiche les résultats d'une requête dans le Treeview.
        
        :param results: Liste de dictionnaires représentant les résultats
        """
        self.clear_results()
        
        if not results:
            self.show_message("Aucun résultat à afficher")
            return
        
        # Configurer les colonnes du Treeview
        columns = list(results[0].keys())
        self.results_tree["columns"] = columns
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=100, anchor="w")
        
        # Ajouter les données
        for row in results:
            self.results_tree.insert("", "end", values=[row[col] for col in columns])
    
    def clear_results(self) -> None:
        """
        Efface les résultats affichés.
        """
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.results_tree["columns"] = []
    
    def clear_query(self) -> None:
        """
        Efface le contenu de l'éditeur de requête.
        """
        self.query_editor.delete("1.0", tk.END)
    
    def insert_query_prefix(self, prefix: str) -> None:
        """
        Insère un préfixe de requête dans l'éditeur.
        
        :param prefix: Préfixe à insérer
        """
        self.query_editor.insert(tk.END, prefix)
        if self.current_table and prefix in ("SELECT * FROM ", "INSERT INTO ", "DELETE FROM "):
            self.query_editor.insert(tk.END, self.current_table + " ")
        elif self.current_table and prefix == "UPDATE ":
            self.query_editor.insert(tk.END, self.current_table + " SET ")
    
    def show_message(self, message: str) -> None:
        """
        Affiche un message dans la zone de messages.
        
        :param message: Message à afficher
        """
        self.message_text.config(state="normal")
        self.message_text.delete("1.0", tk.END)
        self.message_text.insert("1.0", message)
        self.message_text.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = PostgreSQLGUI(root)
    root.mainloop()