from fastapi.testclient import TestClient
from app.main import app, employees_db, vacation_requests_db, users_db, hash_password, create_access_token, Employee, VacationRequest
import app.main as main_module

def before_scenario(context, scenario):
    # Reiniciar o banco de dados em memória para garantir isolamento e consistência
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
    
    # Colocar o TestClient no contexto para uso nos steps
    context.client = TestClient(app)
    
    # Helper para autenticação durante o teste BDD
    def auth_as(username: str, role: str, employee_id: int = None):
        token = create_access_token(data={"sub": username, "role": role, "employee_id": employee_id})
        context.client.headers.update({"Authorization": f"Bearer {token}"})
        
    context.auth_as = auth_as
