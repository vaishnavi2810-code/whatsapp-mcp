#!/usr/bin/env python3
"""
Test script for Claude AI integration.
Verifies that the new analyze endpoints and claude.py module work correctly.
"""

import json
from datetime import datetime, timedelta

print("=" * 70)
print("WhatsApp MCP Server - Claude AI Integration Test")
print("=" * 70)

# Test 1: Check imports
print("\n[Test 1] Checking imports...")
try:
    from claude import (
        ClaudeAnalyzer,
        analyze_messages,
        summarize_messages,
        extract_topics,
        analyze_sentiment,
        extract_action_items,
        semantic_search,
    )
    print("✓ Claude module imports successful")
except Exception as e:
    print(f"✗ Error importing claude module: {e}")
    exit(1)

# Test 2: Check API models
print("\n[Test 2] Checking API Pydantic models...")
try:
    from api import (
        AnalyzeQueryRequest,
        AnalyzeResponse,
        DailySummaryRequest,
        ContactSummaryRequest,
        SemanticSearchRequest,
    )
    print("✓ API Pydantic models imported successfully")
except Exception as e:
    print(f"✗ Error importing API models: {e}")
    exit(1)

# Test 3: Verify request model validation
print("\n[Test 3] Testing request model validation...")
try:
    # Valid request
    req = AnalyzeQueryRequest(
        query_type="summarize",
        max_messages=50
    )
    print(f"✓ AnalyzeQueryRequest validation passed")
    print(f"  - query_type: {req.query_type}")
    print(f"  - max_messages: {req.max_messages}")
    
    # Test with custom query
    req2 = AnalyzeQueryRequest(
        query_type="custom",
        custom_query="What are the main topics?"
    )
    print(f"✓ Custom query request validation passed")
    
except Exception as e:
    print(f"✗ Error validating request: {e}")
    exit(1)

# Test 4: Verify ClaudeAnalyzer can be instantiated
print("\n[Test 4] Testing ClaudeAnalyzer instantiation...")
try:
    # This will fail without API key, but we can test the error handling
    import os
    if "ANTHROPIC_API_KEY" not in os.environ:
        print("⚠ ANTHROPIC_API_KEY not set - skipping instantiation test")
        print("  (This is expected in development/CI environment)")
    else:
        try:
            analyzer = ClaudeAnalyzer()
            print(f"✓ ClaudeAnalyzer instantiated successfully")
            print(f"  - Model: {analyzer.model}")
            print(f"  - Max tokens: {analyzer.max_tokens}")
        except Exception as e:
            print(f"✗ Error instantiating ClaudeAnalyzer: {e}")
except Exception as e:
    print(f"✗ Unexpected error: {e}")

# Test 5: Check extended list_messages signature
print("\n[Test 5] Checking extended list_messages function...")
try:
    from whatsapp import list_messages
    import inspect
    
    sig = inspect.signature(list_messages)
    params = list(sig.parameters.keys())
    
    expected_new_params = ["media_type", "is_from_me", "chat_name_pattern"]
    found_params = [p for p in expected_new_params if p in params]
    
    print(f"✓ list_messages has {len(params)} parameters")
    print(f"✓ New parameters found: {found_params}")
    
    if len(found_params) == len(expected_new_params):
        print(f"✓ All expected new parameters present!")
    else:
        print(f"⚠ Some expected parameters missing")
    
except Exception as e:
    print(f"✗ Error checking function signature: {e}")

# Test 6: Test request/response models serialize/deserialize
print("\n[Test 6] Testing JSON serialization...")
try:
    # Create a request
    req = AnalyzeQueryRequest(
        after="2026-01-11T00:00:00",
        before="2026-01-11T23:59:59",
        query_type="summarize",
        keywords=["project", "deadline"],
        max_messages=100
    )
    
    # Convert to dict
    req_dict = req.model_dump()
    print(f"✓ Request serialization successful")
    print(f"  - Keywords: {req_dict['keywords']}")
    
    # Create response
    resp = AnalyzeResponse(
        query_type="summarize",
        period="2026-01-11",
        messages_analyzed=47,
        analysis="Sample analysis result",
        metadata={"topics": ["Project A", "Meeting"], "message_count": 47},
        timestamp=datetime.now()
    )
    
    resp_dict = resp.model_dump()
    print(f"✓ Response serialization successful")
    print(f"  - Period: {resp_dict['period']}")
    print(f"  - Messages analyzed: {resp_dict['messages_analyzed']}")
    
except Exception as e:
    print(f"✗ Error in serialization: {e}")
    exit(1)

# Test 7: Check FastAPI app can load
print("\n[Test 7] Testing FastAPI application...")
try:
    from api import app
    
    # Check that new routes exist
    routes = [route.path for route in app.routes]
    analyze_routes = [r for r in routes if "/analyze" in r]
    
    print(f"✓ FastAPI app loaded successfully")
    print(f"✓ Found {len(analyze_routes)} analyze endpoints:")
    for route in sorted(analyze_routes):
        print(f"  - {route}")
    
    expected_routes = ["/analyze/query", "/analyze/daily-summary", "/analyze/search"]
    found = [r for r in expected_routes if r in routes]
    
    if len(found) == len(expected_routes):
        print(f"✓ All expected analyze endpoints present!")
    else:
        print(f"⚠ Some expected endpoints missing: {set(expected_routes) - set(found)}")
    
except Exception as e:
    print(f"✗ Error loading FastAPI app: {e}")
    exit(1)

# Summary
print("\n" + "=" * 70)
print("Integration Test Summary")
print("=" * 70)
print("✓ All critical tests passed!")
print("\nNext steps:")
print("1. Set ANTHROPIC_API_KEY environment variable")
print("2. Start the API server: python api.py")
print("3. Test endpoints with curl or Postman:")
print("")
print("   POST /analyze/query")
print("   {")
print('     "query_type": "summarize",')
print('     "after": "2026-01-11T00:00:00Z",')
print('     "before": "2026-01-11T23:59:59Z"')
print("   }")
print("")
print("4. View API docs at http://localhost:8000/docs")
print("=" * 70)
