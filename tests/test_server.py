import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Mock unified_planning if not present
try:
    import unified_planning
except ImportError:
    mock_up = MagicMock()
    sys.modules["unified_planning"] = mock_up
    sys.modules["unified_planning.model"] = MagicMock()
    sys.modules["unified_planning.plans"] = MagicMock()
    sys.modules["unified_planning.engines"] = MagicMock()
    sys.modules["unified_planning.grpc"] = MagicMock()
    sys.modules["unified_planning.grpc.proto_writer"] = MagicMock()

try:
    import zmq
except ImportError:
    mock_zmq = MagicMock()
    sys.modules["zmq"] = mock_zmq

from unified_planning.model import Problem, UserType, Object
from unified_planning.plans import PlanGenerationResult, Plan

# Adjust path to import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from request_handlers import RequestHandler
from server import PdSimUnityServer

class TestRequestHandler(unittest.TestCase):
    def setUp(self):
        # Mock the server and its dependencies
        self.mock_server = MagicMock()
        # Mock PdSimProblem (not the UP Problem directly anymore)
        self.mock_server.problem = MagicMock()
        
        # Ensure up_problem is accessible for replan tests
        self.mock_server.problem.up_problem = MagicMock()
        
        self.mock_server.plan_result = MagicMock()
        
        self.handler = RequestHandler(self.mock_server)

    def test_handle_ping(self):
        response = self.handler.handle_ping({})
        self.assertEqual(response, {'status': 'OK'})

    def test_handle_new_object_success(self):
        data = {'name': 'obj2', 'type': 'item'}
        response = self.handler.handle_new_object(data)
        self.assertEqual(response['status'], 'OK')
        # Check if add_object was called on the wrapper
        self.mock_server.problem.add_object.assert_called_with('obj2', 'item')

    def test_handle_new_object_missing_data(self):
        data = {'name': 'obj2'}
        response = self.handler.handle_new_object(data)
        self.assertIn('error', response)

    def test_handle_new_object_existing(self):
        # Configure mock to raise exception when add_object is called
        self.mock_server.problem.add_object.side_effect = ValueError("Object obj1 already exists")
        
        data = {'name': 'obj1', 'type': 'item'}
        response = self.handler.handle_new_object(data)
        self.assertIn('error', response)
        self.assertIn('already exists', response['error'])

    def test_handle_new_object_invalid_type(self):
        # Configure mock to raise exception
        self.mock_server.problem.add_object.side_effect = ValueError("Type unknown_type not found")
        
        data = {'name': 'obj3', 'type': 'unknown_type'}
        response = self.handler.handle_new_object(data)
        self.assertIn('error', response)
        self.assertIn('Type unknown_type not found', response['error'])

    def test_handle_replan_success(self):
        self.mock_server.planner_name = "test_planner"
        self.mock_server.solve_callback = MagicMock()
        
        # Mock result
        mock_result = MagicMock()
        mock_result.plan = MagicMock() # Truty
        self.mock_server.solve_callback.return_value = mock_result
        
        response = self.handler.handle_replan({})
        
        # Expect call with the UNDERLYING up_problem
        self.mock_server.solve_callback.assert_called_with(self.mock_server.problem.up_problem, "test_planner")
        self.assertEqual(self.mock_server.plan_result, mock_result)
        self.assertEqual(response['status'], 'OK')

    def test_handle_replan_failure(self):
        self.mock_server.planner_name = "test_planner"
        self.mock_server.solve_callback = MagicMock()
        
        # Mock result with no plan
        mock_result = MagicMock()
        mock_result.plan = None # Falsy
        self.mock_server.solve_callback.return_value = mock_result
        
        response = self.handler.handle_replan({})
        
        self.assertEqual(response['status'], 'FAILED')

if __name__ == '__main__':
    unittest.main()
