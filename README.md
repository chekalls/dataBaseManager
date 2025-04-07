# PostgreSQL Database Manager - Documentation

## Overview

This professional database management system provides a comprehensive solution for interacting with PostgreSQL databases through both a Python API and a graphical user interface (GUI). The tool is designed for developers, database administrators, and data analysts who need efficient access to PostgreSQL databases.

## Features

### Core Functionality
- **Database Connection Management**: Secure connection handling with support for all PostgreSQL connection parameters
- **CRUD Operations**: Full Create, Read, Update, Delete functionality
- **Transaction Control**: Begin, commit, and rollback transactions
- **Table Management**: Create, drop, and inspect table structures
- **Data Querying**: Execute arbitrary SQL queries with parameterized inputs

### Graphical Interface (Tkinter)
- **Intuitive Table Browser**: Navigate database schema with ease
- **Query Editor**: Write and execute SQL with syntax assistance
- **Visual Results Display**: Tabular presentation of query results
- **Table Structure Viewer**: Inspect column definitions and data types
- **Quick CRUD Actions**: One-click access to common operations

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- psycopg2 library

### Setup
```bash
# Clone the repository
https://github.com/chekalls/dataBaseManager.git

# Navigate to project directory
cd dataBaseManager

# Install dependencies
pip install -r requirements.txt