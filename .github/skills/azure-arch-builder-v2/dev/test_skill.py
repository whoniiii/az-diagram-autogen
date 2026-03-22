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
# 7 Sub-Scenarios (Round 1 — Basic)
# ────────────────────────────────────────────────
SCENARIOS_R1 = {
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
# 20 Complex Scenarios (Round 2 — Stress Test)
# ────────────────────────────────────────────────
SCENARIOS_R2 = {
    # ── Level 3: Complex (7 scenarios) ──
    "C01-full-pe-rbac-rag": {
        "name": "Full PE + RBAC Chain RAG",
        "group": "complex",
        "level": 3,
        "user_request": "RAG 챗봇을 만들건데, 모든 서비스에 PE 적용하고 RBAC도 자동으로 설정해줘. Log Analytics도 붙여줘.",
        "user_choices": [
            {"question_pattern": "지역|region", "answer": "East US 2"},
            {"question_pattern": "이름|프로젝트", "answer": "enterprise-rag"},
            {"question_pattern": "SKU|티어", "answer": "운영 환경 수준으로"},
            {"question_pattern": "VNet|CIDR", "answer": "10.0.0.0/16, PE 서브넷 10.0.1.0/24"},
            {"question_pattern": "모니터링|로그", "answer": "Log Analytics + App Insights 둘 다"},
        ],
        "expected_path": "A",
        "expected_services": {
            "required_types": ["ai_foundry", "ai_search", "storage", "keyvault", "log_analytics"],
            "min_count": 6,
            "max_count": 18,
            "must_have_private": True,
        },
        "expected_connections": {
            "min_count": 5,
            "must_have_type": "private",
        },
        "expected_vnet": True,
        "test_focus": ["PE dual DNS (Foundry=2 zones)", "ADLS dual PE (blob+dfs)", "RBAC chain", "Log Analytics"],
    },
    "C02-fabric-capacity-multi-workspace": {
        "name": "Fabric Capacity + Multi-Workspace",
        "group": "complex",
        "level": 3,
        "user_request": "Microsoft Fabric을 만들어줘. 워크스페이스 2개 (dev, prod) 필요하고, ADLS Gen2 연결해줘.",
        "user_choices": [
            {"question_pattern": "지역|region", "answer": "East US 2"},
            {"question_pattern": "이름|프로젝트", "answer": "fabric-analytics"},
            {"question_pattern": "SKU|용량", "answer": "F64"},
            {"question_pattern": "관리자|admin|이메일", "answer": "admin@contoso.com"},
            {"question_pattern": "워크스페이스|workspace", "answer": "dev-workspace, prod-workspace"},
        ],
        "expected_path": "A",
        "expected_services": {
            "required_types": ["fabric", "storage"],
            "min_count": 3,
            "max_count": 8,
        },
        "expected_connections": {
            "min_count": 2,
        },
        "test_focus": ["Fabric admin email required", "Capacity SKU region check", "Workspace dependency"],
    },
    "C03-multi-region-dr": {
        "name": "Multi-Region DR Architecture",
        "group": "complex",
        "level": 3,
        "user_request": "East US에 메인 RAG 시스템 만들고, West Europe에 DR replica도 구성해줘.",
        "user_choices": [
            {"question_pattern": "이름|프로젝트", "answer": "global-rag-dr"},
            {"question_pattern": "모델|GPT", "answer": "GPT-4o 양쪽 리전 모두"},
            {"question_pattern": "장애 복구|failover", "answer": "Active-Passive 구성으로"},
            {"question_pattern": "스토리지|복제", "answer": "GRS 스토리지로 자동 복제"},
        ],
        "expected_path": "A",
        "expected_services": {
            "required_types": ["ai_foundry", "ai_search", "storage", "keyvault"],
            "min_count": 8,
            "max_count": 20,
        },
        "expected_connections": {
            "min_count": 6,
        },
        "test_focus": ["Cross-region model availability", "GRS storage", "Multi-region diagram", "Failover connections"],
    },
    "C04-ampls-monitor-5zone": {
        "name": "AMPLS + Monitor PE (5-Zone DNS)",
        "group": "complex",
        "level": 3,
        "user_request": "Foundry + Storage + Log Analytics를 만들되, 전부 Private Endpoint으로 보호해줘. 모니터링도 PE로.",
        "user_choices": [
            {"question_pattern": "지역|region", "answer": "East US 2"},
            {"question_pattern": "이름|프로젝트", "answer": "secure-monitoring"},
            {"question_pattern": "VNet|CIDR", "answer": "10.0.0.0/16"},
            {"question_pattern": "AMPLS|모니터.*PE", "answer": "네, Azure Monitor Private Link Scope 포함"},
        ],
        "expected_path": "A",
        "expected_services": {
            "required_types": ["ai_foundry", "storage", "keyvault", "log_analytics"],
            "min_count": 5,
            "max_count": 18,
            "must_have_private": True,
        },
        "expected_connections": {
            "min_count": 4,
            "must_have_type": "private",
        },
        "expected_vnet": True,
        "test_focus": ["AMPLS 5 DNS zones", "Monitor PE complexity", "Foundry dual DNS", "ADLS dual PE"],
    },
    "C05-databricks-vnet-injection": {
        "name": "Databricks VNet Injection + PE",
        "group": "complex",
        "level": 3,
        "user_request": "Databricks를 VNet에 주입하고, ADLS Gen2와 Key Vault도 PE로 연결해줘. ETL 파이프라인 구성.",
        "user_choices": [
            {"question_pattern": "지역|region", "answer": "East US 2"},
            {"question_pattern": "이름|프로젝트", "answer": "data-engineering"},
            {"question_pattern": "VNet|CIDR", "answer": "10.0.0.0/16, Databricks 서브넷 2개 포함"},
            {"question_pattern": "ETL|파이프라인", "answer": "Data Factory도 추가해줘"},
        ],
        "expected_path": "A",
        "expected_services": {
            "required_types": ["databricks", "storage", "keyvault", "data_factory"],
            "min_count": 4,
            "max_count": 12,
        },
        "expected_connections": {
            "min_count": 3,
        },
        "expected_vnet": True,
        "test_focus": ["Databricks managed RG", "VNet injection subnets", "ADLS dual PE", "Data Factory PE"],
    },
    "C06-multi-sub-landing-zone": {
        "name": "Multi-Subscription Landing Zone",
        "group": "complex",
        "level": 3,
        "user_request": "Azure Landing Zone 구조로 만들어줘. connectivity 구독에 Hub VNet + Firewall, workload 구독에 AI 서비스.",
        "user_choices": [
            {"question_pattern": "이름|프로젝트", "answer": "enterprise-landing-zone"},
            {"question_pattern": "구독|subscription", "answer": "connectivity-sub, workload-ai-sub"},
            {"question_pattern": "Hub.*VNet|CIDR", "answer": "Hub: 10.0.0.0/16, Spoke: 10.1.0.0/16"},
            {"question_pattern": "방화벽|Firewall", "answer": "Azure Firewall Premium"},
            {"question_pattern": "AI.*서비스", "answer": "Foundry + AI Search + Storage"},
        ],
        "expected_path": "A",
        "expected_services": {
            "required_types": ["firewall", "ai_foundry"],
            "min_count": 6,
            "max_count": 20,
        },
        "expected_connections": {
            "min_count": 4,
        },
        "expected_vnet": True,
        "expected_hierarchy": True,
        "test_focus": ["Multi-subscription hierarchy", "Hub-Spoke VNet", "Cross-sub peering", "Firewall routing"],
    },
    "C07-microservices-aks-full": {
        "name": "Full AKS Microservices",
        "group": "complex",
        "level": 3,
        "user_request": "AKS 기반 마이크로서비스 아키텍처 만들어줘. ACR, Redis, SQL, Key Vault, App Gateway 전부 포함.",
        "user_choices": [
            {"question_pattern": "지역|region", "answer": "East US 2"},
            {"question_pattern": "이름|프로젝트", "answer": "microservices-platform"},
            {"question_pattern": "노드.*수|node.*count", "answer": "3개 노드"},
            {"question_pattern": "네트워크|ingress", "answer": "App Gateway Ingress Controller 사용"},
            {"question_pattern": "PE|프라이빗", "answer": "전부 PE 적용"},
        ],
        "expected_path": "A",
        "expected_services": {
            "required_types": ["aks", "acr", "redis", "sql_database", "keyvault", "app_gateway"],
            "min_count": 6,
            "max_count": 15,
        },
        "expected_connections": {
            "min_count": 5,
        },
        "expected_vnet": True,
        "test_focus": ["AKS + ACR integration", "AGIC ingress", "Multi-service PE", "Redis PE"],
    },

    # ── Level 4: Edge Cases (7 scenarios) ──
    "C08-unknown-service-eventgrid": {
        "name": "Unknown Service Fallback (Event Grid)",
        "group": "edge",
        "level": 4,
        "user_request": "Foundry + Event Grid + Cosmos DB를 만들어줘. Event Grid로 이벤트 처리하고 싶어.",
        "user_choices": [
            {"question_pattern": "지역|region", "answer": "East US 2"},
            {"question_pattern": "이름|프로젝트", "answer": "event-driven-ai"},
            {"question_pattern": "Event Grid.*토픽|topic", "answer": "시스템 토픽으로"},
        ],
        "expected_path": "A",
        "expected_services": {
            "required_types": ["ai_foundry", "cosmos_db"],
            "min_count": 3,
            "max_count": 10,
        },
        "expected_connections": {
            "min_count": 2,
        },
        "test_focus": ["Unknown service fallback workflow", "Event Grid PE mapping", "MS Docs fetch for unknown"],
    },
    "C09-vm-sku-unavailable": {
        "name": "VM SKU Region Unavailable",
        "group": "edge",
        "level": 4,
        "user_request": "Korea Central에 Standard_D4s_v5 VM으로 점프박스 만들어줘. Bastion도 붙여줘.",
        "user_choices": [
            {"question_pattern": "이름|프로젝트", "answer": "jump-server"},
            {"question_pattern": "SKU|대안|alternative", "answer": "그럼 추천해주는 걸로"},
            {"question_pattern": "Bastion|접속", "answer": "Azure Bastion Basic"},
        ],
        "expected_path": "A",
        "expected_services": {
            "required_types": ["vm", "bastion"],
            "min_count": 2,
            "max_count": 8,
        },
        "expected_connections": {
            "min_count": 1,
        },
        "expected_vnet": True,
        "test_focus": ["VM SKU region availability check", "Alternative suggestion", "Bastion subnet requirement"],
    },
    "C10-secure-param-sql-password": {
        "name": "@secure() SQL Password + KV Storage",
        "group": "edge",
        "level": 4,
        "user_request": "SQL Server + App Service + Key Vault 만들어줘. SQL 비밀번호는 Key Vault에 저장해줘.",
        "user_choices": [
            {"question_pattern": "지역|region", "answer": "East US 2"},
            {"question_pattern": "이름|프로젝트", "answer": "secure-webapp"},
            {"question_pattern": "인증|auth", "answer": "Azure AD 전용 인증 사용"},
            {"question_pattern": "비밀번호|password", "answer": "배포 시 입력할게"},
        ],
        "expected_path": "A",
        "expected_services": {
            "required_types": ["sql_database", "app_service", "keyvault"],
            "min_count": 3,
            "max_count": 7,
        },
        "expected_connections": {
            "min_count": 2,
        },
        "test_focus": ["@secure() param handling", "No newGuid() in module", "KV secret storage", "AAD-only auth"],
    },
    "C11-adls-hns-impossible-change": {
        "name": "ADLS Gen2 HNS Retroactive (Impossible)",
        "group": "edge",
        "level": 4,
        "user_request": "기존에 있는 Storage Account에 Data Lake 기능 (HNS) 을 활성화하고 싶어.",
        "user_choices": [
            {"question_pattern": "스토리지|storage.*이름", "answer": "mystorageaccount"},
            {"question_pattern": "새로.*만들|recreate", "answer": "새 계정 만들어줘"},
            {"question_pattern": "이름|프로젝트", "answer": "data-lake-migration"},
        ],
        "expected_path": "B",
        "expected_services": {
            "required_types": ["storage"],
            "min_count": 1,
            "max_count": 5,
        },
        "expected_connections": {
            "min_count": 0,
        },
        "test_focus": ["HNS cannot be changed post-creation", "Must create new account", "Data migration warning"],
    },
    "C12-naming-collision-detection": {
        "name": "Naming Collision (customSubDomainName)",
        "group": "edge",
        "level": 4,
        "user_request": "Foundry 만들어줘. 이름은 'my-ai-service'로 해줘.",
        "user_choices": [
            {"question_pattern": "지역|region", "answer": "East US 2"},
            {"question_pattern": "이름.*고유|unique|충돌", "answer": "그럼 알아서 고유한 이름으로"},
        ],
        "expected_path": "A",
        "expected_services": {
            "required_types": ["ai_foundry", "keyvault"],
            "min_count": 2,
            "max_count": 6,
        },
        "expected_connections": {
            "min_count": 1,
        },
        "test_focus": ["customSubDomainName uniqueness", "uniqueString() enforcement", "Static name rejection"],
    },
    "C13-service-ambiguity-cognitive": {
        "name": "Service Ambiguity (코그니티브 서비스)",
        "group": "edge",
        "level": 4,
        "user_request": "코그니티브 서비스로 AI 만들 거야. 문서 분석이랑 챗봇 둘 다 필요해.",
        "user_choices": [
            {"question_pattern": "서비스.*종류|Foundry|OpenAI|Search", "answer": "Foundry로 챗봇, Document Intelligence로 문서 분석"},
            {"question_pattern": "지역|region", "answer": "East US 2"},
            {"question_pattern": "이름|프로젝트", "answer": "ai-document-chat"},
        ],
        "expected_path": "A",
        "expected_services": {
            "required_types": ["ai_foundry"],
            "min_count": 3,
            "max_count": 10,
        },
        "expected_connections": {
            "min_count": 2,
        },
        "test_focus": ["Service disambiguation", "Document Intelligence type", "Multi-AI service coordination"],
    },
    "C14-post-deploy-delta-pe-add": {
        "name": "Post-Deploy Delta (Add PE)",
        "group": "edge",
        "level": 4,
        "user_request": "방금 배포한 RAG 아키텍처에 Private Endpoint를 추가하고 싶어.",
        "user_choices": [
            {"question_pattern": "서비스|어떤.*PE", "answer": "Foundry, Search, Storage, Key Vault 전부"},
            {"question_pattern": "VNet|CIDR", "answer": "10.0.0.0/16"},
            {"question_pattern": "확인|proceed", "answer": "진행해줘"},
        ],
        "expected_path": "A",
        "expected_services": {
            "required_types": ["ai_foundry", "ai_search", "storage", "keyvault"],
            "min_count": 5,
            "max_count": 18,
            "must_have_private": True,
        },
        "expected_connections": {
            "min_count": 4,
            "must_have_type": "private",
        },
        "expected_vnet": True,
        "test_focus": ["Delta Confirmation Rule (Phase 1, not Phase 0)", "publicNetworkAccess: Disabled", "PE addition to existing"],
    },

    # ── Level 5: Maximum Complexity (6 scenarios) ──
    "C15-enterprise-data-platform": {
        "name": "Enterprise Data Platform (Full Stack)",
        "group": "max",
        "level": 5,
        "user_request": "엔터프라이즈 데이터 플랫폼 만들어줘. Fabric + Databricks + ADLS + ADF + SQL + Key Vault + PE 전부. 3개 RG로 나눠줘.",
        "user_choices": [
            {"question_pattern": "지역|region", "answer": "East US 2"},
            {"question_pattern": "이름|프로젝트", "answer": "data-platform-enterprise"},
            {"question_pattern": "RG.*분리|리소스.*그룹", "answer": "rg-data (Fabric, Databricks, ADLS), rg-etl (ADF, SQL), rg-security (KV)"},
            {"question_pattern": "Fabric.*SKU|용량", "answer": "F64"},
            {"question_pattern": "관리자|admin", "answer": "admin@contoso.com"},
            {"question_pattern": "PE|프라이빗", "answer": "전부 PE 적용"},
            {"question_pattern": "VNet|CIDR", "answer": "10.0.0.0/16"},
        ],
        "expected_path": "A",
        "expected_services": {
            "required_types": ["fabric", "databricks", "storage", "data_factory", "sql_database", "keyvault"],
            "min_count": 6,
            "max_count": 20,
        },
        "expected_connections": {
            "min_count": 5,
        },
        "expected_vnet": True,
        "expected_hierarchy": True,
        "test_focus": ["Multi-RG hierarchy", "Fabric admin email", "Databricks VNet", "6+ service PE", "ADLS dual PE"],
    },
    "C16-multi-sub-ai-data-mesh": {
        "name": "Multi-Subscription AI Data Mesh",
        "group": "max",
        "level": 5,
        "user_request": "데이터 메시 아키텍처를 만들어줘. 플랫폼 구독에 Foundry + Fabric, 도메인별 구독 2개에 각각 ADLS + ADF + SQL.",
        "user_choices": [
            {"question_pattern": "이름|프로젝트", "answer": "data-mesh"},
            {"question_pattern": "구독|subscription", "answer": "platform-sub, domain-sales-sub, domain-finance-sub"},
            {"question_pattern": "RG", "answer": "각 구독마다 rg-data, rg-security"},
            {"question_pattern": "지역|region", "answer": "East US 2"},
            {"question_pattern": "PE|프라이빗", "answer": "플랫폼 구독만 PE 적용"},
        ],
        "expected_path": "A",
        "expected_services": {
            "required_types": ["ai_foundry", "fabric", "storage", "data_factory", "sql_database", "keyvault"],
            "min_count": 10,
            "max_count": 30,
        },
        "expected_connections": {
            "min_count": 8,
        },
        "expected_hierarchy": True,
        "test_focus": ["3-subscription hierarchy", "Cross-sub data flow", "Selective PE", "Domain isolation"],
    },
    "C17-mission-critical-aks-multi-region": {
        "name": "Mission-Critical AKS Multi-Region",
        "group": "max",
        "level": 5,
        "user_request": "미션 크리티컬 AKS를 만들어줘. East US + West Europe 2개 리전, Front Door로 글로벌 로드밸런싱, Cosmos DB 멀티리전.",
        "user_choices": [
            {"question_pattern": "이름|프로젝트", "answer": "mission-critical"},
            {"question_pattern": "구독|subscription", "answer": "global-sub, region-east-sub, region-west-sub"},
            {"question_pattern": "ACR", "answer": "글로벌 ACR 하나로 공유"},
            {"question_pattern": "Cosmos.*일관성|consistency", "answer": "Session consistency"},
            {"question_pattern": "모니터링", "answer": "App Insights + Log Analytics 양쪽 리전"},
        ],
        "expected_path": "A",
        "expected_services": {
            "required_types": ["aks", "front_door", "cosmos_db", "acr", "keyvault"],
            "min_count": 8,
            "max_count": 25,
        },
        "expected_connections": {
            "min_count": 6,
        },
        "expected_hierarchy": True,
        "test_focus": ["Multi-region AKS", "Front Door routing", "Cosmos DB multi-region", "Global ACR", "3-sub hierarchy"],
    },
    "C18-iot-streaming-analytics": {
        "name": "IoT + Streaming Analytics Full Stack",
        "group": "max",
        "level": 5,
        "user_request": "IoT 솔루션 만들어줘. IoT Hub → Stream Analytics → Cosmos DB + ADLS, Function App으로 알람, App Insights 모니터링.",
        "user_choices": [
            {"question_pattern": "지역|region", "answer": "East US 2"},
            {"question_pattern": "이름|프로젝트", "answer": "iot-analytics"},
            {"question_pattern": "디바이스.*수|scale", "answer": "S1 허브, 10만 디바이스"},
            {"question_pattern": "알람|alert", "answer": "Function App에서 Event Hub로 알림"},
            {"question_pattern": "PE|프라이빗", "answer": "IoT Hub, Cosmos DB, Storage만 PE"},
        ],
        "expected_path": "A",
        "expected_services": {
            "required_types": ["iot_hub", "stream_analytics", "cosmos_db", "storage", "function_app"],
            "min_count": 6,
            "max_count": 15,
        },
        "expected_connections": {
            "min_count": 5,
        },
        "test_focus": ["IoT Hub PE", "Stream Analytics job", "Event-driven Function", "Selective PE", "Hot+Cold path"],
    },
    "C19-hybrid-network-vpn-expressroute": {
        "name": "Hybrid Network (VPN + ExpressRoute)",
        "group": "max",
        "level": 5,
        "user_request": "하이브리드 네트워크 구성해줘. Hub VNet에 VPN Gateway + Firewall + Bastion. Spoke VNet에 App Service + SQL.",
        "user_choices": [
            {"question_pattern": "이름|프로젝트", "answer": "hybrid-network"},
            {"question_pattern": "Hub.*CIDR", "answer": "10.0.0.0/16"},
            {"question_pattern": "Spoke.*CIDR", "answer": "10.1.0.0/16"},
            {"question_pattern": "VPN|온프레미스", "answer": "S2S VPN, 온프레미스 CIDR 192.168.0.0/16"},
            {"question_pattern": "Firewall.*SKU", "answer": "Azure Firewall Premium"},
            {"question_pattern": "RG", "answer": "rg-hub, rg-workload"},
        ],
        "expected_path": "A",
        "expected_services": {
            "required_types": ["vpn_gateway", "firewall", "bastion", "app_service", "sql_database"],
            "min_count": 5,
            "max_count": 15,
        },
        "expected_connections": {
            "min_count": 4,
        },
        "expected_vnet": True,
        "expected_hierarchy": True,
        "test_focus": ["Hub-Spoke topology", "VPN Gateway config", "Firewall rules", "Bastion subnet", "VNet peering"],
    },
    "C20-ai-ml-full-lifecycle": {
        "name": "AI/ML Full Lifecycle Platform",
        "group": "max",
        "level": 5,
        "user_request": "AI/ML 전체 라이프사이클 플랫폼 만들어줘. Foundry + AI Hub + Databricks + ADLS + AI Search + Key Vault + Log Analytics + App Insights. 5개 RG로. PE 전부.",
        "user_choices": [
            {"question_pattern": "지역|region", "answer": "East US 2"},
            {"question_pattern": "이름|프로젝트", "answer": "ai-ml-platform"},
            {"question_pattern": "RG.*분리", "answer": "rg-foundry (Foundry+Search), rg-ml (AI Hub+Databricks), rg-data (ADLS), rg-security (KV), rg-monitor (Log Analytics+App Insights)"},
            {"question_pattern": "VNet|CIDR", "answer": "10.0.0.0/16"},
            {"question_pattern": "PE|프라이빗", "answer": "전부 PE 적용"},
            {"question_pattern": "모델|deployment", "answer": "GPT-4o + text-embedding-3-small"},
        ],
        "expected_path": "A",
        "expected_services": {
            "required_types": ["ai_foundry", "ai_search", "databricks", "storage", "keyvault", "log_analytics", "app_insights"],
            "min_count": 8,
            "max_count": 25,
        },
        "expected_connections": {
            "min_count": 7,
        },
        "expected_vnet": True,
        "expected_hierarchy": True,
        "test_focus": ["5-RG hierarchy", "Foundry vs AI Hub distinction", "8+ service PE", "ADLS dual PE", "AMPLS potential", "Full RBAC chain"],
    },
}

# Merge all scenarios
SCENARIOS = {**SCENARIOS_R1, **SCENARIOS_R2}


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
