#!/usr/bin/env python
"""Test script to verify engine, skills, and context updates work correctly"""

import sys
import logging
from io import StringIO

# Setup logging to capture all messages
log_stream = StringIO()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=log_stream,
    force=True,
)

logger = logging.getLogger(__name__)

def test_imports():
    """Test all imports work correctly"""
    print("\n" + "="*70)
    print("TEST 1: Verifying all imports...")
    print("="*70)
    
    try:
        from config import SKILL_DEPS, API_TEST_ENDPOINTS
        print("✓ config imported successfully")
        print(f"  - Skill dependencies: {list(SKILL_DEPS.keys())}")
        print(f"  - API endpoints configured: {len(API_TEST_ENDPOINTS)}")
        
        from core.context import Context
        print("✓ core.context imported successfully")
        
        from core.registry import Registry, SkillValidationError
        print("✓ core.registry imported successfully")
        
        from core.engine import Engine
        print("✓ core.engine imported successfully")
        
        from core.loader import load_skills
        print("✓ core.loader imported successfully")
        
        from ai.planner import choose_skill
        print("✓ ai.planner imported successfully")
        
        from tools.executor import run_cmd
        print("✓ tools.executor imported successfully")
        
        print("\n✅ All imports successful!\n")
        return True
    except Exception as e:
        print(f"\n❌ Import failed: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def test_context():
    """Test Context object works correctly"""
    print("\n" + "="*70)
    print("TEST 2: Verifying Context object...")
    print("="*70)
    
    try:
        from core.context import Context
        from core.models import Finding, Severity, FindingCategory
        
        ctx = Context("example.com")
        print(f"✓ Context created: {ctx}")
        print(f"  - Target: {ctx.target}")
        print(f"  - Initial findings: {len(ctx.findings)}")
        print(f"  - Initial errors: {len(ctx.errors)}")
        print(f"  - Execution history: {len(ctx.metadata['execution_history'])}")
        
        # Test adding data
        ctx.subdomains.append("www.example.com")
        # findings must always be Finding instances (see Context.findings
        # docstring) — a raw string breaks any code that reads f.is_verified,
        # f.effective_severity, etc.
        ctx.findings.append(Finding(
            title="Test finding",
            severity=Severity.LOW,
            category=FindingCategory.MISCONFIGURED,
            source="test_system",
            target=ctx.target,
        ))
        ctx.add_error("test_skill", "Test error")
        ctx.add_execution("test_skill", 1.5, True)
        
        print(f"\n✓ Context updates working:")
        print(f"  - Subdomains: {len(ctx.subdomains)}")
        print(f"  - Findings: {len(ctx.findings)}")
        print(f"  - Errors: {len(ctx.errors)}")
        print(f"  - Execution history: {len(ctx.metadata['execution_history'])}")
        
        print(f"\n✓ Execution time: {ctx.get_execution_time():.2f}s")
        print(f"✓ Repr: {ctx}")
        
        print("\n✅ Context object working correctly!\n")
        return True
    except Exception as e:
        print(f"\n❌ Context test failed: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def test_registry():
    """Test Registry and skill registration"""
    print("\n" + "="*70)
    print("TEST 3: Verifying Registry...")
    print("="*70)
    
    try:
        from core.registry import Registry, SkillValidationError
        
        registry = Registry()
        print(f"✓ Registry created: {len(registry)} skills")
        
        # Test valid skill registration
        def dummy_run(ctx):
            return ctx
        
        valid_skill = {"name": "test_skill", "run": dummy_run}
        registry.register(valid_skill)
        print(f"✓ Valid skill registered")
        print(f"  - Registry now has: {len(registry)} skills")
        print(f"  - Skills: {registry.list_skills()}")
        
        # Test retrieval
        retrieved = registry.get("test_skill")
        print(f"✓ Skill retrieved: {retrieved['name']}")
        
        # Test invalid skill
        try:
            invalid_skill = {"name": "invalid"}  # Missing 'run'
            registry.register(invalid_skill)
            print(f"❌ Invalid skill should have been rejected!")
            return False
        except SkillValidationError:
            print(f"✓ Invalid skill correctly rejected")
        
        print("\n✅ Registry working correctly!\n")
        return True
    except Exception as e:
        print(f"\n❌ Registry test failed: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def test_skill_loading():
    """Test skill loading from disk"""
    print("\n" + "="*70)
    print("TEST 4: Verifying Skill Loading...")
    print("="*70)
    
    try:
        from core.registry import Registry
        from core.loader import load_skills
        
        registry = Registry()
        print(f"✓ Empty registry created: {len(registry)} skills")
        
        registry = load_skills(registry)
        print(f"✓ Skills loaded: {len(registry)} skills")
        print(f"  - Loaded skills: {registry.list_skills()}")
        
        # Verify each skill has required structure
        for skill_name in registry.list_skills():
            skill = registry.get(skill_name)
            assert "name" in skill, f"Skill {skill_name} missing 'name'"
            assert "run" in skill, f"Skill {skill_name} missing 'run'"
            assert callable(skill["run"]), f"Skill {skill_name} 'run' not callable"
            print(f"  ✓ {skill_name} structure valid")
        
        print("\n✅ All skills loaded and valid!\n")
        return True
    except Exception as e:
        print(f"\n❌ Skill loading test failed: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def test_planner():
    """Test skill planning logic"""
    print("\n" + "="*70)
    print("TEST 5: Verifying Planner Logic...")
    print("="*70)
    
    try:
        from core.context import Context
        from core.registry import Registry
        from core.loader import load_skills
        from ai.planner import choose_skill
        
        ctx = Context("example.com")
        registry = Registry()
        registry = load_skills(registry)
        
        # Test 1: First skill should be 'recon'
        next_skill = choose_skill(ctx, registry)
        print(f"✓ First skill chosen: {next_skill}")
        assert next_skill == "recon", f"Expected 'recon', got '{next_skill}'"
        
        # Test 2: After recon, still needs data
        ctx.executed_skills.append("recon")
        ctx.subdomains.append("www.example.com")
        next_skill = choose_skill(ctx, registry)
        print(f"✓ After recon: {next_skill}")
        
        # Test 3: Build up execution
        ctx.executed_skills.append("exposure")
        ctx.services.append("80/tcp open http")
        next_skill = choose_skill(ctx, registry)
        print(f"✓ After exposure: {next_skill}")
        
        # Test 4: All skills executed
        ctx.executed_skills = registry.list_skills()
        next_skill = choose_skill(ctx, registry)
        print(f"✓ All executed: {next_skill}")
        assert next_skill == "report", f"Expected 'report', got '{next_skill}'"
        
        print("\n✅ Planner logic working correctly!\n")
        return True
    except Exception as e:
        print(f"\n❌ Planner test failed: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def test_engine_execution():
    """Test Engine execution with a minimal run"""
    print("\n" + "="*70)
    print("TEST 6: Verifying Engine Execution...")
    print("="*70)
    
    try:
        from core.context import Context
        from core.registry import Registry
        from core.loader import load_skills
        from core.engine import Engine
        
        ctx = Context("example.com")
        registry = Registry()
        registry = load_skills(registry)
        
        print(f"✓ Setup: {len(registry)} skills loaded")
        
        engine = Engine(registry)
        print(f"✓ Engine created")
        
        # Run engine
        result = engine.run(ctx)
        
        print(f"\n✓ Engine execution completed:")
        print(f"  - Execution count: {engine.execution_count}")
        print(f"  - Skills executed: {len(result.executed_skills)}")
        print(f"  - Executed: {result.executed_skills}")
        print(f"  - Findings collected: {len(result.findings)}")
        print(f"  - Errors: {len(result.errors)}")
        print(f"  - Total time: {result.get_execution_time():.2f}s")
        
        # Verify context was updated
        assert len(result.executed_skills) > 0, "No skills executed"
        assert len(result.subdomains) > 0, "Subdomains not populated"
        assert len(result.services) > 0, "Services not populated"
        assert len(result.findings) > 0, "Findings not populated"
        assert result.report, "Report not generated"
        
        print(f"\n✓ Context updates verified:")
        print(f"  - Subdomains: {len(result.subdomains)}")
        print(f"  - Services: {len(result.services)}")
        print(f"  - Findings: {len(result.findings)}")
        print(f"  - Report: {result.report}")
        
        print("\n✅ Engine execution working correctly!\n")
        return True
    except Exception as e:
        print(f"\n❌ Engine test failed: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def test_full_run():
    """Test a complete run from import to report"""
    print("\n" + "="*70)
    print("TEST 7: Full Integration Test")
    print("="*70)
    
    try:
        from core.context import Context
        from core.registry import Registry
        from core.loader import load_skills
        from core.engine import Engine
        from main import format_report
        
        # Create and run
        ctx = Context("testdomain.io")
        registry = Registry()
        registry = load_skills(registry)
        engine = Engine(registry)
        result = engine.run(ctx)
        
        # Generate report
        report = format_report(result)
        
        print(f"✓ Full run completed")
        print(f"  - Target: {result.target}")
        print(f"  - Skills executed: {len(result.executed_skills)}/7")
        print(f"  - Total findings: {len(result.findings)}")
        print(f"  - Report length: {len(report)} characters")
        
        # Verify report content
        assert result.target in report, "Target not in report"
        assert str(len(result.findings)) in report, "Findings count not in report"
        
        print(f"\n✓ Report generated successfully")
        print(f"\nSample report output:")
        print(report[:500] + "...\n")
        
        print("✅ Full integration test passed!\n")
        return True
    except Exception as e:
        print(f"\n❌ Full integration test failed: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "#"*70)
    print("#  BUG-BOUNTY-AI - SYSTEM VERIFICATION TEST SUITE")
    print("#"*70)
    
    tests = [
        ("Imports", test_imports),
        ("Context", test_context),
        ("Registry", test_registry),
        ("Skill Loading", test_skill_loading),
        ("Planner Logic", test_planner),
        ("Engine Execution", test_engine_execution),
        ("Full Integration", test_full_run),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {str(e)}")
            results[test_name] = False
    
    # Summary
    print("\n" + "#"*70)
    print("#  TEST SUMMARY")
    print("#"*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    print(f"\n  Total: {passed}/{total} tests passed\n")
    
    # Print captured logs
    print("\n" + "#"*70)
    print("#  DETAILED LOG OUTPUT")
    print("#"*70 + "\n")
    print(log_stream.getvalue())
    
    if passed == total:
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED - SYSTEM IS READY TO USE!")
        print("="*70 + "\n")
        return 0
    else:
        print("\n" + "="*70)
        print(f"❌ {total - passed} TEST(S) FAILED - REVIEW ERRORS ABOVE")
        print("="*70 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
