import psycopg2
from psycopg2.extras import Json
import part_material as p
import hammer as h
import random
from config import load_config


class DBMS:
    def __init__(self):
        # Connect to the PostgreSQL database server 
        config = load_config()
        try:
            with psycopg2.connect(**config) as conn:
                print('Connected to the PostgreSQL server.')
                self.conn = conn
        except (psycopg2.DatabaseError, Exception) as error:
            print(error)

    def __del__(self):
        self.conn.close()
        print('Database connection closed.')

    def get_material(self, material_id: int) -> p.Material:
        # Get material data from the database
        query = f"SELECT * FROM materials WHERE id = {material_id}"
        with self.conn.cursor() as cur:
            cur.execute(query)
            material = cur.fetchone()
            material_object = p.Material(material[1], material[2])
            return material_object

    def get_start_mesh(self, mesh_id:int ) -> 'dict[str,object]':
        # Get mesh data from the database 
        query = f"SELECT mesh_definition FROM starting_meshes WHERE id = {mesh_id}"
        with self.conn.cursor() as cur:
            cur.execute(query)
            mesh = cur.fetchone()
            return mesh[0]
        
    def get_target_mesh(self, mesh_id: int) -> 'dict[str,object]':
        # Get mesh data from the database 
        query = f"SELECT mesh_definition FROM target_meshes WHERE id = {mesh_id}"
        with self.conn.cursor() as cur:
            cur.execute(query)
            mesh = cur.fetchone()
            return mesh[0]

    def get_hammer(self, hammer_id: int) -> 'dict[str,object]':
        # Get hammer data from the database 
        query = f"SELECT * FROM hammers WHERE id = {hammer_id}"
        with self.conn.cursor() as cur:
            cur.execute(query)
            hammer = cur.fetchone()
            hammer_object = h.Hammer(hammer[1], hammer[2], hammer[3])
            return hammer_object.get_dict()
        
    def record_action(self, position: 'list[int]', rotation: 'list[int]', result: 'dict[str,object]') -> bool:
        # Record an action in the 
        self.current_step += 1 # Increment step counter
        query = f"INSERT INTO strike (position, rotation, result, step_number, series_id)\
            VALUES (array{position}, array{rotation}, {Json(result)}, {self.current_step}, {self.current_series})"
        with self.conn.cursor() as cur:
            cur.execute(query)
            return True
        
    def start_series(self, start_mesh_id: int, target_mesh_id: int, material_id: int, hammer_id: int) -> bool:
        # Record the start of a series in the database 
        self.current_series = random.randint(1,10000000) # Generate uuid for the new series
        self.current_step = 0 # Reset step counter
        query = f"INSERT INTO part_series (id, start_mesh_id, target_mesh_id, material_id, hammer_id) VALUES \
            ({self.current_series},{start_mesh_id}, {target_mesh_id}, {material_id}, {hammer_id})"
        with self.conn.cursor() as cur:
            cur.execute(query)
            return True
        
    def end_series(self, score: float) -> bool:
        # Record the end of a series in the database 
        query = f"UPDATE part_series SET score = {score} WHERE id = {self.current_series}"
        with self.conn.cursor() as cur:
            cur.execute(query)
            self.conn.commit() # Only commit after the series is complete
            return True
    def undo_strike(self):
        # Undo the last strike in the database
        query = f"DELETE FROM strike WHERE series_id = {self.current_series} AND step_number = {self.current_step}"
        with self.conn.cursor() as cur:
            cur.execute(query)
        #return mesh from before the last strike
        self.current_step -= 1
        if self.current_step ==0:
            query = f"SELECT mesh_definition FROM starting_meshes WHERE id = (SELECT start_mesh_id FROM part_series WHERE id = {self.current_series})"
        else:
            query = f"SELECT result FROM strike WHERE series_id = {self.current_series} AND step_number = {self.current_step}"
        with self.conn.cursor() as cur:
            cur.execute(query)
            mesh = cur.fetchone()
            return mesh[0]

    
