# language: pt
Funcionalidade: Fluxo de Aprovação de Férias do Empregado
  Como um gestor de recursos humanos
  Quero gerenciar as solicitações de férias dos empregados
  Para que o saldo de férias seja debitado corretamente após a aprovação

  Contexto:
    Dado que existe um empregado cadastrado com os seguintes dados:
      | nome           | cargo                 | data_contratacao | total_dias |
      | Roberto Santos | Engenheiro de Software | 2023-01-15       | 30         |

  Cenário: Solicitação de férias criada com status pendente
    Dado que o empregado de nome "Roberto Santos" possui 30 dias de férias disponíveis
    Quando ele solicita férias de "2026-12-01" a "2026-12-10"
    Então uma nova solicitação de férias deve ser criada com status "PENDING" de 10 dias
    E o saldo de férias disponíveis do empregado deve permanecer 30 dias

  Cenário: Aprovação de solicitação de férias debita o saldo
    Dado que existe uma solicitação de férias "PENDING" de "2026-12-01" a "2026-12-10" (10 dias) para o empregado "Roberto Santos"
    Quando o gestor aprova a solicitação de férias
    Então o status da solicitação deve ser alterado para "APPROVED"
    E o saldo de férias do empregado deve ser atualizado para 20 dias disponíveis e 10 dias tirados

  Cenário: Rejeição de solicitação de férias aprovada estorna o saldo
    Dado que existe uma solicitação de férias "APPROVED" de "2026-12-01" a "2026-12-10" (10 dias) para o empregado "Roberto Santos"
    Quando o gestor rejeita a solicitação de férias
    Então o status da solicitação deve ser alterado para "REJECTED"
    E o saldo de férias do empregado deve ser estornado para 30 dias disponíveis e 0 dias tirados
