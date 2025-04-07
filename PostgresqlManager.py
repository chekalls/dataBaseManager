import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor
from typing import List, Dict, Union, Optional, Any

class PostgreSQLManager:
    """
    Gestionnaire de base de données PostgreSQL qui fournit des méthodes pour:
    - Se connecter/déconnecter
    - Exécuter des requêtes
    - Gérer les transactions
    - Créer/supprimer des tables
    - Insérer/mettre à jour/supprimer des données
    """
    
    def __init__(self, dbname: str, user: str, password: str, host: str = 'localhost', port: int = 5432):
        """
        Initialise le gestionnaire avec les paramètres de connexion.
        
        :param dbname: Nom de la base de données
        :param user: Nom d'utilisateur
        :param password: Mot de passe
        :param host: Hôte (par défaut 'localhost')
        :param port: Port (par défaut 5432)
        """
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None
        self.cursor = None
    
    def connect(self) -> None:
        """Établit une connexion à la base de données PostgreSQL."""
        try:
            self.connection = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            # Utilisation d'un curseur qui retourne des dictionnaires
            self.cursor = self.connection.cursor(cursor_factory=DictCursor)
            print("Connexion à PostgreSQL établie avec succès.")
        except Exception as e:
            print(f"Erreur lors de la connexion à PostgreSQL: {e}")
            raise
    
    def disconnect(self) -> None:
        """Ferme la connexion à la base de données."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("Connexion à PostgreSQL fermée.")
    
    def execute_query(self, query: str, params: Optional[tuple] = None, fetch: bool = False) -> Optional[List[Dict]]:
        """
        Exécute une requête SQL et retourne éventuellement les résultats.
        
        :param query: Requête SQL à exécuter
        :param params: Paramètres pour la requête (optionnel)
        :param fetch: Si True, retourne les résultats (pour SELECT)
        :return: Résultats de la requête ou None
        """
        try:
            self.cursor.execute(query, params)
            if fetch:
                return [dict(row) for row in self.cursor.fetchall()]
            self.connection.commit()
            return None
        except Exception as e:
            self.connection.rollback()
            print(f"Erreur lors de l'exécution de la requête: {e}")
            raise
    
    def create_table(self, table_name: str, columns: Dict[str, str], if_not_exists: bool = True) -> None:
        """
        Crée une nouvelle table dans la base de données.
        
        :param table_name: Nom de la table
        :param columns: Dictionnaire des colonnes (nom: type)
        :param if_not_exists: Si True, ajoute la clause IF NOT EXISTS
        """
        if_not_exists_clause = "IF NOT EXISTS" if if_not_exists else ""
        columns_def = ", ".join([f"{col_name} {col_type}" for col_name, col_type in columns.items()])
        
        query = f"CREATE TABLE {if_not_exists_clause} {table_name} ({columns_def});"
        self.execute_query(query)
        print(f"Table '{table_name}' créée avec succès.")
    
    def drop_table(self, table_name: str, if_exists: bool = True) -> None:
        """
        Supprime une table de la base de données.
        
        :param table_name: Nom de la table
        :param if_exists: Si True, ajoute la clause IF EXISTS
        """
        if_exists_clause = "IF EXISTS" if if_exists else ""
        query = f"DROP TABLE {if_exists_clause} {table_name};"
        self.execute_query(query)
        print(f"Table '{table_name}' supprimée avec succès.")
    
    def insert_data(self, table_name: str, data: Dict[str, Any]) -> None:
        """
        Insère des données dans une table.
        
        :param table_name: Nom de la table
        :param data: Dictionnaire des données à insérer (colonne: valeur)
        """
        columns = data.keys()
        values = [data[col] for col in columns]
        
        query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            sql.Identifier(table_name),
            sql.SQL(', ').join(map(sql.Identifier, columns)),
            sql.SQL(', ').join(sql.Placeholder() * len(values))
        )
        
        self.execute_query(query, tuple(values))
        print(f"Données insérées dans '{table_name}' avec succès.")
    
    def update_data(self, table_name: str, data: Dict[str, Any], condition: str, condition_params: Optional[tuple] = None) -> None:
        """
        Met à jour des données dans une table.
        
        :param table_name: Nom de la table
        :param data: Dictionnaire des données à mettre à jour (colonne: nouvelle valeur)
        :param condition: Condition WHERE pour la mise à jour
        :param condition_params: Paramètres pour la condition (optionnel)
        """
        set_clause = ", ".join([f"{col} = %s" for col in data.keys()])
        values = tuple(data.values())
        
        if condition_params:
            values += condition_params
        
        query = f"UPDATE {table_name} SET {set_clause} WHERE {condition};"
        self.execute_query(query, values)
        print(f"Données mises à jour dans '{table_name}' avec succès.")
    
    def delete_data(self, table_name: str, condition: str, condition_params: Optional[tuple] = None) -> None:
        """
        Supprime des données d'une table.
        
        :param table_name: Nom de la table
        :param condition: Condition WHERE pour la suppression
        :param condition_params: Paramètres pour la condition (optionnel)
        """
        query = f"DELETE FROM {table_name} WHERE {condition};"
        self.execute_query(query, condition_params)
        print(f"Données supprimées de '{table_name}' avec succès.")
    
    def select_data(self, table_name: str, columns: List[str] = ["*"], condition: Optional[str] = None, condition_params: Optional[tuple] = None) -> List[Dict]:
        """
        Récupère des données d'une table.
        
        :param table_name: Nom de la table
        :param columns: Liste des colonnes à récupérer (par défaut toutes)
        :param condition: Condition WHERE (optionnelle)
        :param condition_params: Paramètres pour la condition (optionnel)
        :return: Liste des lignes sous forme de dictionnaires
        """
        cols = ", ".join(columns)
        query = f"SELECT {cols} FROM {table_name}"
        
        if condition:
            query += f" WHERE {condition}"
        
        query += ";"
        
        return self.execute_query(query, condition_params, fetch=True)
    
    def begin_transaction(self) -> None:
        """Commence une transaction."""
        self.execute_query("BEGIN;")
    
    def commit_transaction(self) -> None:
        """Valide la transaction en cours."""
        self.execute_query("COMMIT;")
    
    def rollback_transaction(self) -> None:
        """Annule la transaction en cours."""
        self.execute_query("ROLLBACK;")
    
    def table_exists(self, table_name: str) -> bool:
        """
        Vérifie si une table existe dans la base de données.
        
        :param table_name: Nom de la table à vérifier
        :return: True si la table existe, False sinon
        """
        query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = %s
        );
        """
        result = self.execute_query(query, (table_name,), fetch=True)
        return result[0]['exists'] if result else False
    
    def get_table_columns(self, table_name: str) -> List[str]:
        """
        Récupère la liste des colonnes d'une table.
        
        :param table_name: Nom de la table
        :return: Liste des noms de colonnes
        """
        query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = %s;
        """
        result = self.execute_query(query, (table_name,), fetch=True)
        return [row['column_name'] for row in result] if result else []


# Exemple d'utilisation
if __name__ == "__main__":
    # Configuration de la connexion (à adapter)
    db_config = {
        "dbname": "ma_base_de_donnees",
        "user": "mon_utilisateur",
        "password": "mon_mot_de_passe",
        "host": "localhost",
        "port": 5432
    }
    
    # Initialisation du gestionnaire
    db_manager = PostgreSQLManager(**db_config)
    
    try:
        # Connexion
        db_manager.connect()
        
        # Création d'une table (si elle n'existe pas)
        if not db_manager.table_exists("clients"):
            db_manager.create_table(
                table_name="clients",
                columns={
                    "id": "SERIAL PRIMARY KEY",
                    "nom": "VARCHAR(100) NOT NULL",
                    "email": "VARCHAR(100) UNIQUE",
                    "date_inscription": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
                }
            )
        
        # Insertion de données
        db_manager.insert_data(
            table_name="clients",
            data={
                "nom": "Jean Dupont",
                "email": "jean.dupont@example.com"
            }
        )
        
        # Sélection de données
        clients = db_manager.select_data("clients")
        print("Clients:", clients)
        
        # Mise à jour de données
        db_manager.update_data(
            table_name="clients",
            data={"nom": "Jean DUPONT"},
            condition="email = %s",
            condition_params=("jean.dupont@example.com",)
        )
        
        # Suppression de données
        # db_manager.delete_data(
        #     table_name="clients",
        #     condition="id = %s",
        #     condition_params=(1,)
        # )
        
    except Exception as e:
        print(f"Une erreur est survenue: {e}")
    finally:
        # Déconnexion
        db_manager.disconnect()