import pytest
from fastapi.testclient import TestClient
from app.main import app, employees_db, vacation_requests_db, users_db, hash_password, create_access_token, Employee, VacationRequest
import app.main as main_module

client = TestClient(app)

# Helper function to generate auth headers for test client
def get_auth_headers(username: str, role: str, employee_id: int = None):
    token = create_access_token(data={"sub": username, "role": role, "employee_id": employee_id})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(autouse=True)
def reset_db():
    # Limpar e repopular os dicionários globais para manter as referências
    employees_db.clear()
    employees_db.update({
        1: Employee(id=1, name="João Silva", role="Engenheiro de Software", hire_date="2023-01-15", total_vacation_days=30, vacation_days_taken=10, vacation_days_left=20),
        2: Employee(id=2, name="Maria Oliveira", role="Tech Lead", hire_date="2022-05-10", total_vacation_days=30, vacation_days_taken=0, vacation_days_left=30),
        3: Employee(id=3, name="Carlos Souza", role="Product Manager", hire_date="2024-03-01", total_vacation_days=30, vacation_days_taken=5, vacation_days_left=25)
    })
    
    vacation_requests_db.clear()
    vacation_requests_db.update({
        1: VacationRequest(id=1, employee_id=1, start_date="2025-01-02", end_date="2025-01-11", days=10, status="APPROVED"),
        2: VacationRequest(id=2, employee_id=2, start_date="2026-07-01", end_date="2026-07-15", days=15, status="PENDING"),
        3: VacationRequest(id=3, employee_id=3, start_date="2025-04-10", end_date="2025-04-14", days=5, status="APPROVED"),
        4: VacationRequest(id=4, employee_id=3, start_date="2026-12-20", end_date="2027-01-05", days=17, status="PENDING")
    })
    
    users_db.clear()
    users_db.update({
        "admin": {
            "username": "admin",
            "hashed_password": hash_password("admin123"),
            "role": "ADMIN",
            "employee_id": None
        },
        "joao": {
            "username": "joao",
            "hashed_password": hash_password("joao123"),
            "role": "EMPLOYEE",
            "employee_id": 1
        },
        "maria": {
            "username": "maria",
            "hashed_password": hash_password("maria123"),
            "role": "EMPLOYEE",
            "employee_id": 2
        },
        "carlos": {
            "username": "carlos",
            "hashed_password": hash_password("carlos123"),
            "role": "EMPLOYEE",
            "employee_id": 3
        }
    })
    
    main_module.employee_id_counter = 4
    main_module.vacation_id_counter = 5
    yield

# ==========================================
# TESTES DE AUTENTICAÇÃO (AUTH)
# ==========================================

def test_login_success():
    payload = {"username": "joao", "password": "joao123"}
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == "joao"
    assert data["user"]["role"] == "EMPLOYEE"
    assert data["user"]["employee_id"] == 1

def test_login_invalid_credentials():
    payload = {"username": "joao", "password": "wrongpassword"}
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Usuário ou senha incorretos"

def test_get_me_success():
    headers = get_auth_headers("maria", "EMPLOYEE", 2)
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "maria"
    assert data["role"] == "EMPLOYEE"
    assert data["employee_id"] == 2

def test_get_me_unauthorized():
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

# ==========================================
# TESTES DE FUNCIONÁRIOS (EMPLOYEES)
# ==========================================

