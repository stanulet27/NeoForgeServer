import sys
import test_simulator as sim
import database_handler as dbms
import dummy_database as dummy
from flask import Flask, request, jsonify
from flask_cors import CORS
class App:
    def __init__(self,  standalone: bool = False):
        if not standalone:
            self.db = dbms.DBMS()
        else:
            self.db = dummy.DBMS()
        self.app = Flask(__name__)
        self.sim: sim.SimulationHandler = None
        self.env_options = None
        CORS(self.app)
        self.setup_routes()

    def setup_routes(self):

        @self.app.route('/material', methods=['GET'])
        def get_material():
            #return selected material
            print("Request received to get material. Selected material ID: ", self.env_options['MaterialID'])
            return jsonify(self.sim.return_material()) 
            
        @self.app.route('/hammer', methods=['GET'])
        def get_hammer():
            #return selected hammer
            print("Request received to get hammer. Selected hammer ID: ", self.env_options['HammerID'])
            return jsonify(self.db.get_hammer(self.env_options['HammerID']))

        @self.app.route('/starting-mesh', methods=['GET'])
        def get_mesh():
            #return selected starting mesh
            print("Request received to get starting mesh. Selected mesh ID: ", self.env_options['StartMeshID'])
            return jsonify(self.db.get_start_mesh(self.env_options['StartMeshID']))

        @self.app.route('/target-mesh', methods=['GET'])
        def get_target_mesh():
            #return selected target mesh
            print("Request received to get target mesh. Selected mesh ID: ", self.env_options['EndMeshID'])
            return jsonify(self.db.get_target_mesh(self.env_options['EndMeshID']))

        @self.app.route('/get-options', methods=['GET'])
        def get_options():
            #return all available options
            return jsonify({})

        @self.app.route('/init', methods=['PUT'])
        def setup():
            print("Request received to setup simulation")
            self.env_options = request.json
            #select starting mesh
            mesh = self.db.get_start_mesh(request.json["StartMeshID"])
            #select material
            material = self.db.get_material(request.json['MaterialID'])
            #initialize simulation
            self.sim = sim.SimulationHandler(mesh, material)
            #start new series
            self.db.start_series(request.json['StartMeshID'],
                                request.json['EndMeshID'], 
                                request.json['MaterialID'], 
                                request.json['HammerID'])
            return jsonify({"Status": "Success"})
        
        @self.app.route('/post-score', methods=['PUT'])
        def post_score():
            print("Request received to post score")
            self.db.end_series(request.json['Score'])
            return jsonify({"Status": "Success"})

        @self.app.route('/undo-strike', methods=['GET'])
        def undo_strike():
            print("Request received to undo last strike") 
            mesh = self.db.undo_strike()
            self.sim.set_mesh(mesh)
            return jsonify(mesh)

        @self.app.route('/press', methods=['PUT'])
        def execute_simulation():
            quaternion = request.json['Rotation']
            translation_vector = request.json['Position']
            force = request.json['DeformationAmount']
            hits = request.json['TopVertices']
            print(f"Request received to execute simulation with force {force}")
            #execute simulation
            result  = self.sim.execute_simulation(hits, force, quaternion, translation_vector)
            #record action
            final_mesh = self.sim.get_result_mesh()
            self.db.record_action(translation_vector, quaternion, final_mesh)
            return jsonify(result)

    def run(self, host='127.0.0.1', port=5000):
        self.app.run(host=host, port=port)


if __name__ == '__main__':
    standalone = False
    if len(sys.argv) > 1 and sys.argv[1] == '-s':
        standalone = True
    app = App(standalone=standalone)
    app.run()
