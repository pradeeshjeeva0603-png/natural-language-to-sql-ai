SCHEMA_DOCUMENTS = {

    "employees": """
TABLE: employees

Columns:
- EMPLOYEE_ID INT PRIMARY KEY
- FIRST_NAME VARCHAR(20)
- LAST_NAME VARCHAR(25)
- email VARCHAR(50)
- PHONE_NUMBER VARCHAR(20)
- HIRE_DATE DATE
- JOB_ID VARCHAR(10)
  FOREIGN KEY → jobs.JOB_ID
- SALARY DECIMAL(8,2)
- COMMISSION_PCT DECIMAL(2,2)
- MANAGER_ID INT
  FOREIGN KEY → employees.EMPLOYEE_ID
- DEPARTMENT_ID INT
  FOREIGN KEY → departments.department_id
""",

    "departments": """
TABLE: departments

Columns:
- department_id INT PRIMARY KEY
- department_name VARCHAR(50)
- manager_id INT
  FOREIGN KEY → employees.EMPLOYEE_ID
- location_id INT
  FOREIGN KEY → locations.LOCATION_ID
""",

    "jobs": """
TABLE: jobs

Columns:
- JOB_ID VARCHAR(20) PRIMARY KEY
- job_title VARCHAR(100)
- MIN_SALARY DECIMAL(10,2)
- MAX_SALARY DECIMAL(10,2)
""",

    "locations": """
TABLE: locations

Columns:
- LOCATION_ID INT PRIMARY KEY
- STREET_ADDRESS VARCHAR(255)
- POSTAL_CODE VARCHAR(20)
- CITY VARCHAR(100)
- STATE_PROVINCE VARCHAR(100)
- COUNTRY_ID CHAR(2)
  FOREIGN KEY → countries.COUNTRY_ID
""",

    "countries": """
TABLE: countries

Columns:
- COUNTRY_ID CHAR(2) PRIMARY KEY
- COUNTRY_NAME VARCHAR(100)
- REGION_ID INT
  FOREIGN KEY → regions.REGION_ID
""",

    "regions": """
TABLE: regions

Columns:
- REGION_ID INT PRIMARY KEY
- REGION_NAME VARCHAR(100)
""",

    "job_history": """
TABLE: job_history

Columns:
- EMPLOYEE_ID INT
  FOREIGN KEY → employees.EMPLOYEE_ID
- START_DATE DATE
- END_DATE DATE
- JOB_ID VARCHAR(20)
  FOREIGN KEY → jobs.JOB_ID
- DEPARTMENT_ID INT
  FOREIGN KEY → departments.department_id
"""
}


DATABASE_SCHEMA = "\n".join(SCHEMA_DOCUMENTS.values())