#!/usr/bin/env python3
"""
Test Suite for VGT Repository
Verifies all components are working correctly
"""

import os
import sys
import importlib.util

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    modules = [
        'simulations.wave_1d',
        'simulations.wave_2d',
        'analysis.dispersion'
    ]
    
    failed = []
    for module in modules:
        try:
            spec = importlib.util.find_spec(module)
            if spec is None:
                failed.append(module)
                print(f"  ✗ {module} - not found")
            else:
                print(f"  ✓ {module}")
        except Exception as e:
            failed.append(module)
            print(f"  ✗ {module} - {str(e)}")
    
    return len(failed) == 0

def test_files():
    """Test that all required files exist."""
    print("\nTesting file structure...")
    
    required_files = [
        'README.md',
        'requirements.txt',
        'LICENSE',
        'CONTRIBUTING.md',
        '.gitignore',
        'thesis/Vibrational_Gravity_Thesis_Complete.md',
        'thesis/Appendix_A.md',
        'thesis/figures/measured_vs_theoretical_dispersion.png',
        'thesis/figures/phase_space_portrait.png',
        'thesis/figures/fourier_spectrum_evolution.png',
        'simulations/wave_1d.py',
        'simulations/wave_2d.py',
        'analysis/dispersion.py',
        'experiments/experimental_protocols.md',
        'docs/quick_start.md',
        'docs/VGT_Funding_Proposal_Templeton.md',
        'examples/complete_demo.py'
    ]
    
    missing = []
    for file in required_files:
        filepath = os.path.join(os.path.dirname(__file__), file)
        if os.path.exists(filepath):
            print(f"  ✓ {file}")
        else:
            missing.append(file)
            print(f"  ✗ {file} - missing")
    
    return len(missing) == 0

def test_directories():
    """Test that all required directories exist."""
    print("\nTesting directories...")
    
    required_dirs = [
        'thesis',
        'thesis/figures',
        'simulations',
        'analysis',
        'experiments',
        'data',
        'data/1d_results',
        'data/2d_results',
        'docs',
        'examples'
    ]
    
    missing = []
    for dir in required_dirs:
        dirpath = os.path.join(os.path.dirname(__file__), dir)
        if os.path.isdir(dirpath):
            print(f"  ✓ {dir}/")
        else:
            missing.append(dir)
            print(f"  ✗ {dir}/ - missing")
    
    return len(missing) == 0

def test_quick_simulation():
    """Run a quick simulation to verify functionality."""
    print("\nTesting quick simulation...")
    
    try:
        # Add parent directory to path
        sys.path.insert(0, os.path.dirname(__file__))
        
        # Try both import methods
        try:
            from simulations.wave_1d import VGTSimulation1D
        except:
            from simulations import VGTSimulation1D
        
        # Run minimal simulation
        sim = VGTSimulation1D(L=5.0, Nx=50, omega0=2.0)
        sim.simulate(Nt=10, save_every=5)
        
        # Check results
        if len(sim.phi_history) > 0 and len(sim.max_amplitude) > 0:
            print("  ✓ Simulation completed successfully")
            print(f"    - Generated {len(sim.phi_history)} snapshots")
            print(f"    - Max amplitude: {max(sim.max_amplitude):.4f}")
            return True
        else:
            print("  ✗ Simulation failed - no data generated")
            return False
            
    except Exception as e:
        print(f"  ✗ Simulation failed - {str(e)}")
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("VGT REPOSITORY TEST SUITE")
    print("=" * 50)
    
    # Change to repository root
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run tests
    results = []
    results.append(("File structure", test_files()))
    results.append(("Directories", test_directories()))
    results.append(("Imports", test_imports()))
    results.append(("Quick simulation", test_quick_simulation()))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results:
        status = "PASSED" if passed else "FAILED"
        symbol = "✓" if passed else "✗"
        print(f"{symbol} {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("ALL TESTS PASSED! Repository is ready for use.")
        print("\nNext steps:")
        print("1. Run 'python examples/complete_demo.py' for full demonstration")
        print("2. Read docs/quick_start.md for usage guide")
        print("3. Check thesis/Vibrational_Gravity_Thesis_Complete.md for theory")
    else:
        print("SOME TESTS FAILED. Please check the errors above.")
        print("\nCommon fixes:")
        print("1. Run 'pip install -r requirements.txt'")
        print("2. Ensure all files were properly copied")
        print("3. Check Python version (requires 3.8+)")
    
    print("=" * 50)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
