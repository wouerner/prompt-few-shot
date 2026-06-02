.PHONY: help up down ps logs shell test test-unit test-bdd clean

# Cores para o output do help
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
RESET  := $(shell tput -Txterm sgr0)

help:
	@echo ""
	@echo "${YELLOW}Comandos disponíveis para desenvolvimento:${RESET}"
	@echo ""
	@echo "  ${GREEN}make up${RESET}          Inicia todos os serviços Docker em segundo plano (com build)"
	@echo "  ${GREEN}make down${RESET}        Para e remove todos os containers ativos"
	@echo "  ${GREEN}make ps${RESET}          Mostra o status de todos os containers"
	@echo "  ${GREEN}make logs${RESET}        Exibe os logs em tempo real do container da API"
	@echo "  ${GREEN}make shell${RESET}       Abre um terminal interativo (bash) no container da API"
	@echo ""
	@echo "${YELLOW}Comandos de Teste:${RESET}"
	@echo ""
	@echo "  ${GREEN}make test${RESET}        Executa todos os testes (Unitários + BDD) gerando relatórios"
	@echo "  ${GREEN}make test-unit${RESET}   Executa apenas os testes unitários (pytest)"
	@echo "  ${GREEN}make test-bdd${RESET}    Executa apenas os testes de comportamento BDD (behave)"
	@echo "  ${GREEN}make clean${RESET}       Limpa resultados e relatórios do Allure gerados localmente"
	@echo ""

up:
	docker compose up --build -d

down:
	docker compose down

ps:
	docker compose ps

logs:
	docker compose logs -f app

shell:
	docker compose exec app bash

test:
	docker compose exec app pytest --alluredir=allure-results
	docker compose exec app behave -f allure_behave.formatter:AllureFormatter -o allure-results tests/bdd

test-unit:
	docker compose exec app pytest --alluredir=allure-results

test-bdd:
	docker compose exec app behave -f allure_behave.formatter:AllureFormatter -o allure-results tests/bdd

clean:
	rm -rf allure-results/* allure-report/*
	@echo "Resultados e relatórios do Allure limpos!"
