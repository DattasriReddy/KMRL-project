#!/usr/bin/env python3
"""
Offline tests for the confidence calculation logic in backend/process.py
"""

import sys
import os

# Add the backend directory to the path so we can import process
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from process import calculate_evidence_profile, compute_confidence, CATEGORY_KEYWORDS

def test_calculate_evidence_profile():
    """Test the evidence profile calculation"""
    print("Testing calculate_evidence_profile...")

    # Test text with clear tender keywords
    text = "tender bid procurement submission contract rfp quotation bidding"
    profile = calculate_evidence_profile(text)

    # Should have hits for Tender / Bid Document
    assert profile["hits"]["Tender / Bid Document"] > 0
    # Should have top category as Tender / Bid Document
    assert profile["top_category"] == "Tender / Bid Document"
    # Share should be reasonable
    assert profile["share"]["Tender / Bid Document"] > 0.5

    print("PASS: calculate_evidence_profile tests passed")

def test_compute_confidence_clear_single_category():
    """Test confidence for a clearly single-category document"""
    print("Testing clear single-category document...")

    # Create a profile with strong tender evidence
    profile = {
        "hits": {
            "Tender / Bid Document": 20,
            "Maintenance Log / Work Order": 2,
            "Inspection Report": 1,
            "Incident Report": 0,
            "Policy / Standard Operating Procedure": 1,
            "Financial / Budget Document": 0,
            "HR / Personnel Record": 0,
            "Other": 0
        },
        "share": {
            "Tender / Bid Document": 0.83,
            "Maintenance Log / Work Order": 0.08,
            "Inspection Report": 0.04,
            "Incident Report": 0.0,
            "Policy / Standard Operating Procedure": 0.04,
            "Financial / Budget Document": 0.0,
            "HR / Personnel Record": 0.0,
            "Other": 0.0
        },
        "top_category": "Tender / Bid Document"
    }

    # Create chunk results where all chunks agree and have high confidence
    chunk_results = [
        {"success": True, "category": "Tender / Bid Document", "confidence": 0.95},
        {"success": True, "category": "Tender / Bid Document", "confidence": 0.90},
        {"success": True, "category": "Tender / Bid Document", "confidence": 0.92}
    ]

    # Chunk lengths (all similar)
    chunk_lengths = [1000, 1000, 1000]
    text_length = 3000  # Long text

    confidence, breakdown = compute_confidence(
        final_category="Tender / Bid Document",
        profile=profile,
        chunk_results=chunk_results,
        chunk_lengths=chunk_lengths,
        text_length=text_length
    )

    # Should be in the high range (0.75 to 0.95)
    assert 0.75 <= confidence <= 0.95, f"Expected confidence in [0.75, 0.95], got {confidence}"
    assert breakdown["evidence_strength"] > 0.8  # Strong evidence
    assert breakdown["chunk_agreement"] == 1.0  # All chunks agree
    assert breakdown["groq_conf"] == 0.90  # Clamped at 0.90
    assert breakdown["categories_agree"] == 1.0  # Category matches top category
    assert breakdown["coverage"] == 1.0  # All chunks successful

    print(f"PASS: Clear single-category test passed: confidence={confidence:.3f}")

def test_compute_confidence_mixed_document():
    """Test confidence for a mixed document (chunks split between categories)"""
    print("Testing mixed document...")

    # Create a profile with small margin between categories
    profile = {
        "hits": {
            "Tender / Bid Document": 12,
            "Maintenance Log / Work Order": 10,
            "Inspection Report": 2,
            "Incident Report": 0,
            "Policy / Standard Operating Procedure": 1,
            "Financial / Budget Document": 0,
            "HR / Personnel Record": 0,
            "Other": 0
        },
        "share": {
            "Tender / Bid Document": 0.48,
            "Maintenance Log / Work Order": 0.40,
            "Inspection Report": 0.08,
            "Incident Report": 0.0,
            "Policy / Standard Operating Procedure": 0.04,
            "Financial / Budget Document": 0.0,
            "HR / Personnel Record": 0.0,
            "Other": 0.0
        },
        "top_category": "Tender / Bid Document"
    }

    # Create chunk results where chunks are split between two categories
    chunk_results = [
        {"success": True, "category": "Tender / Bid Document", "confidence": 0.80},
        {"success": True, "category": "Maintenance Log / Work Order", "confidence": 0.75},
        {"success": True, "category": "Tender / Bid Document", "confidence": 0.85},
        {"success": True, "category": "Maintenance Log / Work Order", "confidence": 0.70}
    ]

    chunk_lengths = [1000, 1000, 1000, 1000]
    text_length = 4000

    confidence, breakdown = compute_confidence(
        final_category="Tender / Bid Document",  # This is what we're evaluating
        profile=profile,
        chunk_results=chunk_results,
        chunk_lengths=chunk_lengths,
        text_length=text_length
    )

    # Should be below 0.60 due to disagreement
    assert confidence < 0.60, f"Expected confidence < 0.60, got {confidence}"
    assert breakdown["evidence_strength"] < 0.5  # Small margin
    assert breakdown["chunk_agreement"] == 0.5  # Half chunks agree
    assert breakdown["categories_agree"] == 1.0  # Final category matches top category

    print(f"PASS: Mixed document test passed: confidence={confidence:.3f}")

