from behave import given, when, then

@given('que existe um empregado cadastrado com os seguintes dados:')
def step_impl(context):
    for row in context.table:
        payload = {
            "name": row['nome'],
            "role": row['cargo'],
            "hire_date": row['data_contratacao'],
            "total_vacation_days": int(row['total_dias'])
        }
        # Verifica se o empregado já existe para não duplicar se rodar múltiplas vezes,
        # mas como reiniciamos o banco antes do cenário, podemos cadastrar diretamente.
        response = context.client.post("/api/v1/employees", json=payload)
        assert response.status_code == 201, f"Falha ao criar empregado: {response.text}"
        data = response.json()
        context.employee_id = data["id"]
        context.employee_name = data["name"]

@given('que o empregado de nome "{nome}" possui {dias:d} dias de férias disponíveis')
def step_impl(context, nome, dias):
    # Buscar empregado por nome
    response = context.client.get("/api/v1/employees")
    assert response.status_code == 200
    employees = response.json()
    emp = next((e for e in employees if e["name"] == nome), None)
    assert emp is not None, f"Empregado {nome} não encontrado"
    assert emp["vacation_days_left"] == dias, f"Esperava {dias} dias disponíveis, mas tem {emp['vacation_days_left']}"
    context.employee_id = emp["id"]

@when('ele solicita férias de "{data_inicio}" a "{data_fim}"')
def step_impl(context, data_inicio, data_fim):
    payload = {
        "employee_id": context.employee_id,
        "start_date": data_inicio,
        "end_date": data_fim
    }
    response = context.client.post("/api/v1/vacations", json=payload)
    context.last_response = response
    if response.status_code == 201:
        context.vacation_id = response.json()["id"]

@then('uma nova solicitação de férias deve ser criada com status "{status}" de {dias:d} dias')
def step_impl(context, status, dias):
    assert context.last_response.status_code == 201, f"Esperava 201 Created, obteve {context.last_response.status_code}. Detalhe: {context.last_response.text}"
    data = context.last_response.json()
    assert data["status"] == status, f"Esperava status {status}, obteve {data['status']}"
    assert data["days"] == dias, f"Esperava {dias} dias, obteve {data['days']}"

@then('o saldo de férias disponíveis do empregado deve permanecer {dias:d} dias')
def step_impl(context, dias):
    response = context.client.get(f"/api/v1/employees/{context.employee_id}")
    assert response.status_code == 200
    assert response.json()["vacation_days_left"] == dias, f"Esperava {dias} dias restantes, obteve {response.json()['vacation_days_left']}"

@given('que existe uma solicitação de férias "{status}" de "{data_inicio}" a "{data_fim}" ({dias:d} dias) para o empregado "{nome}"')
def step_impl(context, status, data_inicio, data_fim, dias, nome):
    # Buscar empregado por nome
    response = context.client.get("/api/v1/employees")
    employees = response.json()
    emp = next((e for e in employees if e["name"] == nome), None)
    assert emp is not None, f"Empregado {nome} não encontrado"
    context.employee_id = emp["id"]
    
    # Solicitar férias (cria como PENDING)
    payload = {
        "employee_id": emp["id"],
        "start_date": data_inicio,
        "end_date": data_fim
    }
    response = context.client.post("/api/v1/vacations", json=payload)
    assert response.status_code == 201, f"Falha ao solicitar férias: {response.text}"
    vac = response.json()
    context.vacation_id = vac["id"]
    
    # Se o status do Gherkin for APPROVED, aprova a solicitação
    if status == "APPROVED":
        status_payload = {"status": "APPROVED"}
        app_res = context.client.patch(f"/api/v1/vacations/{context.vacation_id}/status", json=status_payload)
        assert app_res.status_code == 200, f"Falha ao aprovar férias: {app_res.text}"

@when('o gestor aprova a solicitação de férias')
def step_impl(context):
    payload = {"status": "APPROVED"}
    response = context.client.patch(f"/api/v1/vacations/{context.vacation_id}/status", json=payload)
    context.last_response = response

@when('o gestor rejeita a solicitação de férias')
def step_impl(context):
    payload = {"status": "REJECTED"}
    response = context.client.patch(f"/api/v1/vacations/{context.vacation_id}/status", json=payload)
    context.last_response = response

@then('o status da solicitação deve ser alterado para "{status}"')
def step_impl(context, status):
    assert context.last_response.status_code == 200, f"Esperava 200 OK, obteve {context.last_response.status_code}. Detalhe: {context.last_response.text}"
    assert context.last_response.json()["status"] == status, f"Esperava status {status}, obteve {context.last_response.json()['status']}"

@then('o saldo de férias do empregado deve ser atualizado para {disponiveis:d} dias disponíveis e {tirados:d} dias tirados')
def step_impl(context, disponiveis, tirados):
    response = context.client.get(f"/api/v1/employees/{context.employee_id}")
    assert response.status_code == 200
    emp = response.json()
    assert emp["vacation_days_left"] == disponiveis, f"Esperava {disponiveis} dias disponíveis, obteve {emp['vacation_days_left']}"
    assert emp["vacation_days_taken"] == tirados, f"Esperava {tirados} dias tirados, obteve {emp['vacation_days_taken']}"

@then('o saldo de férias do empregado deve ser estornado para {disponiveis:d} dias disponíveis e {tirados:d} dias tirados')
def step_impl(context, disponiveis, tirados):
    response = context.client.get(f"/api/v1/employees/{context.employee_id}")
    assert response.status_code == 200
    emp = response.json()
    assert emp["vacation_days_left"] == disponiveis, f"Esperava {disponiveis} dias disponíveis, obteve {emp['vacation_days_left']}"
    assert emp["vacation_days_taken"] == tirados, f"Esperava {tirados} dias tirados, obteve {emp['vacation_days_taken']}"
