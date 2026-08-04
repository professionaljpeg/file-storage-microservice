import sys
import secrets
from werkzeug.security import generate_password_hash
# Import the app, database, and APIKey model from your Flask app
from app import app, db, APIKey

def create_api_key(client_name: str) -> str:
    """Generates a secure API key, hashes the secret part, 
    and saves the record to the database."""
    
    # Generate the public KeyID (16 hex chars) and secret string
    key_id = secrets.token_hex(8) 
    secret = secrets.token_urlsafe(32)   
    
    # Hash the secret part using Werkzeug
    secret_hash = generate_password_hash(secret)
    
    # Create the SQLAlchemy model instance
    new_key_record = APIKey(
        key_id=key_id,
        secret_hash=secret_hash,
        client_name=client_name
    )
    
    # Save to the database inside Flask's application context
    with app.app_context():
        db.session.add(new_key_record)
        db.session.commit()
        
    # Return the full key in the 'KeyID.Secret' format
    return f"{key_id}.{secret}"

if __name__ == '__main__':
    # Accept client name from command line or prompt for it
    if len(sys.argv) > 1:
        client_name = " ".join(sys.argv[1:])
    else:
        client_name = input("Enter client/application name (e.g. 'Mobile App'): ").strip()
        
    if not client_name:
        print("Error: Client name cannot be empty.")
        sys.exit(1)
        
    full_api_key = create_api_key(client_name)
    
    print("\n" + "=" * 55)
    print(f" SUCCESS: API Key created for '{client_name}'")
    print("=" * 55)
    print(f"  API Key: {full_api_key}")
    print("=" * 55)
    print(" IMPORTANT: Copy this key now. It cannot be recovered!\n")