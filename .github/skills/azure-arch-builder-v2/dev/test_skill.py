#!/usr/bin/env python3
"""
Azure Arch Builder v2 — E2E Skill Test Framework

Usage:
  python test_skill.py --setup           # Create test directories
  python test_skill.py --validate        # Validate all phase outputs
  python test_skill.py --validate --scenario 1-1  # Validate specific scenario
  python test_skill.py --report          # Generate FIX_REPORT.md

The actual Phase simulation (1→2→3→4) is performed by GHCP sub-agents.
This script handles: scenario definitions, output validation, logging, report generation.
"""

import argparse
import json
import os
import sys
import datetime
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent  # azure-arch-builder-v2/
DEV_DIR = SKILL_ROOT / "dev"
RESULTS_DIR = DEV_DIR / "test-results"
SCRIPTS_DIR = SKILL_ROOT / "scripts"

# ────────────────────────────────────────────────
# 7 Sub-Scenarios
# ────────────────────────────────────────────────
SCENARIOS = {
    "1-1-basic-rag-default": {
        "name": "Basic RAG (Default)",
        "group": 1,
        "user_request": "RAG 챗봇 만들고 싶어",
        "user_choices": [
            {"question_pattern": "지역|region|location", "answer": "East US 2"},
            {"question_pattern": "SKU|티어|tier", "answer": "기본 권장 사항으로"},
            {"question_pattern": "이름|프로젝트|name", "answer": "my-rag-chatbot"},
        ],
        "expected_path": "A",
        "expected_services": {
            "required_types": ["ai_foundry", "ai_search", "storage", "keyvault"],
            "min_count": 4,
            "max_count": 8,
        },
        "expected_connections": {
            "min_count": 3,
        },
    },
    "1-2-basic-rag-korea": {
        "name": "Basic RAG (Korea, Upper SKU)",
        "group": 1,
        "user_request": "RAG 챗봇 만들고 싶어",
        "user_choices": [
            {"question_pattern": "지역|region|location", "answer": "Korea Central"},
            {"question_pattern": "SKU|티어|tier", "answer": "상위 SKU로 (S2 Search, GPT-4o)"},
            {"question_pattern": "이름|프로젝트|name", "answer": "rag-korea-prod"},
        ],
        "expected_path": "A",
        "expected_services": {
            "required_types": ["ai_foundry", "ai_search", "storage", "keyvault"],
            "min_count": 4,
            "max_count": 8,
        },
        "expected_connections": {
            "min_count": 3,
        },
    },
    "1-3-basic-rag-auto": {
        "name": "Basic RAG (Ambiguous - 알아서 해줘)",
        "group": 1,
        "user_request": "RAG 챗봇 만들고 싶어",
        "user_choices": [
            {"question_pattern": ".*", "answer": "알아서 해줘"},
        ],
        "expected_path": "A",
        "expected_services": {
            "required_types": ["ai_foundry", "ai_search", "storage", "keyvault"],
            "min_count": 4,
            "max_count": 8,
        },
        "expected_connections": {
            "min_count": 3,
        },
    },
    "2-1-private-rag-default": {
        "name": "Private RAG (Default VNet)",
        "group": 2,
        "user_request": "프라이빗 엔드포인트 포함해서 RAG 챗봇 만들어줘",
        "user_choices": [
            {"question_pattern": "지역|region|location", "answer": "East US 2"},
            {"question_pattern": "VNet|네트워크|CIDR", "answer": "기본 설정으로"},
            {"question_pattern": "이름|프로젝트|name", "answer": "private-rag"},
        ],
        "expected_path": "A",
        "expected_services": {
            "required_types": ["ai_foundry", "ai_search", "storage", "keyvault"],
            "min_count": 5,
            "max_count": 15,
            "must_have_private": True,
        },
        "expected_connections": {
            "min_count": 3,
            "must_have_type": "private",
        },
        "expected_vnet": True,
    },
    "2-2-private-rag-custom-vnet": {
        "name": "Private RAG (Custom VNet CIDR)",
        "group": 2,
        "user_request": "프라이빗 엔드포인트 포함해서 RAG 챗봇 만들어줘",
        "user_choices": [
            {"question_pattern": "지역|region|location", "answer": "East US 2"},
            {"question_pattern": "VNet|네트워크|CIDR", "answer": "10.1.0.0/16, PE 서브넷은 10.1.1.0/24"},
            {"question_pattern": "이름|프로젝트|name", "answer": "private-rag-custom"},
        ],
        "expected_path": "A",
        "expected_services": {
            "required_types": ["ai_foundry", "ai_search", "storage", "keyvault"],
            "min_count": 5,
            "max_count": 15,
            "must_have_private": True,
        },
        "expected_connections": {
            "min_count": 3,
            "must_have_type": "private",
        },
        "expected_vnet": True,
        "expected_vnet_cidr": "10.1.0.0/16",
    },
    "3-1-webapp-basic": {
        "name": "Web App (Basic)",
        "group": 3,
        "user_request": "App Service로 웹 애플리케이션 만들어줘",
        "user_choices": [
            {"question_pattern": "지역|region|location", "answer": "East US 2"},
            {"question_pattern": "DB|데이터베이스|database", "answer": "Azure SQL Database"},
            {"question_pattern": "이름|프로젝트|name", "answer": "my-webapp"},
        ],
        "expected_path": "A",
        "expected_services": {
            "required_types": ["app_service", "sql_database"],
            "min_count": 2,
            "max_count": 6,
        },
        "expected_connections": {
            "min_count": 1,
        },
    },
    "3-2-webapp-add-cache": {
        "name": "Web App (Add Cache Mid-conversation)",
        "group": 3,
        "user_request": "App Service로 웹 애플리케이션 만들어줘",
        "user_choices": [
            {"question_pattern": "지역|region|location", "answer": "East US 2"},
            {"question_pattern": "DB|데이터베이스|database", "answer": "Azure SQL Database"},
            {"question_pattern": "이름|프로젝트|name", "answer": "my-webapp-cached"},
            {"question_pattern": "확정|확인|proceed|괜찮", "answer": "캐시도 넣어줘. Redis 추가해"},
        ],
        "expected_path": "A",
        "expected_services": {
            "required_types": ["app_service", "sql_database", "redis"],
            "min_count": 3,
            "max_count": 7,
        },
        "expected_connections": {
            "min_count": 2,
        },
    },
}


