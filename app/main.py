import os
import math
from datetime import datetime, date, timedelta, timezone
from typing import List, Dict, Optional, Literal
import jwt
import hashlib
import secrets
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, field_validator

app = FastAPI(
    title="API de Gerenciamento de Férias",
    description="API simples para gerenciamento de férias de funcionários, utilizada para demonstrar Engenharia de Prompt Few-Shot.",
    version="1.0.0",
)

# CORS setup for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# MODELOS PYDANTIC (SCHEMAS)
# ==========================================

class EmployeeBase(BaseModel):
    name: str = Field(..., examples=["João Silva"])
    role: str = Field(..., examples=["Engenheiro de Software"])
    hire_date: str = Field(..., examples=["2023-01-15"])
    total_vacation_days: int = Field(30, ge=0, examples=[30])

    @field_validator("hire_date")
    @classmethod
    def validate_date(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("A data de contratação (hire_date) deve estar no formato AAAA-MM-DD")

class EmployeeCreate(EmployeeBase):
    pass

class Employee(EmployeeBase):
    id: int
    vacation_days_taken: int = 0
    vacation_days_left: int = 30

class VacationRequestBase(BaseModel):
    employee_id: int = Field(..., examples=[1])
    start_date: str = Field(..., examples=["2026-12-20"])
    end_date: str = Field(..., examples=["2027-01-05"])

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_dates(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("As datas devem estar no formato AAAA-MM-DD")

class VacationRequestCreate(VacationRequestBase):
    pass

class VacationRequest(VacationRequestBase):
    id: int
    days: int
    status: Literal["PENDING", "APPROVED", "REJECTED"] = "PENDING"

class StatusUpdate(BaseModel):
    status: Literal["APPROVED", "REJECTED"] = Field(..., examples=["APPROVED"])

class LoginRequest(BaseModel):
    username: str = Field(..., examples=["joao"])
    password: str = Field(..., examples=["joao123"])

class UserResponse(BaseModel):
    username: str
    role: Literal["ADMIN", "EMPLOYEE"]
    employee_id: Optional[int] = None

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# ==========================================
# SEGURANÇA E AUTENTICAÇÃO (JWT & HASHING)
# ==========================================

SECRET_KEY = "supersecretkeyforvacationsapp-at-least-32-bytes"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

security = HTTPBearer()

def hash_password(password: str) -> str:
    # Usando 10.000 iterações para os testes rodarem rápido
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 10000)
    return f"{salt}${dk.hex()}"

def verify_password(password: str, hashed: str) -> bool:
    try:
        salt, hash_hex = hashed.split('$')
        dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 10000)
        return dk.hex() == hash_hex
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de autenticação inválido ou ausente",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = users_db.get(username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_admin_user(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user["role"] != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores podem realizar esta ação."
        )
    return current_user

# ==========================================
# BANCO DE DADOS EM MEMÓRIA (SEED DATA)
# ==========================================

employees_db: Dict[int, Employee] = {
    1: Employee(id=1, name="João Silva", role="Engenheiro de Software", hire_date="2023-01-15", total_vacation_days=30, vacation_days_taken=10, vacation_days_left=20),
    2: Employee(id=2, name="Maria Oliveira", role="Tech Lead", hire_date="2022-05-10", total_vacation_days=30, vacation_days_taken=0, vacation_days_left=30),
    3: Employee(id=3, name="Carlos Souza", role="Product Manager", hire_date="2024-03-01", total_vacation_days=30, vacation_days_taken=5, vacation_days_left=25)
}

vacation_requests_db: Dict[int, VacationRequest] = {
    1: VacationRequest(id=1, employee_id=1, start_date="2025-01-02", end_date="2025-01-11", days=10, status="APPROVED"),
    2: VacationRequest(id=2, employee_id=2, start_date="2026-07-01", end_date="2026-07-15", days=15, status="PENDING"),
    3: VacationRequest(id=3, employee_id=3, start_date="2025-04-10", end_date="2025-04-14", days=5, status="APPROVED"),
    4: VacationRequest(id=4, employee_id=3, start_date="2026-12-20", end_date="2027-01-05", days=17, status="PENDING")
}

users_db: Dict[str, dict] = {
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
}

employee_id_counter = 4
vacation_id_counter = 5

# Helper functions
def calculate_days(start_str: str, end_str: str) -> int:
    start = datetime.strptime(start_str, "%Y-%m-%d").date()
    end = datetime.strptime(end_str, "%Y-%m-%d").date()
    return (end - start).days + 1

def dates_overlap(start1_str: str, end1_str: str, start2_str: str, end2_str: str) -> bool:
    start1 = datetime.strptime(start1_str, "%Y-%m-%d").date()
    end1 = datetime.strptime(end1_str, "%Y-%m-%d").date()
    start2 = datetime.strptime(start2_str, "%Y-%m-%d").date()
    end2 = datetime.strptime(end2_str, "%Y-%m-%d").date()
    return start1 <= end2 and start2 <= end1

# ==========================================
# ENDPOINTS DA API: AUTENTICAÇÃO
# ==========================================

