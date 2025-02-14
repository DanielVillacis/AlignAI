import unittest
import os
import sys
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_testing import TestCase
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from app import app, db, Client

class ClientModelTests(TestCase):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_alignai.db'
    TESTING = True

    def create_app(self):
        app.config.from_object(self)
        return app
    
    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create_client(self):
        # Arrange
        client = Client(
            first_name="John",
            last_name="Doe",
            age=25,
            gender="Male",
            telephone="1234567890",
            email="test@test.com",
            reason="Test reason",
            previous_conditions="None"
        )

        # Act
        db.session.add(client)
        db.session.commit()

        # Assert
        self.assertEqual(client.first_name, "John")
        self.assertEqual(client.last_name, "Doe")
        self.assertEqual(client.age, 25)
        self.assertEqual(client.gender, "Male")
        self.assertEqual(client.telephone, "1234567890")
        self.assertEqual(client.email, "test@test.com")
        self.assertEqual(client.reason, "Test reason")
        self.assertEqual(client.previous_conditions, "None")


    def test_get_clients(self):
        # Arrange
        client = Client(
            first_name="John",
            last_name="Doe",
            age=30,
            gender="Male",
            telephone="1234567890",
            email="john.doe@example.com",
            reason="Test reason",
            previous_conditions="None"
        )

        # Act
        db.session.add(client)
        db.session.commit()
        response = self.client.get('/api/clients')

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)


    def test_update_client(self):
        # Arrange
        client = Client(
            first_name="John",
            last_name="Doe",
            age=30,
            gender="Male",
            telephone="1234567890",
            email="john.doe@example.com",
            reason="Test reason",
            previous_conditions="None"
        )

        # Act
        db.session.add(client)
        db.session.commit()
        response = self.client.put(f'/api/clients/{client.id}', json={
            'first_name': 'Jane',
            'last_name': 'Doe',
            'age': 28,
            'gender': 'Female',
            'telephone': '0987654321',
            'email': 'jane.doe@example.com',
            'reason': 'Updated reason',
            'previous_conditions': 'Updated conditions'
        })

        # Assert
        self.assertEqual(response.status_code, 200)
        updated_client = db.session.get(Client, client.id)
        self.assertEqual(updated_client.first_name, 'Jane')


    def test_delete_client(self):
        # Arrange
        client = Client(
            first_name="John",
            last_name="Doe",
            age=30,
            gender="Male",
            telephone="1234567890",
            email="john.doe@example.com",
            reason="Test reason",
            previous_conditions="None"
        )

        # Act
        db.session.add(client)
        db.session.commit()
        response = self.client.delete(f'/api/clients/{client.id}')

        # Assert
        self.assertEqual(response.status_code, 200)
        remaining_clients = db.session.query(Client).count()
        self.assertEqual(remaining_clients, 0)



if __name__ == '__main__':
    unittest.main()