# ────────────────────────────────────────────────
# Validation Functions
# ────────────────────────────────────────────────

def validate_phase1(scenario_id, scenario):
    """Validate Phase 1 output (architecture design JSON)."""
    result_dir = RESULTS_DIR / scenario_id
    output_file = result_dir / "phase1_output.json"
    issues = []

    if not output_file.exists():
        return [f"CRITICAL: phase1_output.json not found in {result_dir}"]

    try:
        data = json.loads(output_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"CRITICAL: phase1_output.json is invalid JSON: {e}"]

    # Check services
    services = data.get("services", [])
    if not isinstance(services, list):
        issues.append("CRITICAL: 'services' is not a list")
        return issues

    expected = scenario["expected_services"]

    # Count check
    if len(services) < expected["min_count"]:
        issues.append(f"WARN: Only {len(services)} services, expected at least {expected['min_count']}")
    if len(services) > expected["max_count"]:
        issues.append(f"WARN: {len(services)} services, expected at most {expected['max_count']}")

    # Required types check
    actual_types = {s.get("type", "").lower() for s in services}
    for req_type in expected["required_types"]:
        if req_type not in actual_types:
            # Also check common aliases
            aliases = {
                "ai_foundry": ["ai_foundry", "foundry", "openai", "cognitive"],
                "ai_search": ["ai_search", "search", "cognitive_search"],
                "storage": ["storage", "adls", "blob", "storage_account"],
                "keyvault": ["keyvault", "key_vault", "kv"],
                "app_service": ["app_service", "appservice", "webapp"],
                "sql_database": ["sql_database", "sql", "sql_server", "azure_sql"],
                "redis": ["redis", "redis_cache", "cache"],
            }
            found = False
            for alias in aliases.get(req_type, []):
                if alias in actual_types:
                    found = True
                    break
            if not found:
                issues.append(f"CRITICAL: Required service type '{req_type}' not found. Actual types: {actual_types}")

    # Schema check for each service
    required_fields = ["id", "name", "type"]
    for i, svc in enumerate(services):
        for field in required_fields:
            if field not in svc:
                issues.append(f"WARN: Service [{i}] missing field '{field}'")

    # Private check
    if expected.get("must_have_private"):
        private_services = [s for s in services if s.get("private") is True]
        if len(private_services) == 0:
            issues.append("CRITICAL: Expected private services but none found")

    # Connections check
    connections = data.get("connections", [])
    if not isinstance(connections, list):
        issues.append("CRITICAL: 'connections' is not a list")
    else:
        exp_conn = scenario["expected_connections"]
        if len(connections) < exp_conn["min_count"]:
            issues.append(f"WARN: Only {len(connections)} connections, expected at least {exp_conn['min_count']}")

        # Connection type check
        if exp_conn.get("must_have_type"):
            conn_types = {c.get("type", "").lower() for c in connections}
            if exp_conn["must_have_type"] not in conn_types:
                issues.append(f"WARN: Expected connection type '{exp_conn['must_have_type']}' not found")

        # Validate from/to reference valid service IDs
        service_ids = {s.get("id") for s in services}
        for j, conn in enumerate(connections):
            if conn.get("from") not in service_ids:
                issues.append(f"WARN: Connection [{j}] 'from'='{conn.get('from')}' not in service IDs")
            if conn.get("to") not in service_ids:
                issues.append(f"WARN: Connection [{j}] 'to'='{conn.get('to')}' not in service IDs")

    # VNet check
    if scenario.get("expected_vnet"):
        vnet_info = data.get("vnet_info", "")
        if not vnet_info:
            issues.append("WARN: Expected VNet info but none found")
        if scenario.get("expected_vnet_cidr"):
            if scenario["expected_vnet_cidr"] not in str(vnet_info):
                issues.append(f"WARN: Expected VNet CIDR '{scenario['expected_vnet_cidr']}' not in vnet_info")

    return issues


