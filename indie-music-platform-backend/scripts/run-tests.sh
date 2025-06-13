#!/bin/bash
set -e

# インディーズミュージックプラットフォーム包括的テストランナー
# Comprehensive Test Runner for Indie Music Platform

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default values
COVERAGE_THRESHOLD=70
VERBOSE=false
PARALLEL=false
REPORT_DIR="test-reports"
RUN_SECURITY=true
RUN_BOUNDARY=true
RUN_VALIDATION=true
RUN_COMPREHENSIVE=true

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_section() {
    echo -e "\n${PURPLE}=== $1 ===${NC}"
}

# Function to show usage
show_usage() {
    cat << EOF
🎵 Indie Music Platform Test Runner

Usage: $0 [options]

Options:
    -h, --help              Show this help message
    -v, --verbose           Enable verbose output
    -p, --parallel          Run tests in parallel
    -c, --coverage NUM      Set coverage threshold (default: 70)
    --no-security          Skip security tests
    --no-boundary          Skip boundary/edge case tests
    --no-validation        Skip data validation tests
    --no-comprehensive     Skip comprehensive API tests
    --unit-only            Run only unit and integration tests
    --security-only        Run only security tests
    --quick                Run quick test suite (unit + integration)
    --full                 Run full test suite with all categories
    --report-dir DIR       Set report output directory (default: test-reports)

Examples:
    $0                     # Run standard test suite
    $0 --quick             # Quick tests only
    $0 --security-only     # Security tests only
    $0 --full -v -p        # Full suite, verbose, parallel
    $0 --coverage 80       # Require 80% coverage

Test Categories:
    📋 Unit & Integration  - Core functionality tests
    🔒 Security           - OWASP Top 10 vulnerability tests
    ⚡ Boundary           - Edge cases and limit testing
    📊 Validation         - Input validation and data integrity
    🌐 Comprehensive      - Full API endpoint coverage
EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -p|--parallel)
            PARALLEL=true
            shift
            ;;
        -c|--coverage)
            COVERAGE_THRESHOLD="$2"
            shift 2
            ;;
        --no-security)
            RUN_SECURITY=false
            shift
            ;;
        --no-boundary)
            RUN_BOUNDARY=false
            shift
            ;;
        --no-validation)
            RUN_VALIDATION=false
            shift
            ;;
        --no-comprehensive)
            RUN_COMPREHENSIVE=false
            shift
            ;;
        --unit-only)
            RUN_SECURITY=false
            RUN_BOUNDARY=false
            RUN_VALIDATION=false
            RUN_COMPREHENSIVE=false
            shift
            ;;
        --security-only)
            RUN_BOUNDARY=false
            RUN_VALIDATION=false
            RUN_COMPREHENSIVE=false
            shift
            ;;
        --quick)
            RUN_SECURITY=false
            RUN_BOUNDARY=false
            RUN_COMPREHENSIVE=false
            shift
            ;;
        --full)
            RUN_SECURITY=true
            RUN_BOUNDARY=true
            RUN_VALIDATION=true
            RUN_COMPREHENSIVE=true
            shift
            ;;
        --report-dir)
            REPORT_DIR="$2"
            shift 2
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Check if we're in the correct directory
if [[ ! -f "pyproject.toml" ]] || [[ ! -d "app" ]]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Setup
print_section "🚀 Test Environment Setup"

# Create report directory
mkdir -p "$REPORT_DIR"
print_status "Created report directory: $REPORT_DIR"

# Set test environment variables
export TESTING=True
export DATABASE_URL="sqlite:///:memory:"
export SECRET_KEY="test_secret_key_for_test_runner"
export FIREBASE_CREDENTIALS_PATH="tests/mocks/firebase_credentials.json"
export FIREBASE_API_KEY="test_api_key"
export S3_BUCKET_NAME="test-bucket"
export S3_REGION="ap-northeast-1"
export STRIPE_API_KEY="sk_test_dummy"
export STRIPE_WEBHOOK_SECRET="whsec_test_dummy"

print_status "Environment variables configured"

# Build pytest command
PYTEST_CMD="pytest"

# Add verbosity
if [[ "$VERBOSE" == "true" ]]; then
    PYTEST_CMD="$PYTEST_CMD -v"
else
    PYTEST_CMD="$PYTEST_CMD -q"
fi

# Add parallel execution
if [[ "$PARALLEL" == "true" ]]; then
    PYTEST_CMD="$PYTEST_CMD -n auto"
fi