def test_list_employees():
    headers = get_auth_headers("admin", "ADMIN")
    response = client.get("/api/v1/employees", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["name"] == "João Silva"

def test_get_employee_exists_admin():
    headers = get_auth_headers("admin", "ADMIN")
    response = client.get("/api/v1/employees/1", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1

def test_get_employee_exists_self():
    headers = get_auth_headers("joao", "EMPLOYEE", 1)
    response = client.get("/api/v1/employees/1", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1

def test_get_employee_exists_other_denied():
    headers = get_auth_headers("joao", "EMPLOYEE", 1)
    response = client.get("/api/v1/employees/2", headers=headers)
    assert response.status_code == 403
    assert "Você não tem permissão" in response.json()["detail"]

def test_get_employee_not_exists():
    headers = get_auth_headers("admin", "ADMIN")
    response = client.get("/api/v1/employees/99", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Funcionário não encontrado"

def test_create_employee_success():
    headers = get_auth_headers("admin", "ADMIN")
    payload = {
        "name": "Ana Souza",
        "role": "Designer",
        "hire_date": "2025-01-10",
        "total_vacation_days": 30
    }
    response = client.post("/api/v1/employees", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 4
    assert data["name"] == "Ana Souza"
    assert "ana" in users_db

def test_create_employee_denied_for_employee():
    headers = get_auth_headers("joao", "EMPLOYEE", 1)
    payload = {
        "name": "Ana Souza",
        "role": "Designer",
        "hire_date": "2025-01-10",
        "total_vacation_days": 30
    }
    response = client.post("/api/v1/employees", json=payload, headers=headers)
    assert response.status_code == 403

def test_create_employee_invalid_date():
    headers = get_auth_headers("admin", "ADMIN")
    payload = {
        "name": "Ana Souza",
        "role": "Designer",
        "hire_date": "10/01/2025",
        "total_vacation_days": 30
    }
    response = client.post("/api/v1/employees", json=payload, headers=headers)
    assert response.status_code == 422

def test_update_employee():
    headers = get_auth_headers("admin", "ADMIN")
    payload = {
        "name": "João Silva Alterado",
        "role": "Engenheiro Principal",
        "hire_date": "2023-01-15",
        "total_vacation_days": 35
    }
    response = client.put("/api/v1/employees/1", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "João Silva Alterado"
    assert data["vacation_days_left"] == 25

def test_delete_employee():
    headers = get_auth_headers("admin", "ADMIN")
    response = client.delete("/api/v1/employees/3", headers=headers)
    assert response.status_code == 204
    assert 3 not in employees_db
    assert "carlos" not in users_db

# ==========================================
# TESTES DE SOLICITAÇÃO DE FÉRIAS (VACATIONS)
# ==========================================

def test_list_vacations_admin():
    headers = get_auth_headers("admin", "ADMIN")
    response = client.get("/api/v1/vacations", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 4

def test_list_vacations_employee_limited():
    headers = get_auth_headers("joao", "EMPLOYEE", 1)
    response = client.get("/api/v1/vacations", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["employee_id"] == 1

def test_request_vacation_success():
    headers = get_auth_headers("maria", "EMPLOYEE", 2)
    payload = {
        "employee_id": 2,
        "start_date": "2026-12-01",
        "end_date": "2026-12-10"
    }
    response = client.post("/api/v1/vacations", json=payload, headers=headers)
    assert response.status_code == 201
    assert response.json()["id"] == 5

def test_request_vacation_for_other_denied():
    headers = get_auth_headers("joao", "EMPLOYEE", 1)
    payload = {
        "employee_id": 2,
        "start_date": "2026-12-01",
        "end_date": "2026-12-10"
    }
    response = client.post("/api/v1/vacations", json=payload, headers=headers)
    assert response.status_code == 403

def test_request_vacation_employee_not_found():
    headers = get_auth_headers("admin", "ADMIN")
    payload = {
        "employee_id": 99,
        "start_date": "2026-12-01",
        "end_date": "2026-12-10"
    }
    response = client.post("/api/v1/vacations", json=payload, headers=headers)
    assert response.status_code == 404

def test_request_vacation_invalid_dates():
    headers = get_auth_headers("maria", "EMPLOYEE", 2)
    payload = {
        "employee_id": 2,
        "start_date": "2026-12-10",
        "end_date": "2026-12-01"
    }
    response = client.post("/api/v1/vacations", json=payload, headers=headers)
    assert response.status_code == 400

def test_request_vacation_insufficient_balance():
    headers = get_auth_headers("joao", "EMPLOYEE", 1)
    payload = {
        "employee_id": 1,
        "start_date": "2026-01-01",
        "end_date": "2026-01-25"
    }
    response = client.post("/api/v1/vacations", json=payload, headers=headers)
    assert response.status_code == 400

def test_request_vacation_overlap():
    headers = get_auth_headers("maria", "EMPLOYEE", 2)
    payload = {
        "employee_id": 2,
        "start_date": "2026-07-10",
        "end_date": "2026-07-20"
    }
    response = client.post("/api/v1/vacations", json=payload, headers=headers)
    assert response.status_code == 400

# ==========================================
# TESTES DE STATUS E EXCLUSÃO DE FÉRIAS
# ==========================================

def test_approve_vacation_success():
    headers = get_auth_headers("admin", "ADMIN")
    response = client.patch("/api/v1/vacations/2/status", json={"status": "APPROVED"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "APPROVED"
    assert employees_db[2].vacation_days_left == 15

def test_approve_vacation_denied_for_employee():
    headers = get_auth_headers("maria", "EMPLOYEE", 2)
    response = client.patch("/api/v1/vacations/2/status", json={"status": "APPROVED"}, headers=headers)
    assert response.status_code == 403

def test_approve_vacation_insufficient_balance():
    headers = get_auth_headers("admin", "ADMIN")
    employees_db[3].vacation_days_left = 10
    response = client.patch("/api/v1/vacations/4/status", json={"status": "APPROVED"}, headers=headers)
    assert response.status_code == 400

def test_reject_vacation_restores_balance():
    headers = get_auth_headers("admin", "ADMIN")
    response = client.patch("/api/v1/vacations/1/status", json={"status": "REJECTED"}, headers=headers)
    assert response.status_code == 200
    assert employees_db[1].vacation_days_left == 30

def test_delete_vacation_approved_admin():
    headers = get_auth_headers("admin", "ADMIN")
    response = client.delete("/api/v1/vacations/1", headers=headers)
    assert response.status_code == 204
    assert 1 not in vacation_requests_db

def test_delete_vacation_pending_own_employee():
    headers = get_auth_headers("maria", "EMPLOYEE", 2)
    # vacation 2 is PENDING and belongs to employee 2 (maria)
    response = client.delete("/api/v1/vacations/2", headers=headers)
    assert response.status_code == 204
    assert 2 not in vacation_requests_db

def test_delete_vacation_approved_own_employee_denied():
    headers = get_auth_headers("joao", "EMPLOYEE", 1)
    # vacation 1 is APPROVED and belongs to employee 1 (joao). Employees cannot delete approved requests.
    response = client.delete("/api/v1/vacations/1", headers=headers)
    assert response.status_code == 400
    assert "ainda estão pendentes" in response.json()["detail"].lower()
