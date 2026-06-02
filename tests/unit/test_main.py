import pytest
from fastapi.testclient import TestClient
from app.main import app, employees_db, vacation_requests_db, Employee, VacationRequest
import app.main as main_module

client = TestClient(app)

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
    
    main_module.employee_id_counter = 4
    main_module.vacation_id_counter = 5
    yield

# ==========================================
# TESTES DE FUNCIONÁRIOS (EMPLOYEES)
# ==========================================

def test_list_employees():
    # Arrange
    # O banco de dados é populado com 3 funcionários via fixture global `reset_db`

    # Act
    response = client.get("/api/v1/employees")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["name"] == "João Silva"


def test_get_employee_exists():
    # Arrange
    # O funcionário com ID 1 existe no banco de dados via fixture global `reset_db`
    employee_id = 1

    # Act
    response = client.get(f"/api/v1/employees/{employee_id}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == employee_id
    assert data["name"] == "João Silva"


def test_get_employee_not_exists():
    # Arrange
    # O ID 99 não existe no banco de dados
    employee_id = 99

    # Act
    response = client.get(f"/api/v1/employees/{employee_id}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Funcionário não encontrado"


def test_create_employee_success():
    # Arrange
    payload = {
        "name": "Ana Souza",
        "role": "Designer",
        "hire_date": "2025-01-10",
        "total_vacation_days": 30
    }

    # Act
    response = client.post("/api/v1/employees", json=payload)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 4
    assert data["name"] == "Ana Souza"
    assert data["vacation_days_left"] == 30
    assert data["vacation_days_taken"] == 0


def test_create_employee_invalid_date():
    # Arrange
    payload = {
        "name": "Ana Souza",
        "role": "Designer",
        "hire_date": "10/01/2025",  # Formato incorreto (deve ser AAAA-MM-DD)
        "total_vacation_days": 30
    }

    # Act
    response = client.post("/api/v1/employees", json=payload)

    # Assert
    # Erro de validação Pydantic (422)
    assert response.status_code == 422


def test_update_employee():
    # Arrange
    employee_id = 1
    payload = {
        "name": "João Silva Alterado",
        "role": "Engenheiro Principal",
        "hire_date": "2023-01-15",
        "total_vacation_days": 35
    }

    # Act
    response = client.put(f"/api/v1/employees/{employee_id}", json=payload)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "João Silva Alterado"
    assert data["role"] == "Engenheiro Principal"
    assert data["total_vacation_days"] == 35
    # Recálculo de saldo: total_vacation_days (35) - vacation_days_taken (10) = 25
    assert data["vacation_days_left"] == 25


def test_delete_employee():
    # Arrange
    # Deletar funcionário de ID 3 (que tem solicitações de férias 3 e 4)
    employee_id = 3

    # Act
    response = client.delete(f"/api/v1/employees/{employee_id}")

    # Assert
    assert response.status_code == 204
    # Garantir que o funcionário foi removido
    assert employee_id not in employees_db
    # Garantir que as férias associadas foram limpas
    assert 3 not in vacation_requests_db
    assert 4 not in vacation_requests_db


# ==========================================
# TESTES DE SOLICITAÇÃO DE FÉRIAS (VACATIONS)
# ==========================================

def test_list_vacations():
    # Arrange
    # O banco de dados é populado com 4 solicitações via fixture global `reset_db`

    # Act
    response = client.get("/api/v1/vacations")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4


def test_list_vacations_by_employee():
    # Arrange
    # O funcionário com ID 3 possui 2 solicitações registradas no banco via fixture global
    employee_id = 3

    # Act
    response = client.get(f"/api/v1/vacations?employee_id={employee_id}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    for vac in data:
        assert vac["employee_id"] == employee_id


def test_request_vacation_success():
    # Arrange
    payload = {
        "employee_id": 2,
        "start_date": "2026-12-01",
        "end_date": "2026-12-10"
    }

    # Act
    response = client.post("/api/v1/vacations", json=payload)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 5
    assert data["employee_id"] == 2
    assert data["days"] == 10  # 10 dias inclusive
    assert data["status"] == "PENDING"


def test_request_vacation_employee_not_found():
    # Arrange
    payload = {
        "employee_id": 99,
        "start_date": "2026-12-01",
        "end_date": "2026-12-10"
    }

    # Act
    response = client.post("/api/v1/vacations", json=payload)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Funcionário não encontrado"


def test_request_vacation_invalid_dates():
    # Arrange
    payload = {
        "employee_id": 2,
        "start_date": "2026-12-10",
        "end_date": "2026-12-01"  # Data fim anterior à início
    }

    # Act
    response = client.post("/api/v1/vacations", json=payload)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "A data de início deve ser anterior à data de fim"


def test_request_vacation_insufficient_balance():
    # Arrange
    # Funcionário 1 tem apenas 20 dias disponíveis
    payload = {
        "employee_id": 1,
        "start_date": "2026-01-01",
        "end_date": "2026-01-25"  # 25 dias solicitados
    }

    # Act
    response = client.post("/api/v1/vacations", json=payload)

    # Assert
    assert response.status_code == 400
    assert "Saldo insuficiente" in response.json()["detail"]


def test_request_vacation_overlap():
    # Arrange
    # Funcionário 2 já tem férias pendentes de 2026-07-01 a 2026-07-15
    payload = {
        "employee_id": 2,
        "start_date": "2026-07-10",
        "end_date": "2026-07-20"  # Conflita com as férias existentes
    }

    # Act
    response = client.post("/api/v1/vacations", json=payload)

    # Assert
    assert response.status_code == 400
    assert "Conflito de datas" in response.json()["detail"]


# ==========================================
# TESTES DE STATUS E EXCLUSÃO DE FÉRIAS
# ==========================================

def test_approve_vacation_success():
    # Arrange
    # Funcionário 2 tem 30 dias livres. Solicitação 2 tem 15 dias e está PENDING.
    vacation_id = 2
    payload = {"status": "APPROVED"}

    # Act
    response = client.patch(f"/api/v1/vacations/{vacation_id}/status", json=payload)

    # Assert
    assert response.status_code == 200
    assert response.json()["status"] == "APPROVED"
    # Verificar se saldo foi debitado
    emp = employees_db[2]
    assert emp.vacation_days_taken == 15
    assert emp.vacation_days_left == 15


def test_approve_vacation_insufficient_balance():
    # Arrange
    # Funcionário 3 tem 25 dias livres. Solicitação 4 tem 17 dias (PENDING).
    # Vamos artificialmente reduzir o saldo do funcionário 3
    employees_db[3].vacation_days_left = 10
    vacation_id = 4
    payload = {"status": "APPROVED"}

    # Act
    response = client.patch(f"/api/v1/vacations/{vacation_id}/status", json=payload)

    # Assert
    assert response.status_code == 400
    assert "Não é possível aprovar" in response.json()["detail"]


def test_reject_vacation_restores_balance():
    # Arrange
    # Solicitação 1 está APPROVED com 10 dias (Funcionário 1).
    # Vamos rejeitar essa solicitação e garantir que os dias foram estornados.
    vacation_id = 1
    payload = {"status": "REJECTED"}

    # Act
    response = client.patch(f"/api/v1/vacations/{vacation_id}/status", json=payload)

    # Assert
    assert response.status_code == 200
    assert response.json()["status"] == "REJECTED"
    # Verificar estorno no saldo
    emp = employees_db[1]
    assert emp.vacation_days_taken == 0
    assert emp.vacation_days_left == 30


def test_delete_vacation_approved():
    # Arrange
    # Deletar solicitação 1 (APPROVED, 10 dias, Funcionário 1).
    vacation_id = 1

    # Act
    response = client.delete(f"/api/v1/vacations/{vacation_id}")

    # Assert
    assert response.status_code == 204
    # Garantir exclusão
    assert vacation_id not in vacation_requests_db
    # Garantir estorno do saldo
    emp = employees_db[1]
    assert emp.vacation_days_taken == 0
    assert emp.vacation_days_left == 30
