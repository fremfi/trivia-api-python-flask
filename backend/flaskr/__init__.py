#! /usr/bin/env python3
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.sql.expression import func
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                              'Content-Type, Authorization')
        return response

    @app.route('/api/categories', methods=['GET'])
    def get_categories():
        """
        get_categories: fetches all categories for the trivia questions
        Args:
            None
        Returns:
            return an array of categories
        """
        categories = Category.query.all()
        formatted_categories = [category.format() for category in categories]
        return jsonify({
          "success": True,
          "categories": formatted_categories
        })

    @app.route('/api/questions', methods=['GET'])
    def get_questions():
        """
        get_questions: fetches available questions for trivia
        Args:
            page (data type: int)
        Returns:
            returns an array questions
        """
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = Question.query.all()
        if len(questions) - page * QUESTIONS_PER_PAGE < 0:
            abort(404)
        formatted_questions = [question.format() for question in questions]
        categories = Category.query.all()
        formatted_categories = [category.format() for category in categories]

        return jsonify({
          "success": True,
          "questions": formatted_questions[start:end],
          "total_questions": len(questions),
          "categories": formatted_categories,
          "current_category": ""
        })

    @app.route('/api/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        """
        delete_question: deletes a question by id
        Args:
            question_id (data type: int)
        Returns:
            returns success if question is deleted
        """
        question = Question.query.get_or_404(question_id)
        question.delete()
        return jsonify({
          "success": True,
        })

    @app.route('/api/questions', methods=['POST'])
    def create_or_search_question():
        """
        create_or_search_question: creates or searches for trivia questions
        Args:
            searchTerm (data type: str)
            question (data type: str)
            answer (data type: str)
            category (data type: str)
            difficulty (data type: int)
        Returns:
            returns the question that was created or searched for
        """
        # TODO: data validation and better messages
        body = request.get_json()
        search_term = body.get('searchTerm', None)
        question = body.get('question', None)
        answer = body.get('answer', None)
        category = body.get('category', None)
        difficulty = body.get('difficulty', None)

        if search_term:
            if not isinstance(search_term, str):
                abort(404)
            questions = (Question.query.filter(Question.question.ilike(f'%{search_term}%')).all())
            formatted_questions = [question.format() for question in questions]
            return jsonify({
              "success": True,
              "questions": formatted_questions,
              "total_questions": len(questions),
              "current_category": ""
            })

        if not question or not answer or not category or not difficulty:
            abort(400)

        try:
            question = Question(
              question=question,
              answer=answer,
              category=category,
              difficulty=difficulty
            )
            question.insert()
            return jsonify({
              "success": True,
              "question": question.format()
            }), 201
        except ValueError:
            abort(422)

    @app.route('/api/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        """
        get_questions_by_category: fetches trivia questions by category
        Args:
            category_id (data type: int)
        Returns:
            returns an array of questions by category
        """
        questions = Question.query.filter(Question.category == category_id).all()
        formatted_questions = [question.format() for question in questions]

        if not len(questions):
            abort(404)

        return jsonify({
          "success": True,
          "questions": formatted_questions,
          "total_questions": len(formatted_questions),
          "current_category": category_id
        })

    @app.route('/api/quizzes', methods=['POST'])
    def get_quiz_next_question():
        """
        get_quiz_next_question: fetches the next random trivia question in a quiz
        Args:
            previous_questions (data type: list): list of previous question ids
            quiz_category (data type: obj): category type and id
        Returns:
            returns the next random trivia question
        """
        body = request.get_json()
        previous_questions = body.get('previous_questions', None)
        quiz_category = body.get('quiz_category', None)

        if previous_questions is None or quiz_category is None:
            abort(400)

        try:
            quiz_category_id = int(quiz_category["id"])
        except (KeyError, ValueError):
            abort(400)

        if not isinstance(previous_questions, list) and all(isinstance(previous_question, int) for previous_question in previous_questions):
            abort(400)

        if len(previous_questions) > 0:
            if quiz_category_id is 0:  # query all categories
                next_question = Question.query.filter(~Question.id.in_(previous_questions)).order_by(func.random()).first_or_404()
            else:
                next_question = Question.query.filter(Question.category == quiz_category_id, ~Question.id.in_(previous_questions)).order_by(func.random()).first_or_404()
        else:
            if quiz_category_id is 0:  # query all categories
                next_question = Question.query.order_by(func.random()).first_or_404()
            else:
                next_question = Question.query.filter(Question.category == quiz_category_id).order_by(func.random()).first_or_404()

        return jsonify({
          "success": True,
          "question": next_question.format()
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
          "success": False,
          "error": 404,
          "message": "resource not found"
        }), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
          "success": False,
          "error": 400,
          "message": "bad request"
        }), 400

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
          "success": False,
          "error": 422,
          "message": "unprocessable"
        }), 422

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
          "success": False,
          "error": 405,
          "message": "method not allowed"
        }), 405
    return app