@app.post("/api/v1/auth/login", response_model=LoginResponse, tags=["Autenticação"])
def login(req: LoginRequest):
    user = users_db.get(req.username)
    if not user or not verify_password(req.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos"
        )
    
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"], "employee_id": user["employee_id"]}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": user["username"],
            "role": user["role"],
            "employee_id": user["employee_id"]
        }
    }

@app.get("/api/v1/auth/me", response_model=UserResponse, tags=["Autenticação"])
def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "username": current_user["username"],
        "role": current_user["role"],
        "employee_id": current_user["employee_id"]
    }

# ==========================================
# ENDPOINTS DA API: FUNCIONÁRIOS
# ==========================================

@app.get("/api/v1/employees", response_model=List[Employee], tags=["Funcionários"])
def list_employees(current_user: dict = Depends(get_current_user)):
    """Retorna a lista de todos os funcionários cadastrados."""
    return list(employees_db.values())

@app.get("/api/v1/employees/{employee_id}", response_model=Employee, tags=["Funcionários"])
def get_employee(employee_id: int, current_user: dict = Depends(get_current_user)):
    """Retorna os dados de um funcionário específico pelo seu ID."""
    if current_user["role"] != "ADMIN" and current_user["employee_id"] != employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para visualizar os dados de outro funcionário."
        )
    if employee_id not in employees_db:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    return employees_db[employee_id]

@app.post("/api/v1/employees", response_model=Employee, status_code=status.HTTP_201_CREATED, tags=["Funcionários"])
def create_employee(employee_in: EmployeeCreate, current_user: dict = Depends(get_admin_user)):
    """Cadastra um novo funcionário e calcula o saldo de férias inicial."""
    global employee_id_counter
    emp_id = employee_id_counter
    employee_id_counter += 1
    
    new_employee = Employee(
        id=emp_id,
        name=employee_in.name,
        role=employee_in.role,
        hire_date=employee_in.hire_date,
        total_vacation_days=employee_in.total_vacation_days,
        vacation_days_taken=0,
        vacation_days_left=employee_in.total_vacation_days
    )
    employees_db[emp_id] = new_employee
    
    # Auto-gerar credenciais: username é o primeiro nome em minúsculo (limpo)
    first_name = employee_in.name.split()[0].lower()
    username = first_name
    counter = 1
    while username in users_db:
        username = f"{first_name}{counter}"
        counter += 1
        
    users_db[username] = {
        "username": username,
        "hashed_password": hash_password("123456"),
        "role": "EMPLOYEE",
        "employee_id": emp_id
    }
    
    return new_employee

@app.put("/api/v1/employees/{employee_id}", response_model=Employee, tags=["Funcionários"])
def update_employee(employee_id: int, employee_in: EmployeeCreate, current_user: dict = Depends(get_admin_user)):
    """Atualiza as informações de um funcionário específico."""
    if employee_id not in employees_db:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    
    emp = employees_db[employee_id]
    emp.name = employee_in.name
    emp.role = employee_in.role
    emp.hire_date = employee_in.hire_date
    emp.total_vacation_days = employee_in.total_vacation_days
    # Re-calculate left days
    emp.vacation_days_left = emp.total_vacation_days - emp.vacation_days_taken
    
    return emp

@app.delete("/api/v1/employees/{employee_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Funcionários"])
def delete_employee(employee_id: int, current_user: dict = Depends(get_admin_user)):
    """Remove um funcionário e todas as suas solicitações de férias."""
    if employee_id not in employees_db:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    
    # Remove from employees
    del employees_db[employee_id]
    
    # Clean up associated vacations
    to_delete = [vid for vid, vac in vacation_requests_db.items() if vac.employee_id == employee_id]
    for vid in to_delete:
        del vacation_requests_db[vid]
        
    # Remove from users_db
    users_to_delete = [uname for uname, u in users_db.items() if u["employee_id"] == employee_id]
    for uname in users_to_delete:
        del users_db[uname]
        
    return None

# ==========================================
# ENDPOINTS DA API: SOLICITAÇÃO DE FÉRIAS
# ==========================================

@app.get("/api/v1/vacations", response_model=List[VacationRequest], tags=["Férias"])
def list_vacations(employee_id: Optional[int] = None, current_user: dict = Depends(get_current_user)):
    """Retorna todas as solicitações de férias, podendo filtrar por funcionário."""
    if current_user["role"] == "ADMIN":
        if employee_id:
            return [v for v in vacation_requests_db.values() if v.employee_id == employee_id]
        return list(vacation_requests_db.values())
    else:
        # EMPLOYEE só vê as próprias férias
        emp_id = current_user["employee_id"]
        return [v for v in vacation_requests_db.values() if v.employee_id == emp_id]

