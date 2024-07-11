class Schemas:
    regulation_documents = {
        "title": {
            "type": "string",
        },
        "document_url": {
            "type": "string",
        },
    }
    government_contracts = {
        "id": {
            "type": "string",
        },
        "title": {
            "type": "string",
        },
        "status": {
            "type": "string",
        },
        "description": {
            "type": "string",
        },
        "location": {
            "type": "string",
        },
        "type": {
            "type": "string",
        },
        "category": {
            "type": "string",
        },
        "posted_date": {
            "type": "string",
        },
        "due_date": {
            "type": "string",
        },
        "buyer_name": {
            "type": "string",
        },
        "buyer_contact_name": {
            "type": "string",
        },
        "buyer_contact_email": {
            "type": "string",
        },
        "buyer_contact_number": {
            "type": "string",
        },
        "attachments": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"title": {"type": "string"}, "url": {"type": "string"}},
            },
        },
        "procurement_items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "code_type": {"type": "string"},
                    "code": {"type": "string"},
                    "code_description": {"type": "string"},
                    "description": {"type": "string"},
                },
            },
        },
    }

    school_directory = {
        "first_name": {
            "type": "string",
        },
        "last_name": {
            "type": "string",
        },
        "email": {
            "type": "string",
        },
        "phone_number": {
            "type": "string",
        },
        "title": {
            "type": "string",
        },
    }
    government_meetings = {
        "title": {
            "type": "string",
        },
        "description": {
            "type": "string",
        },
        "classification": {
            "type": "string",
        },
        "is_cancelled": {
            "type": "boolean",
        },
        "start_time": {
            "type": "datetime",
        },
        "end_time": {
            "type": "datetime",
        },
        "is_all_day_event": {
            "type": "boolean",
        },
        "time_notes": {
            "type": "string",
        },
        "location": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                },
                "address": {
                    "type": "string",
                },
            },
        },
        "links": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                    },
                    "url": {
                        "type": "string",
                    },
                },
            },
        },
    }
    job_postings = {
        "job_id": {
            "type": "string",
            "description": "A unique identifier for the job posting."
        },
        "department": {
            "type": "string",
            "description": "The department within the company for the job position."
        },
        "title": {
            "type": "string",
            "description": "The title of the job position."
        },
        "job_description": {
            "type": "string",
            "description": "Detailed overview of the job role, including responsibilities and required skills."
        },
        "locations": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "A list of cities or specific locations where the job is available."
        },
        "job_type": {
            "type": "string",
            "description": "The level of experience required for the job, e.g., entry-level, mid-level, senior."
        },
        "date_posted": {
            "type": "string",
            "description": "The date when the job was posted."
        },
        "apply_url": {
            "type": "string",
            "description": "The URL where applicants can apply for the job."
        },
        "job_benefits": {
            "type": "string",
            "description": "A list of benefits provided with the job."
        },
        "qualifications": {
            "type": "string",
            "description": "A list of certifications or professional requirements for the job."
        },
        "preferred_skills": {
            "type": "string",
            "description": "A list of preferred (but not mandatory) skills and qualifications for the job."
        },
        "skills": {
            "type": "string",
            "description": "A list of technical abilities or soft skills required for the job."
        },
        "recruiter_email": {
            "type": "string",
            "description": "Email address of the recruiter or hiring manager for contact."
        },
        "application_deadline": {
            "type": "string",
            "description": "The deadline for submitting job applications."
        },
        "language": {
            "type": "string",
            "description": "The language of the job posting."
        },
        "employment_type": {
            "type": "string",
            "description": "The type of employment (e.g., full-time, part-time, contract)."
        },
        "tags": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "Keywords or phrases related to the job for categorization and searchability."
        }
    }
