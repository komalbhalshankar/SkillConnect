"""
StatsService: Aggregates metrics and statistics for student and admin dashboards.
All values are strictly computed from active database records.
"""
from typing import Dict, Any, List
from app.extensions import db
from app.models.user import User
from app.models.skill import Skill, SkillCategory, UserSkill
from app.models.exchange import ExchangeRequest, ExchangeSession
from app.models.rating import Rating
from app.services.matching_service import MatchingService
from app.services.rating_service import RatingService

class StatsService:

    @staticmethod
    def get_student_dashboard_stats(user: User) -> Dict[str, Any]:
        """
        Aggregate comprehensive database-backed metrics for a student's dashboard.
        Avoids double-counting and adheres strictly to active records.
        """
        teach_count = len(user.teach_skills)
        learn_count = len(user.learn_skills)
        total_skills = teach_count + learn_count

        # Compute compatible matches via the matching engine
        compatible_matches = MatchingService.get_matches_for_user(user)
        compatible_matches_count = len(compatible_matches)

        # Exchange Requests statistics
        pending_received = ExchangeRequest.query.filter_by(
            receiver_id=user.id,
            status='pending'
        ).count()

        pending_sent = ExchangeRequest.query.filter_by(
            sender_id=user.id,
            status='pending'
        ).count()

        accepted_requests = ExchangeRequest.query.filter(
            ((ExchangeRequest.sender_id == user.id) | (ExchangeRequest.receiver_id == user.id)),
            ExchangeRequest.status == 'accepted'
        ).count()

        rejected_requests = ExchangeRequest.query.filter(
            ((ExchangeRequest.sender_id == user.id) | (ExchangeRequest.receiver_id == user.id)),
            ExchangeRequest.status == 'rejected'
        ).count()

        cancelled_requests = ExchangeRequest.query.filter(
            ((ExchangeRequest.sender_id == user.id) | (ExchangeRequest.receiver_id == user.id)),
            ExchangeRequest.status == 'cancelled'
        ).count()

        total_requests = pending_received + pending_sent + accepted_requests + rejected_requests + cancelled_requests

        # Sessions statistics
        user_requests_subquery = db.session.query(ExchangeRequest.id).filter(
            (ExchangeRequest.sender_id == user.id) | (ExchangeRequest.receiver_id == user.id)
        )

        upcoming_sessions = ExchangeSession.query.filter(
            ExchangeSession.request_id.in_(user_requests_subquery),
            ExchangeSession.status == 'scheduled'
        ).order_by(ExchangeSession.scheduled_at.asc()).all()

        completed_sessions = ExchangeSession.query.filter(
            ExchangeSession.request_id.in_(user_requests_subquery),
            ExchangeSession.status == 'completed'
        ).order_by(ExchangeSession.scheduled_at.desc()).all()

        cancelled_sessions_count = ExchangeSession.query.filter(
            ExchangeSession.request_id.in_(user_requests_subquery),
            ExchangeSession.status == 'cancelled'
        ).count()

        upcoming_sessions_count = len(upcoming_sessions)
        completed_sessions_count = len(completed_sessions)
        total_sessions = upcoming_sessions_count + completed_sessions_count + cancelled_sessions_count

        # Find completed sessions where current user hasn't rated their partner yet
        unrated_completed_sessions = [
            s for s in completed_sessions if not s.has_user_rated(user.id)
        ]

        # Ratings & Feedback statistics
        ratings_summary = RatingService.get_user_ratings_summary(user.id)
        received_ratings = ratings_summary['ratings']
        recent_ratings = received_ratings[:5]
        average_rating = ratings_summary['average_rating']
        review_count = ratings_summary['review_count']
        rating_distribution = ratings_summary['distribution']

        # Recent exchange activity (most recent requests involving user)
        recent_requests = ExchangeRequest.query.filter(
            (ExchangeRequest.sender_id == user.id) | (ExchangeRequest.receiver_id == user.id)
        ).order_by(ExchangeRequest.created_at.desc()).limit(5).all()

        # Chart.js safe serialized payloads
        chart_data = {
            'sessions': {
                'labels': ['Scheduled', 'Completed', 'Cancelled'],
                'data': [upcoming_sessions_count, completed_sessions_count, cancelled_sessions_count],
                'colors': ['#0284c7', '#10b981', '#94a3b8'],
                'total': total_sessions
            },
            'requests': {
                'labels': ['Incoming Pending', 'Outgoing Pending', 'Accepted', 'Rejected', 'Cancelled'],
                'data': [pending_received, pending_sent, accepted_requests, rejected_requests, cancelled_requests],
                'colors': ['#0284c7', '#f59e0b', '#10b981', '#ef4444', '#94a3b8'],
                'total': total_requests
            },
            'ratings': {
                'labels': ['5 Stars', '4 Stars', '3 Stars', '2 Stars', '1 Star'],
                'data': [
                    rating_distribution[5],
                    rating_distribution[4],
                    rating_distribution[3],
                    rating_distribution[2],
                    rating_distribution[1]
                ],
                'colors': ['#10b981', '#34d399', '#f59e0b', '#fb923c', '#ef4444'],
                'total': review_count
            }
        }

        return {
            'total_skills': total_skills,
            'teach_count': teach_count,
            'learn_count': learn_count,
            'compatible_matches_count': compatible_matches_count,
            'pending_received': pending_received,
            'pending_sent': pending_sent,
            'accepted_requests': accepted_requests,
            'rejected_requests': rejected_requests,
            'cancelled_requests': cancelled_requests,
            'total_requests': total_requests,
            'upcoming_sessions': upcoming_sessions,
            'upcoming_sessions_count': upcoming_sessions_count,
            'completed_sessions': completed_sessions,
            'completed_sessions_count': completed_sessions_count,
            'cancelled_sessions_count': cancelled_sessions_count,
            'total_sessions': total_sessions,
            'unrated_completed_sessions': unrated_completed_sessions,
            'average_rating': average_rating,
            'review_count': review_count,
            'rating_distribution': rating_distribution,
            'received_ratings': received_ratings,
            'recent_ratings': recent_ratings,
            'recent_requests': recent_requests,
            'chart_data': chart_data
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
        cancelled_sessions = ExchangeSession.query.filter_by(status='cancelled').count()

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
            'cancelled_sessions': cancelled_sessions,
            'total_ratings': total_ratings,
            'avg_platform_rating': avg_platform_rating
        }
