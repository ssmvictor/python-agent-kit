---
name: erp-integration-patterns
description: ERP integration patterns for enterprise systems. Sync strategies, idempotency, key mapping, retry/DLQ patterns. Use for ERP-to-ERP integrations, service-to-DB sync, and enterprise data pipelines.
tier: enterprise
---

# ERP Integration Patterns

Padrões recorrentes para integrações ERP ↔ ERP, serviços ↔ DB, e pipelines de dados enterprise.

---

## 📋 Quando Usar

- Integração entre sistemas ERP (Sankhya, SAP, TOTVS)
- Sync de dados entre APIs externas e banco local
- Pipelines de importação/exportação
- Automação de processos com múltiplas fontes

---

## 🔑 Mapeamento de Chaves

### Princípios

1. **Chave Natural vs Surrogate**: Prefira chaves naturais (CNPJ, código produto) para integração
2. **Tabela de Correspondência**: Mantenha uma tabela `mapping_keys` para tradução entre sistemas
3. **Nullable Foreign Keys**: Nunca confie que o sistema externo terá a mesma FK

### Tabela de Correspondência

```sql
CREATE TABLE integration_key_mapping (
    id SERIAL PRIMARY KEY,
    source_system VARCHAR(50) NOT NULL,
    source_key VARCHAR(100) NOT NULL,
    target_system VARCHAR(50) NOT NULL,
    target_key VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(source_system, source_key, target_system, entity_type)
);
```

### Padrão Python

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class KeyMapping:
    source_system: str
    source_key: str
    target_system: str
    target_key: str
    entity_type: str

class KeyMapper:
    def __init__(self, db_connection):
        self.db = db_connection
        self._cache: dict[tuple, str] = {}
    
    def get_target_key(
        self, 
        source_system: str, 
        source_key: str, 
        target_system: str, 
        entity_type: str
    ) -> Optional[str]:
        cache_key = (source_system, source_key, target_system, entity_type)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        result = self.db.query(
            "SELECT target_key FROM integration_key_mapping WHERE ...",
            params=cache_key
        )
        if result:
            self._cache[cache_key] = result
        return result
```

---

## 🔄 Sync Incremental

### Estratégias

| Estratégia | Quando Usar | Complexidade |
|------------|-------------|--------------|
| **Last Modified** | Fonte tem campo updated_at | Baixa |
| **Watermark** | Fonte tem ID sequencial | Baixa |
| **Change Data Capture** | Alta performance, Oracle GoldenGate | Alta |
| **Full Diff** | Fonte sem controle de mudança | Média |

### Padrão Watermark

```python
from datetime import datetime
from typing import TypeVar, Generic
from dataclasses import dataclass

T = TypeVar('T')

@dataclass
class SyncState:
    entity_type: str
    last_sync_at: datetime
    last_watermark: str
    records_processed: int

class IncrementalSync(Generic[T]):
    def __init__(self, state_repository, source, target):
        self.state_repo = state_repository
        self.source = source
        self.target = target
    
    def sync(self, entity_type: str, batch_size: int = 1000) -> SyncState:
        state = self.state_repo.get_state(entity_type)
        watermark = state.last_watermark if state else None
        
        records = self.source.fetch_since(watermark, limit=batch_size)
        
        for record in records:
            self.target.upsert(record)
            watermark = record.id  # ou record.updated_at
        
        new_state = SyncState(
            entity_type=entity_type,
            last_sync_at=datetime.now(),
            last_watermark=watermark,
            records_processed=len(records)
        )
        self.state_repo.save_state(new_state)
        return new_state
```

---

## 🔁 Idempotência

### Princípios

1. **Chave de Idempotência**: Toda operação deve ter uma chave única
2. **Deduplicação**: Verificar antes de inserir
3. **Upsert Seguro**: Usar `ON CONFLICT DO UPDATE`

### Padrão Upsert

```python
def upsert_record(self, record: dict, natural_key: str) -> bool:
    """
    Upsert seguro usando chave natural.
    Retorna True se inseriu, False se atualizou.
    """
    existing = self.db.query(
        f"SELECT id FROM {self.table} WHERE {natural_key} = ?",
        record[natural_key]
    )
    
    if existing:
        self.db.update(self.table, record, where={natural_key: record[natural_key]})
        return False
    else:
        self.db.insert(self.table, record)
        return True