# Coverage options
PYTEST_CMD="$PYTEST_CMD --cov=app --cov-report=html:$REPORT_DIR/htmlcov --cov-report=xml:$REPORT_DIR/coverage.xml --cov-report=term-missing --cov-fail-under=$COVERAGE_THRESHOLD"

# Test execution tracking
declare -a PASSED_SUITES=()
declare -a FAILED_SUITES=()
declare -a SKIPPED_SUITES=()

# Function to run test suite
run_test_suite() {
    local suite_name="$1"
    local test_path="$2"
    local description="$3"
    local continue_on_error="${4:-true}"
    
    print_section "$description"
    
    local report_file="$REPORT_DIR/${suite_name}-report.html"
    local full_cmd="$PYTEST_CMD $test_path --html=$report_file --self-contained-html"
    
    print_status "Running: $full_cmd"
    
    if eval "$full_cmd"; then
        print_success "$suite_name tests passed"
        PASSED_SUITES+=("$suite_name")
    else
        print_error "$suite_name tests failed"
        FAILED_SUITES+=("$suite_name")
        
        if [[ "$continue_on_error" == "false" ]]; then
            print_error "Stopping due to test failure"
            exit 1
        fi
    fi
}

# Main test execution
print_section "🧪 Running Test Suites"

# Always run unit and integration tests first
run_test_suite "unit-integration" "tests/api/ tests/services/" "📋 Unit & Integration Tests" false

# Run additional test suites based on flags
if [[ "$RUN_SECURITY" == "true" ]]; then
    run_test_suite "security" "tests/security/" "🔒 Security Vulnerability Tests" true
else
    SKIPPED_SUITES+=("security")
fi

if [[ "$RUN_BOUNDARY" == "true" ]]; then
    run_test_suite "boundary" "tests/edge_cases/" "⚡ Boundary & Edge Case Tests" true
else
    SKIPPED_SUITES+=("boundary")
fi

if [[ "$RUN_VALIDATION" == "true" ]]; then
    run_test_suite "validation" "tests/validation/" "📊 Data Validation Tests" true
else
    SKIPPED_SUITES+=("validation")
fi

if [[ "$RUN_COMPREHENSIVE" == "true" ]]; then
    run_test_suite "comprehensive" "tests/comprehensive/" "🌐 Comprehensive API Tests" true
else
    SKIPPED_SUITES+=("comprehensive")
fi

# Generate final report
print_section "📊 Test Results Summary"

echo "Test Execution Summary:"
echo "======================"

if [[ ${#PASSED_SUITES[@]} -gt 0 ]]; then
    print_success "Passed Test Suites (${#PASSED_SUITES[@]}):"
    for suite in "${PASSED_SUITES[@]}"; do
        echo -e "  ${GREEN}✓${NC} $suite"
    done
fi

if [[ ${#FAILED_SUITES[@]} -gt 0 ]]; then
    print_error "Failed Test Suites (${#FAILED_SUITES[@]}):"
    for suite in "${FAILED_SUITES[@]}"; do
        echo -e "  ${RED}✗${NC} $suite"
    done
fi

if [[ ${#SKIPPED_SUITES[@]} -gt 0 ]]; then
    print_warning "Skipped Test Suites (${#SKIPPED_SUITES[@]}):"
    for suite in "${SKIPPED_SUITES[@]}"; do
        echo -e "  ${YELLOW}○${NC} $suite"
    done
fi

# Generate summary file
cat > "$REPORT_DIR/summary.txt" << EOF
Indie Music Platform Test Results Summary
========================================

Execution Date: $(date)
Coverage Threshold: $COVERAGE_THRESHOLD%

Test Suites:
- Passed: ${#PASSED_SUITES[@]}
- Failed: ${#FAILED_SUITES[@]}
- Skipped: ${#SKIPPED_SUITES[@]}

Passed Suites: ${PASSED_SUITES[*]}
Failed Suites: ${FAILED_SUITES[*]}
Skipped Suites: ${SKIPPED_SUITES[*]}

Report Files:
- HTML Coverage: $REPORT_DIR/htmlcov/index.html
- XML Coverage: $REPORT_DIR/coverage.xml
- Individual test reports: $REPORT_DIR/*-report.html
EOF

print_success "Summary saved to: $REPORT_DIR/summary.txt"

# Coverage report info
if [[ -f "$REPORT_DIR/htmlcov/index.html" ]]; then
    print_success "Coverage report available at: $REPORT_DIR/htmlcov/index.html"
fi

# Final status
echo
if [[ ${#FAILED_SUITES[@]} -eq 0 ]]; then
    print_success "🎉 All executed test suites passed!"
    exit 0
else
    print_error "❌ Some test suites failed. Check individual reports for details."
    exit 1
fi