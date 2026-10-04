## 🤖 Natural Language to SQL AI

AI-Assisted Database Query System

Convert natural language questions into SQL queries and execute them directly against a MySQL database using a local Large Language Model (LLM).

Instead of manually writing SQL queries, users can simply ask questions such as:

“Who is the highest paid employee?”

The system retrieves the relevant database schema, generates a MySQL query using an LLM, validates the generated SQL for safety, executes it against the database, and displays the results.


## 🚀 Overview

Natural Language to SQL AI is an AI-assisted database querying system designed to make relational databases accessible through natural language.

The system combines:

* 🧠 Local LLM for SQL generation
* 🔎 Schema Retrieval for relevant database context
* 🛡️ SQL Validation for safer query execution
* 🗄️ MySQL for database operations
* 🐍 Python as the application layer
* 🦙 Ollama for running the local LLM

The overall workflow is:

User Question
      ↓
Schema Retrieval
      ↓
Relevant Database Schema
      ↓
Local LLM
      ↓
SQL Query Generation
      ↓
SQL Validation
      ↓
MySQL Database
      ↓
Query Results


## ✨ Features

🗣️ Natural Language Queries

Ask questions about the database using normal English instead of writing SQL manually.

Example:

How many employees are there?

The system generates:

SELECT COUNT(*) AS employee_count
FROM employees;


🔎 Schema-Aware SQL Generation

The system does not blindly send the entire database structure to the LLM.

A schema retrieval layer identifies tables relevant to the user’s question and provides only the required schema information to the model.

For example:

"Show employees with the highest salaries"

can retrieve the employees table schema before generating the SQL query.

This helps reduce irrelevant context and improves SQL generation accuracy.


## 🧠 Local LLM

SQL generation is performed using a local model through Ollama.

Current model:

mohamedelawakey/sql_coder

Using a local model allows the system to perform SQL generation without sending database information to an external API.


## 🛡️ SQL Validation

Generated SQL is passed through a validation layer before execution.

The system verifies whether the generated query is acceptable before allowing it to reach the database.

If a query fails validation:

Query rejected for safety.

This provides an additional layer of protection between the LLM and the database.


🗄️ MySQL Integration

The application connects directly to a MySQL database and executes validated queries.

The database layer is separated into database.py, keeping database connection logic independent from the AI generation pipeline.

## 🏗️ Project Architecture

                    ┌─────────────────────┐
                    │      User Query     │
                    │ "Who earns most?"   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Schema Retriever   │
                    │                     │
                    │ Finds relevant      │
                    │ database tables     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Local LLM        │
                    │      Ollama         │
                    │                     │
                    │ SQL Generation      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   SQL Validator     │
                    │                     │
                    │ Validate generated  │
                    │ SQL before execution│
                    └──────────┬──────────┘
                               │
                         Valid Query
                               │
                               ▼
                    ┌─────────────────────┐
                    │    MySQL Database   │
                    │                     │
                    │ Execute SQL Query   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Query Results    │
                    └─────────────────────┘


## 📁 Project Structure

natural-language-to-sql-ai/
│
├── app.py
├── database.py
├── schema.py
├── schema_retriever.py
├── sql_validator.py
├── README.md
└── .gitignore

app.py

Main application logic.

Responsibilities include:

* Accepting user questions
* Retrieving relevant schema
* Creating the LLM prompt
* Generating SQL
* Validating SQL
* Executing the query
* Displaying results

The application uses Ollama’s chat interface to generate the SQL query. (GitHub)

database.py

Handles the MySQL database connection and database-related operations.

The application obtains a connection through:

get_connection()

and uses it to execute the generated SQL query. (GitHub)


schema.py

Contains the database schema information used by the retrieval system.

The schema acts as the context provided to the LLM during SQL generation. (GitHub)


schema_retriever.py

Identifies which database tables are relevant to a user’s question.

For example, questions containing terms such as:

employee
salary
manager

can retrieve the employees table.

Similarly, questions about departments, jobs, locations, countries, regions, or job history retrieve their corresponding schemas. (GitHub)


sql_validator.py

Validates generated SQL before it is executed against the database.

This acts as a safety layer between the LLM and MySQL. (GitHub)


## 🛠️ Tech Stack

Technology	Purpose
Python	Application logic
MySQL	Relational database
Ollama	Local LLM runtime
SQL Coder LLM	Natural Language → SQL
RAG / Schema Retrieval	Relevant schema selection
SQL Validation	Query safety
Git & GitHub	Version control

⚙️ Requirements

Before running the project, make sure you have:

* Python 3.9+
* MySQL Server
* Ollama
* A configured MySQL database
* The required Python dependencies

## 🗄️ Database Configuration

Configure your MySQL database connection in database.py.

Example:

import mysql.connector
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="your_username",
        password="your_password",
        database="your_database"
    )

Do not commit your actual database password to GitHub.

For production use, environment variables should be used instead.

## 🔐 Security Considerations

LLMs can sometimes generate incorrect or unsafe SQL. This project therefore introduces a validation layer before executing generated queries.

The intended execution flow is:

LLM Generated SQL
       ↓
SQL Validator
       ↓
   Valid?
   /    \
 Yes     No
  ↓       ↓
MySQL   Reject

Additional production-level improvements could include:

* Read-only database users
* Parameterized queries
* Query timeouts
* SQL parser-based validation
* Table/column allowlists
* Rate limiting
* Query logging
* Row limits
* Role-based database access

## 🧠 How the RAG Component Works

Traditional Text-to-SQL systems may provide the LLM with the complete database schema.

That becomes inefficient as the database grows.

This project uses a lightweight schema retrieval approach:

User Question
      ↓
Identify relevant keywords
      ↓
Select relevant tables
      ↓
Retrieve their schema
      ↓
Send schema + question to LLM
      ↓
Generate SQL

For example:

Question:
"What is the average salary of employees in each department?"

The retriever identifies concepts related to:

employees
departments
salary

and provides the relevant schema to the SQL generation model.

## 🎯 Project Objective

The primary objective of this project is to build an AI-powered interface that allows users to interact with relational databases using natural language.

The system demonstrates how:

Natural Language Processing + Large Language Models + Retrieval + Databases

can be combined to create an AI database assistant.

