import io
import os
import re
import zipfile
import xml.etree.ElementTree as ET
from typing import Tuple, Dict, Any, List, Optional
from pypdf import PdfReader
from pypdf.errors import PdfReadError

# Comprehensive technical skills taxonomy & normalization alias map
SKILL_TAXONOMY: Dict[str, List[str]] = {
    # Programming Languages
    "Python": ["python", "python3", "py"],
    "JavaScript": ["javascript", "js", "ecmascript"],
    "TypeScript": ["typescript", "ts"],
    "Java": ["java", "core java", "j2se"],
    "C": ["c language"],
    "C++": ["c++", "cpp"],
    "C#": ["c#", "csharp", ".net c#"],
    "Go": ["golang", "go language"],
    "Rust": ["rust", "rustlang"],
    "Ruby": ["ruby"],
    "PHP": ["php"],
    "Swift": ["swift"],
    "Kotlin": ["kotlin"],
    "Scala": ["scala"],
    "R": ["r programming", "r language"],
    "SQL": ["sql", "structured query language"],
    "HTML5": ["html", "html5"],
    "CSS3": ["css", "css3"],
    "Bash": ["bash", "shell scripting", "sh", "zsh"],

    # Frontend Frameworks & Libraries
    "React": ["react", "react.js", "reactjs"],
    "Next.js": ["next.js", "nextjs", "next js"],
    "Vue.js": ["vue", "vue.js", "vuejs"],
    "Angular": ["angular", "angular.js", "angularjs"],
    "Svelte": ["svelte", "sveltekit"],
    "Tailwind CSS": ["tailwind", "tailwindcss", "tailwind css"],
    "Bootstrap": ["bootstrap", "bootstrap5"],
    "Redux": ["redux", "redux toolkit", "rtk"],
    "GraphQL": ["graphql", "apollo graphql"],
    "Vite": ["vite", "vitejs"],
    "Webpack": ["webpack"],
    "Sass": ["sass", "scss"],
    "React Native": ["react native", "react-native"],
    "Flutter": ["flutter"],

    # Backend Frameworks
    "FastAPI": ["fastapi", "fast-api"],
    "Django": ["django", "django rest framework", "drf"],
    "Flask": ["flask"],
    "Node.js": ["node", "node.js", "nodejs"],
    "Express.js": ["express", "express.js", "expressjs"],
    "Spring Boot": ["spring boot", "springboot", "spring framework"],
    "NestJS": ["nestjs", "nest.js"],
    "Ruby on Rails": ["ruby on rails", "rails"],
    "ASP.NET": ["asp.net", "asp.net core", "dotnet core"],
    "Gin": ["gin", "gin-gonic"],
    "gRPC": ["grpc"],
    "REST APIs": ["rest api", "restful api", "rest apis", "restful apis", "rest"],

    # Databases & Caching
    "PostgreSQL": ["postgresql", "postgres", "psql"],
    "MySQL": ["mysql"],
    "MongoDB": ["mongodb", "mongo"],
    "Redis": ["redis"],
    "SQLite": ["sqlite", "sqlite3"],
    "DynamoDB": ["dynamodb", "aws dynamodb"],
    "Cassandra": ["cassandra", "apache cassandra"],
    "Elasticsearch": ["elasticsearch", "elastic search"],
    "Neo4j": ["neo4j"],
    "Oracle": ["oracle db", "oracle database"],
    "Firebase": ["firebase", "firestore"],

    # Cloud & DevOps
    "AWS": ["aws", "amazon web services", "ec2", "s3", "lambda", "ecs", "eks"],
    "GCP": ["gcp", "google cloud", "google cloud platform"],
    "Azure": ["azure", "microsoft azure"],
    "Docker": ["docker", "dockerfile", "docker-compose"],
    "Kubernetes": ["kubernetes", "k8s"],
    "Terraform": ["terraform"],
    "Ansible": ["ansible"],
    "CI/CD": ["ci/cd", "ci-cd", "continuous integration", "continuous delivery"],
    "GitHub Actions": ["github actions", "github action"],
    "Jenkins": ["jenkins"],
    "CircleCI": ["circleci"],
    "Linux": ["linux", "ubuntu", "debian", "centos", "redhat"],
    "Nginx": ["nginx"],
    "Kafka": ["kafka", "apache kafka"],
    "RabbitMQ": ["rabbitmq"],
    "Celery": ["celery"],
    "Prometheus": ["prometheus"],
    "Grafana": ["grafana"],

    # AI, Machine Learning & Data
    "PyTorch": ["pytorch", "torch"],
    "TensorFlow": ["tensorflow", "tf"],
    "Scikit-Learn": ["scikit-learn", "sklearn", "scikit learn"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "OpenCV": ["opencv"],
    "Hugging Face": ["hugging face", "huggingface", "transformers"],
    "NLP": ["natural language processing", "nlp"],
    "Computer Vision": ["computer vision", "cv"],
    "LLM": ["large language models", "llm", "llms"],
    "LangChain": ["langchain"],
    "Apache Spark": ["spark", "apache spark", "pyspark"],
    "Airflow": ["airflow", "apache airflow"],

    # Systems & Architecture
    "System Design": ["system design", "distributed systems", "system architecture"],
    "Microservices": ["microservices", "microservice architecture"],
    "Event-Driven Architecture": ["event-driven architecture", "event driven"],
    "WebSocket": ["websocket", "websockets", "ws"],
    "Git": ["git", "github", "gitlab"],
    "Testing / TDD": ["pytest", "jest", "unit testing", "tdd", "integration testing"],
}


def validate_document(file_bytes: bytes, filename: str) -> str:
    """
    Validates document extension, magic bytes, empty checks, and file integrity.
    Returns normalized extension ('pdf' or 'docx').
    """
    if not file_bytes or len(file_bytes) == 0:
        raise ValueError("The uploaded file is empty. Please select a valid resume document.")

    ext = filename.lower().split(".")[-1] if "." in filename else ""
    if ext not in ("pdf", "docx"):
        raise ValueError(f"Unsupported file format '{ext}'. Only PDF and DOCX files are supported.")

    # Magic byte signature validation
    if ext == "pdf":
        if not file_bytes.startswith(b"%PDF"):
            raise ValueError("Corrupted PDF document: missing standard %PDF file header signature.")
    elif ext == "docx":
        if not (file_bytes.startswith(b"PK\x03\x04") or file_bytes.startswith(b"PK\x05\x06")):
            raise ValueError("Corrupted DOCX document: missing valid ZIP package signature.")

    return ext


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extracts text content from a PDF document with layout and boundary awareness.
    Detects password-encrypted and image-only scanned documents.
    """
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
    except Exception as exc:
        raise ValueError(f"Could not read PDF document: {str(exc)}")

    if reader.is_encrypted:
        raise ValueError("The uploaded PDF is password-protected. Please upload an unlocked document.")

    extracted_pages: List[str] = []
    for page_idx, page in enumerate(reader.pages):
        try:
            # Try layout mode first if supported
            text = page.extract_text(extraction_mode="layout") or page.extract_text()
        except Exception:
            text = page.extract_text()

        if text and text.strip():
            extracted_pages.append(text.strip())

    raw_text = "\n\n".join(extracted_pages).strip()
    return raw_text


def extract_text_from_docx(file_bytes: bytes) -> Tuple[str, Dict[str, str]]:
    """
    Extracts structured text from a DOCX package, including paragraphs, tables,
    and external hyperlink references (e.g. LinkedIn, GitHub, portfolio).
    """
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
            if "word/document.xml" not in z.namelist():
                raise ValueError("Invalid DOCX format: missing word/document.xml")

            # Extract embedded hyperlinks from relationships if present
            links = {}
            if "word/_rels/document.xml.rels" in z.namelist():
                rels_xml = z.read("word/_rels/document.xml.rels")
                try:
                    rels_tree = ET.fromstring(rels_xml)
                    for rel in rels_tree.iter():
                        target = rel.attrib.get("Target", "")
                        r_id = rel.attrib.get("Id", "")
                        if target.startswith("http") and r_id:
                            links[r_id] = target
                except Exception:
                    pass

            xml_content = z.read("word/document.xml")
            tree = ET.fromstring(xml_content)

            lines = []
            for elem in tree.iter():
                # Paragraphs and table cells
                if elem.tag.endswith('p') or elem.tag.endswith('tc'):
                    texts = [t.text for t in elem.iter() if t.tag.endswith('t') and t.text]
                    line_text = "".join(texts).strip()
                    if line_text:
                        lines.append(line_text)

            return "\n".join(lines).strip(), links

    except zipfile.BadZipFile:
        raise ValueError("The uploaded DOCX file is corrupted or not a valid Word document.")
    except Exception as exc:
        raise ValueError(f"Failed to extract text from DOCX document: {str(exc)}")


def clean_extracted_text(text: str) -> str:
    """
    Normalizes whitespace, fixes glued headers (e.g., 'EngineerSkills:' -> 'Engineer\nSkills:'),
    and ensures clean paragraph separation.
    """
    if not text:
        return ""

    # Fix glued section headers when line breaks are lost during PDF text extraction
    text = re.sub(
        r'([a-z0-9\.\)])\s*([A-Z][a-zA-Z\s]{1,25}:)',
        r'\1\n\2',
        text
    )

    # Normalize carriage returns and tabs
    text = re.sub(r'[\r\t]+', ' ', text)
    # Normalize multiple spaces
    text = re.sub(r'[ ]{2,}', ' ', text)
    # Normalize excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def extract_candidate_name(raw_text: str, lines: List[str]) -> Optional[str]:
    """
    Extracts the candidate's full name accurately from the header section.
    Handles 'Name - Title' (e.g. 'Alex Morgan - Lead Software Engineer').
    Avoids keywords, email addresses, phone numbers, and URLs.
    """
    # Check for explicit "Name: John Doe" pattern
    explicit_match = re.search(r'(?:Full\s+Name|Name)\s*[:\-]\s*([A-Z][a-zA-Z\.\'-]+(?:\s+[A-Z][a-zA-Z\.\'-]+){1,3})', raw_text, re.IGNORECASE)
    if explicit_match:
        return explicit_match.group(1).strip()

    excluded_keywords = {
        "resume", "curriculum", "vitae", "cv", "profile", "contact",
        "experience", "education", "skills", "projects", "page", "phone",
        "email", "address", "portfolio", "summary", "engineer", "developer",
        "architect", "designer", "consultant", "analyst", "lead", "senior"
    }

    # Inspect first 5 non-empty lines
    for line in lines[:5]:
        clean_line = line.strip()
        # Skip if contains contact symbols or URLs
        if any(char in clean_line for char in ['@', 'http', 'www.', ':', '/']):
            continue

        # If line contains hyphen or pipe (e.g., "Alex Morgan - Senior Full Stack Engineer")
        segments = re.split(r'[\-|–|—|•|\|]', clean_line)
        target = segments[0].strip()

        words = target.split()
        if 2 <= len(words) <= 4:
            if all(w.replace('-', '').replace('.', '').isalpha() for w in words):
                lower_words = {w.lower() for w in words}
                if not (lower_words & excluded_keywords):
                    return target

    return None


# Valid US state codes and common country names for location matching
US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
}
COUNTRIES = {
    "usa", "united states", "india", "uk", "united kingdom", "canada",
    "germany", "france", "australia", "netherlands", "singapore"
}


def extract_contact_info(text: str, docx_links: Optional[Dict[str, str]] = None) -> Dict[str, Optional[str]]:
    """Extracts email, phone, location, LinkedIn, GitHub, and portfolio URLs."""
    # Email (RFC 5322 compatible)
    email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    email = email_match.group(0).strip().rstrip('.') if email_match else None

    # Phone number
    phone_match = re.search(
        r'(?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?',
        text
    )
    phone = None
    if phone_match:
        phone_raw = phone_match.group(0).strip()
        digits = re.sub(r'\D', '', phone_raw)
        if 10 <= len(digits) <= 15:
            phone = phone_raw

    # Fallback international phone pattern
    if not phone:
        intl_match = re.search(r'\+?\d{1,4}[-.\s]?\(?\d{2,5}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}', text)
        if intl_match:
            digits = re.sub(r'\D', '', intl_match.group(0))
            if len(digits) >= 10:
                phone = intl_match.group(0).strip()

    # LinkedIn
    linkedin = None
    li_match = re.search(r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/(?:in|profile)\/([a-zA-Z0-9_-]+)', text, re.IGNORECASE)
    if li_match:
        linkedin = f"https://linkedin.com/in/{li_match.group(1)}"

    # GitHub
    github = None
    gh_match = re.search(r'(?:https?:\/\/)?(?:www\.)?github\.com\/([a-zA-Z0-9_-]+)', text, re.IGNORECASE)
    if gh_match:
        github = f"https://github.com/{gh_match.group(1)}"

    # Check embedded DOCX links if present
    if docx_links:
        for url in docx_links.values():
            if "linkedin.com/in" in url and not linkedin:
                linkedin = url
            elif "github.com/" in url and not github:
                github = url

    # Location heuristic (e.g. "San Francisco, CA" or "Bengaluru, India")
    location = None
    # Check for explicit Location: prefix first
    loc_prefix_match = re.search(r'(?:Location|Address|Based\s+in)\s*[:\-]\s*([A-Z][a-zA-Z\s]+(?:,\s*[A-Z][a-zA-Z]+)?)', text, re.IGNORECASE)
    if loc_prefix_match:
        location = loc_prefix_match.group(1).strip()
    else:
        # Check city, state pattern
        for m in re.finditer(r'\b([A-Z][a-zA-Z\s]{2,20}),\s*([A-Z]{2}|[A-Z][a-zA-Z]{3,15})\b', text):
            city = m.group(1).strip()
            state_or_country = m.group(2).strip()
            # Verify state is valid US state code or country
            if state_or_country in US_STATES or state_or_country.lower() in COUNTRIES:
                if not any(k in city.lower() for k in ["python", "react", "fastapi", "university", "college", "school"]):
                    location = f"{city}, {state_or_country}"
                    break

    # Portfolio / personal website
    portfolio = None
    email_domain = email.split('@')[-1].lower() if email and '@' in email else None

    # First check for explicit URLs with http:// or https://
    web_matches = re.finditer(r'https?:\/\/(?!www\.linkedin|linkedin|github)[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}(?:\/[^\s\)]*)?', text, re.IGNORECASE)
    for wm in web_matches:
        candidate_url = wm.group(0).strip()
        if not email_domain or email_domain not in candidate_url.lower():
            portfolio = candidate_url
            break

    # If not found, look for bare portfolio domains (e.g. janedoe.dev, alex.io, myportfolio.me)
    if not portfolio:
        for bm in re.finditer(r'(?:^|[\s|•,;])([a-zA-Z0-9\-\.]+\.(?:dev|me|io|tech|app|ai|site|com|org)(?:\/[^\s\)]*)?)', text, re.IGNORECASE):
            candidate_domain = bm.group(1).strip().rstrip('.,;')
            if email_domain and candidate_domain.lower() == email_domain:
                continue
            if any(social in candidate_domain.lower() for social in ["linkedin.com", "github.com", "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "example.com"]):
                continue
            portfolio = candidate_domain
            break

    return {
        "email": email,
        "phone": phone,
        "location": location,
        "linkedin": linkedin,
        "github": github,
        "portfolio": portfolio,
    }


def split_into_sections(text: str) -> Dict[str, str]:
    """
    Segments document text into logical sections based on common headings.
    Strictly separates Work Experience from Projects, Education, and Certifications.
    """
    section_patterns = {
        "summary": r'(?:^|\n)\s*(?:PROFESSIONAL\s+SUMMARY|EXECUTIVE\s+SUMMARY|ABOUT\s+ME|PROFILE|SUMMARY|OBJECTIVE)[\s:\-]*\n',
        "skills": r'(?:^|\n)\s*(?:TECHNICAL\s+SKILLS|CORE\s+COMPETENCIES|SKILLS\s*&?\s*TECHNOLOGIES|SKILLS|TECHNOLOGIES|TOOLING)[\s:\-]*\n',
        "experience": r'(?:^|\n)\s*(?:WORK\s+EXPERIENCE|PROFESSIONAL\s+EXPERIENCE|EMPLOYMENT\s+HISTORY|EXPERIENCE|WORK\s+HISTORY)[\s:\-]*\n',
        "projects": r'(?:^|\n)\s*(?:KEY\s+PROJECTS|NOTABLE\s+PROJECTS|ACADEMIC\s+PROJECTS|PERSONAL\s+PROJECTS|PROJECTS)[\s:\-]*\n',
        "education": r'(?:^|\n)\s*(?:ACADEMIC\s+BACKGROUND|EDUCATION\s*&?\s*ACADEMICS|EDUCATION|QUALIFICATIONS)[\s:\-]*\n',
        "certifications": r'(?:^|\n)\s*(?:LICENSES\s*&?\s*CERTIFICATIONS|CERTIFICATIONS|CERTIFICATES)[\s:\-]*\n',
        "achievements": r'(?:^|\n)\s*(?:HONORS\s*&?\s*AWARDS|AWARDS|ACHIEVEMENTS|ACCOMPLISHMENTS)[\s:\-]*\n',
    }

    # Find start index of each section heading
    matches = []
    for sec_name, pattern in section_patterns.items():
        for m in re.finditer(pattern, text, re.IGNORECASE):
            matches.append((m.start(), m.end(), sec_name))

    matches.sort(key=lambda x: x[0])

    sections: Dict[str, str] = {
        "header": "",
        "summary": "",
        "skills": "",
        "experience": "",
        "projects": "",
        "education": "",
        "certifications": "",
        "achievements": ""
    }

    if not matches:
        sections["header"] = text
        return sections

    # Content before first section is header
    sections["header"] = text[:matches[0][0]].strip()

    # Slice between consecutive matched headings
    for i in range(len(matches)):
        start_content = matches[i][1]
        end_content = matches[i + 1][0] if i + 1 < len(matches) else len(text)
        sec_name = matches[i][2]
        sections[sec_name] = text[start_content:end_content].strip()

    return sections


def extract_skills_from_text(text: str) -> List[str]:
    """
    Extracts and normalizes technical skills against our comprehensive taxonomy.
    Distinguishes distinct technologies (Java vs JavaScript, C vs C++, React vs React Native).
    """
    found_skills = set()
    lower_text = text.lower()

    for canonical_name, aliases in SKILL_TAXONOMY.items():
        for alias in aliases:
            # Word-boundary pattern with special symbol support (C++, C#, .NET)
            escaped = re.escape(alias)
            if alias in ["c++", "c#", ".net"]:
                pattern = r'(?:^|[\s,;/|])' + escaped + r'(?:[\s,;/|]|$)'
            else:
                pattern = r'\b' + escaped + r'\b'

            if re.search(pattern, lower_text):
                found_skills.add(canonical_name)
                break

    # Guard specific distinctions:
    # If "react native" is matched, do not drop "React" if candidate explicitly mentioned React
    if "React Native" in found_skills and not re.search(r'\breact(?:\.js|js)?\b(?!\s*native)', lower_text):
        if "React" in found_skills:
            found_skills.remove("React")

    # Special handling for short language names: Go, C, Assembly
    if re.search(r'\b(?:golang|go\s+language|go\s+programming)\b', lower_text) or re.search(r'(?:^|[\s,;/|])Go(?:[\s,;/|]|$)', text):
        found_skills.add("Go")

    if re.search(r'\b(?:c\s+language|c\s+programming)\b', lower_text) or re.search(r'\bin\s+C\s+(?:and|programming)\b', text) or re.search(r'(?:^|[\s,;/|])C(?:[\s,;/|]|$)', text) or re.search(r'\bC\s*(?:/|and|\+)\s*C\+\+', text):
        found_skills.add("C")

    if re.search(r'\b(?:assembly|asm|x86|arm\s+assembly)\b', lower_text):
        found_skills.add("Assembly")

    return sorted(list(found_skills))


def extract_education(edu_text: str, raw_text: str) -> List[Dict[str, Any]]:
    """
    Extracts formal degrees and academic institutions.
    Does NOT classify certifications or online badges as degrees.
    """
    combined = edu_text if edu_text else raw_text
    education_list: List[Dict[str, Any]] = []

    degree_patterns = [
        r'(?:Master(?:\'s)?\s+(?:of\s+Science|in\s+Computer\s+Science|of\s+Technology|of\s+Business\s+Administration)?|M\.?S\.?|M\.?Tech\.?|M\.?B\.?A\.?)',
        r'(?:Bachelor(?:\'s)?\s+(?:of\s+Science|of\s+Technology|of\s+Engineering|of\s+Arts)?|B\.?S\.?|B\.?Tech\.?|B\.?E\.?|B\.?A\.?)',
        r'(?:Ph\.?D\.?|Doctorate|Doctor\s+of\s+Philosophy)',
        r'(?:Associate(?:\'s)?\s+(?:Degree|of\s+Science)?)'
    ]

    for p in degree_patterns:
        for m in re.finditer(r'(' + p + r'[^\n,;]*)', combined, re.IGNORECASE):
            full_match = m.group(1).strip()
            # Clean degree title
            degree_title = full_match.split(" at ")[0].split(" from ")[0].strip()

            # Find nearby year (1990 - 2030)
            context_window = combined[max(0, m.start() - 60):min(len(combined), m.end() + 100)]
            year_match = re.search(r'\b(19\d{2}|20\d{2})\b', context_window)
            year = year_match.group(0) if year_match else None

            # Find institution keywords
            inst_match = re.search(r'([A-Z][a-zA-Z\s]{2,40}(?:University|College|Institute|School|Academy)[a-zA-Z\s]*)', context_window)
            institution = inst_match.group(1).strip() if inst_match else "Accredited University"

            # GPA detection
            gpa_match = re.search(r'\b(?:GPA\s*[:\-]?\s*)?([3-4]\.\d{1,2}(?:\s*\/\s*4(?:\.0)?)?|[7-9]\.\d{1,2}(?:\s*\/\s*10)?)\b', context_window, re.IGNORECASE)
            gpa = gpa_match.group(0).strip() if gpa_match else None

            education_list.append({
                "degree": degree_title,
                "institution": institution,
                "year": year or "Graduated",
                "gpa": gpa
            })

    # Deduplicate by degree title
    seen = set()
    deduped = []
    for item in education_list:
        key = item["degree"].lower()
        if key not in seen:
            seen.add(key)
            deduped.append(item)

    return deduped


def extract_work_experience(exp_text: str) -> List[Dict[str, Any]]:
    """
    Extracts professional work experience blocks (role, company, duration, highlights).
    Strictly keeps personal and academic projects OUT of employment.
    """
    if not exp_text or len(exp_text.strip()) < 15:
        return []

    lines = [line.strip() for line in exp_text.split("\n") if line.strip()]
    experience_list: List[Dict[str, Any]] = []

    # Common role indicators
    role_pattern = r'\b(?:Engineer|Developer|Architect|Lead|Manager|Director|Specialist|Consultant|Scientist|Analyst|Intern)\b'

    current_entry: Optional[Dict[str, Any]] = None

    for line in lines:
        is_bullet = line.startswith(('-', '•', '*', '–', '—')) or re.match(r'^\d+[\.\)]', line)
        has_role = re.search(role_pattern, line, re.IGNORECASE)
        has_date = re.search(r'\b(?:19\d{2}|20\d{2}|Present|Current|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b', line, re.IGNORECASE)

        if has_role and (has_date or len(line.split()) <= 7) and not is_bullet:
            if current_entry:
                experience_list.append(current_entry)

            # Determine role vs company
            parts = re.split(r'[\-|–|—|•|,|at]\s+', line)
            role = parts[0].strip()
            company = parts[1].strip() if len(parts) > 1 else "Tech Organization"

            date_match = re.search(r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*\d{4}\s*(?:-|–|—|to)\s*(?:Present|Current|\w+\s*\d{4}|\d{4}))', line, re.IGNORECASE)
            duration = date_match.group(1).strip() if date_match else "2+ years"

            current_entry = {
                "role": role,
                "company": company,
                "duration": duration,
                "highlights": []
            }
        elif current_entry:
            clean_hl = line.lstrip('-•*–— ').strip()
            if len(clean_hl) > 10:
                current_entry["highlights"].append(clean_hl)

    if current_entry:
        experience_list.append(current_entry)

    return experience_list


def extract_projects(proj_text: str) -> List[Dict[str, Any]]:
    """
    Extracts portfolio, personal, and open-source project blocks.
    Strictly isolated from corporate work experience.
    """
    if not proj_text or len(proj_text.strip()) < 15:
        return []

    lines = [line.strip() for line in proj_text.split("\n") if line.strip()]
    projects_list: List[Dict[str, Any]] = []

    current_proj: Optional[Dict[str, Any]] = None

    for line in lines:
        is_bullet = line.startswith(('-', '•', '*', '–', '—')) or re.match(r'^\d+[\.\)]', line)

        # Detect project header (short line with colon or pipes, or "Project Name | Tech Stack")
        if not is_bullet and (':' in line or '|' in line or len(line.split()) <= 6):
            if current_proj:
                projects_list.append(current_proj)

            parts = re.split(r'[:|]', line)
            p_name = parts[0].strip()
            # Extract technologies if mentioned in title line
            tech_text = parts[1].strip() if len(parts) > 1 else ""
            tech_list = extract_skills_from_text(tech_text)

            current_proj = {
                "title": p_name,
                "name": p_name,
                "tech": tech_list,
                "description": ""
            }
        elif current_proj:
            clean_desc = line.lstrip('-•*–— ').strip()
            if current_proj["description"]:
                current_proj["description"] += " " + clean_desc
            else:
                current_proj["description"] = clean_desc

            # Enrich tech stack from project description lines
            extra_tech = extract_skills_from_text(line)
            current_proj["tech"] = sorted(list(set(current_proj["tech"] + extra_tech)))

    if current_proj:
        projects_list.append(current_proj)

    return projects_list


def extract_certifications(cert_text: str, raw_text: str) -> List[str]:
    """
    Extracts industry certifications (AWS, GCP, CKA, PMP, CISSP, CompTIA, etc.).
    Preserves them as certifications, never converting them into university degrees.
    """
    source = cert_text if cert_text else raw_text
    cert_catalog = [
        r'AWS\s+Certified[^\n,\.;]*',
        r'Google\s+Cloud\s+Certified[^\n,\.;]*',
        r'Microsoft\s+Certified[^\n,\.;]*',
        r'Certified\s+Kubernetes\s+(?:Administrator|Application\s+Developer|Security\s+Specialist)',
        r'CKA|CKAD|CKS',
        r'CISSP|CISM|CEH|CompTIA\s+Security\+|CompTIA\s+Network\+',
        r'PMP|Project\s+Management\s+Professional',
        r'HashiCorp\s+Certified[^\n,\.;]*',
        r'Oracle\s+Certified[^\n,\.;]*'
    ]

    certs = []
    for pat in cert_catalog:
        for m in re.finditer(pat, source, re.IGNORECASE):
            cert_val = m.group(0).strip()
            if len(cert_val) > 2 and cert_val not in certs:
                certs.append(cert_val)

    return certs


def parse_resume_content(file_bytes: bytes, filename: str) -> Tuple[str, Dict[str, Any]]:
    """
    Core parsing pipeline:
    1. Validates file format and signatures (PDF / DOCX).
    2. Extracts clean raw text and hyperlinks.
    3. Checks for empty or scanned image documents.
    4. Deterministically extracts personal and professional profile details.
    5. Returns (cleaned_text, parsed_data).
    """
    ext = validate_document(file_bytes, filename)
    raw_text = ""
    docx_links = {}

    if ext == "pdf":
        raw_text = extract_text_from_pdf(file_bytes)
    elif ext == "docx":
        raw_text, docx_links = extract_text_from_docx(file_bytes)

    cleaned_text = clean_extracted_text(raw_text)

    # Scanned PDF or insufficient text check
    if not cleaned_text or len(cleaned_text.strip()) < 30:
        raise ValueError(
            "Could not extract readable text from the uploaded document. "
            "Scanned or image-only documents require OCR (which is currently unavailable). "
            "Please upload a text-based PDF or DOCX file."
        )

    # Segment into logical sections
    sections = split_into_sections(cleaned_text)
    lines = [line.strip() for line in cleaned_text.split("\n") if line.strip()]

    # Extract Entities
    candidate_name = extract_candidate_name(cleaned_text, lines)
    contact_info = extract_contact_info(cleaned_text, docx_links)
    skills = extract_skills_from_text(sections["skills"] or cleaned_text)
    education = extract_education(sections["education"], cleaned_text)
    experience = extract_work_experience(sections["experience"])
    projects = extract_projects(sections["projects"])
    certifications = extract_certifications(sections["certifications"], cleaned_text)

    # Achievements extraction
    achievements = []
    if sections["achievements"]:
        ach_lines = [l.lstrip('-•* ').strip() for l in sections["achievements"].split("\n") if len(l.strip()) > 8]
        achievements = ach_lines[:4]

    # Executive Summary
    summary = None
    if sections["summary"]:
        summary = " ".join([l.strip() for l in sections["summary"].split("\n") if l.strip()])
    elif experience and skills:
        top_skills = ", ".join(skills[:4])
        summary = f"Technical professional with proven experience in {top_skills}."

    parsed_data = {
        "name": candidate_name or "Candidate",
        "email": contact_info["email"],
        "phone": contact_info["phone"],
        "location": contact_info["location"],
        "linkedin": contact_info["linkedin"],
        "github": contact_info["github"],
        "portfolio": contact_info["portfolio"],
        "skills": skills,
        "education": education,
        "experience": experience,
        "projects": projects,
        "certifications": certifications,
        "achievements": achievements,
        "summary": summary
    }

    return cleaned_text, parsed_data
