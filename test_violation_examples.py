"""
Violation Detection Examples - Shows what content triggers moderation policies.

This script demonstrates the types of content that Azure AI Content Safety can detect.
Post messages similar to these examples in your Teams channel to test the system.
"""

import os
from dotenv import load_dotenv
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeTextOptions
from azure.core.credentials import AzureKeyCredential

load_dotenv()

def analyze_sample(client, category, text):
    """Analyze a sample text and display results."""
    print(f"\n{'='*70}")
    print(f"Testing: {category}")
    print(f"Text: \"{text}\"")
    print("-" * 70)
    
    try:
        request = AnalyzeTextOptions(text=text)
        response = client.analyze_text(request)
        
        # Display results for each category
        categories = [
            ("Hate Speech", response.categories_analysis[0]),
            ("Self-Harm", response.categories_analysis[1]),
            ("Sexual Content", response.categories_analysis[2]),
            ("Violence", response.categories_analysis[3])
        ]
        
        violations_found = False
        for name, result in categories:
            if result.severity > 0:
                violations_found = True
                severity_map = {0: "Safe", 2: "Low", 4: "Medium", 6: "High"}
                severity_label = severity_map.get(result.severity, f"Level {result.severity}")
                print(f"  ⚠️  {name}: {severity_label} (severity: {result.severity})")
        
        if not violations_found:
            print(f"  ✅ CLEAN - No violations detected")
        else:
            print(f"\n  📝 ACTION: This message would be FLAGGED or DELETED based on policy")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")

def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║     Content Moderation Test - Violation Detection           ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    
    # Initialize Content Safety client
    client = ContentSafetyClient(
        endpoint=os.getenv("CONTENT_SAFETY_ENDPOINT"),
        credential=AzureKeyCredential(os.getenv("CONTENT_SAFETY_KEY"))
    )
    
    print("\n🔍 Testing various content types to demonstrate violation detection...")
    
    # Test samples
    samples = [
        ("Clean Message", "Hello everyone! Looking forward to our team meeting today."),
        ("Mild Profanity", "This project is so damn frustrating sometimes."),
        ("Strong Profanity", "I hate this stupid project and everyone involved."),
        ("Hate Speech", "I can't stand working with those idiots from that team."),
        ("Violence", "I want to punch the wall after this terrible meeting."),
        ("PII Leak", "My phone number is 555-1234 and my SSN is 123-45-6789."),
    ]
    
    for category, text in samples:
        analyze_sample(client, category, text)
    
    print(f"\n{'='*70}")
    print("\n📋 Summary of Severity Levels:")
    print("   • 0 = Safe")
    print("   • 2 = Low severity")
    print("   • 4 = Medium severity") 
    print("   • 6 = High severity")
    
    print("\n💡 To Test Your System:")
    print("   1. Post one of these example messages in your Teams 'General' channel")
    print("   2. Run: python test_full_moderation.py")
    print("   3. Or start continuous monitoring: python start_monitoring.py")
    print("\n✅ Test complete!")

if __name__ == "__main__":
    main()
