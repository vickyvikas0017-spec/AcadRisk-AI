from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app.database.connection import db_manager
from app.models.entities import User, Role, AuditLog

class AuthService:
    # In-memory dictionary for login attempt protection: {username: {'attempts': int, 'last_attempt': datetime}}
    FAILED_ATTEMPTS = {}
    MAX_ATTEMPTS = 5

    @classmethod
    def authenticate(cls, username, password):
        # Protection against brute-force login attempts
        attempt_record = cls.FAILED_ATTEMPTS.get(username)
        if attempt_record and attempt_record['attempts'] >= cls.MAX_ATTEMPTS:
            # Check lockout duration (10 minutes)
            seconds_elapsed = (datetime.now() - attempt_record['last_attempt']).total_seconds()
            if seconds_elapsed < 600:
                remaining = int((600 - seconds_elapsed) // 60) + 1
                return None, f"Account temporarily locked due to excessive failed attempts. Please retry in {remaining} minute(s)."
            else:
                cls.FAILED_ATTEMPTS[username] = {'attempts': 0, 'last_attempt': datetime.now()}

        session = db_manager.get_session()
        try:
            lookup_name = username.strip()
            user = session.query(User).filter(
                (User.username == lookup_name) | (User.email == lookup_name)
            ).first()

            # Support demo credential aliases if direct username not found
            if not user:
                if lookup_name.lower() in ('faculty1', 'faculty'):
                    user = session.query(User).filter_by(username='prof_smith').first()
                elif lookup_name.lower() in ('student1', 'student'):
                    user = session.query(User).filter_by(username='john_doe').first()

            if not user:
                return None, "Invalid username or password."

            if user.account_status != 'active':
                return None, "Account is disabled. Contact institutional administrator."

            if not check_password_hash(user.password_hash, password):
                # Increment failed attempts
                curr = cls.FAILED_ATTEMPTS.get(username, {'attempts': 0, 'last_attempt': datetime.now()})
                curr['attempts'] += 1
                curr['last_attempt'] = datetime.now()
                cls.FAILED_ATTEMPTS[username] = curr
                remaining_tries = cls.MAX_ATTEMPTS - curr['attempts']
                if remaining_tries > 0:
                    return None, f"Invalid password. {remaining_tries} attempt(s) remaining before lockout."
                return None, "Account locked due to excessive failed attempts. Try again in 10 minutes."

            # Reset attempts on success
            if username in cls.FAILED_ATTEMPTS:
                del cls.FAILED_ATTEMPTS[username]

            # Log login action
            audit = AuditLog(
                user_id=user.user_id,
                action_type='LOGIN',
                table_name='users',
                record_id=user.user_id,
                old_values=None,
                new_values='{"status": "successful_login"}',
                timestamp=datetime.now()
            )
            session.add(audit)
            session.commit()

            user_data = user.to_dict()
            if user.student_profile:
                user_data['student_id'] = user.student_profile.student_id
                user_data['full_name'] = user.student_profile.student_name
            elif user.role and user.role.role_name == 'STUDENT':
                student = session.query(Student).filter_by(user_id=user.user_id).first()
                if not student:
                    student = session.query(Student).first()
                if student:
                    user_data['student_id'] = student.student_id
                    user_data['full_name'] = student.student_name

            if user.faculty_profile:
                user_data['faculty_id'] = user.faculty_profile.faculty_id
                user_data['full_name'] = user.faculty_profile.faculty_name
            elif user.role and user.role.role_name == 'FACULTY':
                faculty = session.query(Faculty).filter_by(user_id=user.user_id).first()
                if not faculty:
                    faculty = session.query(Faculty).first()
                if faculty:
                    user_data['faculty_id'] = faculty.faculty_id
                    user_data['full_name'] = faculty.faculty_name

            return user_data, None
        finally:
            session.close()

    @classmethod
    def create_user(cls, username, email, password, role_id):
        session = db_manager.get_session()
        try:
            # Check unique constraints
            existing = session.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            if existing:
                return None, "Username or email already registered."

            new_user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                role_id=role_id,
                account_status='active',
                created_at=datetime.now()
            )
            session.add(new_user)
            session.commit()
            return new_user.to_dict(), None
        except Exception as e:
            session.rollback()
            return None, str(e)
        finally:
            session.close()

