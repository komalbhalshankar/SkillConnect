"""
StatsService: Aggregates metrics and statistics for student and admin dashboards.
"""
from typing import Dict, Any, List
from app.extensions import db
from app.models.user import User
from app.models.skill import Skill, SkillCategory, UserSkill
from app.models.exchange import ExchangeRequest, ExchangeSession
from app.models.rating import Rating

class StatsService:

    @staticmethod
    def get_student_dashboard_stats(user: User) -> Dict[str, Any]:
        """
        Aggregate stats for the student's dashboard.
        """
        teach_count = len(user.teach_skills)
        learn_count = len(user.learn_skills)
        total_skills = teach_count + learn_count

        # Pending incoming requests
        pending_received = ExchangeRequest.query.filter_by(
            receiver_id=user.id,
            status='pending'
        ).count()

        # Pending outgoing requests
        pending_sent = ExchangeRequest.query.filter_by(
            sender_id=user.id,
            status='pending'
        ).count()

        # Upcoming scheduled sessions
        user_requests_subquery = db.session.query(ExchangeRequest.id).filter(
            (ExchangeRequest.sender_id == user.id) | (ExchangeRequest.receiver_id == user.id)
        )
        
        upcoming_sessions = ExchangeSession.query.filter(
            ExchangeSession.request_id.in_(user_requests_subquery),
            ExchangeSession.status == 'scheduled'
        ).order_by(ExchangeSession.scheduled_at.asc()).all()

        completed_sessions_count = ExchangeSession.query.filter(
            ExchangeSession.request_id.in_(user_requests_subquery),
            ExchangeSession.status == 'completed'
        ).count()

        cancelled_sessions_count = ExchangeSession.query.filter(
            ExchangeSession.request_id.in_(user_requests_subquery),
            ExchangeSession.status == 'cancelled'
        ).count()

        # Recent received ratings
        recent_ratings = Rating.query.filter_by(reviewee_id=user.id).order_by(Rating.created_at.desc()).limit(5).all()

        return {
            'total_skills': total_skills,
            'teach_count': teach_count,
            'learn_count': learn_count,
            'pending_received': pending_received,
            'pending_sent': pending_sent,
            'upcoming_sessions': upcoming_sessions,
            'upcoming_sessions_count': len(upcoming_sessions),
            'completed_sessions_count': completed_sessions_count,
            'cancelled_sessions_count': cancelled_sessions_count,
            'average_rating': user.average_rating,
            'review_count': user.review_count,
            'recent_ratings': recent_ratings
        }

    @staticmethod
    def get_admin_stats() -> Dict[str, Any]:
        """
        Aggregate global platform statistics for administrators.
        """
        total_users = User.query.filter_by(role='student').count()
        total_admins = User.query.filter_by(role='admin').count()
        total_categories = SkillCategory.query.count()
        total_skills = Skill.query.count()
        total_user_skills = UserSkill.query.count()
        
        total_requests = ExchangeRequest.query.count()
        pending_requests = ExchangeRequest.query.filter_by(status='pending').count()
        accepted_requests = ExchangeRequest.query.filter_by(status='accepted').count()
        rejected_requests = ExchangeRequest.query.filter_by(status='rejected').count()

        total_sessions = ExchangeSession.query.count()
        completed_sessions = ExchangeSession.query.filter_by(status='completed').count()
        scheduled_sessions = ExchangeSession.query.filter_by(status='scheduled').count()
        
        total_ratings = Rating.query.count()
        avg_platform_rating = 0.0
        if total_ratings > 0:
            avg_result = db.session.query(db.func.avg(Rating.score)).scalar()
            avg_platform_rating = round(float(avg_result), 1) if avg_result else 0.0

        return {
            'total_users': total_users,
            'total_admins': total_admins,
            'total_categories': total_categories,
            'total_skills': total_skills,
            'total_user_skills': total_user_skills,
            'total_requests': total_requests,
            'pending_requests': pending_requests,
            'accepted_requests': accepted_requests,
            'rejected_requests': rejected_requests,
            'total_sessions': total_sessions,
            'completed_sessions': completed_sessions,
            'scheduled_sessions': scheduled_sessions,
            'total_ratings': total_ratings,
            'avg_platform_rating': avg_platform_rating
        }
