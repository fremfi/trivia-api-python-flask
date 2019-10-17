import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            "question": "How many rings does the Lakers have?",
            "answer": "Five",
            "difficulty": 1,
            "category": "6"
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/api/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_get_questions(self):
        res = self.client().get('/api/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    def test_404_sent_requesting_beyond_valid_questions_page(self):
        res = self.client().get('/api/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    def test_delete_question(self):
        res = self.client().delete('/api/questions/4')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 4).one_or_none()

        self.assertEqual(data['success'], True)
        self.assertEqual(question, None)

    def test_404_sent_if_question_being_deleted_does_not_exist(self):
        res = self.client().delete('/api/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    def test_create_question(self):
        res = self.client().post('/api/questions', json=self.new_question)
        data = json.loads(res.data)

        question = Question.query.filter(Question.question == "How many rings does the Lakers have?").first()

        self.assertEqual(res.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertEqual(data['question']['question'], self.new_question['question'])

    def test_400_sent_if_posted_question_isnt_formatted_correctly(self):
        res = self.client().post('/api/questions', json={
            "answer": "Five",
            "difficulty": "1",
            "category": "6"
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "bad request")

    def test_search_for_question(self):
        res = self.client().post('/api/questions', json={"searchTerm": "world cup"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 2)
        self.assertTrue(len(data['questions']))

    def test_get_questions_by_category(self):
        res = self.client().get('/api/categories/3/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 3)
        self.assertEqual(len(data['questions']), 3)
        self.assertEqual(data['current_category'], 3)

    def test_404_sent_requesting_questions_with_none_existent_category(self):
        res = self.client().get('/api/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    def test_get_quiz_next_question(self):
        res = self.client().post('/api/quizzes', json={
            "previous_questions": [],
            "quiz_category": {
                "type": "ALL",
                "id": 0
            }
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_404_sent_requesting_quiz_next_question_if_doesnt_exist(self):
        res = self.client().post('/api/quizzes', json={
            "previous_questions": [5, 9, 12, 23],
            "quiz_category": {
                "type": "Sports",
                "id": 4
            }
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()