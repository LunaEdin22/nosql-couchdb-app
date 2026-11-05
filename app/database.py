import os
import time
import requests
from typing import Any, Dict, List, Optional
from requests.auth import HTTPBasicAuth

COUCHDB_HOST = os.getenv("COUCHDB_HOST", "localhost")
COUCHDB_PORT = os.getenv("COUCHDB_PORT", "5984")
COUCHDB_USER = os.getenv("COUCHDB_USER", "admin")
COUCHDB_PASSWORD = os.getenv("COUCHDB_PASSWORD", "password")
COUCHDB_DB_NAME = os.getenv("COUCHDB_DB_NAME", "products_db")

# Build base URL with or without direct auth
COUCHDB_BASE_URL = os.getenv(
    "COUCHDB_URL",
    f"http://{COUCHDB_HOST}:{COUCHDB_PORT}"
)

AUTH = HTTPBasicAuth(COUCHDB_USER, COUCHDB_PASSWORD) if COUCHDB_USER and COUCHDB_PASSWORD else None

def get_db_url() -> str:
    return f"{COUCHDB_BASE_URL.rstrip('/')}/{COUCHDB_DB_NAME}"

def ensure_database_exists(max_retries: int = 10, delay: int = 2) -> bool:
    """Verifies that CouchDB is accessible and creates the database if it does not exist."""
    db_url = get_db_url()
    for attempt in range(1, max_retries + 1):
        try:
            # Check server status
            res = requests.get(COUCHDB_BASE_URL, auth=AUTH, timeout=5)
            if res.status_code == 200:
                # Check if specific database exists
                db_res = requests.get(db_url, auth=AUTH, timeout=5)
                if db_res.status_code == 200:
                    return True
                elif db_res.status_code == 404:
                    # Create database
                    create_res = requests.put(db_url, auth=AUTH, timeout=5)
                    if create_res.status_code in (200, 201):
                        return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(delay)
    return False

def get_all_documents(limit: int = 50, skip: int = 0) -> List[Dict[str, Any]]:
    """Retrieves all documents from CouchDB using the _all_docs endpoint."""
    url = f"{get_db_url()}/_all_docs"
    params = {"include_docs": "true", "limit": limit, "skip": skip}
    response = requests.get(url, params=params, auth=AUTH, timeout=5)
    response.raise_for_status()
    data = response.json()
    
    products = []
    for row in data.get("rows", []):
        doc = row.get("doc", {})
        # Skip design documents
        if doc.get("_id", "").startswith("_design/"):
            continue
        products.append({
            "id": doc.get("_id"),
            "rev": doc.get("_rev"),
            "name": doc.get("name"),
            "category": doc.get("category"),
            "price": doc.get("price"),
            "stock": doc.get("stock", 0),
            "tags": doc.get("tags", []),
            "specs": doc.get("specs", {}),
            "status": doc.get("status", "active")
        })
    return products

def get_document_by_id(doc_id: str) -> Optional[Dict[str, Any]]:
    """Gets a specific document by its ID."""
    url = f"{get_db_url()}/{doc_id}"
    response = requests.get(url, auth=AUTH, timeout=5)
    if response.status_code == 404:
        return None
    response.raise_for_status()
    doc = response.json()
    return {
        "id": doc.get("_id"),
        "rev": doc.get("_rev"),
        "name": doc.get("name"),
        "category": doc.get("category"),
        "price": doc.get("price"),
        "stock": doc.get("stock", 0),
        "tags": doc.get("tags", []),
        "specs": doc.get("specs", {}),
        "status": doc.get("status", "active")
    }

def create_document(doc_data: Dict[str, Any]) -> Dict[str, Any]:
    """Inserts a new JSON document into CouchDB."""
    url = get_db_url()
    response = requests.post(url, json=doc_data, auth=AUTH, timeout=5)
    response.raise_for_status()
    result = response.json()
    return {
        "id": result.get("id"),
        "rev": result.get("rev"),
        **doc_data
    }

def update_document(doc_id: str, update_fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Updates an existing document while respecting CouchDB MVCC revision tokens."""
    url = f"{get_db_url()}/{doc_id}"
    get_res = requests.get(url, auth=AUTH, timeout=5)
    if get_res.status_code == 404:
        return None
    get_res.raise_for_status()
    doc = get_res.json()
    
    # Merge existing fields with new values
    for key, value in update_fields.items():
        if value is not None:
            doc[key] = value
            
    put_res = requests.put(url, json=doc, auth=AUTH, timeout=5)
    put_res.raise_for_status()
    result = put_res.json()
    return {
        "id": result.get("id"),
        "rev": result.get("rev"),
        "name": doc.get("name"),
        "category": doc.get("category"),
        "price": doc.get("price"),
        "stock": doc.get("stock", 0),
        "tags": doc.get("tags", []),
        "specs": doc.get("specs", {}),
        "status": doc.get("status", "active")
    }

def delete_document(doc_id: str) -> bool:
    """Deletes a document from CouchDB using its ID and current revision."""
    url = f"{get_db_url()}/{doc_id}"
    get_res = requests.get(url, auth=AUTH, timeout=5)
    if get_res.status_code == 404:
        return False
    get_res.raise_for_status()
    rev = get_res.json().get("_rev")
    
    del_res = requests.delete(f"{url}?rev={rev}", auth=AUTH, timeout=5)
    return del_res.status_code in (200, 202)

def find_by_category(category: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Executes a CouchDB Mango query to find documents matching a category."""
    url = f"{get_db_url()}/_find"
    payload = {
        "selector": {"category": {"$eq": category}},
        "limit": limit
    }
    response = requests.post(url, json=payload, auth=AUTH, timeout=5)
    response.raise_for_status()
    data = response.json()
    
    results = []
    for doc in data.get("docs", []):
        results.append({
            "id": doc.get("_id"),
            "rev": doc.get("_rev"),
            "name": doc.get("name"),
            "category": doc.get("category"),
            "price": doc.get("price"),
            "stock": doc.get("stock", 0),
            "tags": doc.get("tags", []),
            "specs": doc.get("specs", {}),
            "status": doc.get("status", "active")
        })
    return results