def validate_phase2(scenario_id):
    """Validate Phase 2 output (Bicep compilation)."""
    result_dir = RESULTS_DIR / scenario_id
    bicep_dir = result_dir / "phase2_bicep"
    compile_log = result_dir / "phase2_compile.log"
    issues = []

    if not bicep_dir.exists():
        return ["CRITICAL: phase2_bicep/ directory not found"]

    main_bicep = bicep_dir / "main.bicep"
    if not main_bicep.exists():
        issues.append("CRITICAL: main.bicep not found in phase2_bicep/")

    # Check compile log
    if compile_log.exists():
        log_text = compile_log.read_text(encoding="utf-8")
        if "ERROR" in log_text.upper() or "error" in log_text:
            # Filter out just warnings vs actual errors
            lines = log_text.strip().split("\n")
            error_lines = [l for l in lines if "error" in l.lower() and "warning" not in l.lower()]
            if error_lines:
                issues.append(f"CRITICAL: Bicep compile errors: {'; '.join(error_lines[:3])}")
        if "Build succeeded" in log_text or log_text.strip() == "":
            pass  # OK
    else:
        issues.append("WARN: phase2_compile.log not found (compile not run?)")

    # Check modules directory
    modules_dir = bicep_dir / "modules"
    if not modules_dir.exists():
        issues.append("WARN: modules/ directory not found (all-in-one bicep?)")

    return issues