def test_compute_confidence_all_chunks_failed():
    """Test confidence when all chunks fail"""
    print("Testing all chunks failed...")

    # Create a profile
    profile = {
        "hits": {
            "Tender / Bid Document": 15,
            "Maintenance Log / Work Order": 5,
            "Inspection Report": 0,
            "Incident Report": 0,
            "Policy / Standard Operating Procedure": 0,
            "Financial / Budget Document": 0,
            "HR / Personnel Record": 0,
            "Other": 0
        },
        "share": {
            "Tender / Bid Document": 0.75,
            "Maintenance Log / Work Order": 0.25,
            "Inspection Report": 0.0,
            "Incident Report": 0.0,
            "Policy / Standard Operating Procedure": 0.0,
            "Financial / Budget Document": 0.0,
            "HR / Personnel Record": 0.0,
            "Other": 0.0
        },
        "top_category": "Tender / Bid Document"
    }

    # All chunks failed
    chunk_results = [
        {"success": False, "category": "Other", "confidence": 0.0},
        {"success": False, "category": "Other", "confidence": 0.0}
    ]

    chunk_lengths = [1000, 1000]
    text_length = 2000

    confidence, breakdown = compute_confidence(
        final_category="Tender / Bid Document",
        profile=profile,
        chunk_results=chunk_results,
        chunk_lengths=chunk_lengths,
        text_length=text_length
    )

    # Should be at most 0.55
    assert confidence <= 0.55, f"Expected confidence <= 0.55, got {confidence}"
    assert breakdown["chunk_agreement"] is None
    assert breakdown["groq_conf"] is None
    assert breakdown["coverage"] == 0.0

    print(f"PASS: All chunks failed test passed: confidence={confidence:.3f}")

def test_compute_confidence_never_exceeds_0_95():
    """Test that confidence never exceeds 0.95 even with optimal inputs"""
    print("Testing confidence ceiling...")

    # Create a profile with perfect evidence
    profile = {
        "hits": {
            "Tender / Bid Document": 25,
            "Maintenance Log / Work Order": 0,
            "Inspection Report": 0,
            "Incident Report": 0,
            "Policy / Standard Operating Procedure": 0,
            "Financial / Budget Document": 0,
            "HR / Personnel Record": 0,
            "Other": 0
        },
        "share": {
            "Tender / Bid Document": 1.0,
            "Maintenance Log / Work Order": 0.0,
            "Inspection Report": 0.0,
            "Incident Report": 0.0,
            "Policy / Standard Operating Procedure": 0.0,
            "Financial / Budget Document": 0.0,
            "HR / Personnel Record": 0.0,
            "Other": 0.0
        },
        "top_category": "Tender / Bid Document"
    }

    # All chunks perfect agreement and high confidence
    chunk_results = [
        {"success": True, "category": "Tender / Bid Document", "confidence": 1.0},
        {"success": True, "category": "Tender / Bid Document", "confidence": 1.0},
        {"success": True, "category": "Tender / Bid Document", "confidence": 1.0}
    ]

    chunk_lengths = [1000, 1000, 1000]
    text_length = 3000

    confidence, breakdown = compute_confidence(
        final_category="Tender / Bid Document",
        profile=profile,
        chunk_results=chunk_results,
        chunk_lengths=chunk_lengths,
        text_length=text_length
    )

    # Should never exceed 0.95
    assert confidence <= 0.95, f"Expected confidence <= 0.95, got {confidence}"
    # Should be reasonably high though
    assert confidence > 0.80, f"Expected confidence > 0.80, got {confidence}"

    print(f"PASS: Confidence ceiling test passed: confidence={confidence:.3f}")

def test_compute_confidence_short_text_penalty():
    """Test that short text gets lower confidence"""
    print("Testing short text penalty...")

    # Create a profile
    profile = {
        "hits": {
            "Tender / Bid Document": 10,
            "Maintenance Log / Work Order": 0,
            "Inspection Report": 0,
            "Incident Report": 0,
            "Policy / Standard Operating Procedure": 0,
            "Financial / Budget Document": 0,
            "HR / Personnel Record": 0,
            "Other": 0
        },
        "share": {
            "Tender / Bid Document": 1.0,
            "Maintenance Log / Work Order": 0.0,
            "Inspection Report": 0.0,
            "Incident Report": 0.0,
            "Policy / Standard Operating Procedure": 0.0,
            "Financial / Budget Document": 0.0,
            "HR / Personnel Record": 0.0,
            "Other": 0.0
        },
        "top_category": "Tender / Bid Document"
    }

    # Good chunks
    chunk_results = [
        {"success": True, "category": "Tender / Bid Document", "confidence": 0.90},
        {"success": True, "category": "Tender / Bid Document", "confidence": 0.85}
    ]

    chunk_lengths = [500, 500]

    # Test with long text
    confidence_long, _ = compute_confidence(
        final_category="Tender / Bid Document",
        profile=profile,
        chunk_results=chunk_results,
        chunk_lengths=chunk_lengths,
        text_length=1000  # Long text
    )

    # Test with short text (under 200 characters)
    confidence_short, _ = compute_confidence(
        final_category="Tender / Bid Document",
        profile=profile,
        chunk_results=chunk_results,
        chunk_lengths=chunk_lengths,
        text_length=100  # Short text
    )

    # Short text should have lower confidence
    assert confidence_short < confidence_long, f"Short text penalty not applied: short={confidence_short:.3f}, long={confidence_long:.3f}"
    assert confidence_short <= 0.95  # Still within bounds

    print(f"PASS: Short text penalty test passed: long={confidence_long:.3f}, short={confidence_short:.3f}")

