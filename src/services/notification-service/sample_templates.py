"""
Sample notification templates for the Vetterati ATS system
"""

SAMPLE_TEMPLATES = [
    {
        "name": "Application Received",
        "description": "Confirmation email sent when a candidate submits an application",
        "channel": "email",
        "subject_template": "Application Received - {{ job_title }} at {{ company_name }}",
        "body_template": """
Dear {{ candidate_name }},

Thank you for your interest in the {{ job_title }} position at {{ company_name }}.

We have successfully received your application and our hiring team will review it carefully. You can expect to hear back from us within {{ response_timeframe | default("5-7 business days") }}.

Application Details:
- Position: {{ job_title }}
- Department: {{ department | default("N/A") }}
- Application ID: {{ application_id }}
- Submitted: {{ submission_date }}

In the meantime, feel free to learn more about our company at {{ company_website | default("our website") }}.

Best regards,
{{ recruiter_name | default("The Hiring Team") }}
{{ company_name }}
""",
        "variables": {
            "candidate_name": "string",
            "job_title": "string", 
            "company_name": "string",
            "application_id": "string",
            "submission_date": "datetime",
            "response_timeframe": "string",
            "department": "string",
            "company_website": "string",
            "recruiter_name": "string"
        },
        "tags": ["application", "confirmation", "candidate"]
    },
    {
        "name": "Interview Scheduled",
        "description": "Notification sent when an interview is scheduled",
        "channel": "email",
        "subject_template": "Interview Scheduled - {{ job_title }} at {{ company_name }}",
        "body_template": """
Dear {{ candidate_name }},

Great news! We would like to invite you for an interview for the {{ job_title }} position.

Interview Details:
- Date: {{ interview_date }}
- Time: {{ interview_time }} ({{ timezone }})
- Duration: {{ duration | default("1 hour") }}
- Type: {{ interview_type | default("In-person") }}
{% if interview_location %}
- Location: {{ interview_location }}
{% endif %}
{% if meeting_link %}
- Meeting Link: {{ meeting_link }}
{% endif %}

Interviewer(s): {{ interviewer_names }}

{% if preparation_notes %}
Preparation Notes:
{{ preparation_notes }}
{% endif %}

Please confirm your attendance by replying to this email or clicking the link below:
{{ confirmation_link }}

If you need to reschedule, please contact us at least 24 hours in advance.

Best regards,
{{ recruiter_name }}
{{ company_name }}
""",
        "variables": {
            "candidate_name": "string",
            "job_title": "string",
            "company_name": "string",
            "interview_date": "date",
            "interview_time": "time",
            "timezone": "string",
            "duration": "string",
            "interview_type": "string",
            "interview_location": "string",
            "meeting_link": "string",
            "interviewer_names": "string",
            "preparation_notes": "string",
            "confirmation_link": "string",
            "recruiter_name": "string"
        },
        "tags": ["interview", "scheduling", "candidate"]
    },
    {
        "name": "Interview Reminder",
        "description": "Reminder sent 24 hours before interview",
        "channel": "email",
        "subject_template": "Interview Reminder - Tomorrow at {{ interview_time }}",
        "body_template": """
Dear {{ candidate_name }},

This is a friendly reminder about your upcoming interview for the {{ job_title }} position at {{ company_name }}.

Interview Details:
- Date: {{ interview_date }} (Tomorrow)
- Time: {{ interview_time }} ({{ timezone }})
- Duration: {{ duration | default("1 hour") }}
- Type: {{ interview_type }}
{% if interview_location %}
- Location: {{ interview_location }}
{% endif %}
{% if meeting_link %}
- Meeting Link: {{ meeting_link }}
{% endif %}

Interviewer(s): {{ interviewer_names }}

{% if preparation_checklist %}
Please make sure to:
{{ preparation_checklist }}
{% endif %}

We look forward to meeting with you!

Best regards,
{{ recruiter_name }}
{{ company_name }}
""",
        "variables": {
            "candidate_name": "string",
            "job_title": "string",
            "company_name": "string",
            "interview_date": "date",
            "interview_time": "time",
            "timezone": "string",
            "duration": "string",
            "interview_type": "string",
            "interview_location": "string",
            "meeting_link": "string",
            "interviewer_names": "string",
            "preparation_checklist": "string",
            "recruiter_name": "string"
        },
        "tags": ["interview", "reminder", "candidate"]
    },
    {
        "name": "Application Status Update",
        "description": "General template for application status updates",
        "channel": "email",
        "subject_template": "Application Update - {{ job_title }} at {{ company_name }}",
        "body_template": """
Dear {{ candidate_name }},

We wanted to update you on the status of your application for the {{ job_title }} position at {{ company_name }}.

Status: {{ status_update }}

{% if status_message %}
{{ status_message }}
{% endif %}

{% if next_steps %}
Next Steps:
{{ next_steps }}
{% endif %}

{% if feedback %}
Feedback:
{{ feedback }}
{% endif %}

Thank you for your continued interest in {{ company_name }}. If you have any questions, please don't hesitate to reach out.

Best regards,
{{ recruiter_name }}
{{ company_name }}
""",
        "variables": {
            "candidate_name": "string",
            "job_title": "string",
            "company_name": "string",
            "status_update": "string",
            "status_message": "string",
            "next_steps": "string",
            "feedback": "string",
            "recruiter_name": "string"
        },
        "tags": ["status", "update", "candidate"]
    },
    {
        "name": "New Application Alert",
        "description": "Alert sent to recruiters when a new application is received",
        "channel": "slack",
        "body_template": """
🎯 *New Application Received*

*Position:* {{ job_title }}
*Candidate:* {{ candidate_name }}
*Email:* {{ candidate_email }}
*Application ID:* {{ application_id }}
*Submitted:* {{ submission_date }}

{% if resume_url %}
📄 Resume: {{ resume_url }}
{% endif %}

{% if match_score %}
🎯 Match Score: {{ match_score }}%
{% endif %}

<{{ application_url }}|View Application>
""",
        "variables": {
            "job_title": "string",
            "candidate_name": "string", 
            "candidate_email": "string",
            "application_id": "string",
            "submission_date": "datetime",
            "resume_url": "string",
            "match_score": "number",
            "application_url": "string"
        },
        "tags": ["application", "alert", "recruiter", "internal"]
    },
    {
        "name": "Interview No-Show",
        "description": "Alert when candidate doesn't show up for interview",
        "channel": "slack",
        "body_template": """
⚠️ *Interview No-Show Alert*

*Candidate:* {{ candidate_name }}
*Position:* {{ job_title }}
*Scheduled Time:* {{ interview_time }}
*Interviewer:* {{ interviewer_name }}

The candidate did not attend the scheduled interview.

<{{ candidate_profile_url }}|View Candidate Profile>
""",
        "variables": {
            "candidate_name": "string",
            "job_title": "string",
            "interview_time": "datetime",
            "interviewer_name": "string",
            "candidate_profile_url": "string"
        },
        "tags": ["interview", "no-show", "alert", "internal"]
    },
    {
        "name": "SMS Interview Reminder",
        "description": "SMS reminder sent 2 hours before interview",
        "channel": "sms",
        "body_template": """Hi {{ candidate_name }}, reminder: You have an interview for {{ job_title }} at {{ company_name }} today at {{ interview_time }}. {% if meeting_link %}Join: {{ meeting_link }}{% endif %} Good luck!""",
        "variables": {
            "candidate_name": "string",
            "job_title": "string",
            "company_name": "string",
            "interview_time": "time",
            "meeting_link": "string"
        },
        "tags": ["interview", "reminder", "sms", "candidate"]
    }
]
