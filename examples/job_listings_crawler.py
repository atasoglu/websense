"""
Job Listings Crawler
Demonstrates how to extract job postings and employment opportunities from job boards.
"""

from websense import Scraper
import json


def crawl_job_listings(url: str, job_type: str = None):
    """
    Scrapes a job board and extracts job listing information.

    Args:
        url: The URL of the job board or search results.
        job_type: Optional job type for context (remote, full-time, etc.).
    """
    job_text = f" ({job_type})" if job_type else ""
    print(f"Crawling job listings{job_text}...\n")
    scraper = Scraper()

    try:
        data = scraper.scrape(
            url,
            example={
                "jobs": [
                    {
                        "job_title": "string",
                        "company_name": "string",
                        "location": "city or remote",
                        "job_type": "full-time, part-time, contract, etc.",
                        "salary_range": "salary or salary range with currency",
                        "description": "brief job description",
                        "required_skills": ["skill1", "skill2"],
                        "experience_level": "entry-level, mid-level, senior, etc.",
                        "posted_date": "date when posted",
                        "application_url": "link to apply",
                    }
                ],
                "total_jobs": 0,
                "search_query": "search terms used",
            },
        )

        print("--- Job Listings ---\n")
        print(json.dumps(data, indent=2))

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Example: LinkedIn Jobs
    crawl_job_listings(
        "https://www.linkedin.com/jobs/search/?keywords=python+developer",
        job_type="Remote",
    )