@app.post("/api/v1/vacations", response_model=VacationRequest, status_code=status.HTTP_201_CREATED, tags=["Férias"])
def request_vacation(req: VacationRequestCreate, current_user: dict = Depends(get_current_user)):
    """
    Solicita férias para um funcionário.
    Aplica validações de dias disponíveis e conflitos de datas.
    """
    global vacation_id_counter
    
    # Regra de autorização: funcionário só pode solicitar para si mesmo
    if current_user["role"] != "ADMIN" and current_user["employee_id"] != req.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não pode solicitar férias para outro funcionário."
        )
    
    # 1. Verifica se funcionário existe
    if req.employee_id not in employees_db:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    
    emp = employees_db[req.employee_id]
    
    # 2. Valida datas
    start_date_obj = datetime.strptime(req.start_date, "%Y-%m-%d").date()
    end_date_obj = datetime.strptime(req.end_date, "%Y-%m-%d").date()
    
    if start_date_obj >= end_date_obj:
        raise HTTPException(status_code=400, detail="A data de início deve ser anterior à data de fim")
        
    days = (end_date_obj - start_date_obj).days + 1
    
    # 3. Verifica saldo de dias disponíveis
    if days > emp.vacation_days_left:
        raise HTTPException(
            status_code=400, 
            detail=f"Saldo insuficiente. O funcionário possui apenas {emp.vacation_days_left} dias disponíveis, mas solicitou {days} dias."
        )
        
    # 4. Verifica sobreposição de férias ativas (PENDING ou APPROVED)
    for existing in vacation_requests_db.values():
        if existing.employee_id == req.employee_id and existing.status in ["PENDING", "APPROVED"]:
            if dates_overlap(req.start_date, req.end_date, existing.start_date, existing.end_date):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Conflito de datas. O funcionário já tem férias solicitadas ou aprovadas para o período de {existing.start_date} a {existing.end_date}."
                )
                
    # 5. Salva a solicitação (por padrão criada como PENDING)
    vac_id = vacation_id_counter
    vacation_id_counter += 1
    
    new_request = VacationRequest(
        id=vac_id,
        employee_id=req.employee_id,
        start_date=req.start_date,
        end_date=req.end_date,
        days=days,
        status="PENDING"
    )
    vacation_requests_db[vac_id] = new_request
    return new_request

@app.patch("/api/v1/vacations/{vacation_id}/status", response_model=VacationRequest, tags=["Férias"])
def update_vacation_status(vacation_id: int, status_update: StatusUpdate, current_user: dict = Depends(get_admin_user)):
    """
    Aprova ou rejeita uma solicitação de férias.
    Ao aprovar, debita automaticamente os dias do saldo do funcionário.
    """
    if vacation_id not in vacation_requests_db:
        raise HTTPException(status_code=404, detail="Solicitação de férias não encontrada")
        
    req = vacation_requests_db[vacation_id]
    emp = employees_db[req.employee_id]
    
    new_status = status_update.status
    old_status = req.status
    
    if old_status == new_status:
        return req
        
    # Cenário 1: Mudando para APPROVED
    if new_status == "APPROVED":
        # Recalcula se o saldo ainda é suficiente (pode ter mudado)
        if req.days > emp.vacation_days_left:
            raise HTTPException(
                status_code=400,
                detail=f"Não é possível aprovar. O saldo atual do funcionário é de {emp.vacation_days_left} dias, e a solicitação é de {req.days} dias."
            )
        emp.vacation_days_taken += req.days
        emp.vacation_days_left = emp.total_vacation_days - emp.vacation_days_taken
        
    # Cenário 2: Mudando de APPROVED para REJECTED ou PENDING (restauração de saldo)
    elif old_status == "APPROVED" and new_status in ["REJECTED", "PENDING"]:
        emp.vacation_days_taken = max(0, emp.vacation_days_taken - req.days)
        emp.vacation_days_left = emp.total_vacation_days - emp.vacation_days_taken
        
    req.status = new_status
    return req

@app.delete("/api/v1/vacations/{vacation_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Férias"])
def delete_vacation(vacation_id: int, current_user: dict = Depends(get_current_user)):
    """Cancela uma solicitação de férias. Restaura o saldo de dias do funcionário se já estivesse aprovada."""
    if vacation_id not in vacation_requests_db:
        raise HTTPException(status_code=404, detail="Solicitação de férias não encontrada")
        
    req = vacation_requests_db[vacation_id]
    emp = employees_db[req.employee_id]
    
    # Regra de autorização: funcionário só pode cancelar suas próprias férias se estiverem PENDENTES
    if current_user["role"] != "ADMIN":
        if current_user["employee_id"] != req.employee_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para cancelar as férias de outro funcionário."
            )
        if req.status != "PENDING":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Você só pode cancelar solicitações de férias que ainda estão pendentes."
            )
              
    # Se estava aprovada, devolve os dias ao funcionário
    if req.status == "APPROVED":
        emp.vacation_days_taken = max(0, emp.vacation_days_taken - req.days)
        emp.vacation_days_left = emp.total_vacation_days - emp.vacation_days_taken
        
    del vacation_requests_db[vacation_id]
    return None


# ==========================================
# SPA E ARQUIVOS ESTÁTICOS
# ==========================================

# Rota para carregar o index.html principal
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def serve_index():
    static_file_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(static_file_path):
        with open(static_file_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Erro: Arquivo frontend não encontrado na pasta app/static!</h1>", status_code=404)

# Monta arquivos estáticos para CSS e JS
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")
