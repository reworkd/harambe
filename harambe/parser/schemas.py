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
        "company_description": {
            "type": "string",
            "description": "A brief description of the company within the job post."
        },
        "level": {
            "type": "string",
            "description": "The tier of the job within the company's structure."
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
            "description": "Overview of the job role"
        },
        "locations": {
            "type": "string",
            "description": "A list of cities or specific locations where the job is available."
        },
        "salary_range": {
            "type": "object",
            "properties": {
                "min": {"type": "string", "description": "Minimum salary offered."},
                "max": {"type": "string", "description": "Maximum salary offered."},
                "currency": {"type": "string", "description": "The currency of the salary."}
            }
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
        "work_hours": {
            "type": "string",
            "description": "The expected work hours for the job."
        },
        "job_benefits": {
            "type": "string",
            "description": "A list of benefits provided with the job."
        },
        "qualifications": {
            "type": "string",
            "description": "A list of required qualifications for the job."
        },
        "preferred_qualifications": {
            "type": "string",
            "description": "A list of preferred (but not mandatory) qualifications for the job."
        },
        "role": {
            "type": "string",
            "description": "Details about the role including responsibilities and required skills."
        },
        "skills": {
            "type": "string",
            "description": "A list of knowledge, skills or abilities required for the job."
        },
        "education": {
            "type": "string",
            "description": "Listed requirements for education or past experience"
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