def validate_phase3(scenario_id):
    """Validate Phase 3 output (Bicep review)."""
    result_dir = RESULTS_DIR / scenario_id
    review_log = result_dir / "phase3_review.log"
    issues = []

    if not review_log.exists():
        return ["WARN: phase3_review.log not found (review not run?)"]

    log_text = review_log.read_text(encoding="utf-8")
    if "CRITICAL" in log_text or "FAIL" in log_text.upper():
        issues.append(f"CRITICAL: Review found critical issues")
    if not log_text.strip():
        issues.append("WARN: phase3_review.log is empty")

    return issues


def validate_phase4(scenario_id):
    """Validate Phase 4 output (deployment validate)."""
    result_dir = RESULTS_DIR / scenario_id
    validate_log = result_dir / "phase4_validate.log"
    issues = []

    if not validate_log.exists():
        return ["INFO: phase4_validate.log not found (validate not run — needs Azure subscription)"]

    log_text = validate_log.read_text(encoding="utf-8")
    if "error" in log_text.lower():
        issues.append(f"CRITICAL: Deployment validate failed")
    if "Succeeded" in log_text or "succeeded" in log_text:
        pass  # OK

    return issues


def validate_diagram(scenario_id):
    """Validate diagram output."""
    result_dir = RESULTS_DIR / scenario_id
    html_file = result_dir / "diagram.html"
    png_file = result_dir / "diagram.png"
    issues = []

    if not html_file.exists():
        return ["WARN: diagram.html not found"]

    html_text = html_file.read_text(encoding="utf-8")
    if len(html_text) < 1000:
        issues.append("WARN: diagram.html is suspiciously small")

    # Check for error indicators in HTML
    if "Error" in html_text[:500] or "error" in html_text[:500]:
        issues.append("WARN: diagram.html may contain errors")

    if not png_file.exists():
        issues.append("INFO: diagram.png not found (screenshot not taken)")

    return issues


# ────────────────────────────────────────────────
# Main Commands
# ────────────────────────────────────────────────

def cmd_setup():
    """Create all test result directories."""
    print("=== Setting up test directories ===")
    for scenario_id in SCENARIOS:
        d = RESULTS_DIR / scenario_id
        d.mkdir(parents=True, exist_ok=True)
        (d / "phase2_bicep").mkdir(exist_ok=True)
        print(f"  Created: {d.relative_to(DEV_DIR)}")
    print(f"\nTotal: {len(SCENARIOS)} scenarios ready")
    print(f"Results dir: {RESULTS_DIR}")


