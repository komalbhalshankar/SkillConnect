"""
SkillConnect — Application Entry Point.
Supports running the web server as well as direct CLI commands:
- python run.py               (Starts development server)
- python run.py init-db       (Initializes database safely)
- python run.py seed-skills   (Seeds standard categories & skills)
- python run.py create-admin  (Creates admin account interactively)
"""
import os
import sys
from app import create_app

app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    # If subcommands like init-db, seed-skills, create-admin are passed directly
    if len(sys.argv) > 1 and sys.argv[1] in ['init-db', 'seed-skills', 'create-admin']:
        app.cli.main(args=sys.argv[1:])
    else:
        app.run(host='127.0.0.1', port=5000, debug=True)
