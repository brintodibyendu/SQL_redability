from flask import Flask, request, jsonify
import sqlparse
from sqlparse.sql import Where, Comparison, Identifier
from sqlparse.tokens import Keyword, DML, Comment, Whitespace, Newline, Name, Operator
from flask import render_template
# ... [Previous functions remain the same]

def is_comment(token):
    """ Check if the token is a comment """
    return token.ttype in Comment

def contains_error_handling(token_list):
    """ Check for patterns that might indicate error handling """
    error_handling_keywords = ["CASE", "WHEN", "THEN", "ELSE", "END", "COALESCE", "TRY", "CATCH"]
    for token in token_list:
        if token.ttype is Keyword and token.value.upper() in error_handling_keywords:
            return True
    return False

def contains_complex_joins_or_subqueries(token_list):
    """ Check for complex joins or subqueries """
    join_keywords = ["JOIN", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL JOIN"]
    for token in token_list:
        if token.ttype is Keyword and token.value.upper() in join_keywords:
            return True
        if isinstance(token, Identifier) and token.has_alias():
            return True  # Check for subqueries with alias
    return False

def contains_complex_where_conditions(token_list):
    """ Check for complex conditions in WHERE clause """
    for token in token_list:
        if isinstance(token, Where):
            for child in token:
                if isinstance(child, Comparison):
                    # Further checks can be added here for complexity
                    return True
    return False

def is_query_updatable(parsed):
    """ Basic check for query updatability """
    # Checking for complex joins or subqueries
    complex_joins_or_subqueries = contains_complex_joins_or_subqueries(parsed.tokens)

    # Checking for complex WHERE conditions
    complex_where_conditions = contains_complex_where_conditions(parsed.tokens)

    # Checking if the query is a DML statement (INSERT, UPDATE, DELETE)
    is_dml = any(token.ttype is DML for token in parsed.tokens)

    return not complex_joins_or_subqueries and not complex_where_conditions and is_dml

def has_good_formatting(sql_query):
    """ Check for good formatting based on line breaks and indentation """
    major_clauses = ["SELECT", "FROM", "WHERE", "ORDER BY", "GROUP BY", "HAVING", "JOIN", "ON", "UNION"]
    parsed = sqlparse.parse(sql_query)[0]
    previous_token = None

    for token in parsed.flatten():
        if token.ttype is Keyword and token.value.upper() in major_clauses:
            if previous_token is not None and previous_token.ttype is not Newline:
                return False
        previous_token = token

    return True


def suggest_error_handling(sql_query):
    """ Provide basic suggestions for error handling in the SQL query """
    suggestions = []
    parsed = sqlparse.parse(sql_query)[0]

    # Check for division operations which might lead to division by zero
    for token in parsed.flatten():
        if token.ttype is Operator and token.value == '/':
            suggestions.append("Consider using NULLIF to avoid division by zero errors.")

    # Check for potential NULL issues
    if 'NULL' in sql_query.upper():
        suggestions.append("Consider using COALESCE or IS NULL checks to handle NULL values.")

    # This is a placeholder for more complex error handling checks
    # ...

    return suggestions if suggestions else ""

def generate_well_indented_query(sql_query):
    """ Generate a well-indented version of the SQL query """
    return sqlparse.format(sql_query, reindent=True, keyword_case='upper')



def evaluate_sql_readability(sql_query):
    """ Evaluate various aspects of SQL query readability and quality """
    parsed = sqlparse.parse(sql_query)[0]

    # Criteria evaluations
    comment_count = sum(1 for t in parsed.flatten() if is_comment(t))
    has_error_handling = contains_error_handling(parsed.tokens)
    updatable = is_query_updatable(parsed)
    well_formatted = has_good_formatting(sql_query)

    # Generate the well-indented query
    well_indented_query = generate_well_indented_query(sql_query) if not well_formatted else ""

    # Generate a readability report
    report = {
        "Well Formatted": well_formatted,
        "Comments Count": comment_count,
        "Potential Error Handling": has_error_handling,
        "Easily Updatable": updatable,
        "Well-Indented Query": well_indented_query,
        "Error Handling Suggestion": suggest_error_handling(sql_query),
        "Updatability Suggestion": ""  # Placeholder for manual input
    }

    return report


# Evaluate the query
#readability_report = evaluate_sql_readability(sql_query)
#print(readability_report)









app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/readability', methods=['POST'])
def readability():
    data = request.json
    sql_query = data.get('sql_query')
    if not sql_query:
        return jsonify({"error": "No SQL query provided"}), 400

    report = evaluate_sql_readability(sql_query)
    return jsonify(report)

if __name__ == '__main__':
    app.run(debug=True)