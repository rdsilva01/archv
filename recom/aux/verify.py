def verify_documents(documents, required_fields):
    all_documents_valid = True  # Track if all documents are valid

    for i, doc in enumerate(documents):
        missing_or_empty_fields = [field for field in required_fields if not doc.get(field)]  # Check if the field is missing or empty
        
        if missing_or_empty_fields:
            print(f"Document {i} (nid: {doc.get('nid', 'unknown')}) is missing or has empty fields: {missing_or_empty_fields}")
            all_documents_valid = False  # Mark as invalid if any field is missing or empty
    
    if all_documents_valid:
        print("All documents contain the required fields and are not empty.")
    else:
        print("Some documents are missing required fields or have empty content.")

    return all_documents_valid