def cmd_validate(target_scenario=None):
    """Run validation on all (or specific) scenario outputs."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    all_results = {}

    scenarios_to_check = SCENARIOS
    if target_scenario:
        scenarios_to_check = {k: v for k, v in SCENARIOS.items() if target_scenario in k}
        if not scenarios_to_check:
            print(f"ERROR: No scenario matching '{target_scenario}'")
            return

    print(f"=== Validating {len(scenarios_to_check)} scenarios ({timestamp}) ===\n")

    for scenario_id, scenario in scenarios_to_check.items():
        print(f"--- [{scenario_id}] {scenario['name']} ---")
        result = {
            "phase1": validate_phase1(scenario_id, scenario),
            "phase2": validate_phase2(scenario_id),
            "phase3": validate_phase3(scenario_id),
            "phase4": validate_phase4(scenario_id),
            "diagram": validate_diagram(scenario_id),
        }
        all_results[scenario_id] = result

        for phase, issues in result.items():
            if not issues:
                print(f"  {phase}: PASS")
            else:
                for issue in issues:
                    severity = issue.split(":")[0]
                    symbol = {"CRITICAL": "X", "WARN": "!", "INFO": "i"}.get(severity, "?")
                    print(f"  {phase}: [{symbol}] {issue}")

        # Overall status
        all_issues = [i for issues in result.values() for i in issues]
        criticals = [i for i in all_issues if i.startswith("CRITICAL")]
        warns = [i for i in all_issues if i.startswith("WARN")]
        if criticals:
            print(f"  => FAIL ({len(criticals)} critical, {len(warns)} warnings)\n")
        elif warns:
            print(f"  => PASS with warnings ({len(warns)})\n")
        else:
            print(f"  => PASS\n")

        # Save summary log
        summary_path = RESULTS_DIR / scenario_id / "test_summary.log"
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(f"Test: {scenario_id} ({scenario['name']})\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"User Request: {scenario['user_request']}\n\n")
            for phase, issues in result.items():
                f.write(f"[{phase}]\n")
                if not issues:
                    f.write("  PASS\n")
                else:
                    for issue in issues:
                        f.write(f"  {issue}\n")
                f.write("\n")

    return all_results


def cmd_report():
    """Generate FIX_REPORT.md from validation results."""
    print("=== Generating FIX_REPORT.md ===\n")
    results = cmd_validate()
    if not results:
        return

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_path = RESULTS_DIR / "FIX_REPORT.md"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# Skill Test Fix Report\n\n")
        f.write(f"Generated: {timestamp}\n\n")

        # Summary table
        f.write("## Summary\n\n")
        f.write("| Scenario | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Diagram | Overall |\n")
        f.write("|----------|---------|---------|---------|---------|---------|--------|\n")

        fix_items = []

        for scenario_id, result in results.items():
            row = [scenario_id]
            overall = "PASS"
            for phase in ["phase1", "phase2", "phase3", "phase4", "diagram"]:
                issues = result[phase]
                criticals = [i for i in issues if i.startswith("CRITICAL")]
                warns = [i for i in issues if i.startswith("WARN")]
                infos = [i for i in issues if i.startswith("INFO")]
                if criticals:
                    row.append(f"FAIL ({len(criticals)})")
                    overall = "FAIL"
                    for c in criticals:
                        fix_items.append((scenario_id, phase, c))
                elif warns:
                    row.append(f"WARN ({len(warns)})")
                    if overall != "FAIL":
                        overall = "WARN"
                    for w in warns:
                        fix_items.append((scenario_id, phase, w))
                elif infos:
                    row.append("SKIP")
                else:
                    row.append("PASS")
            row.append(overall)
            f.write("| " + " | ".join(row) + " |\n")

        # Fix items
        if fix_items:
            f.write(f"\n## Issues Found ({len(fix_items)})\n\n")
            for i, (scenario_id, phase, issue) in enumerate(fix_items, 1):
                scenario = SCENARIOS[scenario_id]
                f.write(f"### {i}. [{scenario_id}] {phase}\n\n")
                f.write(f"- **Scenario**: {scenario['name']}\n")
                f.write(f"- **User Request**: {scenario['user_request']}\n")
                f.write(f"- **Issue**: {issue}\n")
                f.write(f"- **Fix Suggestion**: _To be filled after analysis_\n\n")
        else:
            f.write("\n## No Issues Found\n\nAll scenarios passed validation.\n")

    print(f"\nFIX_REPORT.md generated at: {report_path}")


def cmd_list():
    """List all scenarios."""
    print("=== Test Scenarios ===\n")
    for scenario_id, scenario in SCENARIOS.items():
        result_dir = RESULTS_DIR / scenario_id
        has_p1 = (result_dir / "phase1_output.json").exists()
        has_p2 = (result_dir / "phase2_bicep" / "main.bicep").exists()
        has_diag = (result_dir / "diagram.html").exists()
        status = []
        if has_p1: status.append("P1")
        if has_p2: status.append("P2")
        if has_diag: status.append("DG")
        status_str = ",".join(status) if status else "empty"
        print(f"  [{scenario_id}] {scenario['name']}")
        print(f"    Request: {scenario['user_request']}")
        print(f"    Status: [{status_str}]")
        print()


def cmd_prompt(scenario_id, phase):
    """Print the prompt that should be sent to a sub-agent for a given scenario+phase."""
    if scenario_id not in SCENARIOS:
        print(f"ERROR: Unknown scenario '{scenario_id}'")
        return

    scenario = SCENARIOS[scenario_id]

    if phase == "1":
        choices_text = "\n".join([
            f"  - If asked about '{c['question_pattern']}': answer '{c['answer']}'"
            for c in scenario["user_choices"]
        ])
        print(f"""=== Phase 1 Prompt for [{scenario_id}] ===