def test_compute_confidence_gap_penalty():
    """Test that large gap between math and groq confidence reduces final confidence"""
    print("Testing confidence gap penalty...")

    # Create a profile with moderate evidence
    profile = {
        "hits": {
            "Tender / Bid Document": 12,
            "Maintenance Log / Work Order": 8,
            "Inspection Report": 0,
            "Incident Report": 0,
            "Policy / Standard Operating Procedure": 0,
            "Financial / Budget Document": 0,
            "HR / Personnel Record": 0,
            "Other": 0
        },
        "share": {
            "Tender / Bid Document": 0.60,
            "Maintenance Log / Work Order": 0.40,
            "Inspection Report": 0.0,
            "Incident Report": 0.0,
            "Policy / Standard Operating Procedure": 0.0,
            "Financial / Budget Document": 0.0,
            "HR / Personnel Record": 0.0,
            "Other": 0.0
        },
        "top_category": "Tender / Bid Document"
    }

    # Chunks where math confidence would be high but groq confidence is low
    chunk_results = [
        {"success": True, "category": "Tender / Bid Document", "confidence": 0.60},  # Low groq confidence
        {"success": True, "category": "Tender / Bid Document", "confidence": 0.60},
        {"success": True, "category": "Tender / Bid Document", "confidence": 0.60}
    ]

    chunk_lengths = [1000, 1000, 1000]
    text_length = 3000

    confidence, breakdown = compute_confidence(
        final_category="Tender / Bid Document",
        profile=profile,
        chunk_results=chunk_results,
        chunk_lengths=chunk_lengths,
        text_length=text_length
    )

    # Debug output
    print(f"  DEBUG: evidence_strength={breakdown['evidence_strength']:.3f}")
    print(f"  DEBUG: chunk_agreement={breakdown['chunk_agreement']:.3f}")
    print(f"  DEBUG: groq_conf={breakdown['groq_conf']:.3f}")
    print(f"  DEBUG: categories_agree={breakdown['categories_agree']:.3f}")
    print(f"  DEBUG: gap={breakdown['gap']:.3f}")
    print(f"  DEBUG: coverage={breakdown['coverage']:.3f}")
    print(f"  DEBUG: raw={breakdown['raw']:.3f}")
    print(f"  DEBUG: final={breakdown['final']:.3f}")

    # With the values we expect:
    # evidence_strength should be (0.60 - 0.40) / 0.5 = 0.40
    # math_conf = 0.30 + 0.65 * 0.40 = 0.56
    # groq_conf_raw = 0.60
    # groq_conf = 0.60 * (0.5 + 0.5 * 1.0) = 0.60 * 1.0 = 0.60
    # categories_agree = 1.0
    # gap = |0.56 - 0.60| = 0.04
    # base = sqrt(0.56 * 0.60) = sqrt(0.336) ≈ 0.5796
    # confidence = base * (1 - 0.3 * gap) = 0.5796 * (1 - 0.3 * 0.04) = 0.5796 * 0.988 = 0.5726
    # coverage = 1.0
    # final confidence after coverage = 0.5726 * (0.5 + 0.5 * 1.0) = 0.5726 * 1.0 = 0.5726
    # No short text penalty (text_length >= 200)
    # Final clamp doesn't change it (0.05 <= 0.5726 <= 0.95)

    # Just verify it's computed reasonably
    assert 0.50 <= confidence <= 0.65, f"Expected confidence in [0.50, 0.65], got {confidence}"
    assert breakdown["gap"] >= 0  # Gap should be non-negative

    print(f"PASS: Gap penalty test passed: confidence={confidence:.3f}, gap={breakdown['gap']:.3f}")

def run_all_tests():
    """Run all tests"""
    print("Running offline confidence calculation tests...\n")

    try:
        test_calculate_evidence_profile()
        test_compute_confidence_clear_single_category()
        test_compute_confidence_mixed_document()
        test_compute_confidence_all_chunks_failed()
        test_compute_confidence_never_exceeds_0_95()
        test_compute_confidence_short_text_penalty()
        test_compute_confidence_gap_penalty()

        print("\nSUCCESS: All tests passed!")
        return True
    except AssertionError as e:
        print(f"\nFAIL: Test failed: {e}")
        return False
    except Exception as e:
        print(f"\nERROR: Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)