```

### Padrão SQL (Oracle/PostgreSQL)

```sql
-- PostgreSQL
INSERT INTO produtos (codigo, nome, preco)
VALUES (:codigo, :nome, :preco)
ON CONFLICT (codigo) DO UPDATE SET
    nome = EXCLUDED.nome,
    preco = EXCLUDED.preco,
    updated_at = NOW();

-- Oracle
MERGE INTO produtos dest
USING (SELECT :codigo as codigo, :nome as nome, :preco as preco FROM dual) src
ON (dest.codigo = src.codigo)
WHEN MATCHED THEN UPDATE SET dest.nome = src.nome, dest.preco = src.preco
WHEN NOT MATCHED THEN INSERT (codigo, nome, preco) VALUES (src.codigo, src.nome, src.preco);
```

---

## 🔄 Retry e Dead Letter Queue

### Princípios

1. **Exponential Backoff**: Aumentar tempo entre retries
2. **Max Retries**: Definir limite (geralmente 3-5)
3. **DLQ**: Mover para fila de falhas após max retries
4. **Alertas**: Notificar quando DLQ cresce

### Padrão Python

```python
import time
from dataclasses import dataclass
from typing import Callable, TypeVar
from functools import wraps

T = TypeVar('T')

@dataclass
class RetryConfig:
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0

def with_retry(config: RetryConfig):
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < config.max_retries:
                        delay = min(
                            config.base_delay * (config.exponential_base ** attempt),
                            config.max_delay
                        )
                        time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator

# Uso
@with_retry(RetryConfig(max_retries=3))
def sync_record(record: dict) -> bool:
    # lógica de sync
    pass
```

---

## 📊 Observabilidade

### Logs Estruturados

```python
import logging
import json
from datetime import datetime
from typing import Any

class IntegrationLogger:
    def __init__(self, integration_name: str):
        self.logger = logging.getLogger(integration_name)
        self.integration_name = integration_name
    
    def log_sync(
        self,
        entity_type: str,
        action: str,
        record_id: str,
        success: bool,
        details: dict[str, Any] = None
    ):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "integration": self.integration_name,
            "entity_type": entity_type,
            "action": action,
            "record_id": record_id,
            "success": success,
            "details": details or {}
        }
        
        if success:
            self.logger.info(json.dumps(log_entry))
        else:
            self.logger.error(json.dumps(log_entry))
```

### Métricas Essenciais

| Métrica | Descrição |
|---------|-----------|
| `integration.records_synced` | Registros sincronizados por entidade |
| `integration.errors` | Erros por tipo e entidade |
| `integration.latency_ms` | Tempo de sync por batch |
| `integration.dlq_size` | Tamanho da fila de erros |

---

## 📝 Contrato de Integração

### Template

```yaml
integration:
  name: "sankhya-to-pamcard"
  version: "1.0.0"
  
entities:
  - name: "produto"
    source:
      system: "sankhya"
      table: "TGFPRO"
      key: "CODPROD"
    target:
      system: "pamcard"
      endpoint: "/api/produtos"
      key: "codigo"
    mapping:
      - source: "CODPROD"
        target: "codigo"
      - source: "DESCRPROD"
        target: "descricao"
      - source: "VLRVENDA"
        target: "preco"
    
sync:
  strategy: "incremental"
  watermark_field: "DTALTER"
  batch_size: 500
  schedule: "0 */2 * * *"  # A cada 2 horas
  
error_handling:
  max_retries: 3
  dlq_table: "integration_dlq"
  alert_threshold: 100
```

---

## ⚠️ Anti-Patterns

| ❌ Evitar | ✅ Fazer |
|-----------|----------|
| Sync completo sempre | Usar watermark/incremental |
| Confiar em IDs externos | Mapear para chaves locais |
| Ignorar falhas | DLQ + alertas |
| Logs texto livre | Logs estruturados JSON |
| Hardcode de endpoints | Config externa (env/yaml) |