You are simulating the Azure Architecture Builder v2 skill's Phase 1 (Architecture Design).

Read the file: {SKILL_ROOT / 'prompts' / 'phase1-advisor.md'}
Also read: {SKILL_ROOT / 'SKILL.md'} for context.

User Request: "{scenario['user_request']}"

Simulate the conversation as if these were the user's answers to follow-up questions:
{choices_text}

OUTPUT REQUIREMENTS:
You must produce a JSON file at: {RESULTS_DIR / scenario_id / 'phase1_output.json'}

The JSON must have this exact structure:
{{
  "architecture_description": "Brief description of the architecture",
  "services": [
    {{
      "id": "unique-id",
      "name": "Display Name",
      "type": "service_type",
      "sku": "SKU if applicable",
      "private": false,
      "details": ["detail1", "detail2"]
    }}
  ],
  "connections": [
    {{
      "from": "service-id-1",
      "to": "service-id-2",
      "label": "Connection Label",
      "type": "api|data|security|private|network|default"
    }}
  ],
  "vnet_info": "VNet CIDR info if applicable, empty string otherwise",
  "hierarchy": []
}}

Valid service types: ai_foundry, ai_search, storage, keyvault, app_service, sql_database, 
redis, cosmos_db, function_app, vm, aks, acr, event_hub, iot_hub, databricks, 
data_factory, fabric, cdn, front_door, app_gateway, vpn_gateway, firewall, 
bastion, nsg, log_analytics, app_insights, devops, stream_analytics

Write the JSON file directly. Do not ask questions — use the simulated answers above.
""")

    elif phase == "2":
        p1_output = RESULTS_DIR / scenario_id / "phase1_output.json"
        bicep_dir = RESULTS_DIR / scenario_id / "phase2_bicep"
        print(f"""=== Phase 2 Prompt for [{scenario_id}] ===

You are simulating the Azure Architecture Builder v2 skill's Phase 2 (Bicep Generation).

Read these files:
1. {SKILL_ROOT / 'prompts' / 'bicep-generator.md'} — Bicep generation rules
2. {p1_output} — Phase 1 architecture output

Generate Bicep code based on the architecture in phase1_output.json.

OUTPUT REQUIREMENTS:
Write all files to: {bicep_dir}/
- main.bicep (orchestration)
- main.bicepparam (parameters)  
- modules/*.bicep (one per service group)

Follow the rules in bicep-generator.md strictly.
Use the latest stable API versions you know.
Location parameter should default to the deployment resource group location.
""")


def main():
    parser = argparse.ArgumentParser(description="Azure Arch Builder v2 — E2E Skill Tester")
    parser.add_argument("--setup", action="store_true", help="Create test directories")
    parser.add_argument("--validate", action="store_true", help="Validate phase outputs")
    parser.add_argument("--report", action="store_true", help="Generate FIX_REPORT.md")
    parser.add_argument("--list", action="store_true", help="List all scenarios")
    parser.add_argument("--prompt", nargs=2, metavar=("SCENARIO", "PHASE"), help="Print sub-agent prompt")
    parser.add_argument("--scenario", type=str, help="Target specific scenario (with --validate)")

    args = parser.parse_args()

    if args.setup:
        cmd_setup()
    elif args.validate:
        cmd_validate(args.scenario)
    elif args.report:
        cmd_report()
    elif args.list:
        cmd_list()
    elif args.prompt:
        cmd_prompt(args.prompt[0], args.prompt[1])
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
